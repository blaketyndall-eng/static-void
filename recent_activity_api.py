from fastapi import FastAPI

from event_logger import EventLogger

app = FastAPI(title="Recent Activity API")
logger = EventLogger(filepath="var/integrated_intelligence_events.jsonl")


@app.get("/api/v1/activity/recent")
def get_recent_activity(limit: int = 25) -> dict:
    events = logger.recent(limit=limit)
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
    return {"count": len(items), "items": items}
