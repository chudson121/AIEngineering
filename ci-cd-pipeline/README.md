# Enterprise AI CI/CD Pipeline (GitHub Actions)

Implementation of the [Enterprise Reference Architecture: LLM and Agent Evaluation, CI/CD, and Observability](../architectures/enterprise-llm-agent-evaluation-reference-architecture.md) as a runnable GitHub Actions pipeline.

---

## Pipeline Overview

```
PR opened / commit pushed
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  01 · Validate Artifacts & Contracts  (every PR)                            │
│  ┌────────────────┐  ┌─────────────────┐  ┌──────────────────┐             │
│  │ Prompt render  │  │ Tool schema     │  │ Secrets scan     │             │
│  │ & hash (Jinja) │  │ validation      │  │ (Gitleaks /      │             │
│  │                │  │ (jsonschema /   │  │  TruffleHog)     │             │
│  │                │  │  pydantic)      │  │                  │             │
│  └────────────────┘  └─────────────────┘  └──────────────────┘             │
│  ┌──────────────────────────────────────────────────────────────┐           │
│  │ Release manifest builder  (DVC + Git SHA + prompt/tool hash) │           │
│  └──────────────────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
        │ ✅ passes
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  02 · Retrieval Relevance & Groundedness  (on merge to main / release)      │
│  ┌────────────────────────────────┐  ┌───────────────────────────────────┐  │
│  │ RAGAS                          │  │ DeepEval                          │  │
│  │  · context_recall ≥ 0.85       │  │  · faithfulness ≥ 0.95            │  │
│  │  · context_precision ≥ 0.80    │  │  · hallucination_rate ≤ 0.05      │  │
│  │  · context_relevancy ≥ 0.80    │  │  · answer_relevancy ≥ 0.85        │  │
│  └────────────────────────────────┘  └───────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ Citation validity + ACL check  (zero unauthorized retrievals)          │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│  Results → MLflow + LangSmith                                               │
└─────────────────────────────────────────────────────────────────────────────┘
        │ ✅ passes
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  03 · Agent Task Completion & Tool-Call Accuracy  (staging)                 │
│  ┌────────────────────────────┐  ┌───────────────────────────────────────┐  │
│  │ Tool schema & arg          │  │ Sandbox integration                   │  │
│  │ validation (pytest +       │  │  · Standard task completion ≥ 90%     │  │
│  │  mocked tools)             │  │  · Terminal state verification        │  │
│  └────────────────────────────┘  │  · Trajectory safety checks           │  │
│                                  └───────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ Prompt injection + security robustness  (DeepEval adversarial suite)   │  │
│  │ Zero unauthorized actions = HARD BLOCK                                 │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│  Ephemeral sandbox on Azure Container Apps or AWS ECS (OIDC auth)           │
└─────────────────────────────────────────────────────────────────────────────┘
        │ ✅ passes
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  04 · Regression Datasets & Baseline Comparison  (staging)                  │
│  ┌────────────────────────────────────────────┐                             │
│  │ DVC pull → all dataset slices              │                             │
│  │  · golden_set  · boundary_set              │                             │
│  │  · adversarial_set  · historical_failures  │                             │
│  └────────────────────────────────────────────┘                             │
│  ┌──────────────────────────────────┐  ┌───────────────────────────────┐   │
│  │ Evidently AI – candidate vs      │  │ k6 / pytest-benchmark         │   │
│  │ baseline comparison              │  │  · p95 latency ≤ 3 000 ms     │   │
│  │  · score delta gates             │  │  · completion rate ≥ 99%      │   │
│  └──────────────────────────────────┘  └───────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ Human approval gate  (GitHub Environment: staging-approval)            │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
        │ ✅ approved
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  05 · Prompt / Model Versioning & Traceability  (on push to main + tags)    │
│  ┌────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐│
│  │ MLflow Prompt       │  │ MLflow Model Registry │  │ DVC dataset version  ││
│  │ Registry            │  │  (OpenAI / Azure /    │  │  push + lock         ││
│  │ (SHA-256 per file)  │  │   Anthropic / Bedrock)│  │                      ││
│  └────────────────────┘  └──────────────────────┘  └──────────────────────┘│
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ Final effective release manifest → GitHub Release + Azure Blob / S3   │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│  Production registry promotion gated by GitHub Environment reviewer         │
└─────────────────────────────────────────────────────────────────────────────┘
        │ ✅ versioned
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  06 · Deploy – Shadow / Canary / Production                                  │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ Build + sign container image (Cosign + GHCR)                         │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────┐  ┌────────────────────────────────────────┐ │
│  │ Azure Container Apps       │  │ AWS ECS Fargate                        │ │
│  │  · Shadow / canary weights │  │  · CodeDeploy canary traffic split     │ │
│  │  · Blue/green swap         │  │  · Blue/green task definition swap     │ │
│  └────────────────────────────┘  └────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ OTel + LangFuse trace bootstrap  │  Canary health check + auto-rollback│  │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
        │ ✅ deployed
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  07 · Production Traces, Latency & Failure Monitoring  (scheduled)          │
│  ┌─────────────────────────┐  ┌──────────────────────────────────────────┐  │
│  │ Every 30 min            │  │ Daily                                    │  │
│  │  · Prometheus SLO probe  │  │  · LangFuse 5% trace quality sample     │  │
│  │  · PagerDuty + Slack     │  │  · Evidently drift detection            │  │
│  │    on breach             │  │  · Incident replay → regression         │  │
│  └─────────────────────────┘  │    dataset promotion                     │  │
│                                └──────────────────────────────────────────┘  │
│  Grafana dashboard sync from JSON                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
.github/workflows/
  01-validate-artifacts.yml          # PR gate: prompt render, schema, secrets, unit tests
  02-eval-retrieval-groundedness.yml # RAGAS + DeepEval + citation ACL check
  03-eval-agent-tasks.yml            # Agent sandbox, tool-call accuracy, security
  04-regression-and-comparison.yml   # Full regression suite + Evidently + human gate
  05-versioning-traceability.yml     # MLflow registry, DVC, release manifest, GitHub Release
  06-deploy-canary.yml               # Container build, Azure/AWS deploy, OTel, auto-rollback
  07-production-monitoring.yml       # Scheduled health probes, drift, incident replay

config/
  model-routing.yaml                 # LLM provider routing (OpenAI / Azure / Anthropic / Bedrock)
  slos.yaml                          # Service Level Objectives + Prometheus queries
  thresholds/
    retrieval.yaml                   # RAGAS metric gates
    groundedness.yaml                # DeepEval faithfulness/hallucination gates
    agent.yaml                       # Task completion + tool-call gates
    security.yaml                    # Zero-unauthorized-action gates
    latency.yaml                     # p95/p99 SLO gates
    regression.yaml                  # Baseline delta gates
    production-slo.yaml              # Production alert thresholds

scripts/
  build_manifest.py                  # Build effective release manifest
  check_thresholds.py                # Generic threshold enforcer (all workflows)
  eval_retrieval.py                  # RAGAS retrieval evaluation
  eval_groundedness.py               # DeepEval groundedness + hallucination
  monitoring/
    probe_latency.py                 # Prometheus SLO health probe
    sample_traces.py                 # LangFuse trace sampler + judge
    run_drift_report.py              # Evidently drift report
    alert_pagerduty.py               # PagerDuty alert dispatcher
    replay_incidents.py              # Incident replay harness
    promote_to_regression.py         # Regression dataset promotion
    sync_grafana.py                  # Grafana dashboard provisioner

monitoring/
  k6-load-test.js                    # k6 load test (latency SLO gate)
  grafana/dashboards/                # Grafana dashboard JSON (provisioned by workflow 07)

evals/
  datasets/                          # DVC-tracked eval dataset JSONL files
    rag_golden_set.jsonl.dvc
    golden_set.jsonl.dvc
    boundary_set.jsonl.dvc
    adversarial_set.jsonl.dvc
    historical_failures.jsonl.dvc
    security_fixtures.jsonl.dvc

requirements.txt                     # Production dependencies
requirements-dev.txt                 # Dev / test dependencies
Makefile                             # Local developer commands
```

