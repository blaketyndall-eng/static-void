"""30/60/90 execution plan implementation utilities.

This module turns the software-arm advancement docs into practical, reusable
assets for weekly operation: plan bootstrap, scorecard capture, evidence
tracking, and 90-day summary generation.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

import config
from telemetry import Telemetry

TrackName = Literal["coding", "debugging", "design"]


class TrackCommitment(BaseModel):
    """A single committed deliverable for a capability track."""

    track: TrackName
    commitment: str
    delivered: bool = False
    notes: str = ""


class WeeklyScorecard(BaseModel):
    """Shared scorecard schema used across all capability tracks."""

    week_start: str
    week_end: str
    planned_commitments: int = 0
    delivered_commitments: int = 0
    defects_opened: int = 0
    defects_closed: int = 0
    defect_escape_rate: float = 0.0
    mtti_hours: float = 0.0
    mttr_hours: float = 0.0
    ux_task_success_rate: float = 0.0
    ux_cycle_time_days: float = 0.0
    component_reuse_count: int = 0
    playbook_reuse_count: int = 0
    template_reuse_count: int = 0
    deployments: int = 0
    failed_deployments: int = 0
    restored_incidents: int = 0
    total_lead_time_hours: float = 0.0
    commitments: list[TrackCommitment] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    adjustments: list[str] = Field(default_factory=list)


class TrackEvidence(BaseModel):
    """Evidence item proving track advancement based on shipped work."""

    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()[:19]
    )
    track: TrackName
    level: Literal["L1", "L2", "L3"]
    shipped_item: str
    artifact_type: str
    artifact_path: str = ""
    summary: str = ""


class PlanBootstrap(BaseModel):
    """Core 90-day plan timeline and ownership model."""

    start_date: str
    day_30: str
    day_60: str
    day_90: str
    track_owners: dict[TrackName, str] = Field(default_factory=dict)
    weekly_ritual_day: str = "Friday"
    monthly_review_day: str = "Last Friday"


class ExecutionPlanManager:
    """File-backed manager for 30/60/90 plan operation."""

    ROOT = config.META_DIR / "execution_plan"
    BOOTSTRAP_FILE = ROOT / "bootstrap.json"
    SCORECARD_FILE = ROOT / "weekly_scorecards.jsonl"
    EVIDENCE_FILE = ROOT / "track_evidence.jsonl"

    def __init__(self):
        self.ROOT.mkdir(parents=True, exist_ok=True)
        self.telemetry = Telemetry()

    @staticmethod
    def _parse_date(value: str) -> date:
        return datetime.strptime(value, "%Y-%m-%d").date()

    def bootstrap_plan(
        self,
        start_date: str | None = None,
        coding_owner: str = "",
        debugging_owner: str = "",
        design_owner: str = "",
    ) -> PlanBootstrap:
        """Initialize plan timeline and ownership metadata."""
        start = self._parse_date(start_date) if start_date else date.today()

        plan = PlanBootstrap(
            start_date=start.isoformat(),
            day_30=(start + timedelta(days=30)).isoformat(),
            day_60=(start + timedelta(days=60)).isoformat(),
            day_90=(start + timedelta(days=90)).isoformat(),
            track_owners={
                "coding": coding_owner,
                "debugging": debugging_owner,
                "design": design_owner,
            },
        )
        self.BOOTSTRAP_FILE.write_text(plan.model_dump_json(indent=2))
        self.telemetry.log_event(
            "execution_plan_bootstrapped",
            payload={
                "start_date": plan.start_date,
                "day_30": plan.day_30,
                "day_60": plan.day_60,
                "day_90": plan.day_90,
            },
        )
        return plan

    def get_bootstrap(self) -> PlanBootstrap | None:
        """Load existing 90-day timeline, if present."""
        if not self.BOOTSTRAP_FILE.exists():
            return None
        return PlanBootstrap.model_validate_json(self.BOOTSTRAP_FILE.read_text())

    def current_phase(self, on_date: str | None = None) -> str:
        """Return active phase name for a given date."""
        plan = self.get_bootstrap()
        if not plan:
            return "uninitialized"

        today = self._parse_date(on_date) if on_date else date.today()
        start = self._parse_date(plan.start_date)
        d30 = self._parse_date(plan.day_30)
        d60 = self._parse_date(plan.day_60)
        d90 = self._parse_date(plan.day_90)

        if today < start:
            return "pre-start"
        if start <= today <= d30:
            return "days_0_30"
        if d30 < today <= d60:
            return "days_31_60"
        if d60 < today <= d90:
            return "days_61_90"
        return "post_90"

    def add_weekly_scorecard(self, card: WeeklyScorecard) -> None:
        """Append one weekly scorecard entry to the ledger."""
        start = self._parse_date(card.week_start)
        end = self._parse_date(card.week_end)
        if end < start:
            raise ValueError("week_end must be on or after week_start")
        with open(self.SCORECARD_FILE, "a") as f:
            f.write(card.model_dump_json() + "\n")
        self.telemetry.log_event(
            "weekly_scorecard_added",
            payload={
                "week_start": card.week_start,
                "week_end": card.week_end,
                "planned": card.planned_commitments,
                "delivered": card.delivered_commitments,
                "deployments": card.deployments,
                "failed_deployments": card.failed_deployments,
            },
        )

    def add_evidence(self, evidence: TrackEvidence) -> None:
        """Append one advancement evidence item."""
        with open(self.EVIDENCE_FILE, "a") as f:
            f.write(evidence.model_dump_json() + "\n")
        self.telemetry.log_event(
            "track_evidence_added",
            payload={
                "track": evidence.track,
                "level": evidence.level,
                "artifact_type": evidence.artifact_type,
            },
        )

    def _read_jsonl(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        rows: list[dict] = []
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return rows

    def get_scorecards(self) -> list[dict]:
        return self._read_jsonl(self.SCORECARD_FILE)

    def get_evidence(self) -> list[dict]:
        return self._read_jsonl(self.EVIDENCE_FILE)

    def summarize(self) -> dict:
        """Compute operational summary for reviews and closeout."""
        cards = self.get_scorecards()
        evidence = self.get_evidence()

        delivered = sum(c.get("delivered_commitments", 0) for c in cards)
        planned = sum(c.get("planned_commitments", 0) for c in cards)
        defects_opened = sum(c.get("defects_opened", 0) for c in cards)
        defects_closed = sum(c.get("defects_closed", 0) for c in cards)

        by_track: dict[str, int] = {"coding": 0, "debugging": 0, "design": 0}
        for item in evidence:
            track = item.get("track")
            if track in by_track:
                by_track[track] += 1

        return {
            "phase": self.current_phase(),
            "weeks_recorded": len(cards),
            "planned_commitments": planned,
            "delivered_commitments": delivered,
            "delivery_rate": round((delivered / planned), 3) if planned else 0,
            "defects_opened": defects_opened,
            "defects_closed": defects_closed,
            "evidence_count": len(evidence),
            "evidence_by_track": by_track,
            "reliability_metrics": self.compute_reliability_metrics(cards),
        }

    @staticmethod
    def compute_reliability_metrics(cards: list[dict]) -> dict:
        """Compute a lightweight DORA-style reliability snapshot from scorecards."""
        if not cards:
            return {
                "deployment_frequency_per_week": 0.0,
                "change_failure_rate": 0.0,
                "mean_lead_time_hours": 0.0,
                "restoration_rate": 0.0,
            }

        deployments = sum(c.get("deployments", 0) for c in cards)
        failed_deployments = sum(c.get("failed_deployments", 0) for c in cards)
        restored_incidents = sum(c.get("restored_incidents", 0) for c in cards)
        total_lead_time_hours = sum(c.get("total_lead_time_hours", 0.0) for c in cards)

        return {
            "deployment_frequency_per_week": round(deployments / max(len(cards), 1), 3),
            "change_failure_rate": round(
                (failed_deployments / deployments), 3
            ) if deployments else 0.0,
            "mean_lead_time_hours": round(
                (total_lead_time_hours / deployments), 3
            ) if deployments else 0.0,
            "restoration_rate": round(
                (restored_incidents / failed_deployments), 3
            ) if failed_deployments else 0.0,
        }
