from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class ReservationStatusEnum(str, Enum):
    BOOKED = "BOOKED"
    CHECKED_IN = "CHECKED_IN"
    CHECKED_OUT = "CHECKED_OUT"
    CANCELED = "CANCELED"

class ReservationCreate(BaseModel):
    property_id: int
    guest_id: int
    room_id: Optional[int] = None
    check_in: datetime
    check_out: datetime
    price: Optional[float] = None
    payment_status: Optional[str] = None

class ReservationUpdate(BaseModel):
    status: Optional[ReservationStatusEnum] = None
    room_id: Optional[int] = None
    price: Optional[float] = None
    payment_status: Optional[str] = None

class ReservationRead(BaseModel):
    id: int
    property_id: int
    guest_id: int
    room_id: Optional[int]
    check_in: datetime
    check_out: datetime
    status: ReservationStatusEnum
    price: Optional[float]
    payment_status: Optional[str]

    class Config:
        orm_mode = True
