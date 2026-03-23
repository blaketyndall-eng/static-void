from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from event_logger import EventLogger
from packages.storage.session import get_db
from product_surface_services_packaged import (
    build_attention_needed,
    build_decision_board_summary,
    build_evaluation_readiness,
    build_evaluation_summary,
    build_ranked_recommendation_summary,
    build_recent_activity,
    build_recommendation_cards,
)
from telemetry_events import (
    ACTIVITY_RECENT_VIEWED,
    DECISION_BOARD_ATTENTION_NEEDED_VIEWED,
    DECISION_BOARD_SUMMARY_VIEWED,
    EVALUATION_READINESS_VIEWED,
    EVALUATION_SUMMARY_VIEWED,
    RECOMMENDATION_CARDS_VIEWED,
    RECOMMENDATION_RANKED,
)
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

app = FastAPI(title="Observed Packaged Product Surface API")
activity_logger = EventLogger(filepath="var/integrated_intelligence_events.jsonl")
telemetry = TelemetryLogger(filepath="var/product_surface_packaged_telemetry.jsonl")


@app.get("/api/v1/decision-board/summary")
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


@app.get("/api/v1/decision-board/attention-needed")
def get_attention_needed(db: Session = Depends(get_db)) -> dict:
    payload = build_attention_needed(db)
    emit_view_event(telemetry, DECISION_BOARD_ATTENTION_NEEDED_VIEWED, returned_count=payload.get("count", 0))
    return payload


@app.get("/api/v1/activity/recent")
def get_recent_activity(limit: int = 25) -> dict:
    payload = build_recent_activity(activity_logger, limit=limit)
    emit_view_event(telemetry, ACTIVITY_RECENT_VIEWED, returned_count=payload.get("count", 0), limit=limit)
    return payload


@app.get("/api/v1/evaluations/{evaluation_id}/summary")
def get_evaluation_summary(evaluation_id: str, db: Session = Depends(get_db)) -> dict:
    payload = build_evaluation_summary(db, evaluation_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="evaluation not found")
    counts = payload.get("counts", {})
    emit_view_event(
        telemetry,
        EVALUATION_SUMMARY_VIEWED,
        evaluation_id=evaluation_id,
        evidence_count=counts.get("evidence", 0),
        artifact_count=counts.get("artifacts", 0),
        recommendation_count=counts.get("recommendations", 0),
    )
    return payload


@app.get("/api/v1/evaluations/{evaluation_id}/readiness")
def get_evaluation_readiness(evaluation_id: str, db: Session = Depends(get_db)) -> dict:
    payload = build_evaluation_readiness(db, evaluation_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="evaluation not found")
    emit_view_event(
        telemetry,
        EVALUATION_READINESS_VIEWED,
        evaluation_id=evaluation_id,
        score=payload.get("score", 0),
        level=payload.get("level", "early"),
        blocker_count=len(payload.get("blockers", [])),
    )
    return payload


@app.get("/api/v1/evaluations/{evaluation_id}/recommendation-cards")
def get_recommendation_cards(evaluation_id: str, db: Session = Depends(get_db)) -> dict:
    payload = build_recommendation_cards(db, evaluation_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="evaluation not found")
    emit_view_event(telemetry, RECOMMENDATION_CARDS_VIEWED, evaluation_id=evaluation_id, returned_count=len(payload.get("cards", [])))
    return payload


@app.get("/api/v1/evaluations/{evaluation_id}/ranked-recommendation-summary")
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
