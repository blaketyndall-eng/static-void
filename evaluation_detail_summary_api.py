from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from db_session import get_db
from repository_decision_outputs import ArtifactRepository, EvidenceRepository, RecommendationRepository
from repository_evaluations import EvaluationRepository

app = FastAPI(title="Evaluation Detail Summary API")


@app.get("/api/v1/evaluations/{evaluation_id}/summary")
def get_evaluation_summary(evaluation_id: str, db: Session = Depends(get_db)) -> dict:
    evaluation_repo = EvaluationRepository(db)
    artifact_repo = ArtifactRepository(db)
    evidence_repo = EvidenceRepository(db)
    recommendation_repo = RecommendationRepository(db)

    evaluation = evaluation_repo.get(evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="evaluation not found")

    artifacts = [
        item.model_dump(mode="json")
        for item in artifact_repo.list()
        if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id
    ]
    evidence = [
        item.model_dump(mode="json")
        for item in evidence_repo.list()
        if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id
    ]
    recommendations = [
        item.model_dump(mode="json")
        for item in recommendation_repo.list()
        if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id
    ]

    latest_recommendation = recommendations[-1] if recommendations else None

    return {
        "evaluation": evaluation.model_dump(mode="json"),
        "counts": {
            "criteria": len(evaluation.criteria),
            "evidence": len(evidence),
            "artifacts": len(artifacts),
            "recommendations": len(recommendations),
        },
        "latest_recommendation": latest_recommendation,
        "artifacts": artifacts,
        "evidence": evidence,
    }
