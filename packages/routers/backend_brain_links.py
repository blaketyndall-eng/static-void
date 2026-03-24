from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.brain_links import CreateBrainLinkRequest
from packages.domain.brain_links import BrainLinkRecord, BrainLinkType
from packages.repositories.brain_links import BrainLinkRepository
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/brain-links", tags=["brain_links"])
telemetry = TelemetryLogger(filepath="var/brain_links_telemetry.jsonl")


@router.post("")
def create_brain_link(payload: CreateBrainLinkRequest, db: Session = Depends(get_db)) -> dict:
    try:
        target_type = BrainLinkType(payload.target_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid target_type") from exc

    repo = BrainLinkRepository(db)
    record = BrainLinkRecord(
        source_arm=payload.source_arm,
        source_id=payload.source_id,
        target_type=target_type,
        target_id=payload.target_id,
        notes=payload.notes,
    )
    saved = repo.create(record)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_brain_link", brain_link_id=saved.id, source_arm=saved.source_arm)
    return saved.model_dump(mode="json")


@router.get("")
def list_brain_links(db: Session = Depends(get_db)) -> list[dict]:
    repo = BrainLinkRepository(db)
    payload = [item.model_dump(mode="json") for item in repo.list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="list_brain_links", returned_count=len(payload))
    return payload


@router.get("/source/{source_arm}/{source_id}")
def list_brain_links_for_source(source_arm: str, source_id: str, db: Session = Depends(get_db)) -> dict:
    repo = BrainLinkRepository(db)
    items = [item.model_dump(mode="json") for item in repo.list_for_source(source_arm, source_id)]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="list_brain_links_for_source", source_arm=source_arm, source_id=source_id, returned_count=len(items))
    return {"count": len(items), "items": items}


@router.get("/modules/summary")
def get_brain_module_summary(db: Session = Depends(get_db)) -> dict:
    repo = BrainLinkRepository(db)
    items = [item.model_dump(mode="json") for item in repo.summarize_modules()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_brain_module_summary", returned_count=len(items))
    return {"count": len(items), "items": items}
