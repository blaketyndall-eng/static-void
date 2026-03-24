from fastapi import FastAPI

from packages.routers.backend_marketing import router as marketing_router

app = FastAPI(title="Marketing Hub API")
app.include_router(marketing_router)
