from backend.core.service import BaseService
from .repository import (
    PropertyRepository, RoomRepository, RoomTypeRepository, RatePlanRepository, RoomStatusLogRepository
)
from .models import Room
from sqlalchemy.orm import Session

# Import exceptions from the new exceptions.py module
from backend.room_service.exceptions import InvalidStatusTransition, NoAvailableRoom

class PropertyService(BaseService):
    def __init__(self, db: Session):
        self.repo = PropertyRepository(db)

    def validate(self, *args, **kwargs):
        pass
    # Add business logic methods as needed

class RoomService(BaseService):
    def __init__(self, db: Session):
        self.repo = RoomRepository(db)

    def validate(self, *args, **kwargs):
        pass

    def allocate_room(self, property_id: int, room_type_id: int):
        rooms = self.repo.list(property_id=property_id)
        for room in rooms:
            if room.type_id == room_type_id and room.status == "AVAILABLE":
                return room
        # Raise if no available room
        raise NoAvailableRoom(f"No available room for property_id={property_id}, room_type_id={room_type_id}")

    def mark_room_status(self, room_id: int, status: str):
        room = self.repo.get(room_id)
        if not room:
            raise InvalidStatusTransition(f"Room {room_id} not found")
        if room.status == status:
            raise InvalidStatusTransition(f"Room {room_id} is already in status {status}")
        # Optionally, add more robust state transition validation here
        old_status = room.status
        room.status = status
        self.repo.db.commit()
        self.repo.db.refresh(room)
        return room

class RoomTypeService(BaseService):
    def __init__(self, db: Session):
        self.repo = RoomTypeRepository(db)
    def validate(self, *args, **kwargs):
        pass

class RatePlanService(BaseService):
    def __init__(self, db: Session):
        self.repo = RatePlanRepository(db)
    def validate(self, *args, **kwargs):
        pass

class RoomStatusLogService(BaseService):
    def __init__(self, db: Session):
        self.repo = RoomStatusLogRepository(db)
    def validate(self, *args, **kwargs):
        pass
