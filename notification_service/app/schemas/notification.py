from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum

class NotificationType(str, Enum):
    INFO = "INFO"
    ALERT = "ALERT"
    WARNING = "WARNING"
    REMINDER = "REMINDER"  # Add REMINDER to support all test types

class NotificationBase(BaseModel):
    property_id: int
    type: NotificationType
    message: str
    recipient: str

    @validator("message")
    def message_must_not_be_blank(cls, v):
        if not v or not v.strip():
            raise ValueError("Message must not be blank")
        return v

    @validator("recipient")
    def recipient_must_not_be_blank(cls, v):
        if not v or not v.strip():
            raise ValueError("Recipient must not be blank")
        return v

class NotificationCreate(NotificationBase):
    pass

class NotificationRead(NotificationBase):
    id: int
    is_read: bool
    class Config:
        orm_mode = True

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
