from fastapi.testclient import TestClient

from app_backend_router_packaged import app
from test_assertions import assert_telemetry_contains
from test_factories import create_evaluation, create_evidence_record
from test_support import reset_database_state


def test_backend_router_telemetry_with_shared_helpers() -> None:
    reset_database_state()
    client = TestClient(app)

    evaluation = create_evaluation(client, title="Factory telemetry backend")
    evaluation_id = evaluation["id"]
    create_evidence_record(client, evaluation_id, title="Factory security note")

    generated = client.post(f"/api/v1/evaluations/{evaluation_id}/generate-recommendation")
    assert generated.status_code == 200
    recommendation_id = generated.json()["recommendation"]["id"]

    why = client.get(f"/api/v1/recommendations/{recommendation_id}/why")
    assert why.status_code == 200

    assert_telemetry_contains(
        "var/backend_packaged_telemetry.jsonl",
        [
            "evaluation.created",
            "evaluation.evidence_record_created",
            "recommendation.generated",
            "recommendation.why_viewed",
        ],
    )
