from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from event_logger import EventLogger
from packages.contracts.core import AttachEvidenceRequest, CreateEvaluationRequest
from packages.contracts.decision_outputs import CreateArtifactRequest, CreateEvidenceRequest, CreateRecommendationRequest
from packages.domain.core import EvaluationRecord, EvaluationStatus, EventCategory, new_id
from packages.domain.decision_outputs import ArtifactRecord, ArtifactType, EvidenceKind, EvidenceRecord, RecommendationRecord, RecommendationStatus, new_output_id
from packages.repositories.decision_outputs import ArtifactRepository, EvidenceRepository, RecommendationRepository
from packages.repositories.evaluations import EvaluationRepository
from packages.storage.session import get_db
from telemetry_events import EVALUATION_CREATED, EVALUATION_EVIDENCE_RECORD_CREATED, RECOMMENDATION_CREATED
from telemetry_helpers import emit_action_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1", tags=["evaluations"])
logger = EventLogger(filepath="var/integrated_intelligence_events.jsonl")
telemetry = TelemetryLogger(filepath="var/backend_packaged_telemetry.jsonl")


@router.post("/evaluations")
def create_evaluation(payload: CreateEvaluationRequest, db: Session = Depends(get_db)) -> dict:
    repo = EvaluationRepository(db)
    record = EvaluationRecord(
        id=new_id("eval"),
        title=payload.title,
        decision_owner=payload.decision_owner,
        criteria=payload.criteria,
    )
    saved = repo.create(evaluation=record)
    logger.log(category=EventCategory.evaluation, event_type="created", entity_type="evaluation", entity_id=saved.id, payload={"title": saved.title})
    emit_action_event(telemetry, EVALUATION_CREATED, evaluation_id=saved.id, title=saved.title, criteria_count=len(saved.criteria))
    return saved.model_dump(mode="json")


@router.post("/evaluations/{evaluation_id}/status/{status}")
def update_evaluation_status(evaluation_id: str, status: str, db: Session = Depends(get_db)) -> dict:
    try:
        target_status = EvaluationStatus(status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid status") from exc
    repo = EvaluationRepository(db)
    record = repo.update_status(evaluation_id, target_status)
    if record is None:
        raise HTTPException(status_code=404, detail="evaluation not found")
    logger.log(category=EventCategory.evaluation, event_type="status_updated", entity_type="evaluation", entity_id=record.id, payload={"status": record.status.value})
    return record.model_dump(mode="json")


@router.post("/evaluations/{evaluation_id}/evidence-link")
def attach_evidence_link(evaluation_id: str, payload: AttachEvidenceRequest, db: Session = Depends(get_db)) -> dict:
    repo = EvaluationRepository(db)
    record = repo.attach_evidence(evaluation_id, payload.evidence_id)
    if record is None:
        raise HTTPException(status_code=404, detail="evaluation not found")
    logger.log(category=EventCategory.evaluation, event_type="evidence_linked", entity_type="evaluation", entity_id=record.id, payload={"evidence_id": payload.evidence_id})
    return record.model_dump(mode="json")


@router.post("/evaluations/{evaluation_id}/evidence-records")
def create_evaluation_evidence(evaluation_id: str, payload: CreateEvidenceRequest, db: Session = Depends(get_db)) -> dict:
    evaluation_repo = EvaluationRepository(db)
    if evaluation_repo.get(evaluation_id) is None:
        raise HTTPException(status_code=404, detail="evaluation not found")
    try:
        kind = EvidenceKind(payload.evidence_kind)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid evidence_kind") from exc
    evidence_repo = EvidenceRepository(db)
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
    logger.log(category=EventCategory.evaluation, event_type="evidence_record_created", entity_type="evaluation", entity_id=evaluation_id, payload={"evidence_id": saved.id, "title": saved.title})
    emit_action_event(telemetry, EVALUATION_EVIDENCE_RECORD_CREATED, evaluation_id=evaluation_id, evidence_id=saved.id, title=saved.title)
    return saved.model_dump(mode="json")


@router.post("/evaluations/{evaluation_id}/artifacts")
def create_evaluation_artifact(evaluation_id: str, payload: CreateArtifactRequest, db: Session = Depends(get_db)) -> dict:
    evaluation_repo = EvaluationRepository(db)
    if evaluation_repo.get(evaluation_id) is None:
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
    logger.log(category=EventCategory.recommendation, event_type="artifact_created", entity_type="artifact", entity_id=saved.id, payload={"title": saved.title, "linked_evaluation_id": evaluation_id})
    return saved.model_dump(mode="json")


@router.post("/evaluations/{evaluation_id}/recommendations")
def create_evaluation_recommendation(evaluation_id: str, payload: CreateRecommendationRequest, db: Session = Depends(get_db)) -> dict:
    evaluation_repo = EvaluationRepository(db)
    if evaluation_repo.get(evaluation_id) is None:
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
    logger.log(category=EventCategory.recommendation, event_type="recommendation_created", entity_type="recommendation", entity_id=saved.id, payload={"title": saved.title, "status": saved.status.value})
    emit_action_event(telemetry, RECOMMENDATION_CREATED, evaluation_id=evaluation_id, recommendation_id=saved.id, status=saved.status.value)
    return saved.model_dump(mode="json")
