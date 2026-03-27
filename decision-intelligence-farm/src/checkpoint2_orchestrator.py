"""Next major checkpoint 2: run weekly operating loop end-to-end."""

from __future__ import annotations

from pathlib import Path

from artifact_registry import ArtifactRegistry
from checkpoint_integration import (
    build_experiment_backlog,
    persist_customer_snapshot,
    persist_gtm_backlog,
    promotion_decision_with_model_ops,
)
from customer_intelligence import FeedbackItem
from dashboard_artifacts import build_dashboard
from governance_bot import recommend_actions
from pipeline_runner import PipelineRun
from revenue_gtm import summarize_experiments


class WeeklyLoopOrchestrator:
    def __init__(self, registry_dir: str | Path):
        self.registry_dir = Path(registry_dir)
        self.registry = ArtifactRegistry(self.registry_dir)

    def run(
        self,
        *,
        run_id: str,
        feedback: list[FeedbackItem],
        quality_passed: bool,
        supply_chain_passed: bool,
        baseline_pass_rate: float,
        candidate_pass_rate: float,
        safety_incidents: int,
        delivery_rate: float,
    ) -> dict:
        pipeline = PipelineRun(run_id=run_id)
        pipeline.mark("collect_feedback", "passed", f"items={len(feedback)}")

        customer_snapshot = persist_customer_snapshot(self.registry_dir, feedback)
        pipeline.mark("customer_snapshot", "passed", str(customer_snapshot))

        backlog = build_experiment_backlog(feedback)
        backlog_artifact = persist_gtm_backlog(self.registry_dir, backlog)
        pipeline.mark("gtm_backlog", "passed", str(backlog_artifact))

        promotion = promotion_decision_with_model_ops(
            quality_passed=quality_passed,
            supply_chain_passed=supply_chain_passed,
            baseline_pass_rate=baseline_pass_rate,
            candidate_pass_rate=candidate_pass_rate,
            safety_incidents=safety_incidents,
            delivery_rate=delivery_rate,
        )
        pipeline.mark("promotion_decision", "passed" if promotion["promote"] else "failed")

        dashboard = build_dashboard(
            execution_summary={"delivery_rate": delivery_rate},
            quality_summary={"passed": quality_passed},
            supply_summary={"passed": supply_chain_passed},
            ai_eval_summary={"pass_rate": candidate_pass_rate},
            automation_audit_summary={"status_counts": {"missing": 0}},
        )
        dashboard["gtm_summary"] = summarize_experiments(backlog)
        dashboard["promotion"] = promotion

        actions = recommend_actions(dashboard)

        dashboard_path = self.registry.register("weekly_dashboard", dashboard)
        actions_path = self.registry.register("weekly_actions", {"actions": actions})
        pipeline.mark("dashboard", "passed", str(dashboard_path))
        pipeline.mark("actions", "passed", str(actions_path))

        return {
            "pipeline": pipeline.summary(),
            "dashboard_path": str(dashboard_path),
            "actions_path": str(actions_path),
            "actions": actions,
            "promotion": promotion,
        }
