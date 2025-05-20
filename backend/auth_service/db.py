from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.base import Base
from backend.room_service.models import Property  # Use Property from room_service

DATABASE_URL = "sqlite:///./auth_service.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
