from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.system_events import CreateSystemEventRequest
from packages.domain.system_events import SystemEventRecord, SystemEventType
from packages.repositories.system_events import SystemEventRepository
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/system-events", tags=["system_events"])
telemetry = TelemetryLogger(filepath="var/system_events_telemetry.jsonl")


@router.post("")
def create_system_event(payload: CreateSystemEventRequest, db: Session = Depends(get_db)) -> dict:
    try:
        event_type = SystemEventType(payload.event_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid event_type") from exc

    repo = SystemEventRepository(db)
    event = SystemEventRecord(
        event_type=event_type,
        source_arm=payload.source_arm,
        source_id=payload.source_id,
        summary=payload.summary,
        metadata=payload.metadata,
    )
    saved = repo.create(event)
    emit_action_event(
        telemetry,
        API_REQUEST_COMPLETED,
        route="create_system_event",
        event_id=saved.id,
        event_type=saved.event_type.value,
    )
    return saved.model_dump(mode="json")


@router.get("")
def list_system_events(db: Session = Depends(get_db)) -> list[dict]:
    repo = SystemEventRepository(db)
    payload = [item.model_dump(mode="json") for item in repo.list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="list_system_events", returned_count=len(payload))
    return payload


@router.get("/source/{source_arm}/{source_id}")
def list_system_events_for_source(source_arm: str, source_id: str, db: Session = Depends(get_db)) -> dict:
    repo = SystemEventRepository(db)
    items = [item.model_dump(mode="json") for item in repo.list_for_source(source_arm, source_id)]
    emit_view_event(
        telemetry,
        API_REQUEST_COMPLETED,
        route="list_system_events_for_source",
        source_arm=source_arm,
        source_id=source_id,
        returned_count=len(items),
    )
    return {"count": len(items), "items": items}
