# ══════════════════════════════════════════════════════════════════════════════
# Makefile – local developer commands mirroring the GitHub Actions CI/CD pipeline
# RA Reference: Enterprise LLM & Agent Evaluation Architecture
# ══════════════════════════════════════════════════════════════════════════════

.PHONY: help install validate-all eval-retrieval eval-groundedness \
        eval-agents regression load-test build-manifest \
        run-full-ci monitor-health

PYTHON     := python3
PROVIDER   ?= openai
DATASET    ?= evals/datasets/rag_golden_set.jsonl
REPORTS    := reports

help:          ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2}'

# ── Setup ─────────────────────────────────────────────────────────────────────
install:       ## Install all Python dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# ── Stage 1 – Artifact validation ────────────────────────────────────────────
validate-prompts:  ## Validate all prompt templates
	$(PYTHON) scripts/validate_prompts.py \
	  --prompt-dir prompts/ \
	  --schema-dir config/prompt-schemas/ \
	  --output $(REPORTS)/prompt-validation.json

validate-tools:    ## Validate all tool JSON schemas
	$(PYTHON) scripts/validate_tool_schemas.py \
	  --tools-dir tools/ \
	  --output $(REPORTS)/tool-schema-validation.json

build-manifest:    ## Build effective release manifest
	$(PYTHON) scripts/build_manifest.py \
	  --git-sha $$(git rev-parse HEAD) \
	  --git-ref $$(git rev-parse --abbrev-ref HEAD) \
	  --output  release-manifest.json

validate-all: validate-prompts validate-tools build-manifest  ## Run all artifact validations

# ── Stage 2 – Retrieval & groundedness evaluation ────────────────────────────
eval-retrieval:    ## Run RAGAS retrieval evaluation (PROVIDER=openai|azure_openai|anthropic)
	mkdir -p $(REPORTS)
	$(PYTHON) scripts/eval_retrieval.py \
	  --dataset   $(DATASET) \
	  --provider  $(PROVIDER) \
	  --metrics   context_recall,context_precision,context_relevancy \
	  --output    $(REPORTS)/retrieval_metrics.json \
	  --mlflow-experiment retrieval-eval-local \
	  --mlflow-run-name   local-$$(git rev-parse --short HEAD)
	$(PYTHON) scripts/check_thresholds.py \
	  --report $(REPORTS)/retrieval_metrics.json \
	  --gates  config/thresholds/retrieval.yaml \
	  --fail-on-breach

eval-groundedness: ## Run DeepEval groundedness + hallucination tests
	mkdir -p $(REPORTS)
	$(PYTHON) scripts/eval_groundedness.py \
	  --dataset  $(DATASET) \
	  --provider $(PROVIDER) \
	  --output   $(REPORTS)/groundedness_metrics.json
	$(PYTHON) scripts/check_thresholds.py \
	  --report $(REPORTS)/groundedness_metrics.json \
	  --gates  config/thresholds/groundedness.yaml \
	  --fail-on-breach

# ── Stage 3 – Agent task evaluation ──────────────────────────────────────────
eval-agents:       ## Run agent task suite (mocked tools, local sandbox)
	mkdir -p $(REPORTS)
	pytest tests/agent/ \
	  --provider=$(PROVIDER) \
	  --junitxml=$(REPORTS)/agent-task-tests.xml \
	  -v --tb=short
	$(PYTHON) scripts/check_thresholds.py \
	  --report $(REPORTS)/agent_standard_results.json \
	  --gates  config/thresholds/agent.yaml \
	  --fail-on-breach

eval-security:     ## Run prompt injection & security tests
	mkdir -p $(REPORTS)
	$(PYTHON) scripts/eval_security.py \
	  --fixtures evals/datasets/security_fixtures.jsonl \
	  --provider $(PROVIDER) \
	  --output   $(REPORTS)/security_results.json
	$(PYTHON) scripts/check_thresholds.py \
	  --report $(REPORTS)/security_results.json \
	  --gates  config/thresholds/security.yaml \
	  --fail-on-breach

# ── Stage 4 – Regression ─────────────────────────────────────────────────────
regression:        ## Run full regression dataset suite
	mkdir -p $(REPORTS)/regression
	$(PYTHON) scripts/run_regression.py \
	  --golden      evals/datasets/golden_set.jsonl \
	  --boundary    evals/datasets/boundary_set.jsonl \
	  --adversarial evals/datasets/adversarial_set.jsonl \
	  --failures    evals/datasets/historical_failures.jsonl \
	  --provider    $(PROVIDER) \
	  --output-dir  $(REPORTS)/regression/
	$(PYTHON) scripts/check_thresholds.py \
	  --report $(REPORTS)/regression/candidate_metrics.json \
	  --gates  config/thresholds/regression.yaml \
	  --fail-on-breach

# ── Stage 5 – Load test ───────────────────────────────────────────────────────
load-test:         ## Run k6 load test against ENDPOINT (default: localhost:8000)
	ENDPOINT ?= http://localhost:8000
	k6 run \
	  --out json=$(REPORTS)/k6_results.json \
	  --env LLM_PROVIDER=$(PROVIDER) \
	  --env ENDPOINT=$${ENDPOINT} \
	  monitoring/k6-load-test.js
	$(PYTHON) scripts/check_thresholds.py \
	  --report $(REPORTS)/k6_results.json \
	  --gates  config/thresholds/latency.yaml \
	  --fail-on-breach

# ── Full local CI run ─────────────────────────────────────────────────────────
run-full-ci: validate-all eval-retrieval eval-groundedness eval-agents eval-security regression
	@echo ""
	@echo "✅ Full local CI pipeline complete. Check reports/ for results."

# ── Production monitoring (local probe) ──────────────────────────────────────
monitor-health:    ## Run production health probe against PROMETHEUS_URL
	$(PYTHON) scripts/monitoring/probe_latency.py \
	  --prometheus-url $${PROMETHEUS_URL} \
	  --slo-config     config/slos.yaml \
	  --output         $(REPORTS)/latency-probe.json
	$(PYTHON) scripts/check_thresholds.py \
	  --report $(REPORTS)/latency-probe.json \
	  --gates  config/thresholds/production-slo.yaml \
	  --no-fail

# ── Dataset management ────────────────────────────────────────────────────────
dvc-pull:          ## Pull all evaluation datasets from DVC remote
	dvc pull evals/datasets/

dvc-push:          ## Push updated datasets to DVC remote
	dvc push evals/datasets/

# ── Clean ─────────────────────────────────────────────────────────────────────
clean:             ## Remove generated reports
	rm -rf $(REPORTS)/ release-manifest*.json sandbox-info.json
