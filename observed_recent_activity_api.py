from fastapi import FastAPI

from event_logger import EventLogger
from telemetry_events import ACTIVITY_RECENT_VIEWED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

app = FastAPI(title="Observed Recent Activity API")
activity_logger = EventLogger(filepath="var/integrated_intelligence_events.jsonl")
telemetry = TelemetryLogger(filepath="var/activity_surface_telemetry.jsonl")


@app.get("/api/v1/activity/recent-observed")
def get_recent_activity_observed(limit: int = 25) -> dict:
    events = activity_logger.recent(limit=limit)
    items = []
    for event in reversed(events):
        items.append(
            {
                "id": event.get("id"),
                "event_type": event.get("event_type"),
                "entity_type": event.get("entity_type"),
                "entity_id": event.get("entity_id"),
                "category": event.get("category"),
                "time": event.get("created_at", event.get("timestamp")),
                "payload": event.get("payload", {}),
            }
        )

    emit_view_event(
        telemetry,
        ACTIVITY_RECENT_VIEWED,
        returned_count=len(items),
        limit=limit,
    )

    return {"count": len(items), "items": items}
