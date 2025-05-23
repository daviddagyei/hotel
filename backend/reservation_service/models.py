from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime, Float, String
from sqlalchemy.orm import relationship
from backend.core.base import Base, BaseORMModel
import enum

class ReservationStatusEnum(enum.Enum):
    BOOKED = "BOOKED"
    CHECKED_IN = "CHECKED_IN"
    CHECKED_OUT = "CHECKED_OUT"
    CANCELED = "CANCELED"

class Reservation(BaseORMModel, Base):
    __tablename__ = "reservations"
    property_id = Column(Integer, nullable=False)  # Removed ForeignKey
    guest_id = Column(Integer, nullable=False)     # Removed ForeignKey
    room_id = Column(Integer, nullable=True)       # Removed ForeignKey
    check_in = Column(DateTime, nullable=False)
    check_out = Column(DateTime, nullable=False)
    status = Column(Enum(ReservationStatusEnum), default=ReservationStatusEnum.BOOKED, nullable=False)
    price = Column(Float, nullable=True)
    payment_status = Column(String, nullable=True)  # Placeholder for payment integration
    # Relationships (optional for MVP):
    # guest = relationship("Guest")
    # room = relationship("Room")
