from backend.core.base import Base
from sqlalchemy import Column, Integer

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True)

class Property(Base):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True)

class Staff(Base):
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True)
