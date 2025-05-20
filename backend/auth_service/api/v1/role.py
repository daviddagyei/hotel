from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.auth_service.schemas.role import RoleCreate, RoleRead
from backend.auth_service.services.role_service import RoleService
from backend.auth_service.db import get_db
from typing import List

router = APIRouter()

def get_role_service(db: Session = Depends(get_db)):
    return RoleService(db)

@router.post("/roles/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
def create_role(role: RoleCreate, service: RoleService = Depends(get_role_service)):
    db_role = service.create_role(role)
    return db_role

@router.get("/roles/", response_model=List[RoleRead])
def list_roles(service: RoleService = Depends(get_role_service)):
    return service.list_roles()

@router.get("/roles/{role_id}", response_model=RoleRead)
def get_role(role_id: int, service: RoleService = Depends(get_role_service)):
    role = service.repo.get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.patch("/roles/{role_id}", response_model=RoleRead)
def update_role(role_id: int, update: RoleCreate, service: RoleService = Depends(get_role_service)):
    role = service.repo.get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    updated = service.repo.update(role, update.dict(exclude_unset=True))
    return updated

@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: int, service: RoleService = Depends(get_role_service)):
    role = service.repo.get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    service.repo.delete(role)
    return None
