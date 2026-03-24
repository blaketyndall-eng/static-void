from fastapi import FastAPI

from packages.routers.backend_investment import router as investment_router
from packages.routers.backend_investment_options import router as investment_options_router
from packages.routers.backend_investment_swing import router as investment_swing_router

app = FastAPI(title="Multi-Engine Investment Analyst Backend API")
app.include_router(investment_router)
app.include_router(investment_swing_router)
app.include_router(investment_options_router)
