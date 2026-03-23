from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from db_models_sqlalchemy import Base as CoreBase
from decision_outputs_db_models import ArtifactORM, EvidenceORM, RecommendationORM
from app_backend_next import app


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    CoreBase.metadata.create_all(bind=db_session.engine)
    ArtifactORM.metadata.create_all(bind=db_session.engine)
    RecommendationORM.metadata.create_all(bind=db_session.engine)
    EvidenceORM.metadata.create_all(bind=db_session.engine)


def test_backend_next_alias_executes_router_runtime() -> None:
    reset_state()
    client = TestClient(app)

    evaluation = client.post(
        "/api/v1/evaluations",
        json={
            "title": "Alias backend review",
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
            "detail": "Vendor supports SSO and SOC 2.",
        },
    )
    assert evidence.status_code == 200

    generated = client.post(f"/api/v1/evaluations/{evaluation_id}/generate-recommendation")
    assert generated.status_code == 200
    recommendation_id = generated.json()["recommendation"]["id"]

    why = client.get(f"/api/v1/recommendations/{recommendation_id}/why")
    assert why.status_code == 200
    assert why.json()["recommendation"]["id"] == recommendation_id
