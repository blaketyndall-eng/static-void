from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from db_models_sqlalchemy import Base
from foundation_api_db_events import app, logger


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    events_path = Path("var/events.jsonl")
    if events_path.exists():
        events_path.unlink()
    Base.metadata.create_all(bind=db_session.engine)
    logger.filepath.parent.mkdir(parents=True, exist_ok=True)


def test_source_creation_writes_event() -> None:
    reset_state()
    client = TestClient(app)

    response = client.post(
        "/api/v1/sources",
        json={
            "name": "TrustRadius",
            "source_type": "website",
            "trust_score": 0.76,
            "freshness_label": "monthly",
        },
    )
    assert response.status_code == 200

    events = client.get("/api/v1/events")
    assert events.status_code == 200
    payload = events.json()
    assert len(payload) == 1
    assert payload[0]["event_type"] == "created"
    assert payload[0]["entity_type"] == "source"


def test_evaluation_updates_write_events() -> None:
    reset_state()
    client = TestClient(app)

    created = client.post(
        "/api/v1/evaluations",
        json={
            "title": "Vendor governance review",
            "decision_owner": "blake",
            "criteria": [{"name": "Control", "weight": 0.4}],
        },
    )
    assert created.status_code == 200
    evaluation_id = created.json()["id"]

    status_response = client.post(f"/api/v1/evaluations/{evaluation_id}/status/review")
    assert status_response.status_code == 200

    evidence_response = client.post(
        f"/api/v1/evaluations/{evaluation_id}/evidence",
        json={"evidence_id": "artifact_456"},
    )
    assert evidence_response.status_code == 200

    events = client.get("/api/v1/events")
    assert events.status_code == 200
    payload = events.json()
    assert [item["event_type"] for item in payload] == [
        "created",
        "status_updated",
        "evidence_attached",
    ]
