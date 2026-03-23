from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from event_logger import EventLogger
from packages.contracts.core import CreateOpportunityRequest, CreateSourceRequest
from packages.domain.core import EventCategory, OpportunityRecord, OpportunityStage, SourceRecord, SourceType, new_id
from packages.repositories.opportunities import OpportunityRepository
from packages.repositories.sources import SourceRepository
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1", tags=["sources", "opportunities"])
logger = EventLogger(filepath="var/integrated_intelligence_events.jsonl")
telemetry = TelemetryLogger(filepath="var/backend_packaged_telemetry.jsonl")


@router.post("/sources")
def create_source(payload: CreateSourceRequest, db: Session = Depends(get_db)) -> dict:
    try:
        source_type = SourceType(payload.source_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid source_type") from exc
    repo = SourceRepository(db)
    record = SourceRecord(
        id=new_id("src"),
        name=payload.name,
        source_type=source_type,
        trust_score=payload.trust_score,
        freshness_label=payload.freshness_label,
        owner=payload.owner,
        notes=payload.notes,
        tags=payload.tags,
    )
    saved = repo.create(source=record)
    logger.log(category=EventCategory.source, event_type="created", entity_type="source", entity_id=saved.id, payload={"name": saved.name})
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_source", source_id=saved.id)
    return saved.model_dump(mode="json")


@router.post("/opportunities")
def create_opportunity(payload: CreateOpportunityRequest, db: Session = Depends(get_db)) -> dict:
    repo = OpportunityRepository(db)
    record = OpportunityRecord(
        id=new_id("opp"),
        title=payload.title,
        summary=payload.summary,
        source_ids=payload.source_ids,
        themes=payload.themes,
        score=payload.score,
    )
    saved = repo.create(opportunity=record)
    logger.log(category=EventCategory.opportunity, event_type="created", entity_type="opportunity", entity_id=saved.id, payload={"title": saved.title, "score": saved.score})
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_opportunity", opportunity_id=saved.id)
    return saved.model_dump(mode="json")


@router.post("/opportunities/{opportunity_id}/stage/{stage}")
def update_opportunity_stage(opportunity_id: str, stage: str, db: Session = Depends(get_db)) -> dict:
    try:
        target_stage = OpportunityStage(stage)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid stage") from exc
    repo = OpportunityRepository(db)
    record = repo.update_stage(opportunity_id, target_stage)
    if record is None:
        raise HTTPException(status_code=404, detail="opportunity not found")
    logger.log(category=EventCategory.opportunity, event_type="stage_updated", entity_type="opportunity", entity_id=record.id, payload={"stage": record.stage.value})
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="update_opportunity_stage", opportunity_id=record.id, stage=record.stage.value)
    return record.model_dump(mode="json")
