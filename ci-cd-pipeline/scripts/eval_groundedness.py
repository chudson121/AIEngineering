#!/usr/bin/env python3
"""
eval_groundedness.py
====================
Runs DeepEval groundedness and hallucination tests.
Supports OpenAI, Azure OpenAI, and Anthropic judge models.
Logs results to MLflow.

Usage:
  python scripts/eval_groundedness.py \
    --dataset   evals/datasets/rag_golden_set.jsonl \
    --provider  openai|azure_openai|anthropic \
    --output    reports/groundedness_metrics.json \
    --mlflow-experiment groundedness-eval
"""

import argparse
import json
import os
from pathlib import Path

import mlflow
from deepeval import evaluate as deepeval_evaluate
from deepeval.metrics import (
    FaithfulnessMetric,
    HallucinationMetric,
    AnswerRelevancyMetric,
)
from deepeval.models import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCase
from rich.console import Console

console = Console()


def build_deepeval_model(provider: str):
    """Return a DeepEval-compatible LLM wrapper."""
    if provider == "azure_openai":
        from deepeval.models import AzureOpenAI as DeepEvalAzure
        return DeepEvalAzure(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
            deployment_id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            azure_api_key=os.environ["AZURE_OPENAI_API_KEY"],
        )
    elif provider == "anthropic":
        # DeepEval wraps any LangChain chat model
        from langchain_anthropic import ChatAnthropic
        from deepeval.models.base_model import DeepEvalBaseModel
        lc_model = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=os.environ["ANTHROPIC_API_KEY"],
            temperature=0,
        )
        # Use DeepEval's custom model wrapper
        return lc_model   # passed via custom_model param in metrics
    else:
        return "gpt-4o"   # DeepEval default string-based OpenAI selection


def load_test_cases(path: str) -> list[LLMTestCase]:
    cases = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            cases.append(
                LLMTestCase(
                    input=row["question"],
                    actual_output=row["answer"],
                    expected_output=row.get("expected_answer", ""),
                    retrieval_context=row.get("contexts", []),
                    context=row.get("contexts", []),
                )
            )
    return cases


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset",           required=True)
    ap.add_argument("--provider",          default="openai")
    ap.add_argument("--output",            required=True)
    ap.add_argument("--mlflow-experiment", default="groundedness-eval")
    ap.add_argument("--mlflow-run-name",   default="eval-run")
    args = ap.parse_args()

    test_cases = load_test_cases(args.dataset)
    model      = build_deepeval_model(args.provider)

    metrics = [
        FaithfulnessMetric(threshold=0.95, model=model, include_reason=True),
        HallucinationMetric(threshold=0.05, model=model),
        AnswerRelevancyMetric(threshold=0.85, model=model),
    ]

    console.print(f"[bold cyan]Running DeepEval on {len(test_cases)} test cases...[/]")

    mlflow.set_experiment(args.mlflow_experiment)
    with mlflow.start_run(run_name=args.mlflow_run_name) as run:
        mlflow.set_tag("provider", args.provider)

        results = deepeval_evaluate(test_cases, metrics)

        # Aggregate scores
        scores = {
            "faithfulness":         0.0,
            "hallucination_rate":   0.0,
            "answer_relevancy":     0.0,
            "unsupported_claim_rate": 0.0,
        }

        for tc in test_cases:
            for metric in metrics:
                scores["faithfulness"]       += getattr(metric, "score", 0) if "Faithfulness" in type(metric).__name__ else 0
                scores["hallucination_rate"] += getattr(metric, "score", 0) if "Hallucination" in type(metric).__name__ else 0

        n = max(len(test_cases), 1)
        scores = {k: v / n for k, v in scores.items()}

        for name, value in scores.items():
            mlflow.log_metric(name, value)

        output = {
            "metrics": scores,
            "run_id":  run.info.run_id,
            "provider": args.provider,
            "test_case_count": len(test_cases),
        }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)

    console.print(f"[green]✅ Groundedness metrics saved → {args.output}[/]")


if __name__ == "__main__":
    main()
