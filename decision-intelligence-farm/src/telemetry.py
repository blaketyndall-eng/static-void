"""Sprint 1 telemetry helpers: trace IDs + structured event logging."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import config


class Telemetry:
    """File-backed telemetry helper with per-event trace correlation IDs."""

    LOG_FILE = config.META_DIR / "telemetry_events.jsonl"

    def __init__(self):
        self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def new_trace_id() -> str:
        return str(uuid.uuid4())

    def log_event(
        self,
        name: str,
        payload: dict[str, Any],
        trace_id: str | None = None,
        severity: str = "info",
        source: str = "execution_plan",
    ) -> dict[str, Any]:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat()[:19],
            "trace_id": trace_id or self.new_trace_id(),
            "name": name,
            "severity": severity,
            "source": source,
            "payload": payload,
        }
        with open(self.LOG_FILE, "a") as f:
            f.write(json.dumps(event) + "\n")
        return event

    def read_recent(self, limit: int = 100) -> list[dict[str, Any]]:
        if not self.LOG_FILE.exists():
            return []

        rows: list[dict[str, Any]] = []
        with open(self.LOG_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return rows[-limit:]

    def trace_coverage(self, limit: int = 200) -> float:
        rows = self.read_recent(limit=limit)
        if not rows:
            return 0.0
        with_trace = sum(1 for r in rows if r.get("trace_id"))
        return round(with_trace / len(rows), 3)
