from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from db_models_sqlalchemy import Base as CoreBase
from decision_outputs_db_models import ArtifactORM, EvidenceORM, RecommendationORM
from integrated_foundation_app import app, logger


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    events_path = Path("var/events.jsonl")
    if events_path.exists():
        events_path.unlink()
    CoreBase.metadata.create_all(bind=db_session.engine)
    ArtifactORM.metadata.create_all(bind=db_session.engine)
    RecommendationORM.metadata.create_all(bind=db_session.engine)
    EvidenceORM.metadata.create_all(bind=db_session.engine)
    logger.filepath.parent.mkdir(parents=True, exist_ok=True)


def test_artifact_and_recommendation_events_are_emitted() -> None:
    reset_state()
    client = TestClient(app)

    evaluation = client.post(
        "/api/v1/evaluations",
        json={
            "title": "Output review",
            "decision_owner": "blake",
            "criteria": [{"name": "Security", "weight": 0.4}],
        },
    )
    assert evaluation.status_code == 200
    evaluation_id = evaluation.json()["id"]

    artifact = client.post(
        f"/api/v1/evaluations/{evaluation_id}/artifacts",
        json={
            "title": "Recommendation memo",
            "artifact_type": "recommendation_memo",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "content": "Move forward with finalist.",
        },
    )
    assert artifact.status_code == 200

    recommendation = client.post(
        f"/api/v1/evaluations/{evaluation_id}/recommendations",
        json={
            "title": "Advance vendor",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "summary": "Advance to procurement review.",
            "rationale": "Best fit on security and workflow alignment.",
            "status": "proposed",
        },
    )
    assert recommendation.status_code == 200

    events = client.get("/api/v1/events")
    assert events.status_code == 200
    payload = events.json()
    event_types = [row["event_type"] for row in payload]
    assert "artifact_created" in event_types
    assert "recommendation_created" in event_types
