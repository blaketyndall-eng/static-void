from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from db_models_sqlalchemy import Base as CoreBase
from decision_outputs_db_models import ArtifactORM, EvidenceORM, RecommendationORM
from decision_workflow_api import app


def reset_db() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    CoreBase.metadata.create_all(bind=db_session.engine)
    ArtifactORM.metadata.create_all(bind=db_session.engine)
    RecommendationORM.metadata.create_all(bind=db_session.engine)
    EvidenceORM.metadata.create_all(bind=db_session.engine)


def test_linked_outputs_flow() -> None:
    reset_db()
    client = TestClient(app)

    evaluation_response = client.post(
        "/api/v1/evaluations",
        json={
            "title": "Strategic vendor evaluation",
            "decision_owner": "blake",
            "criteria": [{"name": "Security", "weight": 0.4}],
        },
    )
    assert evaluation_response.status_code == 200
    evaluation_id = evaluation_response.json()["id"]

    evidence_response = client.post(
        f"/api/v1/evaluations/{evaluation_id}/evidence-records",
        json={
            "title": "SOC 2 note",
            "evidence_kind": "note",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "detail": "Vendor has current SOC 2 Type II.",
        },
    )
    assert evidence_response.status_code == 200
    evidence_id = evidence_response.json()["id"]

    artifact_response = client.post(
        f"/api/v1/evaluations/{evaluation_id}/artifacts",
        json={
            "title": "Evaluation brief",
            "artifact_type": "comparison_brief",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "content": "Top vendors narrowed to two finalists.",
        },
    )
    assert artifact_response.status_code == 200
    artifact_id = artifact_response.json()["id"]

    recommendation_response = client.post(
        f"/api/v1/evaluations/{evaluation_id}/recommendations",
        json={
            "title": "Proceed with finalist",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "summary": "Advance to security review and pricing validation.",
            "rationale": "Best alignment on security and workflow fit.",
            "status": "proposed",
            "artifact_ids": [artifact_id],
            "evidence_ids": [evidence_id],
        },
    )
    assert recommendation_response.status_code == 200

    outputs_response = client.get(f"/api/v1/evaluations/{evaluation_id}/outputs")
    assert outputs_response.status_code == 200
    payload = outputs_response.json()
    assert payload["evaluation"]["id"] == evaluation_id
    assert len(payload["evidence"]) == 1
    assert len(payload["artifacts"]) == 1
    assert len(payload["recommendations"]) == 1
