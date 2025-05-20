from fastapi import FastAPI
from backend.guest_service.api.v1 import guests
from backend.core.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.room_service.models import Property  # Use canonical Property model

app = FastAPI()
app.include_router(guests.router, prefix="/api/v1", tags=["guests"])

# Dependency for DB session (for demo, use SQLite in-memory)
DATABASE_URL = "sqlite:///./guest_service.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Dependency
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
