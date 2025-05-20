from backend.core.schema import BaseSchema
from typing import Optional
from datetime import datetime

class PropertyCreate(BaseSchema):
    name: str
    location: Optional[str] = None

class PropertyRead(BaseSchema):
    name: str
    location: Optional[str] = None

class RoomTypeCreate(BaseSchema):
    property_id: int
    name: str
    base_rate: float

class RoomTypeRead(BaseSchema):
    property_id: int
    name: str
    base_rate: float

class RoomCreate(BaseSchema):
    property_id: int
    number: str
    type_id: int
    floor: Optional[str] = None
    amenities: Optional[str] = None

class RoomRead(BaseSchema):
    property_id: int
    number: str
    type_id: int
    status: str
    floor: Optional[str] = None
    amenities: Optional[str] = None

class RatePlanCreate(BaseSchema):
    property_id: int
    room_type_id: int
    name: str
    daily_rate: float
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class RatePlanRead(BaseSchema):
    property_id: int
    room_type_id: int
    name: str
    daily_rate: float
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class RoomStatusLogRead(BaseSchema):
    room_id: int
    old_status: str
    new_status: str
    changed_at: datetime
    changed_by: Optional[str] = None