---

## Quick Start

### 1. Fork / clone and install

```bash
git clone https://github.com/your-org/ai-cicd-pipeline
cd ai-cicd-pipeline
pip install -r requirements-dev.txt
```

### 2. Set GitHub Secrets and Variables

#### Required Secrets

| Secret | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic (Claude) API key |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key |
| `AZURE_CLIENT_ID` | Azure service principal client ID (OIDC) |
| `AZURE_TENANT_ID` | Azure tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |
| `AZURE_STORAGE_ACCOUNT` | Azure Blob Storage account name |
| `AZURE_SAS_TOKEN` | Azure SAS token for DVC remote |
| `AWS_ROLE_ARN` | AWS IAM role ARN for OIDC federation |
| `AWS_ACCESS_KEY_ID` | AWS access key (fallback if no OIDC) |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key (fallback) |
| `MLFLOW_TRACKING_TOKEN` | MLflow tracking server auth token |
| `LANGSMITH_API_KEY` | LangSmith API key |
| `LANGFUSE_PUBLIC_KEY` | LangFuse public key |
| `LANGFUSE_SECRET_KEY` | LangFuse secret key |
| `DEEPEVAL_API_KEY` | DeepEval API key |
| `PAGERDUTY_API_KEY` | PagerDuty API key |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL |
| `PROMETHEUS_BEARER` | Prometheus bearer token |
| `GRAFANA_API_KEY` | Grafana API key |

