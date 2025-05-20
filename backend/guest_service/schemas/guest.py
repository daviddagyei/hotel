from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class GuestBase(BaseModel):
    property_id: Optional[int] = None
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None

class GuestCreate(GuestBase):
    pass

class GuestRead(GuestBase):
    id: int

    class Config:
        orm_mode = True
