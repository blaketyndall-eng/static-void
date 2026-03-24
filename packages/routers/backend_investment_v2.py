from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.investment import CreateInvestmentThesisRequest, UpdateInvestmentStatusRequest
from packages.domain.investment import InvestmentThesis, InvestmentStatus, RecommendationState
from packages.domain.system_events import SystemEventType
from packages.repositories.investment import InvestmentThesisRepository
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v2/investment", tags=["investment_v2"])
telemetry = TelemetryLogger(filepath="var/investment_telemetry.jsonl")


@router.post("/theses")
def create_investment_thesis_v2(payload: CreateInvestmentThesisRequest, db: Session = Depends(get_db)) -> dict:
    repo = InvestmentThesisRepository(db)
    thesis = InvestmentThesis(**payload.model_dump())
    saved = repo.create(thesis)
    record_system_event(
        db,
        event_type=SystemEventType.investment_thesis_created,
        source_arm="investment",
        source_id=saved.id,
        summary=f"Created investment thesis {saved.ticker}",
        metadata={"asset_class": saved.asset_class.value, "ticker": saved.ticker, "recommendation_state": saved.recommendation_state.value},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_investment_thesis_v2", thesis_id=saved.id, ticker=saved.ticker)
    return saved.model_dump(mode="json")


@router.post("/theses/{thesis_id}/status")
def update_investment_status_v2(thesis_id: str, payload: UpdateInvestmentStatusRequest, db: Session = Depends(get_db)) -> dict:
    repo = InvestmentThesisRepository(db)
    thesis = repo.get(thesis_id)
    if thesis is None:
        raise HTTPException(status_code=404, detail="investment thesis not found")
    try:
        status = InvestmentStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid status") from exc
    updated = repo.update_status(thesis_id, status)
    if updated is None:
        raise HTTPException(status_code=404, detail="investment thesis not found")
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm="investment",
        source_id=thesis_id,
        summary=f"Updated investment thesis {updated.ticker} to {updated.status.value}",
        metadata={"status": updated.status.value},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="update_investment_status_v2", thesis_id=thesis_id, status=updated.status.value)
    return updated.model_dump(mode="json")


@router.get("/theses")
def list_investment_theses_v2(db: Session = Depends(get_db)) -> list[dict]:
    repo = InvestmentThesisRepository(db)
    payload = [item.model_dump(mode="json") for item in repo.list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="list_investment_theses_v2", returned_count=len(payload))
    return payload
