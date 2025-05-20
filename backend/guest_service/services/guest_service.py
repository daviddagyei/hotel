from backend.guest_service.repositories.guest_repository import GuestRepository
from backend.guest_service.schemas.guest import GuestCreate
from backend.guest_service.models.guest import Guest
from sqlalchemy.orm import Session
from typing import Optional, List

class GuestService:
    def __init__(self, db: Session):
        self.repo = GuestRepository(db)

    def create_or_update_guest(self, data: GuestCreate) -> Guest:
        existing = self.repo.get_by_email(data.email)
        if existing:
            return self.repo.update(existing, data.dict(exclude_unset=True))
        guest = Guest(**data.dict())
        return self.repo.create(guest)

    def get_guest_by_id(self, guest_id: int) -> Optional[Guest]:
        return self.repo.get(guest_id)

    def search_guest(self, query: str) -> List[Guest]:
        # Return empty list if query is empty or only whitespace
        if not query or not query.strip():
            return []
        q = f"%{query.lower()}%"
        return self.repo.db.query(Guest).filter(
            (Guest.first_name.ilike(q)) |
            (Guest.last_name.ilike(q)) |
            (Guest.email.ilike(q))
        ).all()
