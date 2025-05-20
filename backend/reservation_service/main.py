from fastapi import FastAPI
from backend.reservation_service.api import router as reservation_router

app = FastAPI()
app.include_router(reservation_router, prefix="/api/v1")
