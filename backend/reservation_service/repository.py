from backend.reservation_service.models import Reservation
from sqlalchemy.orm import Session
from typing import List, Optional

class ReservationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, id: int) -> Optional[Reservation]:
        return self.db.query(Reservation).filter(Reservation.id == id).first()

    def list(self, property_id: int = None, guest_id: int = None) -> List[Reservation]:
        query = self.db.query(Reservation)
        if property_id:
            query = query.filter(Reservation.property_id == property_id)
        if guest_id:
            query = query.filter(Reservation.guest_id == guest_id)
        return query.all()

    def list_reservations(self, property_id: int = None, guest_id: int = None, start_date: str = None, end_date: str = None) -> List[Reservation]:
        query = self.db.query(Reservation)
        if property_id:
            query = query.filter(Reservation.property_id == property_id)
        if guest_id:
            query = query.filter(Reservation.guest_id == guest_id)
        if start_date:
            query = query.filter(Reservation.check_in >= start_date)
        if end_date:
            query = query.filter(Reservation.check_out <= end_date)
        return query.all()

    def create(self, obj_in) -> Reservation:
        db_obj = Reservation(**obj_in.dict())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, id: int, obj_in) -> Reservation:
        db_obj = self.get(id)
        if db_obj is None:
            raise AttributeError(f"Reservation with id {id} does not exist.")
        for field, value in obj_in.dict(exclude_unset=True).items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> None:
        db_obj = self.get(id)
        if db_obj is not None:
            self.db.delete(db_obj)
            self.db.commit()
