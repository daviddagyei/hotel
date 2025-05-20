from pydantic import BaseModel, EmailStr
from typing import Optional, List

class StaffBase(BaseModel):
    property_id: Optional[int] = None
    username: str
    email: EmailStr
    is_active: Optional[bool] = True

class StaffCreate(StaffBase):
    password: str

class StaffRead(StaffBase):
    id: int
    roles: List[str] = []
    class Config:
        orm_mode = True

class StaffUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    class Config:
        extra = "allow"
