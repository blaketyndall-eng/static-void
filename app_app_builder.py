from fastapi import FastAPI

from packages.routers.backend_app_builder import router as app_builder_router
from packages.routers.backend_app_builder_persistent import router as app_builder_persistent_router

app = FastAPI(title="App Development Tool API")
app.include_router(app_builder_router)
app.include_router(app_builder_persistent_router)
