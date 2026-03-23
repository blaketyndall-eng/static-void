from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from db_session import get_db
from decision_outputs_contracts import (
    CreateArtifactRequest,
    CreateEvidenceRequest,
    CreateRecommendationRequest,
)
from decision_outputs_models import (
    ArtifactRecord,
    ArtifactType,
    EvidenceKind,
    EvidenceRecord,
    RecommendationRecord,
    RecommendationStatus,
    new_output_id,
)
from repository_decision_outputs import (
    ArtifactRepository,
    EvidenceRepository,
    RecommendationRepository,
)
from repository_evaluations import EvaluationRepository

app = FastAPI(title="Decision Workflow API")


@app.get("/api/v1/evaluations/{evaluation_id}/outputs")
def get_evaluation_outputs(evaluation_id: str, db: Session = Depends(get_db)) -> dict:
    evaluation_repo = EvaluationRepository(db)
    evaluation = evaluation_repo.get(evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="evaluation not found")

    artifact_repo = ArtifactRepository(db)
    recommendation_repo = RecommendationRepository(db)
    evidence_repo = EvidenceRepository(db)

    artifacts = [
        item.model_dump(mode="json")
        for item in artifact_repo.list()
        if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id
    ]
    recommendations = [
        item.model_dump(mode="json")
        for item in recommendation_repo.list()
        if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id
    ]
    evidence = [
        item.model_dump(mode="json")
        for item in evidence_repo.list()
        if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id
    ]

    return {
        "evaluation": evaluation.model_dump(mode="json"),
        "artifacts": artifacts,
        "recommendations": recommendations,
        "evidence": evidence,
    }


@app.post("/api/v1/evaluations/{evaluation_id}/evidence-records")
def create_evaluation_evidence(
    evaluation_id: str,
    payload: CreateEvidenceRequest,
    db: Session = Depends(get_db),
) -> dict:
    evaluation_repo = EvaluationRepository(db)
    evaluation = evaluation_repo.get(evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="evaluation not found")

    try:
        kind = EvidenceKind(payload.evidence_kind)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid evidence_kind") from exc

    evidence_repo = EvidenceRepository(db)
    evaluation_repo = EvaluationRepository(db)

    evidence = EvidenceRecord(
        id=new_output_id("evd"),
        title=payload.title,
        evidence_kind=kind,
        linked_entity_type="evaluation",
        linked_entity_id=evaluation_id,
        source_id=payload.source_id,
        artifact_id=payload.artifact_id,
        detail=payload.detail,
        metadata=payload.metadata,
    )
    saved = evidence_repo.create(evidence)
    evaluation_repo.attach_evidence(evaluation_id, saved.id)
    return saved.model_dump(mode="json")


@app.post("/api/v1/evaluations/{evaluation_id}/artifacts")
def create_evaluation_artifact(
    evaluation_id: str,
    payload: CreateArtifactRequest,
    db: Session = Depends(get_db),
) -> dict:
    evaluation_repo = EvaluationRepository(db)
    evaluation = evaluation_repo.get(evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="evaluation not found")

    try:
        artifact_type = ArtifactType(payload.artifact_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid artifact_type") from exc

    artifact_repo = ArtifactRepository(db)
    artifact = ArtifactRecord(
        id=new_output_id("art"),
        title=payload.title,
        artifact_type=artifact_type,
        linked_entity_type="evaluation",
        linked_entity_id=evaluation_id,
        content=payload.content,
        metadata=payload.metadata,
    )
    saved = artifact_repo.create(artifact)
    return saved.model_dump(mode="json")


@app.post("/api/v1/evaluations/{evaluation_id}/recommendations")
def create_evaluation_recommendation(
    evaluation_id: str,
    payload: CreateRecommendationRequest,
    db: Session = Depends(get_db),
) -> dict:
    evaluation_repo = EvaluationRepository(db)
    evaluation = evaluation_repo.get(evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="evaluation not found")

    try:
        status = RecommendationStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid status") from exc

    recommendation_repo = RecommendationRepository(db)
    recommendation = RecommendationRecord(
        id=new_output_id("rec"),
        title=payload.title,
        linked_entity_type="evaluation",
        linked_entity_id=evaluation_id,
        summary=payload.summary,
        rationale=payload.rationale,
        status=status,
        artifact_ids=payload.artifact_ids,
        evidence_ids=payload.evidence_ids,
    )
    saved = recommendation_repo.create(recommendation)
    return saved.model_dump(mode="json")
