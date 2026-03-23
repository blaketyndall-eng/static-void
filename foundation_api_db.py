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
from domain_models import EvaluationRecord, EvaluationStatus, OpportunityRecord, OpportunityStage, SourceRecord, SourceType, new_id
from repository_evaluations import EvaluationRepository
from repository_opportunities import OpportunityRepository
from repository_sources import SourceRepository
from settings import get_settings

settings = get_settings()
app = FastAPI(title=f"{settings.app_name} Database Foundation")
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


@app.get("/api/v1/sources")
def list_sources(db: Session = Depends(get_db)) -> list[dict]:
    repo = SourceRepository(db)
    return [item.model_dump(mode="json") for item in repo.list()]


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
    return saved.model_dump(mode="json")


@app.get("/api/v1/opportunities")
def list_opportunities(db: Session = Depends(get_db)) -> list[dict]:
    repo = OpportunityRepository(db)
    return [item.model_dump(mode="json") for item in repo.list()]


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
    return saved.model_dump(mode="json")


@app.post("/api/v1/opportunities/{opportunity_id}/stage/{stage}")
def update_opportunity_stage(opportunity_id: str, stage: str, db: Session = Depends(get_db)) -> dict:
    try:
        target_stage = OpportunityStage(stage)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid stage") from exc
    repo = OpportunityRepository(db)
    record = repo.update_stage(opportunity_id, target_stage)
    if record is None:
        raise HTTPException(status_code=404, detail="opportunity not found")
    return record.model_dump(mode="json")


@app.get("/api/v1/evaluations")
def list_evaluations(db: Session = Depends(get_db)) -> list[dict]:
    repo = EvaluationRepository(db)
    return [item.model_dump(mode="json") for item in repo.list()]


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
    return record.model_dump(mode="json")
