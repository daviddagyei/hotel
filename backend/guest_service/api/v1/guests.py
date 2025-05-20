from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.guest_service.schemas.guest import GuestCreate, GuestRead
from backend.guest_service.services.guest_service import GuestService
from backend.guest_service.models.guest import Guest
from backend.core.base import Base
from backend.guest_service.db import get_db
from typing import List

router = APIRouter()

def get_guest_service(db: Session = Depends(get_db)):
    return GuestService(db)

@router.post("/guests/", response_model=GuestRead, status_code=status.HTTP_201_CREATED)
def create_guest(guest: GuestCreate, service: GuestService = Depends(get_guest_service)):
    db_guest = service.create_or_update_guest(guest)
    return db_guest

@router.get("/guests/{guest_id}", response_model=GuestRead)
def get_guest(guest_id: int, service: GuestService = Depends(get_guest_service)):
    guest = service.get_guest_by_id(guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    return guest

@router.get("/guests/search/", response_model=List[GuestRead])
def search_guests(q: str, service: GuestService = Depends(get_guest_service)):
    return service.search_guest(q)
