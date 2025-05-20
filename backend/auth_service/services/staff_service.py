from backend.auth_service.repositories.staff_repository import StaffRepository
from backend.auth_service.models.staff import Staff
from backend.auth_service.models.staff_role import StaffRole
from backend.auth_service.models.role import Role
from backend.auth_service.schemas.staff import StaffCreate, StaffUpdate
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import Optional, List

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class StaffService:
    def __init__(self, db: Session):
        self.repo = StaffRepository(db)
        self.db = db

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_staff(self, data: StaffCreate) -> Staff:
        hashed_password = self.get_password_hash(data.password)
        staff = Staff(
            property_id=data.property_id,
            username=data.username,
            email=data.email,
            hashed_password=hashed_password,
            is_active=data.is_active
        )
        return self.repo.create(staff)

    def authenticate(self, username: str, password: str) -> Optional[Staff]:
        staff = self.repo.get_by_username(username)
        if staff and self.verify_password(password, staff.hashed_password):
            return staff
        return None

    def assign_role(self, staff_id: int, role_id: int):
        staff_role = StaffRole(staff_id=staff_id, role_id=role_id)
        self.db.add(staff_role)
        self.db.commit()
        return staff_role
