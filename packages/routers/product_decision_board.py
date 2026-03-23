from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from event_logger import EventLogger
from packages.storage.session import get_db
from product_surface_services_packaged import build_attention_needed, build_decision_board_summary, build_recent_activity
from telemetry_events import ACTIVITY_RECENT_VIEWED, DECISION_BOARD_ATTENTION_NEEDED_VIEWED, DECISION_BOARD_SUMMARY_VIEWED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1", tags=["decision_board"])
activity_logger = EventLogger(filepath="var/integrated_intelligence_events.jsonl")
telemetry = TelemetryLogger(filepath="var/product_surface_packaged_telemetry.jsonl")


@router.get("/decision-board/summary")
def get_decision_board_summary(db: Session = Depends(get_db)) -> dict:
    payload = build_decision_board_summary(db)
    counts = payload.get("counts", {})
    emit_view_event(
        telemetry,
        DECISION_BOARD_SUMMARY_VIEWED,
        source_count=counts.get("sources", 0),
        opportunity_count=counts.get("opportunities", 0),
        evaluation_count=counts.get("evaluations", 0),
        recommendation_count=counts.get("recommendations", 0),
    )
    return payload


@router.get("/decision-board/attention-needed")
def get_attention_needed(db: Session = Depends(get_db)) -> dict:
    payload = build_attention_needed(db)
    emit_view_event(telemetry, DECISION_BOARD_ATTENTION_NEEDED_VIEWED, returned_count=payload.get("count", 0))
    return payload


@router.get("/activity/recent")
def get_recent_activity(limit: int = 25) -> dict:
    payload = build_recent_activity(activity_logger, limit=limit)
    emit_view_event(telemetry, ACTIVITY_RECENT_VIEWED, returned_count=payload.get("count", 0), limit=limit)
    return payload
