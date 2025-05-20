from fastapi import FastAPI
from backend.auth_service.api.v1 import staff, role, auth
from backend.core.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = FastAPI()
app.include_router(staff.router, prefix="/api/v1", tags=["staff"])
app.include_router(role.router, prefix="/api/v1", tags=["roles"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])

DATABASE_URL = "sqlite:///./auth_service.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
