from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from db_models_sqlalchemy import Base as CoreBase
from decision_outputs_db_models import ArtifactORM, EvidenceORM, RecommendationORM
from app_backend_router_full import app


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    CoreBase.metadata.create_all(bind=db_session.engine)
    ArtifactORM.metadata.create_all(bind=db_session.engine)
    RecommendationORM.metadata.create_all(bind=db_session.engine)
    EvidenceORM.metadata.create_all(bind=db_session.engine)


def test_backend_detail_views_return_entity_payloads() -> None:
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
    source_id = source.json()["id"]

    opportunity = client.post(
        "/api/v1/opportunities",
        json={
            "title": "Detail view opportunity",
            "summary": "Track vendor signals for evaluations.",
            "themes": ["signals"],
            "score": 81,
        },
    )
    assert opportunity.status_code == 200
    opportunity_id = opportunity.json()["id"]

    evaluation = client.post(
        "/api/v1/evaluations",
        json={
            "title": "Detail view evaluation",
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
    evidence_id = evidence.json()["id"]

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
    recommendation_id = recommendation.json()["id"]

    generated = client.post(f"/api/v1/evaluations/{evaluation_id}/generate-recommendation")
    assert generated.status_code == 200
    artifact_id = generated.json()["score_artifact"]["id"]

    source_detail = client.get(f"/api/v1/sources/{source_id}")
    assert source_detail.status_code == 200
    assert source_detail.json()["id"] == source_id

    opportunity_detail = client.get(f"/api/v1/opportunities/{opportunity_id}")
    assert opportunity_detail.status_code == 200
    assert opportunity_detail.json()["id"] == opportunity_id

    evaluation_detail = client.get(f"/api/v1/evaluations/{evaluation_id}")
    assert evaluation_detail.status_code == 200
    assert evaluation_detail.json()["id"] == evaluation_id

    recommendation_detail = client.get(f"/api/v1/recommendations/{recommendation_id}")
    assert recommendation_detail.status_code == 200
    assert recommendation_detail.json()["id"] == recommendation_id

    artifact_detail = client.get(f"/api/v1/artifacts/{artifact_id}")
    assert artifact_detail.status_code == 200
    assert artifact_detail.json()["id"] == artifact_id

    evidence_detail = client.get(f"/api/v1/evidence/{evidence_id}")
    assert evidence_detail.status_code == 200
    assert evidence_detail.json()["id"] == evidence_id
