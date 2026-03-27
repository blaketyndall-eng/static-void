# AI Scientist-v2 Adaptation Plan for Decision Intelligence Console

This document summarizes what is reusable from **SakanaAI/AI-Scientist-v2** and how to adapt the pattern into our app safely.

## What AI Scientist-v2 contributes (pattern-level)

From the repository and README flow, the core transferable pattern is:
1. **Ideation stage** (generate/refine structured ideas from a topic file).
2. **Agentic tree-search experimentation stage** (best-first exploration with parallel workers, debug depth, and staged expansion).
3. **Writeup/review stage** (synthesize outputs and evaluate quality).
4. **Literature/novelty integration** via Semantic Scholar API.
5. **Strong sandbox caution** because LLM-generated code is executed.

## Mapping into our existing app

### Existing assets we already have
- `execution_plan.py`: scorecards, evidence, and reliability snapshots.
- `quality_gates.py`: tiered pre-merge/release gate policy.
- `supply_chain.py`: SBOM/provenance/SLA checks.
- `ai_eval.py`: eval harness for task + refusal behavior.
- `automation_intelligence_audit.py`: repo maturity audit and recommendations.

### New sprint implementation (this commit)
- `research_loop.py`: lightweight tree-search-like loop skeleton with nodes, branching, weighted scoring, frontier selection, and snapshot export.
- `research_loop_cli.py`: JSON-driven entry point to run loop snapshots and extract top frontier nodes.
- `test_research_loop.py`: regression test for branching/scoring/frontier behavior.

## Proposed architecture for full integration

## Layer A — Research Orchestration
- `ResearchLoop` (new) manages idea graph and candidate ranking.
- Inputs: topic briefs + constraints + prior evidence.
- Outputs: prioritized experiment candidates.

## Layer B — Safe Experiment Runtime
- Use `quality_gates` before running generated experiment plans.
- Use `supply_chain` to attach SBOM/provenance artifacts to experiment outputs.
- Keep runtime in isolated sandbox/container with restricted network and package policy.

## Layer C — Evaluation + Governance
- Evaluate outputs with `ai_eval` + domain-specific metrics.
- Log scorecards/evidence into `execution_plan`.
- Run `automation_intelligence_audit` on schedule for continuous process upgrades.

## Practical 3-step rollout

1. **Pilot (1–2 weeks):**
   - Run idea generation + frontier ranking only (no autonomous code execution).
   - Human approve top candidates before experiments.
2. **Constrained execution (2–4 weeks):**
   - Allow scripted experiments in restricted containers.
   - Enforce quality gates and provenance generation.
3. **Scaled loop (4+ weeks):**
   - Enable periodic batch runs with dashboarded outcomes.
   - Tighten model eval thresholds and automated rollback rules.

## Key guardrails (non-negotiable)

- Never run model-generated code outside sandboxed execution.
- Require provenance + artifact digest for every experiment.
- Gate promotion by both performance and policy-alignment checks.
- Maintain audit trails for idea lineage and decision rationale.

## Why this fits our app

AI Scientist-v2 is optimized for autonomous scientific discovery; our app is a decision-intelligence operating system. The adaptation should copy the **loop structure** (idea → explore → evaluate → report), while grounding execution in our existing reliability, security, and governance primitives.

## External research sources

- AI Scientist-v2 repository: https://github.com/SakanaAI/AI-Scientist-v2
- AI Scientist-v2 paper listing in repo README (`arXiv:2504.08066`)
- AI Scientist (v1) repository for template mechanics and review pipeline: https://github.com/SakanaAI/AI-Scientist
