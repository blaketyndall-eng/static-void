from fastapi import FastAPI

from packages.routers.backend_investment import router as investment_router

app = FastAPI(title="Investment Analyst Backend API")
app.include_router(investment_router)
