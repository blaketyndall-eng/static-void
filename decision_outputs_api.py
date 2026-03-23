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

app = FastAPI(title="Decision Outputs API")


@app.get("/api/v1/artifacts")
def list_artifacts(db: Session = Depends(get_db)) -> list[dict]:
    repo = ArtifactRepository(db)
    return [item.model_dump(mode="json") for item in repo.list()]


@app.post("/api/v1/artifacts")
def create_artifact(payload: CreateArtifactRequest, db: Session = Depends(get_db)) -> dict:
    try:
        artifact_type = ArtifactType(payload.artifact_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid artifact_type") from exc
    repo = ArtifactRepository(db)
    record = ArtifactRecord(
        id=new_output_id("art"),
        title=payload.title,
        artifact_type=artifact_type,
        linked_entity_type=payload.linked_entity_type,
        linked_entity_id=payload.linked_entity_id,
        content=payload.content,
        metadata=payload.metadata,
    )
    saved = repo.create(record)
    return saved.model_dump(mode="json")


@app.get("/api/v1/recommendations")
def list_recommendations(db: Session = Depends(get_db)) -> list[dict]:
    repo = RecommendationRepository(db)
    return [item.model_dump(mode="json") for item in repo.list()]


@app.post("/api/v1/recommendations")
def create_recommendation(payload: CreateRecommendationRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = RecommendationStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid status") from exc
    repo = RecommendationRepository(db)
    record = RecommendationRecord(
        id=new_output_id("rec"),
        title=payload.title,
        linked_entity_type=payload.linked_entity_type,
        linked_entity_id=payload.linked_entity_id,
        summary=payload.summary,
        rationale=payload.rationale,
        status=status,
        artifact_ids=payload.artifact_ids,
        evidence_ids=payload.evidence_ids,
    )
    saved = repo.create(record)
    return saved.model_dump(mode="json")


@app.get("/api/v1/evidence")
def list_evidence(db: Session = Depends(get_db)) -> list[dict]:
    repo = EvidenceRepository(db)
    return [item.model_dump(mode="json") for item in repo.list()]


@app.post("/api/v1/evidence")
def create_evidence(payload: CreateEvidenceRequest, db: Session = Depends(get_db)) -> dict:
    try:
        kind = EvidenceKind(payload.evidence_kind)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid evidence_kind") from exc
    repo = EvidenceRepository(db)
    record = EvidenceRecord(
        id=new_output_id("evd"),
        title=payload.title,
        evidence_kind=kind,
        linked_entity_type=payload.linked_entity_type,
        linked_entity_id=payload.linked_entity_id,
        source_id=payload.source_id,
        artifact_id=payload.artifact_id,
        detail=payload.detail,
        metadata=payload.metadata,
    )
    saved = repo.create(record)
    return saved.model_dump(mode="json")
