# AI Engineering

Standards, best practices, and reference architectures for designing, building, evaluating, operating, and governing AI-enabled systems.

This repository is intended to help teams move from promising AI prototypes to reliable engineering systems. It focuses on the practices around models and applications: requirements, data, prompts, retrieval, tools, evaluation, release management, observability, security, and governance.

## Why this repository exists

AI systems require more than conventional software delivery practices. Their behavior can vary with model versions, prompts, retrieval data, tool outputs, and real-world context. A production-ready process therefore needs evidence that a system is:

- **Useful:** It completes the intended task and answers the user's actual question.
- **Grounded:** Its claims and actions are supported by authorized, current evidence.
- **Safe:** It protects data, respects policy, and cannot use model output to bypass authorization.
- **Reliable:** It handles uncertainty, failures, retries, fallbacks, and changing dependencies.
- **Operable:** Its latency, cost, quality, and failure modes are observable.
- **Governable:** Its decisions, artifacts, approvals, and exceptions are reviewable.

## Start here

| Resource | What it covers |
| --- | --- |
| [Enterprise LLM and Agent Evaluation Reference Architecture](architectures/enterprise-llm-agent-evaluation-reference-architecture.md) | Evaluation, CI/CD, agent safety, observability, release gates, governance, and an implementation roadmap |
| [Implementation checklist](architectures/enterprise-llm-agent-evaluation-reference-architecture.md#12-implementation-checklist) | A concise set of practices to apply to an AI system |
| [Open decisions](architectures/enterprise-llm-agent-evaluation-reference-architecture.md#13-open-decisions-for-the-implementing-organization) | Questions each organization must answer for its risk, data, and operating model |

## Core principles

1. **Risk-weight controls.** The rigor of evaluation, approval, monitoring, and human oversight should match the impact of failure.
2. **Version the effective system.** Track application code, prompts, models, routing, inference parameters, retrieval configuration, corpus and index versions, tools, policies, guardrails, datasets, and evaluators as one tested release bundle.
3. **Use layered evidence.** Combine deterministic tests, representative datasets, adversarial cases, calibrated model judges, human review, and production signals.
4. **Separate concerns.** Test retrieval, generation, tool selection, tool arguments, side effects, and terminal state independently before relying on an aggregate outcome.
5. **Enforce authorization outside the model.** Model refusals and prompt instructions are not security boundaries. Every sensitive read and write needs independent policy enforcement.
6. **Fail safely.** When evidence is missing, authorization is ambiguous, or a dependency is unavailable, abstain, ask for clarification, route to a human, or use a tested fallback.
7. **Design for feedback.** Convert confirmed production failures into privacy-reviewed, versioned regression cases.

## Engineering lifecycle

The recommended lifecycle is:

**Define risk → design controls → version artifacts → evaluate → approve → release gradually → observe → learn and improve**

At each stage, retain enough evidence to answer:

- What changed?
- Which model, prompt, data, tools, and policies were effective at runtime?
- What tests were run, on which dataset and evaluator versions?
- Which risks or exceptions were accepted, by whom, and until when?
- How will the release be paused, rolled back, or replaced?

## Practice areas

### Requirements and risk

Define the task, intended users, prohibited uses, data classes, failure severity, human escalation path, and success measures before selecting a model. Classify workflows by impact so a low-risk drafting assistant does not inherit the same controls as an agent that changes external state.

### Data and retrieval

Treat source content, metadata, permissions, freshness, chunking, embeddings, indexes, and ranking configuration as release inputs. Evaluate retrieval relevance, authorization filtering, freshness, citation support, and missing-evidence behavior separately from response generation.

### Prompts, models, and tools

Version prompts and templates, model routes and fallbacks, inference parameters, output contracts, tool schemas, authorization policies, and guardrails. Keep secrets out of prompts and manifests. For agents, test schema validity, argument grounding, bounded execution, retries, idempotency, forbidden actions, and the final environment state.

### Evaluation and release

Use a staged evaluation ladder: fast local checks, pull request tests, full staging evaluations, progressive production, and continuous monitoring. Compare candidates with a known baseline on pinned datasets. Report slice-level results and uncertainty; do not treat one judge score or one aggregate benchmark as proof of quality or safety.

### Security and privacy

Test direct and indirect prompt injection, data exfiltration, cross-tenant access, malicious tool responses, unsafe parameters, sensitive output disclosure, and over-refusal. Use synthetic data and fake credentials in tests. Apply least privilege, independent authorization, retention limits, redaction, access controls, and audit logging.

### Reliability, cost, and operations

Measure end-to-end and component latency, time to first token, failures, timeouts, rate limits, retries, fallback usage, token consumption, and cost per successful task. Trace retrieval, model calls, guardrails, and tools with a correlated release identifier while minimizing retained content.

### Governance and incident response

Assign owners for quality, datasets, evaluation, security, release approval, and incidents. Maintain decision records and approved exceptions. For severe regressions, pause the rollout or disable the risky capability, assess side effects, preserve privacy-safe evidence, roll back or fix, and add a reviewed regression case.

## Browse the repository

### Strategy

- [AI Board Perspective](strategy/board-perspective.md)
- [AI and Strategic Advantage](strategy/ai%20and%20strategic%20advantage.md)
- [AI Digital Transformation](strategy/digital%20transformation.md)

### Governance

- [AI Center of Excellence](governance/ai%20coe%20-%20getting%20your%20ai%20enabled%20business%20there.md)
- [AI Code of Conduct](governance/code%20of%20conduct.md)
- [AI Ethics and Validation White Paper](governance/ethics%20and%20validation%20-%20whitepaper.md)

### Architecture

- [AI Application Reference Architecture](architectures/app%20reference%20architecture.md)
- [AI RAG Systems](architectures/rag%20systems.md)
- [AI Observability](architectures/observability.md)
- [Enterprise LLM and Agent Evaluation Reference Architecture](architectures/enterprise-llm-agent-evaluation-reference-architecture.md)

### Secure delivery

- [AI Development Lifecycle](secure-delivery/development%20lifecycle.md)
- [Application Security with Generative AI](secure-delivery/application%20security%20with%20generative%20ai.md)
- [Responsible Development and Release of Generative AI](secure-delivery/ai%20-%20responsible%20development%20and%20release%20of%20gen%20ai.md)
- [Enterprise AI CI/CD Pipeline](ci-cd-pipeline/README.md)

### Agents

- [Building Effective Agents](agents/building-agents.md)
- [Autonomous AI Agents](agents/autonomous-agents.md)

### Implementation

- [AI Implementation Strategy](strategy/implementation%20strategy.md)
- [AI Roadmap](strategy/ai%20roadmap.md)
- [AI Strategy Workshop](strategy/strategy%20workshop.md)
- [AI Steering Committee](governance/steering%20committee.md)
- [AI Operational Framework](governance/operational%20framework.md)
- [AI Observability](architectures/observability.md)
- [AI Risk Assessment and Mitigation Plan](governance/risk%20assessment%20and%20mitigation%20plan.md)

### Standards

- [AI Engineering Secure SDLC Standard](standards/engineering.md)

### Repository tooling

- [Lowercase filename utility](scripts/lowercase-file-names.ps1) - Renames files recursively while excluding `ci-cd-pipeline` and `README.md` files. Preview changes with `pwsh -File .\scripts\lowercase-file-names.ps1 -WhatIf`.

## Repository map

| Area | Intended contents |
| --- | --- |
| `strategy/` | Executive context, transformation, and strategic positioning |
| `governance/` | Operating models, ethics, conduct, and organizational enablement |
| `architectures/` | Application and enterprise reference architectures |
| `secure-delivery/` | Development lifecycle, application security, and responsible release |
| `agents/` | Agent design, capabilities, and autonomy |
| `ci-cd-pipeline/` | CI/CD implementation reference |
| Cross-cutting implementation | Strategy, roadmap, operating model, observability, and risk guidance organized by subject |
| `standards/` | Normative requirements and minimum controls |
| `best_practices/` | Recommended implementation patterns and checklists |
| `patterns/` | Reusable designs for common AI engineering problems |
| `templates/` | Evaluation plans, release manifests, decision records, and review forms |
| `examples/` | Concrete, non-production examples and walkthroughs |

The last three directories are reserved for future additions. Add new material to the most specific existing category before creating another top-level folder.

## Document conventions

Each substantial document should state its:

- **Status:** Draft, proposed, reference, or approved standard.
- **Audience and scope:** Who should use it and which systems it covers.
- **Assumptions and non-goals:** What it does not guarantee.
- **Required controls:** Practices that are normative for the stated scope.
- **Examples and thresholds:** Clearly labeled as illustrative unless formally approved.
- **Ownership and review date:** Who maintains it and when it should be revisited.

Reference architectures describe a coherent approach. They are not universal mandates: adapt thresholds, retention, controls, and approval requirements to the application's risk, traffic, data, contractual commitments, and measured baseline.

## Contributing

Useful contributions include new reference architectures, standards, implementation checklists, evaluation patterns, incident learnings, and corrections to existing guidance.

When proposing a change:

1. Explain the problem and the audience.
2. State whether the guidance is normative or illustrative.
3. Include assumptions, trade-offs, failure modes, and measurable acceptance criteria.
4. Prefer vendor-neutral language; identify provider-specific behavior where it matters.
5. Include security, privacy, operational, and governance implications.
6. Keep examples reproducible and free of secrets or sensitive data.

## Status

This repository is an evolving engineering reference. The current primary documents are the [AI Engineering Secure SDLC Standard](standards/engineering.md) and [Enterprise LLM and Agent Evaluation Reference Architecture](architectures/enterprise-llm-agent-evaluation-reference-architecture.md). New guidance should build on their emphasis on versioned release bundles, layered evaluation, independent authorization, privacy-safe observability, controlled rollout, and continuous improvement.
