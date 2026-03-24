from fastapi import FastAPI

from packages.routers.backend_marketing import router as marketing_router
from packages.routers.backend_marketing_views import router as marketing_views_router

app = FastAPI(title="Marketing Hub V2 API")
app.include_router(marketing_router)
app.include_router(marketing_views_router)
