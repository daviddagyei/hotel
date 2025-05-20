from backend.auth_service.repositories.role_repository import RoleRepository
from backend.auth_service.models.role import Role
from backend.auth_service.schemas.role import RoleCreate
from sqlalchemy.orm import Session
from typing import Optional, List

class RoleService:
    def __init__(self, db: Session):
        self.repo = RoleRepository(db)

    def create_role(self, data: RoleCreate) -> Role:
        role = Role(name=data.name, description=data.description)
        return self.repo.create(role)

    def get_role_by_name(self, name: str) -> Optional[Role]:
        return self.repo.get_by_name(name)

    def list_roles(self) -> List[Role]:
        return self.repo.list()
