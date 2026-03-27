"""CLI helpers for operating the 30/60/90 execution plan."""

from __future__ import annotations

import argparse
import json

from execution_plan import (
    ExecutionPlanManager,
    TrackCommitment,
    TrackEvidence,
    WeeklyScorecard,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="30/60/90 execution plan CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    boot = sub.add_parser("bootstrap", help="Initialize 90-day plan")
    boot.add_argument("--start-date", default=None, help="YYYY-MM-DD")
    boot.add_argument("--coding-owner", default="")
    boot.add_argument("--debugging-owner", default="")
    boot.add_argument("--design-owner", default="")

    summary = sub.add_parser("summary", help="Show current plan summary")
    summary.add_argument("--as-json", action="store_true")

    evidence = sub.add_parser("add-evidence", help="Append track advancement evidence")
    evidence.add_argument("--track", choices=["coding", "debugging", "design"], required=True)
    evidence.add_argument("--level", choices=["L1", "L2", "L3"], required=True)
    evidence.add_argument("--shipped-item", required=True)
    evidence.add_argument("--artifact-type", required=True)
    evidence.add_argument("--artifact-path", default="")
    evidence.add_argument("--summary", default="")

    score = sub.add_parser("add-scorecard", help="Append weekly scorecard")
    score.add_argument("--week-start", required=True)
    score.add_argument("--week-end", required=True)
    score.add_argument("--planned", type=int, default=0)
    score.add_argument("--delivered", type=int, default=0)
    score.add_argument("--defects-opened", type=int, default=0)
    score.add_argument("--defects-closed", type=int, default=0)
    score.add_argument("--defect-escape-rate", type=float, default=0.0)
    score.add_argument("--mtti-hours", type=float, default=0.0)
    score.add_argument("--mttr-hours", type=float, default=0.0)
    score.add_argument("--ux-task-success", type=float, default=0.0)
    score.add_argument("--ux-cycle-days", type=float, default=0.0)
    score.add_argument("--component-reuse", type=int, default=0)
    score.add_argument("--playbook-reuse", type=int, default=0)
    score.add_argument("--template-reuse", type=int, default=0)
    score.add_argument("--deployments", type=int, default=0)
    score.add_argument("--failed-deployments", type=int, default=0)
    score.add_argument("--restored-incidents", type=int, default=0)
    score.add_argument("--total-lead-time-hours", type=float, default=0.0)
    score.add_argument(
        "--commitment",
        action="append",
        default=[],
        help="Track commitment in the format track|statement|delivered(true/false)|notes",
    )
    score.add_argument("--blocker", action="append", default=[])
    score.add_argument("--adjustment", action="append", default=[])

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manager = ExecutionPlanManager()

    if args.command == "bootstrap":
        plan = manager.bootstrap_plan(
            start_date=args.start_date,
            coding_owner=args.coding_owner,
            debugging_owner=args.debugging_owner,
            design_owner=args.design_owner,
        )
        print(plan.model_dump_json(indent=2))
        return

    if args.command == "summary":
        payload = manager.summarize()
        if args.as_json:
            print(json.dumps(payload, indent=2))
        else:
            for key, value in payload.items():
                print(f"{key}: {value}")
        return

    if args.command == "add-evidence":
        manager.add_evidence(
            TrackEvidence(
                track=args.track,
                level=args.level,
                shipped_item=args.shipped_item,
                artifact_type=args.artifact_type,
                artifact_path=args.artifact_path,
                summary=args.summary,
            )
        )
        print("Evidence added.")
        return

    if args.command == "add-scorecard":
        commitments: list[TrackCommitment] = []
        for raw in args.commitment:
            parts = raw.split("|", 3)
            if len(parts) < 2:
                continue
            track = parts[0].strip()
            statement = parts[1].strip()
            delivered = len(parts) > 2 and parts[2].strip().lower() == "true"
            notes = parts[3].strip() if len(parts) > 3 else ""
            commitments.append(
                TrackCommitment(
                    track=track, commitment=statement, delivered=delivered, notes=notes
                )
            )

        manager.add_weekly_scorecard(
            WeeklyScorecard(
                week_start=args.week_start,
                week_end=args.week_end,
                planned_commitments=args.planned,
                delivered_commitments=args.delivered,
                defects_opened=args.defects_opened,
                defects_closed=args.defects_closed,
                defect_escape_rate=args.defect_escape_rate,
                mtti_hours=args.mtti_hours,
                mttr_hours=args.mttr_hours,
                ux_task_success_rate=args.ux_task_success,
                ux_cycle_time_days=args.ux_cycle_days,
                component_reuse_count=args.component_reuse,
                playbook_reuse_count=args.playbook_reuse,
                template_reuse_count=args.template_reuse,
                deployments=args.deployments,
                failed_deployments=args.failed_deployments,
                restored_incidents=args.restored_incidents,
                total_lead_time_hours=args.total_lead_time_hours,
                commitments=commitments,
                blockers=args.blocker,
                adjustments=args.adjustment,
            )
        )
        print("Scorecard added.")


if __name__ == "__main__":
    main()
