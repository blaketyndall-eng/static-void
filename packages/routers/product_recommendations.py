from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.storage.session import get_db
from product_surface_services_packaged import build_ranked_recommendation_summary, build_recommendation_cards
from telemetry_events import RECOMMENDATION_CARDS_VIEWED, RECOMMENDATION_RANKED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1", tags=["recommendation_views"])
telemetry = TelemetryLogger(filepath="var/product_surface_packaged_telemetry.jsonl")


@router.get("/evaluations/{evaluation_id}/recommendation-cards")
def get_recommendation_cards(evaluation_id: str, db: Session = Depends(get_db)) -> dict:
    payload = build_recommendation_cards(db, evaluation_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="evaluation not found")
    emit_view_event(
        telemetry,
        RECOMMENDATION_CARDS_VIEWED,
        evaluation_id=evaluation_id,
        returned_count=len(payload.get("cards", [])),
    )
    return payload


@router.get("/evaluations/{evaluation_id}/ranked-recommendation-summary")
def get_ranked_recommendation_summary(evaluation_id: str, db: Session = Depends(get_db)) -> dict:
    payload = build_ranked_recommendation_summary(db, evaluation_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="evaluation not found")
    emit_view_event(
        telemetry,
        RECOMMENDATION_RANKED,
        evaluation_id=evaluation_id,
        returned_count=payload.get("count", 0),
        top_recommendation_id=(payload.get("top_recommendation") or {}).get("id"),
    )
    return payload
