from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.opportunity_hunter import (
    CreateOpportunityCandidateRequest,
    CreateOpportunityScanRequest,
    UpsertOpportunitySignalRequest,
)
from packages.domain.opportunity_hunter import (
    OpportunityCandidate,
    OpportunityMarketSignal,
    OpportunityScan,
    OpportunityType,
)
from packages.repositories.opportunity_hunter import (
    OpportunityCandidateRepository,
    OpportunityScanRepository,
    OpportunitySignalRepository,
    build_learning_snapshot,
)
from packages.services.opportunity_hunter_engine import (
    OPPORTUNITY_SOURCE_STACK,
    evaluate_opportunity_candidate,
    summarize_scan,
)
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/opportunities", tags=["opportunity_hunter"])
telemetry = TelemetryLogger(filepath="var/opportunity_hunter_telemetry.jsonl")


@router.post("/scans")
def create_opportunity_scan(payload: CreateOpportunityScanRequest, db: Session = Depends(get_db)) -> dict:
    repo = OpportunityScanRepository(db)
    scan = OpportunityScan(
        name=payload.name,
        focus=payload.focus,
        source_arms=payload.source_arms,
        source_queries=payload.source_queries,
        notes=payload.notes,
    )
    saved = repo.create(scan)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_opportunity_scan", scan_id=saved.id)
    return saved.model_dump(mode="json")


@router.get("/scans")
def list_opportunity_scans(db: Session = Depends(get_db)) -> list[dict]:
    repo = OpportunityScanRepository(db)
    payload = [item.model_dump(mode="json") for item in repo.list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="list_opportunity_scans", returned_count=len(payload))
    return payload


@router.post("/scans/{scan_id}/candidates")
def create_opportunity_candidate(scan_id: str, payload: CreateOpportunityCandidateRequest, db: Session = Depends(get_db)) -> dict:
    scan_repo = OpportunityScanRepository(db)
    if scan_repo.get(scan_id) is None:
        raise HTTPException(status_code=404, detail="scan not found")
    try:
        opportunity_type = OpportunityType(payload.opportunity_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid opportunity_type") from exc
    repo = OpportunityCandidateRepository(db)
    candidate = OpportunityCandidate(
        scan_id=scan_id,
        title=payload.title,
        opportunity_type=opportunity_type,
        summary=payload.summary,
        target_users=payload.target_users,
        related_apps=payload.related_apps,
        related_industries=payload.related_industries,
        evidence_notes=payload.evidence_notes,
        demand_score=payload.demand_score,
        competition_score=payload.competition_score,
        whitespace_score=payload.whitespace_score,
        priority_score=payload.priority_score,
    )
    saved = repo.create(candidate)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_opportunity_candidate", scan_id=scan_id, candidate_id=saved.id)
    return saved.model_dump(mode="json")


@router.get("/scans/{scan_id}/candidates")
def list_opportunity_candidates(scan_id: str, db: Session = Depends(get_db)) -> dict:
    repo = OpportunityCandidateRepository(db)
    items = [item.model_dump(mode="json") for item in repo.list_for_scan(scan_id)]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="list_opportunity_candidates", scan_id=scan_id, returned_count=len(items))
    return {"count": len(items), "items": items}


@router.post("/candidates/{candidate_id}/signals")
def upsert_opportunity_signal(candidate_id: str, payload: UpsertOpportunitySignalRequest, db: Session = Depends(get_db)) -> dict:
    signal_repo = OpportunitySignalRepository(db)
    signal = OpportunityMarketSignal(candidate_id=candidate_id, **payload.model_dump())
    saved = signal_repo.upsert(signal)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="upsert_opportunity_signal", candidate_id=candidate_id)
    return saved.model_dump(mode="json")


@router.get("/candidates/{candidate_id}/signals")
def get_opportunity_signal(candidate_id: str, db: Session = Depends(get_db)) -> dict:
    signal_repo = OpportunitySignalRepository(db)
    signal = signal_repo.get(candidate_id)
    if signal is None:
        raise HTTPException(status_code=404, detail="signal not found")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_opportunity_signal", candidate_id=candidate_id)
    return signal.model_dump(mode="json")


@router.get("/candidates/{candidate_id}/evaluation")
def get_opportunity_candidate_evaluation(candidate_id: str, db: Session = Depends(get_db)) -> dict:
    candidate_repo = OpportunityCandidateRepository(db)
    signal_repo = OpportunitySignalRepository(db)

    candidates = []
    for scan in OpportunityScanRepository(db).list():
        candidates.extend(candidate_repo.list_for_scan(scan.id))
    candidate = next((item for item in candidates if item.id == candidate_id), None)
    if candidate is None:
        raise HTTPException(status_code=404, detail="candidate not found")

    signal = signal_repo.get(candidate_id)
    evaluation = evaluate_opportunity_candidate(candidate, signal)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_opportunity_candidate_evaluation", candidate_id=candidate_id, priority_score=evaluation.priority_score)
    return evaluation.model_dump(mode="json")


@router.get("/scans/{scan_id}/summary")
def get_opportunity_scan_summary(scan_id: str, db: Session = Depends(get_db)) -> dict:
    scan_repo = OpportunityScanRepository(db)
    candidate_repo = OpportunityCandidateRepository(db)
    scan = scan_repo.get(scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="scan not found")
    candidates = candidate_repo.list_for_scan(scan_id)
    learning = build_learning_snapshot(scan_id, candidates)
    payload = summarize_scan(scan, candidates, learning)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_opportunity_scan_summary", scan_id=scan_id, returned_count=len(candidates))
    return payload


@router.get("/source-stack")
def get_opportunity_source_stack() -> dict:
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_opportunity_source_stack", returned_count=len(OPPORTUNITY_SOURCE_STACK))
    return OPPORTUNITY_SOURCE_STACK
