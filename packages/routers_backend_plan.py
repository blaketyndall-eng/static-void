BACKEND_ROUTER_CLUSTERS = {
    "sources": [
        "POST /api/v1/sources",
    ],
    "opportunities": [
        "POST /api/v1/opportunities",
        "POST /api/v1/opportunities/{opportunity_id}/stage/{stage}",
    ],
    "evaluations": [
        "POST /api/v1/evaluations",
        "POST /api/v1/evaluations/{evaluation_id}/status/{status}",
        "POST /api/v1/evaluations/{evaluation_id}/evidence-link",
        "POST /api/v1/evaluations/{evaluation_id}/evidence-records",
    ],
    "outputs": [
        "POST /api/v1/evaluations/{evaluation_id}/artifacts",
        "POST /api/v1/evaluations/{evaluation_id}/recommendations",
    ],
    "recommendations": [
        "POST /api/v1/evaluations/{evaluation_id}/generate-recommendation",
        "GET /api/v1/recommendations/{recommendation_id}/why",
    ],
    "events": [
        "GET /health",
    ],
}
