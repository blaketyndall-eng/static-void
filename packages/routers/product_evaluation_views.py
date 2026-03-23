from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.storage.session import get_db
from product_surface_services_packaged import build_evaluation_readiness, build_evaluation_summary
from telemetry_events import EVALUATION_READINESS_VIEWED, EVALUATION_SUMMARY_VIEWED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1", tags=["evaluation_views"])
telemetry = TelemetryLogger(filepath="var/product_surface_packaged_telemetry.jsonl")


@router.get("/evaluations/{evaluation_id}/summary")
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


@router.get("/evaluations/{evaluation_id}/readiness")
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
