import json
from pathlib import Path
from typing import Any

from domain_models import EventCategory, EventRecord, new_id


class EventLogger:
    def __init__(self, filepath: str = "var/events.jsonl") -> None:
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        *,
        category: EventCategory,
        event_type: str,
        entity_type: str,
        entity_id: str,
        actor: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> EventRecord:
        record = EventRecord(
            id=new_id("evt"),
            category=category,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actor=actor,
            payload=payload or {},
        )
        with self.filepath.open("a", encoding="utf-8") as handle:
            handle.write(record.model_dump_json() + "\n")
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
