from fastapi import FastAPI

from packages.routers.backend_app_builder import router as app_builder_router
from packages.routers.backend_app_builder_persistent import router as app_builder_persistent_router
from packages.routers.backend_app_builder_v2 import router as app_builder_v2_router

app = FastAPI(title="App Development Tool V2 API")
app.include_router(app_builder_router)
app.include_router(app_builder_persistent_router)
app.include_router(app_builder_v2_router)
