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

router = APIRouter(prefix="/api/v1", tags=["query_views"])
telemetry = TelemetryLogger(filepath="var/backend_packaged_telemetry.jsonl")


@router.get("/sources")
def list_sources(db: Session = Depends(get_db)) -> list[dict]:
    repo = SourceRepository(db)
    payload = [item.model_dump(mode="json") for item in repo.list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="list_sources", returned_count=len(payload))
    return payload


@router.get("/opportunities")
def list_opportunities(db: Session = Depends(get_db)) -> list[dict]:
    repo = OpportunityRepository(db)
    payload = [item.model_dump(mode="json") for item in repo.list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="list_opportunities", returned_count=len(payload))
    return payload


@router.get("/evaluations")
def list_evaluations(db: Session = Depends(get_db)) -> list[dict]:
    repo = EvaluationRepository(db)
    payload = [item.model_dump(mode="json") for item in repo.list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="list_evaluations", returned_count=len(payload))
    return payload


@router.get("/evaluations/{evaluation_id}/outputs")
def get_evaluation_outputs(evaluation_id: str, db: Session = Depends(get_db)) -> dict:
    evaluation_repo = EvaluationRepository(db)
    artifact_repo = ArtifactRepository(db)
    recommendation_repo = RecommendationRepository(db)
    evidence_repo = EvidenceRepository(db)

    evaluation = evaluation_repo.get(evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="evaluation not found")

    payload = {
        "evaluation": evaluation.model_dump(mode="json"),
        "artifacts": [
            item.model_dump(mode="json")
            for item in artifact_repo.list()
            if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id
        ],
        "recommendations": [
            item.model_dump(mode="json")
            for item in recommendation_repo.list()
            if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id
        ],
        "evidence": [
            item.model_dump(mode="json")
            for item in evidence_repo.list()
            if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id
        ],
    }
    emit_view_event(
        telemetry,
        API_REQUEST_COMPLETED,
        route="get_evaluation_outputs",
        evaluation_id=evaluation_id,
        artifact_count=len(payload["artifacts"]),
        recommendation_count=len(payload["recommendations"]),
        evidence_count=len(payload["evidence"]),
    )
    return payload
