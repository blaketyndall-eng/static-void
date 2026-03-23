from fastapi import FastAPI

from packages.routers.backend_evaluations import router as evaluations_router
from packages.routers.backend_recommendations import router as recommendations_router
from packages.routers.backend_sources_opportunities import router as sources_opportunities_router

app = FastAPI(title="Router-Based Packaged Backend API")
app.include_router(sources_opportunities_router)
app.include_router(evaluations_router)
app.include_router(recommendations_router)
