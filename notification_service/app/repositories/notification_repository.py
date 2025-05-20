from sqlalchemy.orm import Session
from ..models.notification import Notification
from ..schemas.notification import NotificationCreate, NotificationUpdate
from typing import List, Optional

class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, notification_in: NotificationCreate) -> Notification:
        notif = Notification(**notification_in.dict())
        self.db.add(notif)
        self.db.commit()
        self.db.refresh(notif)
        return notif

    def get(self, notif_id: int) -> Optional[Notification]:
        return self.db.query(Notification).filter(Notification.id == notif_id).first()

    def list_for_recipient(self, recipient: str, property_id: Optional[int] = None) -> List[Notification]:
        q = self.db.query(Notification).filter(Notification.recipient == recipient)
        if property_id:
            q = q.filter(Notification.property_id == property_id)
        return q.order_by(Notification.id.desc()).all()

    def mark_as_read(self, notif_id: int) -> Optional[Notification]:
        notif = self.get(notif_id)
        if notif:
            notif.is_read = True
            self.db.commit()
            self.db.refresh(notif)
        return notif
