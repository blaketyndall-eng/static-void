from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from db_models_sqlalchemy import Base as CoreBase
from decision_outputs_db_models import ArtifactORM, EvidenceORM, RecommendationORM
from app_backend_router_packaged import app as backend_app
from app_product_router_packaged import app as product_app


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    CoreBase.metadata.create_all(bind=db_session.engine)
    ArtifactORM.metadata.create_all(bind=db_session.engine)
    RecommendationORM.metadata.create_all(bind=db_session.engine)
    EvidenceORM.metadata.create_all(bind=db_session.engine)


def test_product_router_runtime_summary_views() -> None:
    reset_state()
    backend = TestClient(backend_app)
    product = TestClient(product_app)

    backend.post(
        "/api/v1/sources",
        json={
            "name": "G2",
            "source_type": "website",
            "trust_score": 0.8,
            "freshness_label": "weekly",
            "tags": ["reviews"],
        },
    )

    backend.post(
        "/api/v1/opportunities",
        json={
            "title": "Decision board opportunity",
            "summary": "Track vendor signals for evaluations.",
            "themes": ["signals"],
            "score": 81,
        },
    )

    evaluation = backend.post(
        "/api/v1/evaluations",
        json={
            "title": "Product router review",
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

    board = product.get("/api/v1/decision-board/summary")
    assert board.status_code == 200
    assert board.json()["counts"]["evaluations"] == 1

    attention = product.get("/api/v1/decision-board/attention-needed")
    assert attention.status_code == 200

    activity = product.get("/api/v1/activity/recent")
    assert activity.status_code == 200

    summary = product.get(f"/api/v1/evaluations/{evaluation_id}/summary")
    assert summary.status_code == 200
    assert summary.json()["counts"]["recommendations"] >= 1

    readiness = product.get(f"/api/v1/evaluations/{evaluation_id}/readiness")
    assert readiness.status_code == 200
    assert readiness.json()["score"] >= 0

    cards = product.get(f"/api/v1/evaluations/{evaluation_id}/recommendation-cards")
    assert cards.status_code == 200
    assert len(cards.json()["cards"]) >= 1

    ranked = product.get(f"/api/v1/evaluations/{evaluation_id}/ranked-recommendation-summary")
    assert ranked.status_code == 200
    assert ranked.json()["count"] >= 1
