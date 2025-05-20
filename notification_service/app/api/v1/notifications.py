from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from notification_service.app.schemas.notification import NotificationCreate, NotificationRead, NotificationUpdate
from notification_service.app.services.notification_service import NotificationService
from notification_service.app.models.notification import Notification
from backend.auth_service.db import get_db  # Reuse DB dependency pattern
from typing import List, Optional

router = APIRouter()

@router.post("/", response_model=NotificationRead, status_code=201)
def create_notification(notification: NotificationCreate, db: Session = Depends(get_db)):
    service = NotificationService(db)
    notif = service.create_notification(notification)
    return notif

@router.get("/{notif_id}", response_model=NotificationRead)
def get_notification(notif_id: int, db: Session = Depends(get_db)):
    service = NotificationService(db)
    notif = service.get_notification(notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notif

@router.get("/", response_model=List[NotificationRead])
def list_notifications(recipient: str, property_id: Optional[int] = None, db: Session = Depends(get_db)):
    service = NotificationService(db)
    return service.list_notifications(recipient, property_id)

@router.patch("/{notif_id}/read", response_model=NotificationRead)
def mark_as_read(notif_id: int, db: Session = Depends(get_db)):
    service = NotificationService(db)
    notif = service.mark_as_read(notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notif
