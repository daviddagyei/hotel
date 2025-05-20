from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class TaskTypeEnum(str, Enum):
    HOUSEKEEPING = "HOUSEKEEPING"
    MAINTENANCE = "MAINTENANCE"

class TaskStatusEnum(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class TaskBase(BaseModel):
    property_id: int
    task_type: TaskTypeEnum
    room_id: Optional[int] = None
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    scheduled_time: Optional[datetime] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[TaskStatusEnum] = None
    assigned_to: Optional[int] = None
    scheduled_time: Optional[datetime] = None

class TaskRead(TaskBase):
    id: int
    status: TaskStatusEnum
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True
