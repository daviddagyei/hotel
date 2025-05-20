from fastapi import FastAPI
from backend.reservation_service.api import router as reservation_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(reservation_router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "*"  # For dev, allow all. Remove or restrict for production.
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
