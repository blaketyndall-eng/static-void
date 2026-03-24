from fastapi import FastAPI

from packages.routers.backend_master_console import router as master_console_router

app = FastAPI(title="Master Console API")
app.include_router(master_console_router)
