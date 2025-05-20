from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.housekeeping_service.api.v1 import tasks

app = FastAPI(title="Housekeeping & Maintenance Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router, prefix="/api/v1")

# Routers will be included here
