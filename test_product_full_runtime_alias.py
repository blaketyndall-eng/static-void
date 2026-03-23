from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from db_models_sqlalchemy import Base as CoreBase
from decision_outputs_db_models import ArtifactORM, EvidenceORM, RecommendationORM
from app_backend_router_full import app as backend_app
from app_product_full_runtime import app as product_app


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    CoreBase.metadata.create_all(bind=db_session.engine)
    ArtifactORM.metadata.create_all(bind=db_session.engine)
    RecommendationORM.metadata.create_all(bind=db_session.engine)
    EvidenceORM.metadata.create_all(bind=db_session.engine)


def test_product_full_runtime_alias_runs() -> None:
    reset_state()
    backend = TestClient(backend_app)
    product = TestClient(product_app)

    evaluation = backend.post(
        "/api/v1/evaluations",
        json={
            "title": "Full alias product",
            "decision_owner": "blake",
            "criteria": [{"name": "Security", "weight": 0.4}],
        },
    )
    assert evaluation.status_code == 200
    evaluation_id = evaluation.json()["id"]

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

    combined = product.get("/api/v1/decision-board/combined")
    assert combined.status_code == 200
    summary = product.get(f"/api/v1/evaluations/{evaluation_id}/summary")
    assert summary.status_code == 200
