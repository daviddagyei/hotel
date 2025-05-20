# Reporting Service main entrypoint
from fastapi import FastAPI
from .api.v1.reports import router as reports_router

app = FastAPI()
app.include_router(reports_router, prefix="/api/v1/reports", tags=["reports"])
