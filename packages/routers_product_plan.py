PRODUCT_ROUTER_CLUSTERS = {
    "decision_board": [
        "GET /api/v1/decision-board/summary",
        "GET /api/v1/decision-board/attention-needed",
    ],
    "activity": [
        "GET /api/v1/activity/recent",
    ],
    "evaluation_views": [
        "GET /api/v1/evaluations/{evaluation_id}/summary",
        "GET /api/v1/evaluations/{evaluation_id}/readiness",
    ],
    "recommendation_views": [
        "GET /api/v1/evaluations/{evaluation_id}/recommendation-cards",
        "GET /api/v1/evaluations/{evaluation_id}/ranked-recommendation-summary",
    ],
}
