from fastapi.testclient import TestClient

from app_backend_router_full import app as backend_app
from app_product_router_full import app as product_app
from test_factories import create_opportunity, create_seeded_evaluation_flow, create_source
from test_support import reset_database_state


def test_product_combined_views_with_shared_factories() -> None:
    reset_database_state()
    backend = TestClient(backend_app)
    product = TestClient(product_app)

    create_source(backend, name="Factory G2")
    create_opportunity(backend, title="Factory combined opportunity")
    flow = create_seeded_evaluation_flow(backend, title="Factory combined evaluation")

    combined = product.get("/api/v1/decision-board/combined")
    assert combined.status_code == 200
    payload = combined.json()
    assert "summary" in payload
    assert "attention_needed" in payload
    assert "recent_activity" in payload
    assert payload["summary"]["counts"]["evaluations"] == 1
    assert payload["summary"]["counts"]["sources"] == 1
    assert payload["summary"]["counts"]["opportunities"] == 1
