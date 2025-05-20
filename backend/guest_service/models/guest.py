from sqlalchemy import Column, Integer, String, ForeignKey
from backend.core.base import Base, BaseORMModel

class Guest(BaseORMModel, Base):
    __tablename__ = "guests"
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), index=True, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, index=True, unique=True)
    phone = Column(String)
    address = Column(String, nullable=True)
    # Add more fields as needed (demographics, preferences, etc.)
