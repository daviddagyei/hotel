from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.base import Base

DATABASE_URL = "sqlite:///../housekeeping_service.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
