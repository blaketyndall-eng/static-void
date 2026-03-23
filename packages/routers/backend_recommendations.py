from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from event_logger import EventLogger
from packages.repositories.decision_outputs import ArtifactRepository, EvidenceRepository, RecommendationRepository
from packages.repositories.evaluations import EvaluationRepository
from packages.storage.session import get_db
from recommendation_intelligence import average_component_score, generate_recommendation_draft, summarize_component_scores
from packages.domain.core import EventCategory
from packages.domain.decision_outputs import ArtifactRecord, ArtifactType, RecommendationRecord, new_output_id
from telemetry_events import RECOMMENDATION_GENERATED, RECOMMENDATION_WHY_VIEWED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1", tags=["recommendations"])
logger = EventLogger(filepath="var/integrated_intelligence_events.jsonl")
telemetry = TelemetryLogger(filepath="var/backend_packaged_telemetry.jsonl")


@router.post("/evaluations/{evaluation_id}/generate-recommendation")
def generate_recommendation(evaluation_id: str, db: Session = Depends(get_db)) -> dict:
    evaluation_repo = EvaluationRepository(db)
    evaluation = evaluation_repo.get(evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="evaluation not found")

    artifact_repo = ArtifactRepository(db)
    evidence_repo = EvidenceRepository(db)
    recommendation_repo = RecommendationRepository(db)
    artifacts = [item.model_dump(mode="json") for item in artifact_repo.list() if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id]
    evidence = [item.model_dump(mode="json") for item in evidence_repo.list() if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id]
    draft = generate_recommendation_draft(evaluation_title=evaluation.title, criteria=evaluation.criteria, evidence_records=evidence, artifact_records=artifacts)

    score_artifact = ArtifactRecord(
        id=new_output_id("art"),
        title=f"Score breakdown for {evaluation.title}",
        artifact_type=ArtifactType.research_note,
        linked_entity_type="evaluation",
        linked_entity_id=evaluation_id,
        content=draft.rationale,
        metadata={
            "total_score": draft.total_score,
            "component_scores": summarize_component_scores(draft.components),
            "average_component_score": average_component_score(draft.components),
            "evidence_notes": draft.evidence_notes,
        },
    )
    saved_score_artifact = artifact_repo.create(score_artifact)

    recommendation = RecommendationRecord(
        id=new_output_id("rec"),
        title=draft.title,
        linked_entity_type="evaluation",
        linked_entity_id=evaluation_id,
        summary=draft.summary,
        rationale=draft.rationale,
        status=draft.status,
        artifact_ids=[item["id"] for item in artifacts] + [saved_score_artifact.id],
        evidence_ids=[item["id"] for item in evidence],
    )
    saved = recommendation_repo.create(recommendation)

    logger.log(category=EventCategory.recommendation, event_type="recommendation_generated", entity_type="recommendation", entity_id=saved.id, payload={"evaluation_id": evaluation_id, "total_score": draft.total_score, "score_artifact_id": saved_score_artifact.id})
    emit_action_event(telemetry, RECOMMENDATION_GENERATED, evaluation_id=evaluation_id, recommendation_id=saved.id, total_score=draft.total_score, evidence_count=len(evidence), artifact_count=len(artifacts))

    return {
        "recommendation": saved.model_dump(mode="json"),
        "score": draft.total_score,
        "component_scores": summarize_component_scores(draft.components),
        "evidence_notes": draft.evidence_notes,
        "score_artifact": saved_score_artifact.model_dump(mode="json"),
    }


@router.get("/recommendations/{recommendation_id}/why")
def get_recommendation_why(recommendation_id: str, db: Session = Depends(get_db)) -> dict:
    recommendation_repo = RecommendationRepository(db)
    artifact_repo = ArtifactRepository(db)
    recommendations = recommendation_repo.list()
    target = next((item for item in recommendations if item.id == recommendation_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="recommendation not found")

    artifacts = [item.model_dump(mode="json") for item in artifact_repo.list() if item.id in target.artifact_ids]
    emit_view_event(telemetry, RECOMMENDATION_WHY_VIEWED, recommendation_id=recommendation_id, artifact_count=len(artifacts))
    return {"recommendation": target.model_dump(mode="json"), "why": {"rationale": target.rationale, "artifacts": artifacts}}
