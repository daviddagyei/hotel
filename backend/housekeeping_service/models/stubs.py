from sqlalchemy import Column, Integer
from backend.core.base import Base

class Property(Base):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True)

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True)

class Staff(Base):
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True)
