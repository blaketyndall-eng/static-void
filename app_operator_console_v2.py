from fastapi import FastAPI

from packages.routers.backend_apps import router as apps_router
from packages.routers.backend_apps_metrics import router as apps_metrics_router
from packages.routers.backend_apps_views import router as apps_views_router

app = FastAPI(title="Operator Console V2 API")
app.include_router(apps_router)
app.include_router(apps_metrics_router)
app.include_router(apps_views_router)
