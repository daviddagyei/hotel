from fastapi import FastAPI
from backend.housekeeping_service.api.v1 import tasks

app = FastAPI(title="Housekeeping & Maintenance Service")

app.include_router(tasks.router, prefix="/api/v1")

# Routers will be included here
