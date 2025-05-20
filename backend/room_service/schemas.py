from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PropertyCreate(BaseModel):
    name: str
    location: Optional[str] = None

class PropertyRead(BaseModel):
    name: str
    location: Optional[str] = None

class RoomTypeCreate(BaseModel):
    property_id: int
    name: str
    base_rate: float

class RoomTypeRead(BaseModel):
    property_id: int
    name: str
    base_rate: float

class RoomCreate(BaseModel):
    property_id: int
    number: str
    type_id: int
    status: str = "AVAILABLE"
    floor: Optional[str] = None
    amenities: Optional[str] = None

class RoomRead(BaseModel):
    id: int
    property_id: int
    number: str
    type_id: int
    status: str
    floor: Optional[str] = None
    amenities: Optional[str] = None

class RoomUpdate(BaseModel):
    number: Optional[str] = None
    type_id: Optional[int] = None
    status: Optional[str] = None
    floor: Optional[str] = None
    amenities: Optional[str] = None

class RatePlanCreate(BaseModel):
    property_id: int
    room_type_id: int
    name: str
    daily_rate: float
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class RatePlanRead(BaseModel):
    property_id: int
    room_type_id: int
    name: str
    daily_rate: float
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class RoomStatusLogRead(BaseModel):
    room_id: int
    old_status: str
    new_status: str
    changed_at: datetime
    changed_by: Optional[str] = None
