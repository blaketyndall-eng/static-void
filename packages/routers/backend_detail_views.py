from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.repositories.decision_outputs import ArtifactRepository, EvidenceRepository, RecommendationRepository
from packages.repositories.evaluations import EvaluationRepository
from packages.repositories.opportunities import OpportunityRepository
from packages.repositories.sources import SourceRepository
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1", tags=["detail_views"])
telemetry = TelemetryLogger(filepath="var/backend_packaged_telemetry.jsonl")


@router.get("/sources/{source_id}")
def get_source(source_id: str, db: Session = Depends(get_db)) -> dict:
    repo = SourceRepository(db)
    source = repo.get(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="source not found")
    payload = source.model_dump(mode="json")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_source", source_id=source_id)
    return payload


@router.get("/opportunities/{opportunity_id}")
def get_opportunity(opportunity_id: str, db: Session = Depends(get_db)) -> dict:
    repo = OpportunityRepository(db)
    opportunity = repo.get(opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="opportunity not found")
    payload = opportunity.model_dump(mode="json")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_opportunity", opportunity_id=opportunity_id)
    return payload


@router.get("/evaluations/{evaluation_id}")
def get_evaluation(evaluation_id: str, db: Session = Depends(get_db)) -> dict:
    repo = EvaluationRepository(db)
    evaluation = repo.get(evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="evaluation not found")
    payload = evaluation.model_dump(mode="json")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_evaluation", evaluation_id=evaluation_id)
    return payload


@router.get("/recommendations/{recommendation_id}")
def get_recommendation(recommendation_id: str, db: Session = Depends(get_db)) -> dict:
    repo = RecommendationRepository(db)
    recommendation = next((item for item in repo.list() if item.id == recommendation_id), None)
    if recommendation is None:
        raise HTTPException(status_code=404, detail="recommendation not found")
    payload = recommendation.model_dump(mode="json")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_recommendation", recommendation_id=recommendation_id)
    return payload


@router.get("/artifacts/{artifact_id}")
def get_artifact(artifact_id: str, db: Session = Depends(get_db)) -> dict:
    repo = ArtifactRepository(db)
    artifact = next((item for item in repo.list() if item.id == artifact_id), None)
    if artifact is None:
        raise HTTPException(status_code=404, detail="artifact not found")
    payload = artifact.model_dump(mode="json")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_artifact", artifact_id=artifact_id)
    return payload


@router.get("/evidence/{evidence_id}")
def get_evidence(evidence_id: str, db: Session = Depends(get_db)) -> dict:
    repo = EvidenceRepository(db)
    evidence = next((item for item in repo.list() if item.id == evidence_id), None)
    if evidence is None:
        raise HTTPException(status_code=404, detail="evidence not found")
    payload = evidence.model_dump(mode="json")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_evidence", evidence_id=evidence_id)
    return payload
