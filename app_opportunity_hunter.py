from fastapi import FastAPI

from packages.routers.backend_opportunity_hunter import router as opportunity_router
from packages.routers.backend_opportunity_hunter_scanners import router as opportunity_scanners_router

app = FastAPI(title="Opportunity Hunter API")
app.include_router(opportunity_router)
app.include_router(opportunity_scanners_router)
