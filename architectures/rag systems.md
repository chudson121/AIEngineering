# AI RAG Systems

### What RAG systems are there, and what are the pros and cons of each?

In enterprise architectures, RAG systems generally fall into four design archetypes ranging from simple vector search to autonomous agentic retrieval:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐  
│  1. Naive RAG   │ ──> │2. Advanced RAG  │ ──> │  3. Graph RAG   │ ──> │ 4. Agentic RAG  │  
│ (Embed -> Vector│     │(Chunk/Rerank/   │     │ (Knowledge Graph│     │(Multi-hop/Tool- │  
│  Search -> Gen) │     │ Hybrid Search)  │     │ + Vector Index) │     │ calling Routing)│  
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘  
```

#### A. Naive / Standard Vector RAG

- **How it works:** Chunks documents, generates embeddings (e.g., via OpenAI or Titan), indexes them into a vector database (e.g., OpenSearch, Pinecone, pgvector), performs cosine/top-k similarity search, and injects retrieved chunks into the prompt context.
    
- **Pros:** Fast to build and prototype; low compute overhead; works well for straightforward factual lookups across simple documents.
    
- **Cons:** Poor retrieval accuracy for complex queries; easily misses context across document boundaries (chunking fragmentation); struggles with keyword-heavy searches (e.g., specific part numbers or IDs).
    

#### B. Advanced / Modular RAG (Hybrid Search + Re-ranking)

- **How it works:** Combines dense semantic vector search with sparse keyword search (BM25) via a **Hybrid Search** step, then applies a cross-encoder **Re-ranker** (e.g., Cohere Rerank) to score and prioritize the top NNN most relevant chunks before prompting the LLM.
    
- **Pros:** Dramatically reduces hallucinations; captures both semantic meaning and exact keyword hits; cleans up noise before the context window.
    
- **Cons:** Higher query latency (re-ranking adds 100–300ms); slightly higher ingestion complexity.
    

#### C. Graph RAG (Knowledge Graph + Vector RAG)

- **How it works:** Extracts entities, relationships, and taxonomies from unstructured text to build an interconnected Knowledge Graph (using Neo4j, Amazon Neptune, etc.) alongside embeddings.
    
- **Pros:** Excellent for multi-hop reasoning, relationship mapping, and global corpus summarization (e.g., "What are all the regulatory risks identified across every department?").
    
- **Cons:** High upfront cost and processing time for graph extraction; complex indexing pipelines; specialized query patterns (e.g., Cypher).
    

#### D. Agentic RAG / Router-based RAG

- **How it works:** Uses an LLM agent/orchestrator (e.g., LangGraph, LlamaIndex, AutoGen) that can evaluate the query, route it dynamically to different data sources (SQL database, vector index, web search, API), formulate follow-up sub-queries, and self-correct if retrieved information is incomplete.
    
- **Pros:** Highly flexible; handles multi-step problem solving and disparate enterprise data sources (structured + unstructured).
    
- **Cons:** Higher API costs; variable and longer response latencies; requires guardrails against infinite loops or erratic routing.

### Standardizing Cloud-Native Patterns (Concrete Examples)

Here is how you standardize the four core pillars of the ML lifecycle on AWS using cloud-native services:

#### A. Pipeline Orchestration (SageMaker Pipelines + Step Functions)

- **Pattern:** Infrastructure-as-Code (IaC) reusable DAG templates.
    
- **Concrete Example:** Define a standardized Python module (`ml_pipeline_template.py`) using the SageMaker Python SDK. The pipeline executes:
    
    1. `ProcessingStep` (AWS Glue or SageMaker Processing) for data cleansing.
        
    2. `TrainingStep` pointing to an approved container in ECR.
        
    3. `EvaluationStep` evaluating holdout validation metrics against business thresholds.
        
    4. `ConditionStep` that automatically branches: if metrics pass, call `ModelStep` to register the model; if they fail, send an SNS/Slack alert and terminate.
        

#### B. Feature Management (SageMaker Feature Store)

- **Pattern:** Dual-layer storage (Offline for training, Online for inference) with point-in-time joins.
    
- **Concrete Example:** For a customer churn or transaction system, create standardized **Feature Groups** (e.g., `user_transaction_aggregates`).
    
    - _Offline Layer (S3 + Athena):_ Training pipelines run Athena queries using `as_of` timestamps to pull exact feature states at the time events occurred, preventing data leakage.
        
    - _Online Layer (Ultra-low latency key-value store):_ The live scoring service queries `GetRecord` with `user_id` to retrieve real-time rolling metrics in <10ms.
        

#### C. Model Registration (SageMaker Model Registry)

- **Pattern:** Governed promotion lifecycle with metadata tagging and container hashing.
    
- **Concrete Example:** When a pipeline registers an artifact in a `ModelPackageGroup` (e.g., `CreditScoringModels`), it defaults to status `PendingManualApproval`. The registration record mandates:
    
    - Container image SHA-256 hash.
        
    - S3 URI of model weights.
        
    - Training dataset version/commit hash.
        
    - Accompanying evaluation metric JSON.
        
    - Passing status moves it to `Approved`, which triggers a GitHub Action or EventBridge rule to deploy to staging.
        

#### D. Endpoint Hosting (SageMaker Inference Architectures)

- **Pattern:** Standardized deployment tiers based on latency and throughput SLA.
    
- **Concrete Example:**
    
    - _Real-Time Endpoints (Multi-Model / Single-Model):_ Hosted on Auto-Scaling EC2 instances behind an Application Load Balancer with custom CloudWatch metrics for latency and invocation errors.
        
    - _Serverless / Async Inference:_ Configured for sporadic batch jobs or heavy payloads (e.g., PDF document extraction models) that scale to zero when idle to minimize cloud spend.