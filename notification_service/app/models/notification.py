from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from backend.core.base import Base
import enum

class NotificationType(str, enum.Enum):
    INFO = "INFO"
    ALERT = "ALERT"
    WARNING = "WARNING"
    REMINDER = "REMINDER"  # Add REMINDER to match schema and tests

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, nullable=False)
    type = Column(Enum(NotificationType, name="notificationtype"), nullable=False)
    message = Column(String, nullable=False)
    recipient = Column(String, nullable=False)  # staff_id, role, or channel
    is_read = Column(Boolean, default=False, nullable=False)
    # created_at, updated_at can be added if needed
