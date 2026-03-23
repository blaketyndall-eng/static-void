from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from db_session import get_db
from repository_decision_outputs import RecommendationRepository
from repository_evaluations import EvaluationRepository
from repository_opportunities import OpportunityRepository
from repository_sources import SourceRepository

app = FastAPI(title="Decision Board Summary API")


@app.get("/api/v1/decision-board/summary")
def get_decision_board_summary(db: Session = Depends(get_db)) -> dict:
    source_repo = SourceRepository(db)
    opportunity_repo = OpportunityRepository(db)
    evaluation_repo = EvaluationRepository(db)
    recommendation_repo = RecommendationRepository(db)

    sources = [item.model_dump(mode="json") for item in source_repo.list()]
    opportunities = [item.model_dump(mode="json") for item in opportunity_repo.list()]
    evaluations = [item.model_dump(mode="json") for item in evaluation_repo.list()]
    recommendations = [item.model_dump(mode="json") for item in recommendation_repo.list()]

    latest_recommendations = sorted(
        recommendations,
        key=lambda item: item.get("updated_at", item.get("created_at", "")),
        reverse=True,
    )[:5]

    evaluation_status_counts: dict[str, int] = {}
    for item in evaluations:
        status = item.get("status", "unknown")
        evaluation_status_counts[status] = evaluation_status_counts.get(status, 0) + 1

    opportunity_stage_counts: dict[str, int] = {}
    for item in opportunities:
        stage = item.get("stage", "unknown")
        opportunity_stage_counts[stage] = opportunity_stage_counts.get(stage, 0) + 1

    return {
        "counts": {
            "sources": len(sources),
            "opportunities": len(opportunities),
            "evaluations": len(evaluations),
            "recommendations": len(recommendations),
        },
        "evaluation_status_counts": evaluation_status_counts,
        "opportunity_stage_counts": opportunity_stage_counts,
        "latest_recommendations": latest_recommendations,
    }
