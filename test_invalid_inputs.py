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


def test_invalid_source_type_returns_400() -> None:
    reset_state()
    client = TestClient(app)

    response = client.post(
        "/api/v1/sources",
        json={
            "name": "Unknown source",
            "source_type": "podcast_feed",
            "trust_score": 0.5,
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "invalid source_type"


def test_invalid_opportunity_stage_returns_400() -> None:
    reset_state()
    client = TestClient(app)

    created = client.post(
        "/api/v1/opportunities",
        json={
            "title": "Signal cluster",
            "summary": "Opportunity created for testing.",
            "themes": ["signals"],
        },
    )
    assert created.status_code == 200
    opportunity_id = created.json()["id"]

    response = client.post(f"/api/v1/opportunities/{opportunity_id}/stage/not-a-real-stage")
    assert response.status_code == 400
    assert response.json()["detail"] == "invalid stage"


def test_invalid_evaluation_status_returns_400() -> None:
    reset_state()
    client = TestClient(app)

    created = client.post(
        "/api/v1/evaluations",
        json={
            "title": "AI platform review",
            "decision_owner": "blake",
            "criteria": [{"name": "Security", "weight": 0.4}],
        },
    )
    assert created.status_code == 200
    evaluation_id = created.json()["id"]

    response = client.post(f"/api/v1/evaluations/{evaluation_id}/status/not-a-status")
    assert response.status_code == 400
    assert response.json()["detail"] == "invalid status"


def test_invalid_artifact_type_returns_400() -> None:
    reset_state()
    client = TestClient(app)

    evaluation = client.post(
        "/api/v1/evaluations",
        json={
            "title": "Strategic review",
            "decision_owner": "blake",
            "criteria": [{"name": "Workflow", "weight": 0.3}],
        },
    )
    assert evaluation.status_code == 200
    evaluation_id = evaluation.json()["id"]

    response = client.post(
        f"/api/v1/evaluations/{evaluation_id}/artifacts",
        json={
            "title": "Bad artifact",
            "artifact_type": "spreadsheet_dump",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "content": "n/a",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "invalid artifact_type"


def test_invalid_recommendation_status_returns_400() -> None:
    reset_state()
    client = TestClient(app)

    evaluation = client.post(
        "/api/v1/evaluations",
        json={
            "title": "Vendor review",
            "decision_owner": "blake",
            "criteria": [{"name": "Security", "weight": 0.4}],
        },
    )
    assert evaluation.status_code == 200
    evaluation_id = evaluation.json()["id"]

    response = client.post(
        f"/api/v1/evaluations/{evaluation_id}/recommendations",
        json={
            "title": "Broken recommendation",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "summary": "Should fail.",
            "status": "maybe",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "invalid status"


def test_invalid_evidence_kind_returns_400() -> None:
    reset_state()
    client = TestClient(app)

    evaluation = client.post(
        "/api/v1/evaluations",
        json={
            "title": "Evidence review",
            "decision_owner": "blake",
            "criteria": [{"name": "Security", "weight": 0.4}],
        },
    )
    assert evaluation.status_code == 200
    evaluation_id = evaluation.json()["id"]

    response = client.post(
        f"/api/v1/evaluations/{evaluation_id}/evidence-records",
        json={
            "title": "Broken evidence",
            "evidence_kind": "audio_clip",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "detail": "Should fail.",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "invalid evidence_kind"
