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


def test_integrated_evaluation_outputs_flow() -> None:
    reset_state()
    client = TestClient(app)

    source = client.post(
        "/api/v1/sources",
        json={
            "name": "G2",
            "source_type": "website",
            "trust_score": 0.83,
            "freshness_label": "weekly",
            "tags": ["reviews"],
        },
    )
    assert source.status_code == 200

    opportunity = client.post(
        "/api/v1/opportunities",
        json={
            "title": "Decision intelligence wedge",
            "summary": "Turn vendor and market signals into structured evaluations.",
            "themes": ["signals", "evaluation"],
            "score": 89,
        },
    )
    assert opportunity.status_code == 200
    opportunity_id = opportunity.json()["id"]

    stage_update = client.post(f"/api/v1/opportunities/{opportunity_id}/stage/qualified")
    assert stage_update.status_code == 200
    assert stage_update.json()["stage"] == "qualified"

    evaluation = client.post(
        "/api/v1/evaluations",
        json={
            "title": "Enterprise AI vendor review",
            "decision_owner": "blake",
            "criteria": [{"name": "Security", "weight": 0.4}],
        },
    )
    assert evaluation.status_code == 200
    evaluation_id = evaluation.json()["id"]

    evidence = client.post(
        f"/api/v1/evaluations/{evaluation_id}/evidence-records",
        json={
            "title": "Security note",
            "evidence_kind": "note",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "detail": "Vendor maintains SOC 2 Type II and SSO support.",
        },
    )
    assert evidence.status_code == 200
    evidence_id = evidence.json()["id"]

    artifact = client.post(
        f"/api/v1/evaluations/{evaluation_id}/artifacts",
        json={
            "title": "Comparison brief",
            "artifact_type": "comparison_brief",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "content": "Two finalists remain after workflow and security screening.",
        },
    )
    assert artifact.status_code == 200
    artifact_id = artifact.json()["id"]

    recommendation = client.post(
        f"/api/v1/evaluations/{evaluation_id}/recommendations",
        json={
            "title": "Advance finalist",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "summary": "Proceed to pricing validation and procurement review.",
            "rationale": "Best fit across security, workflow, and adoption confidence.",
            "status": "proposed",
            "artifact_ids": [artifact_id],
            "evidence_ids": [evidence_id],
        },
    )
    assert recommendation.status_code == 200

    outputs = client.get(f"/api/v1/evaluations/{evaluation_id}/outputs")
    assert outputs.status_code == 200
    payload = outputs.json()
    assert len(payload["evidence"]) == 1
    assert len(payload["artifacts"]) == 1
    assert len(payload["recommendations"]) == 1

    events = client.get("/api/v1/events")
    assert events.status_code == 200
    event_types = [row["event_type"] for row in events.json()]
    assert "recommendation_created" in event_types
    assert "artifact_created" in event_types
    assert "evidence_record_created" in event_types
