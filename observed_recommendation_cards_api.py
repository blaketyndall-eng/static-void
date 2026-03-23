from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from db_session import get_db
from repository_decision_outputs import ArtifactRepository, RecommendationRepository
from repository_evaluations import EvaluationRepository
from telemetry_events import RECOMMENDATION_CARDS_VIEWED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

app = FastAPI(title="Observed Recommendation Cards API")
telemetry = TelemetryLogger(filepath="var/evaluation_surface_telemetry.jsonl")


@app.get("/api/v1/evaluations/{evaluation_id}/recommendation-cards-observed")
def get_recommendation_cards_observed(evaluation_id: str, db: Session = Depends(get_db)) -> dict:
    evaluation_repo = EvaluationRepository(db)
    recommendation_repo = RecommendationRepository(db)
    artifact_repo = ArtifactRepository(db)

    evaluation = evaluation_repo.get(evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="evaluation not found")

    recommendations = [item.model_dump(mode="json") for item in recommendation_repo.list() if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id]
    artifacts = {item.id: item.model_dump(mode="json") for item in artifact_repo.list()}

    cards = []
    for recommendation in recommendations:
        linked_artifacts = [artifacts[item_id] for item_id in recommendation.get("artifact_ids", []) if item_id in artifacts]
        cards.append(
            {
                "id": recommendation["id"],
                "title": recommendation["title"],
                "summary": recommendation["summary"],
                "status": recommendation["status"],
                "why": recommendation.get("rationale", ""),
                "artifact_count": len(recommendation.get("artifact_ids", [])),
                "evidence_count": len(recommendation.get("evidence_ids", [])),
                "artifacts": linked_artifacts,
            }
        )

    emit_view_event(
        telemetry,
        RECOMMENDATION_CARDS_VIEWED,
        evaluation_id=evaluation_id,
        returned_count=len(cards),
    )

    return {"evaluation_id": evaluation_id, "cards": cards}
