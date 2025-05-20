from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.auth_service.services.staff_service import StaffService
from backend.auth_service.db import get_db
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login/")
def login(data: LoginRequest, service: StaffService = Depends(lambda db=Depends(get_db): StaffService(db))):
    staff = service.authenticate(data.username, data.password)
    if not staff:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # For MVP, just return staff info (no JWT yet)
    return {"id": staff.id, "username": staff.username, "email": staff.email}
