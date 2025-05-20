from backend.guest_service.models.guest import Guest
from sqlalchemy.orm import Session
from typing import Optional, List

class GuestRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, guest_id: int) -> Optional[Guest]:
        return self.db.query(Guest).filter(Guest.id == guest_id).first()

    def get_by_email(self, email: str) -> Optional[Guest]:
        return self.db.query(Guest).filter(Guest.email == email).first()

    def list(self, property_id: Optional[int] = None) -> List[Guest]:
        query = self.db.query(Guest)
        if property_id:
            query = query.filter(Guest.property_id == property_id)
        return query.all()

    def create(self, guest: Guest) -> Guest:
        self.db.add(guest)
        self.db.commit()
        self.db.refresh(guest)
        return guest

    def update(self, guest: Guest, data: dict) -> Guest:
        for key, value in data.items():
            setattr(guest, key, value)
        self.db.commit()
        self.db.refresh(guest)
        return guest

    def delete(self, guest: Guest):
        self.db.delete(guest)
        self.db.commit()
