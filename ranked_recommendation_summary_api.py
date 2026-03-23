from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from db_session import get_db
from recommendation_ranking import rank_recommendations
from repository_decision_outputs import RecommendationRepository
from repository_evaluations import EvaluationRepository

app = FastAPI(title="Ranked Recommendation Summary API")


@app.get("/api/v1/evaluations/{evaluation_id}/ranked-recommendation-summary")
def get_ranked_recommendation_summary(evaluation_id: str, db: Session = Depends(get_db)) -> dict:
    evaluation_repo = EvaluationRepository(db)
    recommendation_repo = RecommendationRepository(db)

    evaluation = evaluation_repo.get(evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="evaluation not found")

    recommendations = [
        item.model_dump(mode="json")
        for item in recommendation_repo.list()
        if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id
    ]
    ranked = rank_recommendations(recommendations)

    top_recommendation = ranked[0] if ranked else None

    return {
        "evaluation_id": evaluation_id,
        "count": len(ranked),
        "top_recommendation": top_recommendation,
        "recommendations": ranked,
    }
