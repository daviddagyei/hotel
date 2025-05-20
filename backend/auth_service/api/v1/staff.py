from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from backend.auth_service.schemas.staff import StaffCreate, StaffRead, StaffUpdate
from backend.auth_service.services.staff_service import StaffService
from backend.auth_service.models.staff import Staff
from backend.auth_service.db import get_db
from typing import List

router = APIRouter()

def get_staff_service(db: Session = Depends(get_db)):
    return StaffService(db)

@router.post("/staff/", response_model=StaffRead, status_code=status.HTTP_201_CREATED)
def create_staff(staff: StaffCreate, service: StaffService = Depends(get_staff_service)):
    try:
        db_staff = service.create_staff(staff)
        return db_staff
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.get("/staff/{staff_id}", response_model=StaffRead)
def get_staff(staff_id: int, service: StaffService = Depends(get_staff_service)):
    staff = service.repo.get(staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return staff

@router.patch("/staff/{staff_id}", response_model=StaffRead)
def update_staff(staff_id: int, update: StaffUpdate = Body(...), service: StaffService = Depends(get_staff_service)):
    staff = service.repo.get(staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    update_data = update.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")
    try:
        updated = service.repo.update(staff, update_data)
        return updated
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.delete("/staff/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff(staff_id: int, service: StaffService = Depends(get_staff_service)):
    staff = service.repo.get(staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    service.repo.delete(staff)
    return None

@router.post("/staff/{staff_id}/roles/{role_id}", status_code=status.HTTP_200_OK)
def assign_role(staff_id: int, role_id: int, service: StaffService = Depends(get_staff_service)):
    staff = service.repo.get(staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    staff_role = service.assign_role(staff_id, role_id)
    return {"staff_id": staff_role.staff_id, "role_id": staff_role.role_id}
