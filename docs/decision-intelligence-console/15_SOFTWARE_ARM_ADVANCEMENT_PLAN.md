# Software Arm Advancement Plan

The software arm is the build-and-ship capability layer for the organization. This plan defines the capability tracks, advancement criteria, and measurement model.

## Capability Tracks

## 1) Coding Track

### Scope
- Planning and structuring implementation work.
- Writing clean, testable, maintainable code.
- Integrating APIs, data models, and internal services.

### Progression Levels
- **L1 — Executor:** Delivers scoped tasks with clear specifications.
- **L2 — Builder:** Owns modules end-to-end with tests and instrumentation.
- **L3 — Systems Operator:** Designs service boundaries and implementation strategy.

### Evidence of advancement
- Merge quality and low rework rate.
- Time-to-delivery against planned estimates.
- Test coverage on touched surfaces.

---

## 2) Debugging Track

### Scope
- Reproduction and triage discipline.
- Root-cause analysis.
- Incident response and postmortem quality.

### Progression Levels
- **L1 — Triage:** Reliably reproduces and scopes defects.
- **L2 — Resolver:** Resolves multi-layer bugs with minimal regressions.
- **L3 — Reliability Lead:** Improves systemic reliability and failure prevention.

### Evidence of advancement
- Mean-time-to-identify (MTTI).
- Mean-time-to-resolve (MTTR).
- Regression rate after hotfixes.

---

## 3) Design Track

### Scope
- Product/interaction design for decision workflows.
- Information architecture and UX clarity.
- Interface quality across desktop-first console surfaces.

### Progression Levels
- **L1 — Implementer:** Executes approved components and flows accurately.
- **L2 — Product Designer:** Proposes flow improvements with measurable UX gains.
- **L3 — Design Systems Lead:** Defines reusable patterns and quality standards.

### Evidence of advancement
- Usability score improvement on key workflows.
- Reduced user confusion/rework in workflows.
- Reuse percentage of approved component patterns.

---

## Common Advancement Rules

- Advancement requires evidence from shipped work, not planned work.
- Every level-up requires one codified artifact:
  - Coding: architecture note or implementation playbook.
  - Debugging: postmortem template improvement or reliability checklist.
  - Design: reusable pattern or documented UX heuristic.
- Progress is reviewed on a recurring 30/60/90 cycle.

## Operating Metrics Dashboard

Track weekly and review monthly:
- Throughput (planned vs delivered).
- Defect escape rate.
- Recovery speed (MTTI/MTTR).
- UX quality proxy (task success + completion time).
- Reuse ratio (components, templates, playbooks).

## Dependencies

- Shared activity logging.
- Decision and experiment telemetry.
- Source and design provenance standards.
- Baseline CI checks for lint/test/build.
