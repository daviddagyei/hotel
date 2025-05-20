from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Float, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.core.base import Base, BaseORMModel

class Property(BaseORMModel, Base):
    __tablename__ = "properties"
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    rooms = relationship("Room", back_populates="property")

class RoomType(BaseORMModel, Base):
    __tablename__ = "room_types"
    property_id = Column(Integer, ForeignKey("properties.id"), index=True)
    name = Column(String, nullable=False)
    base_rate = Column(Float, nullable=False)
    rooms = relationship("Room", back_populates="room_type")

class Room(BaseORMModel, Base):
    __tablename__ = "rooms"
    __table_args__ = (
        UniqueConstraint('property_id', 'number', name='uix_property_room_number'),
    )
    property_id = Column(Integer, ForeignKey("properties.id"), index=True)
    number = Column(String, nullable=False)
    type_id = Column(Integer, ForeignKey("room_types.id"))
    status = Column(Enum("AVAILABLE", "OCCUPIED", "CLEANING", "MAINTENANCE", name="room_status"), default="AVAILABLE")
    floor = Column(String, nullable=True)
    amenities = Column(String, nullable=True)  # Comma-separated for MVP simplicity
    property = relationship("Property", back_populates="rooms")
    room_type = relationship("RoomType", back_populates="rooms")
    status_logs = relationship("RoomStatusLog", back_populates="room")

class RatePlan(BaseORMModel, Base):
    __tablename__ = "rate_plans"
    property_id = Column(Integer, ForeignKey("properties.id"), index=True)
    room_type_id = Column(Integer, ForeignKey("room_types.id"))
    name = Column(String, nullable=False)
    daily_rate = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

class RoomStatusLog(BaseORMModel, Base):
    __tablename__ = "room_status_logs"
    room_id = Column(Integer, ForeignKey("rooms.id"), index=True)
    old_status = Column(String, nullable=False)
    new_status = Column(String, nullable=False)
    changed_at = Column(DateTime, default=func.now())
    changed_by = Column(String, nullable=True)  # Staff username or id
    room = relationship("Room", back_populates="status_logs")
