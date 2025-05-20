# Reporting Service main entrypoint
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.reports import router as reports_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reports_router, prefix="/api/v1/reports", tags=["reports"])
