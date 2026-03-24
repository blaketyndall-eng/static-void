from fastapi import FastAPI

from packages.routers.backend_investment import router as investment_router
from packages.routers.backend_investment_options import router as investment_options_router
from packages.routers.backend_investment_prediction import router as investment_prediction_router
from packages.routers.backend_investment_swing import router as investment_swing_router

app = FastAPI(title="Three-Engine Investment Analyst Backend API")
app.include_router(investment_router)
app.include_router(investment_swing_router)
app.include_router(investment_options_router)
app.include_router(investment_prediction_router)
