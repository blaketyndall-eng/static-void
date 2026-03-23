from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from db_session import get_db
from decision_outputs_models import RecommendationRecord, new_output_id
from integrated_foundation_app import logger
from recommendation_intelligence import (
    average_component_score,
    generate_recommendation_draft,
    summarize_component_scores,
)
from repository_decision_outputs import (
    ArtifactRepository,
    EvidenceRepository,
    RecommendationRepository,
)
from repository_evaluations import EvaluationRepository
from domain_models import EventCategory

app = FastAPI(title="Recommendation Generation API")


@app.post("/api/v1/evaluations/{evaluation_id}/generate-recommendation")
def generate_recommendation(evaluation_id: str, db: Session = Depends(get_db)) -> dict:
    evaluation_repo = EvaluationRepository(db)
    evaluation = evaluation_repo.get(evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="evaluation not found")

    artifact_repo = ArtifactRepository(db)
    evidence_repo = EvidenceRepository(db)
    recommendation_repo = RecommendationRepository(db)

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

    draft = generate_recommendation_draft(
        evaluation_title=evaluation.title,
        criteria=evaluation.criteria,
        evidence_records=evidence,
        artifact_records=artifacts,
    )

    recommendation = RecommendationRecord(
        id=new_output_id("rec"),
        title=draft.title,
        linked_entity_type="evaluation",
        linked_entity_id=evaluation_id,
        summary=draft.summary,
        rationale=draft.rationale,
        status=draft.status,
        artifact_ids=[item["id"] for item in artifacts],
        evidence_ids=[item["id"] for item in evidence],
    )
    saved = recommendation_repo.create(recommendation)

    logger.log(
        category=EventCategory.recommendation,
        event_type="recommendation_generated",
        entity_type="recommendation",
        entity_id=saved.id,
        payload={
            "evaluation_id": evaluation_id,
            "total_score": draft.total_score,
            "average_component_score": average_component_score(draft.components),
            "component_scores": summarize_component_scores(draft.components),
            "evidence_notes": draft.evidence_notes,
        },
    )

    return {
        "recommendation": saved.model_dump(mode="json"),
        "score": draft.total_score,
        "component_scores": summarize_component_scores(draft.components),
        "evidence_notes": draft.evidence_notes,
    }
