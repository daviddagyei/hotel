from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.base import Base
import os

SQLALCHEMY_DATABASE_URL = os.getenv("RESERVATION_DATABASE_URL", "sqlite:///./backend/reservation_service/reservation_service.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
