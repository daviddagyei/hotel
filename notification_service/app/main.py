# Notification Service main entrypoint
from fastapi import FastAPI
from .api.v1.notifications import router as notifications_router

app = FastAPI()
app.include_router(notifications_router, prefix="/api/v1/notifications", tags=["notifications"])
