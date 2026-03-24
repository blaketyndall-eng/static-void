from fastapi import FastAPI

from packages.routers.backend_apps import router as apps_router
from packages.routers.backend_apps_views import router as apps_views_router

app = FastAPI(title="Operator Console API")
app.include_router(apps_router)
app.include_router(apps_views_router)
