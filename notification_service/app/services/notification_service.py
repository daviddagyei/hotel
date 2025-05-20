from ..repositories.notification_repository import NotificationRepository
from ..schemas.notification import NotificationCreate, NotificationUpdate
from sqlalchemy.orm import Session
from typing import List, Optional

class NotificationService:
    def __init__(self, db: Session):
        self.repo = NotificationRepository(db)

    def create_notification(self, notification_in: NotificationCreate):
        return self.repo.create(notification_in)

    def get_notification(self, notif_id: int):
        return self.repo.get(notif_id)

    def list_notifications(self, recipient: str, property_id: Optional[int] = None):
        return self.repo.list_for_recipient(recipient, property_id)

    def mark_as_read(self, notif_id: int):
        return self.repo.mark_as_read(notif_id)
