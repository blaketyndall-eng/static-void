from fastapi import FastAPI

from packages.routers.product_decision_board import router as decision_board_router
from packages.routers.product_evaluation_views import router as evaluation_views_router
from packages.routers.product_recommendations import router as recommendation_views_router

app = FastAPI(title="Router-Based Packaged Product Surface API")
app.include_router(decision_board_router)
app.include_router(evaluation_views_router)
app.include_router(recommendation_views_router)
