from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.core.base import Base, BaseORMModel

class Role(BaseORMModel, Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    staff_roles = relationship("StaffRole", back_populates="role")
