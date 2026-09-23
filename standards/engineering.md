---
title: AI Engineering Secure SDLC Standard
status: Proposed outline
version: 0.1
---

# AI Engineering Secure SDLC Standard

## 1. Purpose

Define the minimum software development lifecycle practices for AI-enabled systems, including generative AI applications, retrieval-augmented generation (RAG), model integrations, and tool-using agents.

This standard is an implementation guide. It uses external frameworks as reference points without reproducing them:

- **NIST AI RMF** provides the risk-management outcomes and vocabulary.
- **OWASP GenAI Security Project** provides application threat categories, risks, and security guidance.
- **OWASP AI Exchange** provides a broader threat, control, privacy, and testing knowledge base.
- **AI-SDLC Framework** provides an example of how to make AI-assisted development workflows spec-driven, gated, reviewable, and auditable.

The standard translates those references into lifecycle activities, engineering controls, release evidence, and accountable decisions.

## 2. Scope

Apply this standard to systems that:

- Call hosted or self-managed foundation models, traditional ML models, or embedding models.
- Generate, classify, summarize, recommend, retrieve, or transform content.
- Use prompts, context augmentation, RAG, agents, tools, plugins, or external actions.
- Process confidential, personal, regulated, proprietary, or security-sensitive data.
- Use AI coding assistants or agents to create, modify, review, or deploy software.

Classify each system by impact and autonomy. The classification determines which controls are mandatory, which require human approval, and how much evaluation evidence is required.

## 3. Normative language

The terms **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** indicate requirement strength. A team may deviate from a SHOULD only when it records the rationale, compensating controls, owner, and expiration date of the exception.

## 4. Reference model and alignment approach

### 4.1 How to use the references

Do not claim that a system is “NIST compliant” or “OWASP compliant” based only on using these links. Instead:

1. Identify the applicable risk and threat outcomes from the references.
2. Select concrete controls for the system and its impact level.
3. Assign an owner and place the control in the SDLC.
4. Define evidence that can be reviewed or automated.
5. Evaluate residual risk and obtain the required approval.
6. Reassess when the model, data, prompt, tool, policy, or operating context changes.

### 4.2 Reference responsibilities

