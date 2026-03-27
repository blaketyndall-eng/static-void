# 30/60/90 Execution Implementation

This is the concrete implementation path for the software-arm advancement plan, mapped to the coding, debugging, and design tracks.

## Day 0 Setup (pre-work)

- Confirm owners per track (coding/debugging/design).
- Baseline current metrics for throughput, defects, MTTR, and UX.
- Create a shared weekly scorecard and monthly review ritual.
- Define one active project lane used for skill evidence collection.

---

## First 30 Days — Foundation + Instrumentation

### Objectives
- Establish standards and baseline operating rhythm.
- Ensure work is measurable and traceable.
- Start shipping with minimal process overhead.

### Coding track deliverables
- Implementation checklist template for PR quality.
- Definition of done includes tests + telemetry touchpoints.
- One reference module refactored to target standards.

### Debugging track deliverables
- Repro-first bug template in issue workflow.
- Incident severity rubric (S1/S2/S3) and response expectations.
- Initial postmortem template with explicit root-cause sections.

### Design track deliverables
- Core workflow map for top 3 console journeys.
- Baseline UI conventions (layout, hierarchy, interaction states).
- Component inventory for reuse planning.

### Exit criteria (Day 30)
- Weekly scorecard in use for at least 3 consecutive weeks.
- At least one shipped improvement in each track.
- Baseline metrics documented and visible.

---

## Days 31–60 — Capability Lift + Reliability

### Objectives
- Increase delivery quality while raising pace.
- Reduce repeated failure modes.
- Convert early standards into repeatable playbooks.

### Coding track deliverables
- Service/module ownership map with clear boundaries.
- CI gates for lint/test/build on core projects.
- Two documented implementation playbooks (e.g., API integration, schema migration).

### Debugging track deliverables
- Known-failure pattern library with fixes/workarounds.
- MTTR reduction plan for top recurring defect categories.
- Regression guardrails added to CI for critical defect classes.

### Design track deliverables
- Decision workflow UI prototype pass (v2).
- Reusable component specs for the highest-frequency patterns.
- Usability session notes and top 5 UX fixes implemented.

### Exit criteria (Day 60)
- Measurable quality lift vs Day 30 baseline:
  - defect escape rate trending down,
  - MTTR improved,
  - fewer redesign loops.
- At least one playbook per track in active use.

---

## Days 61–90 — Scale + Operational Maturity

### Objectives
- Make performance sustainable and repeatable.
- Move from heroics to systems.
- Lock in advancement evidence for each track.

### Coding track deliverables
- Architecture decision records (ADRs) for major technical choices.
- Backlog segmentation by complexity/risk for better planning accuracy.
- Shared module templates for fast, consistent development starts.

### Debugging track deliverables
- Standard incident review cadence and action tracking.
- Reliability dashboard with category-level trend visibility.
- Preventive testing strategy covering top incident classes.

### Design track deliverables
- Versioned design system starter for console features.
- UX quality checklist integrated into review workflow.
- Task success benchmark improvements on priority journeys.

### Exit criteria (Day 90)
- Evidence-based advancement review complete for all tracks.
- 90-day outcomes documented with next-quarter recommendations.
- Team operating model can onboard new contributors in <14 days.

---

## Governance Cadence

### Weekly
- Track lead sync (30 min): scorecard, blockers, commitments.
- Ship review: what was deployed, what learned, what adjusted.

### Monthly
- Capability review by track level (L1/L2/L3 evidence).
- Metric trend review and intervention planning.

### Day 90 Closeout
- Consolidated retrospective.
- Updated advancement plan and next 30/60/90 cycle.

---

## Scorecard Template (minimum fields)

- Planned vs delivered commitments.
- Defects opened/closed and escape rate.
- MTTI and MTTR by severity.
- UX task success and cycle time.
- Reuse counts (components/playbooks/templates).

## Risks and Mitigations

- **Risk:** Process overhead slows shipping.  
  **Mitigation:** Keep artifacts lightweight; prioritize evidence from shipped outcomes.
- **Risk:** Inconsistent measurement across tracks.  
  **Mitigation:** Enforce one shared scorecard schema.
- **Risk:** Quality regressions during speed push.  
  **Mitigation:** CI gates + incident postmortem action tracking.



## Operational Assets (Implemented)

The plan is now backed by runnable implementation assets in `decision-intelligence-farm/src`:
- `execution_plan.py`: plan bootstrap, phase detection, weekly scorecard ledger, evidence ledger, and summary computation.
- `execution_plan_cli.py`: command line workflow for bootstrapping the cycle, adding scorecards/evidence, and printing summary state.
- `activity_log.py`: execution-aware logging methods (`log_execution`, `log_scorecard`) and timeline icon support.

### Quick-start commands

```bash
python decision-intelligence-farm/src/execution_plan_cli.py bootstrap --start-date 2026-03-27
python decision-intelligence-farm/src/execution_plan_cli.py add-scorecard --week-start 2026-03-23 --week-end 2026-03-29 --planned 5 --delivered 4
python decision-intelligence-farm/src/execution_plan_cli.py summary --as-json
```
