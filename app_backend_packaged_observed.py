from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from event_logger import EventLogger
from packages.contracts.core import AttachEvidenceRequest, CreateEvaluationRequest, CreateOpportunityRequest, CreateSourceRequest
from packages.contracts.decision_outputs import CreateArtifactRequest, CreateEvidenceRequest, CreateRecommendationRequest
from packages.domain.core import EvaluationRecord, EvaluationStatus, EventCategory, OpportunityRecord, OpportunityStage, SourceRecord, SourceType, new_id
from packages.domain.decision_outputs import ArtifactRecord, ArtifactType, EvidenceKind, EvidenceRecord, RecommendationRecord, RecommendationStatus, new_output_id
from packages.repositories.decision_outputs import ArtifactRepository, EvidenceRepository, RecommendationRepository
from packages.repositories.evaluations import EvaluationRepository
from packages.repositories.opportunities import OpportunityRepository
from packages.repositories.sources import SourceRepository
from packages.storage.session import get_db
from recommendation_intelligence import average_component_score, generate_recommendation_draft, summarize_component_scores
from telemetry_events import EVALUATION_CREATED, EVALUATION_EVIDENCE_RECORD_CREATED, RECOMMENDATION_CREATED, RECOMMENDATION_GENERATED, RECOMMENDATION_WHY_VIEWED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

app = FastAPI(title="Observed Packaged Backend API")
logger = EventLogger(filepath="var/integrated_intelligence_events.jsonl")
telemetry = TelemetryLogger(filepath="var/backend_packaged_telemetry.jsonl")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/evaluations")
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


@app.post("/api/v1/evaluations/{evaluation_id}/evidence-records")
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


@app.post("/api/v1/evaluations/{evaluation_id}/recommendations")
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


@app.post("/api/v1/evaluations/{evaluation_id}/generate-recommendation")
def generate_recommendation(evaluation_id: str, db: Session = Depends(get_db)) -> dict:
    evaluation_repo = EvaluationRepository(db)
    evaluation = evaluation_repo.get(evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="evaluation not found")
    artifact_repo = ArtifactRepository(db)
    evidence_repo = EvidenceRepository(db)
    recommendation_repo = RecommendationRepository(db)
    artifacts = [item.model_dump(mode="json") for item in artifact_repo.list() if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id]
    evidence = [item.model_dump(mode="json") for item in evidence_repo.list() if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id]
    draft = generate_recommendation_draft(evaluation_title=evaluation.title, criteria=evaluation.criteria, evidence_records=evidence, artifact_records=artifacts)
    score_artifact = ArtifactRecord(
        id=new_output_id("art"),
        title=f"Score breakdown for {evaluation.title}",
        artifact_type=ArtifactType.research_note,
        linked_entity_type="evaluation",
        linked_entity_id=evaluation_id,
        content=draft.rationale,
        metadata={"total_score": draft.total_score, "component_scores": summarize_component_scores(draft.components), "average_component_score": average_component_score(draft.components), "evidence_notes": draft.evidence_notes},
    )
    saved_score_artifact = artifact_repo.create(score_artifact)
    recommendation = RecommendationRecord(
        id=new_output_id("rec"),
        title=draft.title,
        linked_entity_type="evaluation",
        linked_entity_id=evaluation_id,
        summary=draft.summary,
        rationale=draft.rationale,
        status=draft.status,
        artifact_ids=[item["id"] for item in artifacts] + [saved_score_artifact.id],
        evidence_ids=[item["id"] for item in evidence],
    )
    saved = recommendation_repo.create(recommendation)
    logger.log(category=EventCategory.recommendation, event_type="recommendation_generated", entity_type="recommendation", entity_id=saved.id, payload={"evaluation_id": evaluation_id, "total_score": draft.total_score, "score_artifact_id": saved_score_artifact.id})
    emit_action_event(telemetry, RECOMMENDATION_GENERATED, evaluation_id=evaluation_id, recommendation_id=saved.id, total_score=draft.total_score, evidence_count=len(evidence), artifact_count=len(artifacts))
    return {"recommendation": saved.model_dump(mode="json"), "score": draft.total_score, "component_scores": summarize_component_scores(draft.components), "evidence_notes": draft.evidence_notes, "score_artifact": saved_score_artifact.model_dump(mode="json")}


@app.get("/api/v1/recommendations/{recommendation_id}/why")
def get_recommendation_why(recommendation_id: str, db: Session = Depends(get_db)) -> dict:
    recommendation_repo = RecommendationRepository(db)
    artifact_repo = ArtifactRepository(db)
    recommendations = recommendation_repo.list()
    target = next((item for item in recommendations if item.id == recommendation_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="recommendation not found")
    artifacts = [item.model_dump(mode="json") for item in artifact_repo.list() if item.id in target.artifact_ids]
    emit_view_event(telemetry, RECOMMENDATION_WHY_VIEWED, recommendation_id=recommendation_id, artifact_count=len(artifacts))
    return {"recommendation": target.model_dump(mode="json"), "why": {"rationale": target.rationale, "artifacts": artifacts}}
