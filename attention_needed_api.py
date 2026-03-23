from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from db_session import get_db
from repository_decision_outputs import RecommendationRepository
from repository_evaluations import EvaluationRepository

app = FastAPI(title="Attention Needed API")


@app.get("/api/v1/decision-board/attention-needed")
def get_attention_needed(db: Session = Depends(get_db)) -> dict:
    evaluation_repo = EvaluationRepository(db)
    recommendation_repo = RecommendationRepository(db)

    evaluations = [item.model_dump(mode="json") for item in evaluation_repo.list()]
    recommendations = [item.model_dump(mode="json") for item in recommendation_repo.list()]

    by_evaluation: dict[str, list[dict]] = {}
    for recommendation in recommendations:
        evaluation_id = recommendation.get("linked_entity_id")
        if recommendation.get("linked_entity_type") != "evaluation" or not evaluation_id:
            continue
        by_evaluation.setdefault(evaluation_id, []).append(recommendation)

    items = []
    for evaluation in evaluations:
        evaluation_id = evaluation["id"]
        linked = by_evaluation.get(evaluation_id, [])
        if not linked:
            items.append(
                {
                    "evaluation_id": evaluation_id,
                    "title": evaluation["title"],
                    "reason": "No recommendation exists yet.",
                    "priority": "high",
                }
            )
            continue
        proposed = [item for item in linked if item.get("status") == "proposed"]
        if not proposed:
            items.append(
                {
                    "evaluation_id": evaluation_id,
                    "title": evaluation["title"],
                    "reason": "Recommendation exists but none are proposed yet.",
                    "priority": "medium",
                }
            )

    return {"count": len(items), "items": items}
