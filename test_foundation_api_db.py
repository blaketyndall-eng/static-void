from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from db_models_sqlalchemy import Base
from foundation_api_db import app


def reset_db() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    Base.metadata.create_all(bind=db_session.engine)


def test_source_create_and_list() -> None:
    reset_db()
    client = TestClient(app)

    response = client.post(
        "/api/v1/sources",
        json={
            "name": "G2",
            "source_type": "website",
            "trust_score": 0.8,
            "freshness_label": "weekly",
            "tags": ["reviews"],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "G2"

    listing = client.get("/api/v1/sources")
    assert listing.status_code == 200
    rows = listing.json()
    assert len(rows) == 1
    assert rows[0]["name"] == "G2"


def test_opportunity_stage_update() -> None:
    reset_db()
    client = TestClient(app)

    create_response = client.post(
        "/api/v1/opportunities",
        json={
            "title": "Procurement intelligence wedge",
            "summary": "Track vendor signals for software evaluations.",
            "themes": ["procurement", "signals"],
            "score": 87,
        },
    )
    assert create_response.status_code == 200
    opportunity_id = create_response.json()["id"]

    update_response = client.post(f"/api/v1/opportunities/{opportunity_id}/stage/qualified")
    assert update_response.status_code == 200
    assert update_response.json()["stage"] == "qualified"


def test_evaluation_evidence_flow() -> None:
    reset_db()
    client = TestClient(app)

    create_response = client.post(
        "/api/v1/evaluations",
        json={
            "title": "AI governance vendor review",
            "decision_owner": "blake",
            "criteria": [{"name": "Security", "weight": 0.35}],
        },
    )
    assert create_response.status_code == 200
    evaluation_id = create_response.json()["id"]

    status_response = client.post(f"/api/v1/evaluations/{evaluation_id}/status/review")
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "review"

    evidence_response = client.post(
        f"/api/v1/evaluations/{evaluation_id}/evidence",
        json={"evidence_id": "artifact_123"},
    )
    assert evidence_response.status_code == 200
    assert evidence_response.json()["evidence_ids"] == ["artifact_123"]
