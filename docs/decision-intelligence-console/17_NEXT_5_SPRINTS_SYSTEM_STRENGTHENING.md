# Next 5 Sprints — Execution Map + System Strengthening

This plan assumes **2-week sprints** starting immediately after the 30/60/90 operationalization work.

## Sprint 1 (Weeks 1–2): Instrumentation Baseline + Reliability Visibility

### Objectives
- Make system health and delivery performance visible with minimal friction.
- Establish one trusted telemetry path for execution metrics.

### Scope
- Add baseline service metrics, trace IDs, and structured logs for all core flows.
- Define canonical event schema for execution scorecards and advancement evidence.
- Add a lightweight reliability dashboard with:
  - deployment frequency
  - change lead time
  - failed deployment recovery time
  - change fail rate
  - deployment rework rate

### Done criteria
- 95%+ of core requests include trace correlation IDs.
- Weekly DORA-style metrics report is automated.
- One reliability view is shared in weekly review.

---

## Sprint 2 (Weeks 3–4): Quality Gates + Defect Containment

### Objectives
- Reduce escaped defects and tighten release confidence.
- Standardize pre-merge and pre-release controls.

### Scope
- Define tiered CI gates by risk level (core paths, moderate paths, low-risk docs/config).
- Add regression tests for top incident classes from Sprint 1.
- Add release checklist enforcing:
  - tests green
  - migration rollback validation
  - observability checks

### Done criteria
- Critical-path changes cannot merge without required checks.
- Defect escape rate trends down vs Sprint 1 baseline.
- MTTR improves for top recurring defect class.

---

## Sprint 3 (Weeks 5–6): Secure Supply Chain + Provenance

### Objectives
- Increase trust in build artifacts and dependencies.
- Move toward auditable, reproducible software delivery.

### Scope
- Generate SBOMs for build artifacts and store with releases.
- Add provenance attestations in CI and establish signed release artifacts.
- Introduce dependency risk policy (age, vulnerabilities, abandoned packages).
- Map current engineering controls to SSDF practices and identify gaps.

### Done criteria
- 100% of release builds produce SBOM + provenance metadata.
- Vulnerability SLA policy defined and tracked.
- SSDF control map baseline completed.

---

## Sprint 4 (Weeks 7–8): Agent/AI Risk Controls + Evaluation Harness

### Objectives
- Improve safety and predictability of AI-assisted decision workflows.
- Make model/system behavior measurable and reviewable.

### Scope
- Define risk taxonomy for model misuse, hallucination, and data leakage.
- Implement eval harness with a stable test set for:
  - task accuracy
  - refusal policy alignment
  - source-grounding quality
- Add pre-release AI checks and post-release drift monitoring.
- Create incident response playbook for AI-generated failure modes.

### Done criteria
- Evals required in release path for AI-assisted features.
- First monthly AI risk review completed with tracked actions.
- Misuse and grounding metrics visible in dashboard.

---

## Sprint 5 (Weeks 9–10): UX/System Maturity + Operating Cadence Hardening

### Objectives
- Convert early gains into repeatable operating system behavior.
- Improve usability and delivery predictability in parallel.

### Scope
- Run 2 rounds of usability tests on the top 3 journeys.
- Promote high-performing patterns into versioned design system components.
- Introduce quarterly capability scorecards for coding/debugging/design tracks.
- Publish v1 Operating Handbook (delivery, reliability, security, AI risk, incident process).

### Done criteria
- Task success and completion time improve on priority journeys.
- Repeatable onboarding path (<14 days) validated with one new contributor.
- Operating handbook adopted in weekly/monthly rituals.

---

## Cross-Sprint Program Management

### Governance rhythm
- Weekly: sprint execution + reliability review.
- Biweekly: capability track review (coding/debugging/design).
- Monthly: risk review (security + AI + operational incidents).

### Metrics pack (tracked every sprint)
- Delivery: lead time, deployment frequency, rework rate.
- Stability: failed deployment recovery time, change fail rate, escaped defects.
- Security: vuln backlog age, patch SLA compliance, dependency risk exceptions.
- AI: eval pass rate, hallucination/grounding failure rate, policy violation rate.
- UX: task success, completion time, rework loops.