#### Required Variables

| Variable | Example Value | Description |
|---|---|---|
| `CLOUD_PROVIDER` | `azure` or `aws` | Target cloud platform |
| `DEFAULT_LLM_PROVIDER` | `openai` | Default LLM provider for evaluations |
| `AWS_REGION` | `us-east-1` | AWS region |
| `AZURE_RESOURCE_GROUP` | `ai-app-rg` | Azure resource group |
| `AZURE_CONTAINER_REGISTRY` | `myacrregistry` | Azure Container Registry name |
| `MLFLOW_TRACKING_URI` | `https://mlflow.your-org.com` | MLflow server URI |
| `LANGSMITH_PROJECT` | `ai-app-production` | LangSmith project name |
| `LANGFUSE_HOST` | `https://langfuse.your-org.com` | LangFuse server |
| `OTEL_ENDPOINT` | `https://otel.your-org.com` | OpenTelemetry collector endpoint |
| `PROMETHEUS_URL` | `https://prometheus.your-org.com` | Prometheus server URL |
| `GRAFANA_URL` | `https://grafana.your-org.com` | Grafana server URL |
| `ECS_CLUSTER` | `ai-app-cluster` | AWS ECS cluster name |
| `STAGING_ENDPOINT` | `https://staging.your-org.com` | Staging service URL for load tests |
| `PAGERDUTY_SERVICE_ID` | `PXXXXXX` | PagerDuty service ID |
| `AZURE_JUDGE_DEPLOYMENT` | `gpt-4o-judge` | Azure OpenAI deployment for LLM judge |
| `AZURE_AGENT_DEPLOYMENT` | `gpt-4o-agent` | Azure OpenAI deployment for agent |

### 3. Configure GitHub Environments

Create these environments in **Settings → Environments**:

| Environment | Required Reviewers | Purpose |
|---|---|---|
| `staging` | Optional | Staging sandbox deployments |
| `staging-approval` | ✅ AI platform team | Human approval gate before prod |
| `production` | ✅ Release owners | Full production deployment |
| `production-registry-approval` | ✅ AI governance lead | MLflow model registry promotion |

### 4. Run locally

```bash
# Validate artifacts
make validate-all PROVIDER=openai

# Retrieval evaluation
make eval-retrieval PROVIDER=openai
make eval-retrieval PROVIDER=azure_openai
make eval-retrieval PROVIDER=anthropic

# Groundedness evaluation
make eval-groundedness PROVIDER=openai

# Agent tasks
make eval-agents PROVIDER=openai

# Security tests
make eval-security

# Full regression suite
make regression PROVIDER=openai

# Load test
make load-test ENDPOINT=https://your-staging-app.com

# Full local CI
make run-full-ci PROVIDER=openai
```

