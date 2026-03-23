from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

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
from event_logger import EventLogger

app = FastAPI(title="Packaged Backend API")
logger = EventLogger(filepath="var/integrated_intelligence_events.jsonl")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/sources")
def create_source(payload: CreateSourceRequest, db: Session = Depends(get_db)) -> dict:
    try:
        source_type = SourceType(payload.source_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid source_type") from exc
    repo = SourceRepository(db)
    record = SourceRecord(
        id=new_id("src"),
        name=payload.name,
        source_type=source_type,
        trust_score=payload.trust_score,
        freshness_label=payload.freshness_label,
        owner=payload.owner,
        notes=payload.notes,
        tags=payload.tags,
    )
    saved = repo.create(source=record)
    logger.log(category=EventCategory.source, event_type="created", entity_type="source", entity_id=saved.id, payload={"name": saved.name})
    return saved.model_dump(mode="json")


@app.post("/api/v1/opportunities")
def create_opportunity(payload: CreateOpportunityRequest, db: Session = Depends(get_db)) -> dict:
    repo = OpportunityRepository(db)
    record = OpportunityRecord(
        id=new_id("opp"),
        title=payload.title,
        summary=payload.summary,
        source_ids=payload.source_ids,
        themes=payload.themes,
        score=payload.score,
    )
    saved = repo.create(opportunity=record)
    logger.log(category=EventCategory.opportunity, event_type="created", entity_type="opportunity", entity_id=saved.id, payload={"title": saved.title, "score": saved.score})
    return saved.model_dump(mode="json")


@app.post("/api/v1/opportunities/{opportunity_id}/stage/{stage}")
def update_opportunity_stage(opportunity_id: str, stage: str, db: Session = Depends(get_db)) -> dict:
    try:
        target_stage = OpportunityStage(stage)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid stage") from exc
    repo = OpportunityRepository(db)
    record = repo.update_stage(opportunity_id, target_stage)
    if record is None:
        raise HTTPException(status_code=404, detail="opportunity not found")
    logger.log(category=EventCategory.opportunity, event_type="stage_updated", entity_type="opportunity", entity_id=record.id, payload={"stage": record.stage.value})
    return record.model_dump(mode="json")


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
    return saved.model_dump(mode="json")


@app.post("/api/v1/evaluations/{evaluation_id}/status/{status}")
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


@app.post("/api/v1/evaluations/{evaluation_id}/evidence-link")
def attach_evidence_link(evaluation_id: str, payload: AttachEvidenceRequest, db: Session = Depends(get_db)) -> dict:
    repo = EvaluationRepository(db)
    record = repo.attach_evidence(evaluation_id, payload.evidence_id)
    if record is None:
        raise HTTPException(status_code=404, detail="evaluation not found")
    logger.log(category=EventCategory.evaluation, event_type="evidence_linked", entity_type="evaluation", entity_id=record.id, payload={"evidence_id": payload.evidence_id})
    return record.model_dump(mode="json")


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
    return saved.model_dump(mode="json")


@app.post("/api/v1/evaluations/{evaluation_id}/artifacts")
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
    return {"recommendation": saved.model_dump(mode="json"), "score": draft.total_score, "component_scores": summarize_component_scores(draft.components), "evidence_notes": draft.evidence_notes, "score_artifact": saved_score_artifact.model_dump(mode="json")}