---

## Research-backed strengthening recommendations

1. **Adopt modern DORA five-metric set** for throughput + instability to avoid one-dimensional velocity optimization.
2. **Unify telemetry with OpenTelemetry signals and semantic conventions** so logs/traces/metrics correlate consistently.
3. **Use SSDF as the secure-development baseline** and map current controls to close lifecycle security gaps.
4. **Use OWASP SAMM to prioritize maturity work in iterations** rather than ad hoc security improvements.
5. **Implement supply-chain controls with SLSA + SBOM (SPDX)** for stronger artifact trust and auditability.
6. **Operationalize AI risk management with NIST AI RMF practices and playbook-oriented evidence capture.**

---

## Suggested ownership model

- **Platform lead:** observability, CI/CD controls, provenance.
- **Reliability lead:** incident taxonomy, MTTR program, regression strategy.
- **Security lead:** SSDF mapping, SBOM/provenance policy, vuln operations.
- **AI lead:** eval harness, misuse risk controls, model release gates.
- **Design lead:** workflow UX metrics, design system promotion, adoption quality.


## References (research anchors)

- DORA/Google Cloud: software delivery and operational performance metrics.
- OpenTelemetry specification and semantic conventions.
- NIST SP 800-218 (SSDF).
- OWASP SAMM maturity framework.
- SLSA supply-chain levels and provenance requirements.
- SPDX SBOM specification overview.
- NIST AI Risk Management Framework (AI RMF 1.0).

---

## Sprint 1 implementation update (completed in repo)

- `execution_plan.py` now captures deployment and lead-time fields in weekly scorecards and computes a reliability snapshot (deployment frequency, change failure rate, lead time, restoration rate).
- `execution_plan_cli.py` now supports reliability inputs (`--deployments`, `--failed-deployments`, `--restored-incidents`, `--total-lead-time-hours`) when recording scorecards.
- `telemetry.py` now provides structured JSONL telemetry events with trace IDs and trace-coverage tracking.

## Sprint 2 implementation update (completed in repo)

- `quality_gates.py` now defines tiered policy checks (`core`, `moderate`, `low`) for pre-merge and release readiness.
- `quality_gates_cli.py` now evaluates a JSON change envelope and emits machine-readable gate/checklist output.
- `test_quality_gates.py` now validates core-tier failure behavior and low-tier baseline pass behavior.

## Sprint 3 implementation update (completed in repo)

- `supply_chain.py` now implements lightweight SBOM generation (SPDX-like payload), provenance generation, and critical vulnerability SLA checks.
- `supply_chain_cli.py` now provides `sbom`, `provenance`, and `sla` commands for operating the supply-chain controls.
- `test_supply_chain.py` now validates SBOM generation and vulnerability SLA breach detection behavior.

## Sprint 4 implementation update (completed in repo)

- `ai_eval.py` now provides an evaluation harness for task keyword accuracy + refusal/policy behavior.
- `ai_eval_cli.py` now runs batch evaluation from case/output JSON inputs and emits summary metrics.
- `test_ai_eval.py` now validates normal task pass behavior and must-refuse policy behavior.

## Sprint 5 implementation update (completed in repo)

- `sprint5_ops.py` now provides quarterly capability-health, UX-improvement, and onboarding-readiness checks.
- `automation_intelligence_audit.py` now performs a repository-level automation/intelligence audit and produces prioritized recommendations.
- `automation_intelligence_audit_cli.py` now exposes the audit as a command-line report (human-readable or JSON).
- `test_sprint5_ops.py` and `test_automation_intelligence_audit.py` now validate sprint-5 operating checks and audit behavior.

## Repository automation/intelligence review — immediate opportunities

1. Add CI workflows to automatically run tests, compile checks, and quality gate policies on every PR.
2. Add scheduled audit runs (`automation_intelligence_audit_cli.py`) to track automation maturity trend over time.
3. Consolidate existing CLIs under one unified command router to reduce operator friction and scripting complexity.
4. Auto-publish scorecards/eval summaries to a dashboard artifact for weekly and monthly governance rituals.
