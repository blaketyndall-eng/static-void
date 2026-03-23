from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from api_contracts import (
    AttachEvidenceRequest,
    CreateEvaluationRequest,
    CreateOpportunityRequest,
    CreateSourceRequest,
)
from db_session import get_db
from domain_models import (
    EvaluationRecord,
    EvaluationStatus,
    EventCategory,
    OpportunityRecord,
    OpportunityStage,
    SourceRecord,
    SourceType,
    new_id,
)
from event_logger import EventLogger
from repository_evaluations import EvaluationRepository
from repository_opportunities import OpportunityRepository
from repository_sources import SourceRepository
from settings import get_settings

settings = get_settings()
app = FastAPI(title=f"{settings.app_name} Events Foundation")
logger = EventLogger()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/events")
def list_events(limit: int = 50) -> list[dict]:
    return logger.recent(limit=limit)


@app.post("/api/v1/sources")
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
    logger.log(
        category=EventCategory.source,
        event_type="created",
        entity_type="source",
        entity_id=saved.id,
        payload={"name": saved.name, "source_type": saved.source_type.value},
    )
    return saved.model_dump(mode="json")


@app.post("/api/v1/opportunities")
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
    logger.log(
        category=EventCategory.opportunity,
        event_type="created",
        entity_type="opportunity",
        entity_id=saved.id,
        payload={"title": saved.title, "score": saved.score},
    )
    return saved.model_dump(mode="json")


@app.post("/api/v1/evaluations")
def create_evaluation(payload: CreateEvaluationRequest, db: Session = Depends(get_db)) -> dict:
    repo = EvaluationRepository(db)
    record = EvaluationRecord(
        id=new_id("eval"),
        title=payload.title,
        decision_owner=payload.decision_owner,
        criteria=payload.criteria,
    )
    saved = repo.create(evaluation=record)
    logger.log(
        category=EventCategory.evaluation,
        event_type="created",
        entity_type="evaluation",
        entity_id=saved.id,
        payload={"title": saved.title, "owner": saved.decision_owner},
    )
    return saved.model_dump(mode="json")


@app.post("/api/v1/evaluations/{evaluation_id}/status/{status}")
def update_evaluation_status(evaluation_id: str, status: str, db: Session = Depends(get_db)) -> dict:
    try:
        target_status = EvaluationStatus(status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid status") from exc
    repo = EvaluationRepository(db)
    record = repo.update_status(evaluation_id, target_status)
    if record is None:
        raise HTTPException(status_code=404, detail="evaluation not found")
    logger.log(
        category=EventCategory.evaluation,
        event_type="status_updated",
        entity_type="evaluation",
        entity_id=record.id,
        payload={"status": record.status.value},
    )
    return record.model_dump(mode="json")


@app.post("/api/v1/evaluations/{evaluation_id}/evidence")
def attach_evidence(
    evaluation_id: str,
    payload: AttachEvidenceRequest,
    db: Session = Depends(get_db),
) -> dict:
    repo = EvaluationRepository(db)
    record = repo.attach_evidence(evaluation_id, payload.evidence_id)
    if record is None:
        raise HTTPException(status_code=404, detail="evaluation not found")
    logger.log(
        category=EventCategory.evaluation,
        event_type="evidence_attached",
        entity_type="evaluation",
        entity_id=record.id,
        payload={"evidence_id": payload.evidence_id},
    )
    return record.model_dump(mode="json")
