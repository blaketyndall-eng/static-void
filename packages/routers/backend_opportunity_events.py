from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.opportunity_hunter import CreateOpportunityCandidateRequest, CreateOpportunityScanRequest, UpsertOpportunitySignalRequest
from packages.domain.opportunity_hunter import OpportunityCandidate, OpportunityMarketSignal, OpportunityScan, OpportunityType
from packages.domain.system_events import SystemEventType
from packages.repositories.opportunity_hunter import OpportunityCandidateRepository, OpportunityScanRepository, OpportunitySignalRepository
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v2/opportunities", tags=["opportunity_events"])
telemetry = TelemetryLogger(filepath="var/opportunity_hunter_telemetry.jsonl")


@router.post("/scans")
def create_opportunity_scan_evented(payload: CreateOpportunityScanRequest, db: Session = Depends(get_db)) -> dict:
    repo = OpportunityScanRepository(db)
    scan = OpportunityScan(name=payload.name, focus=payload.focus, source_arms=payload.source_arms, source_queries=payload.source_queries, notes=payload.notes)
    saved = repo.create(scan)
    record_system_event(db, event_type=SystemEventType.opportunity_scan_created, source_arm="opportunity_hunter", source_id=saved.id, summary=f"Created opportunity scan {saved.name}", metadata={"source_arms": saved.source_arms})
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_opportunity_scan_evented", scan_id=saved.id)
    return saved.model_dump(mode="json")


@router.post("/scans/{scan_id}/candidates")
def create_opportunity_candidate_evented(scan_id: str, payload: CreateOpportunityCandidateRequest, db: Session = Depends(get_db)) -> dict:
    scan = OpportunityScanRepository(db).get(scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="scan not found")
    try:
        opportunity_type = OpportunityType(payload.opportunity_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid opportunity_type") from exc
    repo = OpportunityCandidateRepository(db)
    candidate = OpportunityCandidate(scan_id=scan_id, title=payload.title, opportunity_type=opportunity_type, summary=payload.summary, target_users=payload.target_users, related_apps=payload.related_apps, related_industries=payload.related_industries, evidence_notes=payload.evidence_notes, demand_score=payload.demand_score, competition_score=payload.competition_score, whitespace_score=payload.whitespace_score, priority_score=payload.priority_score)
    saved = repo.create(candidate)
    record_system_event(db, event_type=SystemEventType.opportunity_candidate_created, source_arm="opportunity_hunter", source_id=saved.id, summary=f"Created opportunity candidate {saved.title}", metadata={"scan_id": scan_id, "type": saved.opportunity_type.value})
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_opportunity_candidate_evented", candidate_id=saved.id)
    return saved.model_dump(mode="json")


@router.post("/candidates/{candidate_id}/signals")
def upsert_opportunity_signal_evented(candidate_id: str, payload: UpsertOpportunitySignalRequest, db: Session = Depends(get_db)) -> dict:
    signal_repo = OpportunitySignalRepository(db)
    signal = OpportunityMarketSignal(candidate_id=candidate_id, **payload.model_dump())
    saved = signal_repo.upsert(signal)
    record_system_event(db, event_type=SystemEventType.operator_action, source_arm="opportunity_hunter", source_id=candidate_id, summary=f"Updated opportunity signals for {candidate_id}", metadata={"source_stack": saved.source_stack})
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="upsert_opportunity_signal_evented", candidate_id=candidate_id)
    return saved.model_dump(mode="json")