| Reference | Use it for | Do not use it as |
| --- | --- | --- |
| [NIST AI RMF 1.0](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf) | Trustworthiness outcomes and risk-management language | A prescriptive checklist or certification |
| [NIST AI RMF landing page](https://www.nist.gov/itl/ai-risk-management-framework) | Official framework status, profiles, crosswalks, and updates | A substitute for system-specific threat modeling |
| [NIST AI RMF Core](https://airc.nist.gov/airmf-resources/airmf/) | Govern, Map, Measure, and Manage functions, categories, and profiles | A detailed application security test catalog |
| [OWASP GenAI Security Project](https://genai.owasp.org/) | GenAI application risks, LLM Top 10, security resources, and testing topics | A complete enterprise governance model |
| [OWASP AI Exchange](https://owaspai.org/) | AI threats, controls, privacy, development-time risks, runtime risks, and red teaming | A replacement for normal application security controls |
| [AI-SDLC Framework](https://github.com/ai-sdlc-framework/ai-sdlc) | Spec-driven workflow ideas, definition-of-ready, quality gates, review, attestations, and declarative governance | An organizational policy or universal process requirement |

### 4.3 Internal implementation layers

This repository should organize guidance into four layers:

1. **Risk and governance:** Why the system is allowed, who owns it, and what harms matter.
2. **Secure engineering:** How the system is designed, implemented, tested, and protected.
3. **Release assurance:** What evidence is required before promotion and what blocks release.
4. **Operations and learning:** How the system is monitored, incident-managed, reviewed, and improved.

## 5. AI system definition and inventory

Before design work begins, the product owner MUST create an AI system record containing:

- Business purpose, users, intended use, prohibited use, and affected parties.
- System boundary, data flows, trust boundaries, dependencies, and deployment environments.
- Model providers, model identifiers, versions or aliases, fallback routes, and inference settings.
- Prompts, system instructions, policies, retrieval sources, indexes, tools, plugins, and external actions.
- Data classifications, residency requirements, retention limits, and permitted data uses.
- Impact level, autonomy level, risk owner, security owner, data owner, and approval authority.
- Success measures, safety measures, service objectives, cost budget, and rollback strategy.

The inventory MUST be updated when a material AI artifact or behavior changes. A source-code commit alone is not a sufficient release identifier.

## 6. Secure AI engineering lifecycle

### 6.1 Govern and prepare

**Objective:** Establish accountability, constraints, and decision rights before implementation.

**Required practices:**

- Assign named owners for product risk, security, privacy, data, model quality, operations, and release approval.
- Define impact, autonomy, unacceptable outcomes, human oversight, and escalation requirements.
- Define data-use, retention, residency, intellectual-property, accessibility, and vendor requirements.
- Establish a Definition of Ready for AI work: clear purpose, known data, threat assumptions, test plan, owner, and acceptance criteria.
- Record decisions and exceptions in a durable decision record.

**Evidence:** AI system record, risk classification, stakeholder register, decision record, Definition-of-Ready review, and control applicability matrix.

**Reference alignment:** NIST Govern and Map; AI-SDLC Definition-of-Ready and decision records; OWASP AI Exchange governance controls.

### 6.2 Map the system and threat model

**Objective:** Understand how the system can fail, be abused, or cause harm.

**Required practices:**

- Draw data-flow and trust-boundary diagrams for users, applications, models, retrieval, tools, providers, and monitoring.
- Threat-model direct prompt injection, indirect prompt injection, sensitive data disclosure, excessive agency, insecure output handling, supply-chain compromise, model or data poisoning, denial of service, and cross-tenant access.
- Identify conventional application risks at every boundary: authentication, authorization, injection, SSRF, deserialization, secrets, dependencies, isolation, and logging.
- Identify failure modes for hallucination, unsupported claims, stale data, over-refusal, bias, unsafe recommendations, tool loops, duplicate side effects, and provider drift.
- Define abuse cases, security invariants, forbidden actions, and safe failure behavior.

**Evidence:** architecture diagram, data inventory, threat model, abuse-case register, security invariants, and prioritized risk treatment plan.

**Reference alignment:** NIST Map; OWASP GenAI risk categories and [OWASP AI Exchange threats](https://owaspai.org/go/threatsoverview/); standard threat-modeling practice.

### 6.3 Design controls and contracts

**Objective:** Turn risks into enforceable system behavior.

**Required practices:**

- Enforce identity, tenant isolation, authorization, and data filtering independently of model output.
- Define least-privilege tool scopes, allowed arguments, rate limits, timeouts, maximum steps, spending limits, and human approval points.
- Treat retrieved content and tool output as untrusted data, not instructions with system authority.
- Define input, output, citation, tool, and state-transition contracts with machine-checkable schemas where possible.
- Define abstention, clarification, fallback, rollback, and incident-disable behavior.
- Minimize sensitive data sent to providers and retained in prompts, traces, evaluation sets, and logs.
- Select model, provider, embedding, and retrieval dependencies with security, privacy, availability, residency, and exit requirements.

**Evidence:** security architecture, authorization policy, tool registry, schemas, data handling design, provider assessment, control test plan, and rollback design.

**Reference alignment:** NIST Govern, Map, and Manage; OWASP GenAI mitigations; OWASP AI Exchange general controls, data limitation, and development-time controls.

### 6.4 Implement with secure software practices

**Objective:** Build the system using controlled, reviewable changes.

**Required practices:**

- Version application code and the effective AI configuration together: prompts, models, routes, parameters, retrieval configuration, corpus/index, tools, policies, guardrails, datasets, and evaluators.
- Keep secrets in approved secret-management systems; never place secrets in prompts, source code, test fixtures, or manifests.
- Pin or otherwise record dependency, model, container, action, and dataset provenance. Scan dependencies, images, infrastructure, and generated code using the organization's existing security tooling.
- Require peer review for security-sensitive changes and independent review for high-impact or autonomous changes.
- Use isolated fixtures and fake credentials for tests. Prevent test agents from reaching production systems or creating uncontrolled external side effects.
- Make mutating operations authenticated, authorized, bounded, observable, and idempotent where feasible.
- Apply normal secure coding, code review, branch protection, CI, secret scanning, static analysis, dependency scanning, and infrastructure-as-code controls.

**Evidence:** immutable release manifest, pull request review, provenance records, scan results, test isolation configuration, and signed or auditable approval where required.

**Reference alignment:** AI-SDLC workflow and quality-gate concepts; OWASP AI Exchange development-time threats; the organization's secure software development standard.

### 6.5 Verify and evaluate

**Objective:** Produce evidence that the candidate meets functional, security, trustworthiness, and operational requirements.

**Required practices:**

- Maintain versioned golden, boundary, adversarial, historical-failure, synthetic, and holdout datasets with provenance and access controls.
- Test retrieval relevance, authorization, freshness, citation support, and missing-evidence behavior separately from generation.
- Test response correctness, unsupported claims, harmful output, over-refusal, uncertainty, and sensitive data disclosure.
- Test agent tool selection, schema validity, argument grounding, authorization, retries, timeouts, loops, duplicate writes, and terminal state.
- Run prompt-injection and malicious-content tests against user input, retrieved documents, web pages, and tool responses.
- Compare candidate and baseline on the same fixtures and evaluator versions. Report slice-level results, severity, sample size, and uncertainty.
- Calibrate automated judges against human review. Do not use one model judge, embedding score, or benchmark aggregate as the sole release gate.
- Perform load, latency, availability, cost, rate-limit, fallback, and failure-injection tests at the required impact level.

**Evidence:** evaluation plan, dataset manifests, test results, judge calibration, security test report, performance report, baseline comparison, known limitations, and approval decision.

**Reference alignment:** NIST Measure; OWASP GenAI testing resources and [OWASP AI Exchange AI security testing](https://owaspai.org/docs/5_testing/); AI-SDLC quality gates and conformance evidence.

### 6.6 Release and operate

**Objective:** Introduce the system gradually and retain the ability to detect and contain failure.

**Required practices:**

- Promote the same tested release bundle through environments; record the effective runtime manifest.
- Use shadow, canary, feature-flag, or cohort rollout for material changes. Suppress writes and external side effects during shadow execution.
- Define explicit blocking thresholds for critical safety, authorization, quality, latency, reliability, and cost failures.
- Instrument correlated traces and metrics for retrieval, model calls, guardrails, tool calls, output validation, and user-visible results.
- Apply privacy-safe logging: minimize content, redact sensitive values, restrict access, set retention, and audit trace access.
- Monitor provider/model drift, corpus/index freshness, retrieval misses, invalid outputs, tool failures, repeated calls, fallbacks, user feedback, cost, and latency.
- Maintain a tested rollback, disable, fallback, and incident response path.

**Evidence:** release approval, rollout plan, canary dashboard, alert definitions, trace policy, rollback rehearsal, operational readiness review, and post-release decision record.

**Reference alignment:** NIST Measure and Manage; OWASP runtime and operational controls; AI-SDLC progressive gates, attestations, and operator visibility.

### 6.7 Learn and improve

**Objective:** Feed confirmed production evidence back into engineering without creating uncontrolled data reuse.

**Required practices:**

- Triage incidents and quality reports by root cause: data, retrieval, prompt, model, tool, policy, integration, security, or operations.
- Preserve privacy-safe trace references and approved samples only.
- Convert confirmed failures into reviewed regression cases with expected assertions and severity.
- Reassess risk and controls after material changes, incidents, provider changes, corpus changes, or new use cases.
- Review metrics and thresholds for drift, false positives, false negatives, and changing business impact.

**Evidence:** incident report, root-cause classification, approved regression case, corrective action, control update, and follow-up validation.

**Reference alignment:** NIST Manage; OWASP testing and continuous improvement guidance; AI-SDLC checkpoint and attestation concepts.

## 7. Control-to-evidence matrix

The implementation owner SHOULD maintain a project-specific matrix in this form:

| Control ID | Lifecycle stage | Requirement | Owner | Automation | Evidence | NIST alignment | OWASP alignment | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AI-SEC-001 | Govern | Impact and autonomy are classified before build approval | Product / risk | Partial | Approved system record | Govern, Map | AI Exchange governance | Not started |
| AI-SEC-002 | Map | Trust boundaries and abuse cases are documented | Security | Partial | Threat model | Map | GenAI risks, AI Exchange threats | Not started |
| AI-SEC-003 | Design | Tool actions are independently authorized and bounded | Engineering / security | Yes | Policy tests and tool registry | Govern, Manage | Excessive agency, access control | Not started |
| AI-SEC-004 | Implement | Effective AI artifacts are versioned as one release bundle | Engineering | Yes | Release manifest | Govern, Map | Development-time controls | Not started |
| AI-SEC-005 | Verify | Critical security and terminal-state tests pass | QA / security | Yes | Evaluation report | Measure | GenAI testing, AI Exchange testing | Not started |
| AI-SEC-006 | Operate | Privacy-safe traces and rollback are verified | SRE / privacy | Partial | Readiness review | Measure, Manage | Runtime controls, privacy | Not started |
| AI-SEC-007 | Improve | Reviewed production failures become regression cases | Product / quality | Partial | Incident and dataset record | Manage | Testing and continuous improvement | Not started |

The matrix is the bridge between a framework reference and an auditable implementation. A project MAY add controls, but it MUST NOT silently remove a control required by its impact classification.

## 8. Release gates

At minimum, the release decision MUST address:

- **Security:** No unresolved critical authorization bypass, secret exposure, forbidden side effect, or exploitable injection path.
- **Data and privacy:** Approved data sources, retention, provider use, redaction, and access controls.
- **Quality:** Required task completion, groundedness, correctness, abstention, and safety results by critical slice.
- **Operations:** Latency, reliability, availability, rate-limit, fallback, and cost objectives.
- **Change control:** Complete release manifest, baseline comparison, reviewer approvals, exceptions, rollout plan, and rollback plan.

Thresholds are system-specific. They MUST document the denominator, sampling method, evaluator version, severity policy, confidence or uncertainty treatment, and exception authority. A single critical unauthorized action may block a release even when average quality improves.

## 9. Roles and responsibilities

| Role | Accountability |
| --- | --- |
| Product owner | Purpose, users, impact classification, acceptance criteria, and residual risk |
| Engineering owner | Architecture, implementation, artifact versioning, contracts, and remediation |
| Security owner | Threat model, abuse cases, security controls, testing, and exception review |
| Data owner | Provenance, authorization, quality, retention, and permitted use |
| Model / evaluation owner | Datasets, rubrics, judge calibration, baseline, and quality evidence |
| Privacy / legal / compliance | Data-use, regulatory, contractual, residency, and rights requirements |
| SRE / operations | SLOs, telemetry, rollout, rollback, incident response, and cost controls |
| Release authority | Evidence review, approval, conditions, and exception expiry |

## 10. Required artifacts

Every system in scope SHOULD have links to the following artifacts:

- AI system record and impact classification
- Data-flow diagram and threat model
- Control applicability and control-to-evidence matrix
- Effective release manifest
- Prompt, model, retrieval, tool, policy, and dataset version records
- Evaluation plan and results, including security and adversarial tests
- Human review and judge-calibration results where applicable
- Privacy, provider, and dependency assessments
- Release approval, exceptions, rollout, and rollback plan
- Operational readiness review, dashboards, alerts, and trace policy
- Incident records and reviewed regression cases

## 11. Adoption roadmap

### Level 1: Inventory and baseline

Create system records, owners, data flows, impact classifications, release manifests, basic secrets/dependency scanning, and critical security tests.

### Level 2: Repeatable assurance

Version datasets and evaluators, add threat modeling, retrieval and tool tests, baseline comparisons, privacy-safe telemetry, and documented release gates.

### Level 3: Controlled production

Add sandboxed stateful evaluations, calibrated judges, performance and failure-injection testing, canary deployment, rollback rehearsal, and incident-to-regression workflows.

### Level 4: Continuous governance

Automate control evidence, monitor drift and risk signals, expire exceptions, attest release bundles, and periodically reassess controls against updated NIST and OWASP guidance.

## 12. External references

- [AI-SDLC Framework](https://github.com/ai-sdlc-framework/ai-sdlc)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [NIST AI RMF Resource Center](https://airc.nist.gov/airmf-resources/airmf/)
- [NIST AI RMF 1.0 PDF](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf)
- [OWASP GenAI Security Project](https://genai.owasp.org/)
- [OWASP AI Exchange](https://owaspai.org/)

## 13. Review and maintenance

This document is a proposed internal standard, not a certification claim. Review it at least annually and after material updates to the NIST AI RMF, OWASP guidance, organizational risk appetite, or platform architecture. Record changes, rationale, affected controls, and migration expectations.
