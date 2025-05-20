from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from backend.core.base import Base, BaseORMModel
import enum
from backend.housekeeping_service.models.stubs import Property, Room, Staff

class TaskTypeEnum(str, enum.Enum):
    HOUSEKEEPING = "HOUSEKEEPING"
    MAINTENANCE = "MAINTENANCE"

class TaskStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class Task(BaseORMModel, Base):
    __tablename__ = "tasks"
    property_id = Column(Integer, ForeignKey("properties.id"), index=True, nullable=False)
    task_type = Column(Enum(TaskTypeEnum), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    description = Column(String, nullable=True)
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.PENDING, nullable=False)
    assigned_to = Column(Integer, ForeignKey("staff.id"), nullable=True)
    scheduled_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships (optional, for ORM navigation)
    # room = relationship("Room")
    # staff = relationship("Staff")
