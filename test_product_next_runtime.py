from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from db_models_sqlalchemy import Base as CoreBase
from decision_outputs_db_models import ArtifactORM, EvidenceORM, RecommendationORM
from app_backend_router_packaged import app as backend_app
from app_product_next import app as product_app


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    CoreBase.metadata.create_all(bind=db_session.engine)
    ArtifactORM.metadata.create_all(bind=db_session.engine)
    RecommendationORM.metadata.create_all(bind=db_session.engine)
    EvidenceORM.metadata.create_all(bind=db_session.engine)


def test_product_next_runtime_executes_router_surface() -> None:
    reset_state()
    backend = TestClient(backend_app)
    product = TestClient(product_app)

    evaluation = backend.post(
        "/api/v1/evaluations",
        json={
            "title": "Alias product review",
            "decision_owner": "blake",
            "criteria": [{"name": "Security", "weight": 0.4}],
        },
    )
    assert evaluation.status_code == 200
    evaluation_id = evaluation.json()["id"]

    backend.post(
        f"/api/v1/evaluations/{evaluation_id}/evidence-records",
        json={
            "title": "Security note",
            "evidence_kind": "note",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "detail": "Vendor supports SSO and SOC 2.",
        },
    )

    backend.post(
        f"/api/v1/evaluations/{evaluation_id}/recommendations",
        json={
            "title": "Advance vendor",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "summary": "Advance to pricing review.",
            "rationale": "Best fit on security and workflow.",
            "status": "proposed",
        },
    )

    summary = product.get(f"/api/v1/evaluations/{evaluation_id}/summary")
    assert summary.status_code == 200
    readiness = product.get(f"/api/v1/evaluations/{evaluation_id}/readiness")
    assert readiness.status_code == 200
    cards = product.get(f"/api/v1/evaluations/{evaluation_id}/recommendation-cards")
    assert cards.status_code == 200
    ranked = product.get(f"/api/v1/evaluations/{evaluation_id}/ranked-recommendation-summary")
    assert ranked.status_code == 200