---

## LLM Provider Configuration

Each workflow resolves the active provider from the `LLM_PROVIDER` environment variable (defaults to `DEFAULT_LLM_PROVIDER` repository variable). Switch providers per-run or per-environment without changing workflow YAML.

| Provider value | Credentials used | Notes |
|---|---|---|
| `openai` | `OPENAI_API_KEY` | Default; uses `gpt-4o` as judge |
| `azure_openai` | `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT_NAME` | Set deployment name in Variables |
| `anthropic` | `ANTHROPIC_API_KEY` | Uses `claude-3-5-sonnet` |
| `aws_bedrock` | AWS OIDC role (no API key needed) | Bedrock in `AWS_REGION` |

---

## Gate Summary

| Workflow | Gate | Threshold | Block level |
|---|---|---|---|
| 01 | Prompt render | All templates render | PR merge |
| 01 | Tool schema | All payloads valid | PR merge |
| 01 | Secrets scan | Zero secrets found | PR merge |
| 02 | context_recall | ≥ 0.85 | Staging |
| 02 | faithfulness | ≥ 0.95 | Staging |
| 02 | unauthorized retrieval | = 0 | Staging (hard) |
| 03 | Standard task completion | ≥ 90% | Staging |
| 03 | Unauthorized tool actions | = 0 | Staging (hard) |
| 03 | Prompt injection blocked | = 100% | Staging (hard) |
| 04 | Score delta vs baseline | ≤ −3pp | Pre-prod |
| 04 | p95 latency | ≤ 3 000 ms | Pre-prod |
| 04 | Human approval | Required | Pre-prod |
| 06 | Canary error rate | ≤ 1% | Auto-rollback |
| 07 | Production p95 | ≤ 3 500 ms | PagerDuty alert |

---

## Extending the Pipeline

### Add a new LLM provider
1. Add credentials to GitHub Secrets.
2. Add a branch to the `Resolve LLM credentials` step in each workflow.
3. Add the provider to `config/model-routing.yaml`.

### Add a new evaluation metric
1. Add the metric to the relevant `scripts/eval_*.py` and register it in `METRIC_MAP`.
2. Add the threshold gate to the matching `config/thresholds/*.yaml` file.

### Change deployment target
Toggle `CLOUD_PROVIDER` variable between `azure` and `aws`. Each workflow uses `if: vars.CLOUD_PROVIDER == 'azure'` / `'aws'` guards; only the matching job runs.

### Add a new dataset slice
1. Add the JSONL file under `evals/datasets/`.
2. Run `dvc add evals/datasets/<new-file>.jsonl && dvc push`.
3. Commit the `.dvc` lock file.
4. Reference the new slice in `scripts/run_regression.py` and workflow `04`.

---

## RA Section → Workflow Mapping

| RA Section | Workflow(s) | Key tools |
|---|---|---|
| 4.1 Versioned artifacts | 01, 05 | DVC, MLflow, custom manifest builder |
| 4.2 Regression dataset design | 04 | DVC, golden/adversarial/failure slices |
| 5.1 Evaluation ladder | 01–04 | pytest, RAGAS, DeepEval, k6 |
| 5.2 Retrieval relevance | 02 | RAGAS (context_recall, precision) |
| 5.3 Response correctness | 02 | DeepEval (faithfulness, hallucination) |
| 5.4 Agent task completion | 03 | LangSmith, custom sandbox harness |
| 5.5 Security & robustness | 03 | DeepEval adversarial, injection fixtures |
| 5.6 Performance & cost | 04 | k6, pytest-benchmark, MLflow cost tags |
| 6 CI/CD gates | 01–04, 06 | check_thresholds.py, GitHub Environments |
| 7 Runtime controls | 06 | OTel, LangFuse, OIDC auth |
| 8 Production monitoring | 07 | Prometheus, Grafana, Evidently, LangFuse |
| 8.3 Incident response | 07 | Auto-rollback, PagerDuty, LangSmith |
| 9 Governance | 04, 05 | GitHub Environment reviewers, audit trail |
