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


def test_generate_recommendation_and_explain_why() -> None:
    reset_state()
    client = TestClient(app)

    evaluation = client.post(
        "/api/v1/evaluations",
        json={
            "title": "Integrated intelligence review",
            "decision_owner": "blake",
            "criteria": [
                {"name": "Security", "weight": 0.4},
                {"name": "Workflow fit", "weight": 0.35},
                {"name": "Cost control", "weight": 0.25},
            ],
        },
    )
    assert evaluation.status_code == 200
    evaluation_id = evaluation.json()["id"]

    evidence = client.post(
        f"/api/v1/evaluations/{evaluation_id}/evidence-records",
        json={
            "title": "Security evidence",
            "evidence_kind": "note",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "detail": "Vendor supports SSO and current SOC 2 Type II.",
        },
    )
    assert evidence.status_code == 200

    artifact = client.post(
        f"/api/v1/evaluations/{evaluation_id}/artifacts",
        json={
            "title": "Comparison brief",
            "artifact_type": "comparison_brief",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "content": "Two vendors remain after workflow and security review.",
        },
    )
    assert artifact.status_code == 200

    generated = client.post(f"/api/v1/evaluations/{evaluation_id}/generate-recommendation")
    assert generated.status_code == 200
    payload = generated.json()
    recommendation_id = payload["recommendation"]["id"]
    assert payload["score"] > 0
    assert "criteria_coverage" in payload["component_scores"]
    assert payload["score_artifact"]["artifact_type"] == "research_note"

    why = client.get(f"/api/v1/recommendations/{recommendation_id}/why")
    assert why.status_code == 200
    why_payload = why.json()
    assert why_payload["recommendation"]["id"] == recommendation_id
    assert why_payload["why"]["generation_event"]["event_type"] == "recommendation_generated"
    assert len(why_payload["why"]["artifacts"]) >= 1
