from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api_contracts import AttachEvidenceRequest, CreateEvaluationRequest, CreateOpportunityRequest, CreateSourceRequest
from domain_models import EvaluationStatus, OpportunityStage, SourceType
from evaluation_service import EvaluationService
from opportunity_service import OpportunityService
from settings import get_settings
from source_registry import SourceRegistry

settings = get_settings()
app = FastAPI(title=f"{settings.app_name} Foundation")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sources = SourceRegistry()
opportunities = OpportunityService()
evaluations = EvaluationService()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/sources")
def list_sources() -> list[dict]:
    return [item.model_dump(mode="json") for item in sources.list()]


@app.post("/api/v1/sources")
def create_source(payload: CreateSourceRequest) -> dict:
    try:
        source_type = SourceType(payload.source_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid source_type") from exc
    record = sources.create(
        name=payload.name,
        source_type=source_type,
        trust_score=payload.trust_score,
        freshness_label=payload.freshness_label,
        owner=payload.owner,
        notes=payload.notes,
        tags=payload.tags,
    )
    return record.model_dump(mode="json")


@app.get("/api/v1/opportunities")
def list_opportunities() -> list[dict]:
    return [item.model_dump(mode="json") for item in opportunities.list()]


@app.post("/api/v1/opportunities")
def create_opportunity(payload: CreateOpportunityRequest) -> dict:
    record = opportunities.create(
        title=payload.title,
        summary=payload.summary,
        source_ids=payload.source_ids,
        themes=payload.themes,
        score=payload.score,
    )
    return record.model_dump(mode="json")


@app.post("/api/v1/opportunities/{opportunity_id}/stage/{stage}")
def update_opportunity_stage(opportunity_id: str, stage: str) -> dict:
    try:
        target_stage = OpportunityStage(stage)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid stage") from exc
    record = opportunities.update_stage(opportunity_id, target_stage)
    if record is None:
        raise HTTPException(status_code=404, detail="opportunity not found")
    return record.model_dump(mode="json")


@app.get("/api/v1/evaluations")
def list_evaluations() -> list[dict]:
    return [item.model_dump(mode="json") for item in evaluations.list()]


@app.post("/api/v1/evaluations")
def create_evaluation(payload: CreateEvaluationRequest) -> dict:
    record = evaluations.create(
        title=payload.title,
        decision_owner=payload.decision_owner,
        criteria=payload.criteria,
    )
    return record.model_dump(mode="json")


@app.post("/api/v1/evaluations/{evaluation_id}/status/{status}")
def update_evaluation_status(evaluation_id: str, status: str) -> dict:
    try:
        target_status = EvaluationStatus(status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid status") from exc
    record = evaluations.update_status(evaluation_id, target_status)
    if record is None:
        raise HTTPException(status_code=404, detail="evaluation not found")
    return record.model_dump(mode="json")


@app.post("/api/v1/evaluations/{evaluation_id}/evidence")
def attach_evidence(evaluation_id: str, payload: AttachEvidenceRequest) -> dict:
    record = evaluations.attach_evidence(evaluation_id, payload.evidence_id)
    if record is None:
        raise HTTPException(status_code=404, detail="evaluation not found")
    return record.model_dump(mode="json")
