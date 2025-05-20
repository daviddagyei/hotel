from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from backend.core.base import Base

class StaffRole(Base):
    __tablename__ = "staff_roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    staff = relationship("Staff", back_populates="roles")
    role = relationship("Role", back_populates="staff_roles")
