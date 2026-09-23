#!/usr/bin/env python3
"""
eval_retrieval.py
=================
Runs RAGAS retrieval evaluation against a labeled dataset.
Supports OpenAI, Azure OpenAI, and Anthropic judge models.
Logs results to MLflow and optionally LangSmith.

Usage:
  python scripts/eval_retrieval.py \
    --dataset   evals/datasets/rag_golden_set.jsonl \
    --provider  openai|azure_openai|anthropic \
    --metrics   context_recall,context_precision,context_relevancy \
    --output    reports/retrieval_metrics.json \
    --mlflow-experiment retrieval-eval \
    --mlflow-run-name   <git-sha>-retrieval
"""

import argparse
import json
import os
from pathlib import Path

import mlflow
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    ContextPrecision,
    ContextRecall,
    ContextRelevancy,
    Faithfulness,
    AnswerRelevancy,
)
from rich.console import Console

console = Console()

METRIC_MAP = {
    "context_recall":    ContextRecall(),
    "context_precision": ContextPrecision(),
    "context_relevancy": ContextRelevancy(),
    "faithfulness":      Faithfulness(),
    "answer_relevancy":  AnswerRelevancy(),
}


def build_llm(provider: str):
    """Return a LangChain chat model based on the provider env var."""
    if provider == "azure_openai":
        from langchain_openai import AzureChatOpenAI
        return AzureChatOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
            temperature=0,
        )
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=os.environ["ANTHROPIC_API_KEY"],
            temperature=0,
        )
    else:  # openai (default)
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-4o",
            api_key=os.environ["OPENAI_API_KEY"],
            temperature=0,
        )


def load_dataset(path: str) -> Dataset:
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return Dataset.from_list(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset",            required=True)
    ap.add_argument("--provider",           default="openai")
    ap.add_argument("--metrics",            default="context_recall,context_precision,context_relevancy")
    ap.add_argument("--output",             required=True)
    ap.add_argument("--mlflow-experiment",  default="retrieval-eval")
    ap.add_argument("--mlflow-run-name",    default="eval-run")
    args = ap.parse_args()

    console.print(f"[bold cyan]Loading dataset: {args.dataset}[/]")
    dataset = load_dataset(args.dataset)

    metric_names = [m.strip() for m in args.metrics.split(",")]
    metrics = [METRIC_MAP[m] for m in metric_names if m in METRIC_MAP]

    llm = build_llm(args.provider)
    console.print(f"[bold cyan]Running RAGAS with provider={args.provider}, metrics={metric_names}[/]")

    mlflow.set_experiment(args.mlflow_experiment)
    with mlflow.start_run(run_name=args.mlflow_run_name) as run:
        mlflow.set_tag("provider", args.provider)
        mlflow.set_tag("dataset",  args.dataset)

        result = evaluate(dataset, metrics=metrics, llm=llm)
        scores = result.to_pandas().mean(numeric_only=True).to_dict()

        for name, value in scores.items():
            mlflow.log_metric(name, value)
            console.print(f"  {name}: {value:.4f}")

        output = {"metrics": scores, "run_id": run.info.run_id, "provider": args.provider}

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)

    console.print(f"[green]✅ Retrieval metrics saved → {args.output}[/]")


if __name__ == "__main__":
    main()
