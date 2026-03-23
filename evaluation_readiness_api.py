from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from db_session import get_db
from repository_decision_outputs import ArtifactRepository, EvidenceRepository, RecommendationRepository
from repository_evaluations import EvaluationRepository

app = FastAPI(title="Evaluation Readiness API")


@app.get("/api/v1/evaluations/{evaluation_id}/readiness")
def get_evaluation_readiness(evaluation_id: str, db: Session = Depends(get_db)) -> dict:
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

    criteria_count = len(evaluation.criteria)
    evidence_count = len(evidence)
    artifact_count = len(artifacts)
    recommendation_count = len(recommendations)

    score = 0
    score += min(criteria_count, 4) * 20
    score += min(evidence_count, 3) * 15
    score += min(artifact_count, 2) * 10
    score += 20 if recommendation_count > 0 else 0
    score = min(score, 100)

    if score >= 80:
        level = "ready"
    elif score >= 50:
        level = "developing"
    else:
        level = "early"

    blockers = []
    if criteria_count == 0:
        blockers.append("No criteria defined.")
    if evidence_count == 0:
        blockers.append("No evidence attached.")
    if recommendation_count == 0:
        blockers.append("No recommendation generated yet.")

    return {
        "evaluation_id": evaluation_id,
        "score": score,
        "level": level,
        "counts": {
            "criteria": criteria_count,
            "evidence": evidence_count,
            "artifacts": artifact_count,
            "recommendations": recommendation_count,
        },
        "blockers": blockers,
    }
