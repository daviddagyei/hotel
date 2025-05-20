from backend.auth_service.models.role import Role
from sqlalchemy.orm import Session
from typing import Optional, List

class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, role_id: int) -> Optional[Role]:
        return self.db.query(Role).filter(Role.id == role_id).first()

    def get_by_name(self, name: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.name == name).first()

    def list(self) -> List[Role]:
        return self.db.query(Role).all()

    def create(self, role: Role) -> Role:
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def update(self, role: Role, data: dict) -> Role:
        for key, value in data.items():
            setattr(role, key, value)
        self.db.commit()
        self.db.refresh(role)
        return role

    def delete(self, role: Role):
        self.db.delete(role)
        self.db.commit()
