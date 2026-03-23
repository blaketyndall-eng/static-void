import json
from pathlib import Path
from typing import Any


class TelemetryLogger:
    def __init__(self, filepath: str = "var/telemetry.jsonl") -> None:
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        record = {
            "event_name": event_name,
            "payload": payload,
        }
        with self.filepath.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
        return record

    def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self.filepath.exists():
            return []
        rows: list[dict[str, Any]] = []
        with self.filepath.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                rows.append(json.loads(line))
        return rows[-limit:]
