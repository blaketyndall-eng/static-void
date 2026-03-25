from fastapi import FastAPI

from app_sys_v21 import app as base_app
from packages.routers.backend_global_summary_v4 import router as global_summary_v4_router
from packages.routers.backend_master_console_v5 import router as master_console_v5_router

app = FastAPI(title='Unified System Console Expansion API')
for route in base_app.router.routes:
    app.router.routes.append(route)
app.include_router(master_console_v5_router)
app.include_router(global_summary_v4_router)
