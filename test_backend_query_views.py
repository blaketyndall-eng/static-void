from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from db_models_sqlalchemy import Base as CoreBase
from decision_outputs_db_models import ArtifactORM, EvidenceORM, RecommendationORM
from app_backend_router_plus import app


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    CoreBase.metadata.create_all(bind=db_session.engine)
    ArtifactORM.metadata.create_all(bind=db_session.engine)
    RecommendationORM.metadata.create_all(bind=db_session.engine)
    EvidenceORM.metadata.create_all(bind=db_session.engine)


def test_backend_query_views_return_expected_payloads() -> None:
    reset_state()
    client = TestClient(app)

    source = client.post(
        "/api/v1/sources",
        json={
            "name": "G2",
            "source_type": "website",
            "trust_score": 0.8,
            "freshness_label": "weekly",
            "tags": ["reviews"],
        },
    )
    assert source.status_code == 200

    opportunity = client.post(
        "/api/v1/opportunities",
        json={
            "title": "Query view opportunity",
            "summary": "Track vendor signals for evaluations.",
            "themes": ["signals"],
            "score": 81,
        },
    )
    assert opportunity.status_code == 200

    evaluation = client.post(
        "/api/v1/evaluations",
        json={
            "title": "Query view evaluation",
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

    recommendation = client.post(
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
    assert recommendation.status_code == 200

    sources = client.get("/api/v1/sources")
    assert sources.status_code == 200
    assert len(sources.json()) == 1

    opportunities = client.get("/api/v1/opportunities")
    assert opportunities.status_code == 200
    assert len(opportunities.json()) == 1

    evaluations = client.get("/api/v1/evaluations")
    assert evaluations.status_code == 200
    assert len(evaluations.json()) == 1

    outputs = client.get(f"/api/v1/evaluations/{evaluation_id}/outputs")
    assert outputs.status_code == 200
    payload = outputs.json()
    assert payload["evaluation"]["id"] == evaluation_id
    assert len(payload["evidence"]) == 1
    assert len(payload["recommendations"]) == 1
