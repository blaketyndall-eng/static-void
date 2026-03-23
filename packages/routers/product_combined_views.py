from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from event_logger import EventLogger
from packages.storage.session import get_db
from product_surface_services_packaged import (
    build_attention_needed,
    build_decision_board_summary,
    build_recent_activity,
)
from telemetry_events import DECISION_BOARD_SUMMARY_VIEWED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1", tags=["combined_views"])
activity_logger = EventLogger(filepath="var/integrated_intelligence_events.jsonl")
telemetry = TelemetryLogger(filepath="var/product_surface_packaged_telemetry.jsonl")


@router.get("/decision-board/combined")
def get_decision_board_combined(db: Session = Depends(get_db), activity_limit: int = 10) -> dict:
    summary = build_decision_board_summary(db)
    attention = build_attention_needed(db)
    activity = build_recent_activity(activity_logger, limit=activity_limit)
    counts = summary.get("counts", {})

    payload = {
        "summary": summary,
        "attention_needed": attention,
        "recent_activity": activity,
    }

    emit_view_event(
        telemetry,
        DECISION_BOARD_SUMMARY_VIEWED,
        route="decision_board_combined",
        source_count=counts.get("sources", 0),
        opportunity_count=counts.get("opportunities", 0),
        evaluation_count=counts.get("evaluations", 0),
        recommendation_count=counts.get("recommendations", 0),
        attention_count=attention.get("count", 0),
        activity_count=activity.get("count", 0),
    )
    return payload
