"""Build consolidated governance dashboard artifacts from JSON inputs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())


def build_dashboard(
    *,
    execution_summary: dict,
    quality_summary: dict,
    supply_summary: dict,
    ai_eval_summary: dict,
    automation_audit_summary: dict,
) -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat()[:19],
        "execution": execution_summary,
        "quality": quality_summary,
        "supply_chain": supply_summary,
        "ai_eval": ai_eval_summary,
        "automation": automation_audit_summary,
        "alerts": {
            "quality_gate_failed": not quality_summary.get("passed", True),
            "supply_chain_breach": not supply_summary.get("passed", True),
            "ai_eval_regression": ai_eval_summary.get("pass_rate", 1.0) < 0.8,
            "automation_gap": automation_audit_summary.get("status_counts", {}).get("missing", 0)
            > 0,
        },
    }


def write_dashboard(path: str | Path, payload: dict) -> None:
    Path(path).write_text(json.dumps(payload, indent=2))
