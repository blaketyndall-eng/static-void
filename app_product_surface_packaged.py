from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from packages.storage.session import get_db
from event_logger import EventLogger
from product_surface_services_packaged import (
    build_attention_needed,
    build_decision_board_summary,
    build_evaluation_readiness,
    build_evaluation_summary,
    build_ranked_recommendation_summary,
    build_recent_activity,
    build_recommendation_cards,
)

app = FastAPI(title="Packaged Product Surface API")
activity_logger = EventLogger(filepath="var/integrated_intelligence_events.jsonl")


@app.get("/api/v1/decision-board/summary")
def get_decision_board_summary(db: Session = Depends(get_db)) -> dict:
    return build_decision_board_summary(db)


@app.get("/api/v1/decision-board/attention-needed")
def get_attention_needed(db: Session = Depends(get_db)) -> dict:
    return build_attention_needed(db)


@app.get("/api/v1/activity/recent")
def get_recent_activity(limit: int = 25) -> dict:
    return build_recent_activity(activity_logger, limit=limit)


@app.get("/api/v1/evaluations/{evaluation_id}/summary")
def get_evaluation_summary(evaluation_id: str, db: Session = Depends(get_db)) -> dict:
    payload = build_evaluation_summary(db, evaluation_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="evaluation not found")
    return payload


@app.get("/api/v1/evaluations/{evaluation_id}/readiness")
def get_evaluation_readiness(evaluation_id: str, db: Session = Depends(get_db)) -> dict:
    payload = build_evaluation_readiness(db, evaluation_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="evaluation not found")
    return payload


@app.get("/api/v1/evaluations/{evaluation_id}/recommendation-cards")
def get_recommendation_cards(evaluation_id: str, db: Session = Depends(get_db)) -> dict:
    payload = build_recommendation_cards(db, evaluation_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="evaluation not found")
    return payload


@app.get("/api/v1/evaluations/{evaluation_id}/ranked-recommendation-summary")
def get_ranked_recommendation_summary(evaluation_id: str, db: Session = Depends(get_db)) -> dict:
    payload = build_ranked_recommendation_summary(db, evaluation_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="evaluation not found")
    return payload
