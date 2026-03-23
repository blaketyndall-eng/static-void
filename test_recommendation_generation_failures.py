from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from db_models_sqlalchemy import Base as CoreBase
from decision_outputs_db_models import ArtifactORM, EvidenceORM, RecommendationORM
from integrated_intelligence_app import app, logger


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    events_path = Path("var/integrated_intelligence_events.jsonl")
    if events_path.exists():
        events_path.unlink()
    CoreBase.metadata.create_all(bind=db_session.engine)
    ArtifactORM.metadata.create_all(bind=db_session.engine)
    RecommendationORM.metadata.create_all(bind=db_session.engine)
    EvidenceORM.metadata.create_all(bind=db_session.engine)
    logger.filepath.parent.mkdir(parents=True, exist_ok=True)


def test_generate_recommendation_for_missing_evaluation_returns_404() -> None:
    reset_state()
    client = TestClient(app)

    response = client.post("/api/v1/evaluations/eval_missing/generate-recommendation")
    assert response.status_code == 404
    assert response.json()["detail"] == "evaluation not found"


def test_why_endpoint_for_missing_recommendation_returns_404() -> None:
    reset_state()
    client = TestClient(app)

    response = client.get("/api/v1/recommendations/rec_missing/why")
    assert response.status_code == 404
    assert response.json()["detail"] == "recommendation not found"
