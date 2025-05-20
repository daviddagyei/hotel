# This file will initialize the FastAPI app for the room service
from fastapi import FastAPI
from .api import router

app = FastAPI()
app.include_router(router, prefix="/api/v1/room-service")

# Routers will be included here in the future
