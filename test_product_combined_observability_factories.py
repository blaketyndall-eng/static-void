from fastapi.testclient import TestClient

from app_backend_router_full import app as backend_app
from app_product_router_full import app as product_app
from test_assertions import assert_counts, assert_telemetry_contains
from test_factories import create_opportunity, create_seeded_evaluation_flow, create_source
from test_support import reset_database_state


def test_product_combined_observability_with_shared_helpers() -> None:
    reset_database_state()
    backend = TestClient(backend_app)
    product = TestClient(product_app)

    create_source(backend, name="Factory G2")
    create_opportunity(backend, title="Factory combined telemetry opportunity")
    create_seeded_evaluation_flow(backend, title="Factory combined telemetry evaluation")

    combined = product.get("/api/v1/decision-board/combined")
    assert combined.status_code == 200
    payload = combined.json()["summary"]
    assert_counts(payload, sources=1, opportunities=1, evaluations=1)

    assert_telemetry_contains(
        "var/product_surface_packaged_telemetry.jsonl",
        [
            "decision_board.summary_viewed",
        ],
    )
