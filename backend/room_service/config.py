# This file can be used for configuration (e.g., DB connection settings)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.base import Base  # Use shared Base
import os

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./backend/room_service/room_service.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
