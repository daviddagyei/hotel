from backend.core.repository import BaseRepository
from .models import Property, Room, RoomType, RatePlan, RoomStatusLog
from sqlalchemy.orm import Session
from typing import List, Optional

class PropertyRepository(BaseRepository):
    def __init__(self, db: Session):
        self.db = db

    def get(self, id: int) -> Optional[Property]:
        return self.db.query(Property).filter(Property.id == id).first()

    def list(self, property_id: int = None) -> List[Property]:
        query = self.db.query(Property)
        if property_id:
            query = query.filter(Property.id == property_id)
        return query.all()

    def create(self, obj_in) -> Property:
        db_obj = Property(**obj_in.dict())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, id: int, obj_in) -> Property:
        db_obj = self.get(id)
        if db_obj is None:
            raise AttributeError(f"Object with id {id} does not exist.")
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

class RoomRepository(BaseRepository):
    def __init__(self, db: Session):
        self.db = db

    def get(self, id: int) -> Optional[Room]:
        return self.db.query(Room).filter(Room.id == id).first()

    def list(self, property_id: int = None) -> List[Room]:
        query = self.db.query(Room)
        if property_id:
            query = query.filter(Room.property_id == property_id)
        return query.all()

    def create(self, obj_in) -> Room:
        # Accept dict or object with .dict()
        if hasattr(obj_in, 'dict'):
            data = obj_in.dict()
        else:
            data = dict(obj_in)
        # Check for required fields
        required = ['property_id', 'number', 'type_id', 'status', 'floor']
        for field in required:
            if field not in data or data[field] in (None, ""):
                raise ValueError(f"Missing or empty required field: {field}")
        existing = self.db.query(Room).filter(Room.property_id == data['property_id'], Room.number == data['number']).first()
        if existing:
            raise ValueError(f"Room number '{data['number']}' already exists for this property.")
        db_obj = Room(**data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, id: int, obj_in) -> Room:
        db_obj = self.get(id)
        if db_obj is None:
            raise AttributeError(f"Object with id {id} does not exist.")
        if hasattr(obj_in, 'dict'):
            data = obj_in.dict(exclude_unset=True)
        else:
            data = dict(obj_in)
        new_number = data.get('number', db_obj.number)
        new_property_id = data.get('property_id', db_obj.property_id)
        if (new_number != db_obj.number or new_property_id != db_obj.property_id):
            existing = self.db.query(Room).filter(Room.property_id == new_property_id, Room.number == new_number, Room.id != id).first()
            if existing:
                raise ValueError(f"Room number '{new_number}' already exists for this property.")
        for field, value in data.items():
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

class RoomTypeRepository(BaseRepository):
    def __init__(self, db: Session):
        self.db = db

    def get(self, id: int) -> Optional[RoomType]:
        return self.db.query(RoomType).filter(RoomType.id == id).first()

    def list(self, property_id: int = None) -> List[RoomType]:
        query = self.db.query(RoomType)
        if property_id:
            query = query.filter(RoomType.property_id == property_id)
        return query.all()

    def create(self, obj_in) -> RoomType:
        db_obj = RoomType(**obj_in.dict())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, id: int, obj_in) -> RoomType:
        db_obj = self.get(id)
        if db_obj is None:
            raise AttributeError(f"Object with id {id} does not exist.")
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

class RatePlanRepository(BaseRepository):
    def __init__(self, db: Session):
        self.db = db

    def get(self, id: int) -> Optional[RatePlan]:
        return self.db.query(RatePlan).filter(RatePlan.id == id).first()

    def list(self, property_id: int = None) -> List[RatePlan]:
        query = self.db.query(RatePlan)
        if property_id:
            query = query.filter(RatePlan.property_id == property_id)
        return query.all()

    def create(self, obj_in) -> RatePlan:
        db_obj = RatePlan(**obj_in.dict())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, id: int, obj_in) -> RatePlan:
        db_obj = self.get(id)
        if db_obj is None:
            raise AttributeError(f"Object with id {id} does not exist.")
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

class RoomStatusLogRepository(BaseRepository):
    def __init__(self, db: Session):
        self.db = db

    def get(self, id: int) -> Optional[RoomStatusLog]:
        return self.db.query(RoomStatusLog).filter(RoomStatusLog.id == id).first()

    def list(self, property_id: int = None) -> List[RoomStatusLog]:
        query = self.db.query(RoomStatusLog)
        if property_id:
            query = query.join(Room).filter(Room.property_id == property_id)
        return query.all()

    def create(self, obj_in) -> RoomStatusLog:
        db_obj = RoomStatusLog(**obj_in.dict())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, id: int, obj_in) -> RoomStatusLog:
        db_obj = self.get(id)
        if db_obj is None:
            raise AttributeError(f"Object with id {id} does not exist.")
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
