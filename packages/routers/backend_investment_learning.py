from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.repositories.investment import InvestmentThesisRepository
from packages.services.investment_learning import build_learning_summary, review_thesis
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/investment", tags=["investment_learning"])
telemetry = TelemetryLogger(filepath="var/investment_telemetry.jsonl")


@router.get("/theses/{thesis_id}/review")
def get_investment_thesis_review(thesis_id: str, db: Session = Depends(get_db)) -> dict:
    repo = InvestmentThesisRepository(db)
    thesis = repo.get(thesis_id)
    if thesis is None:
        raise HTTPException(status_code=404, detail="investment thesis not found")
    payload = review_thesis(thesis).model_dump(mode="json")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_investment_thesis_review", thesis_id=thesis_id, review_score=payload.get("review_score", 0))
    return payload


@router.get("/learning/summary")
def get_investment_learning_summary(db: Session = Depends(get_db)) -> dict:
    repo = InvestmentThesisRepository(db)
    theses = repo.list()
    payload = build_learning_summary(theses).model_dump(mode="json")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_investment_learning_summary", returned_count=payload.get("total_theses", 0))
    return payload
