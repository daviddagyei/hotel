from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.housekeeping_service.schemas.task import TaskCreate, TaskUpdate, TaskRead, TaskStatusEnum
from backend.housekeeping_service.services.task_service import TaskService
from backend.housekeeping_service.models.task import Task
from backend.housekeeping_service.db import get_db
from typing import List, Optional

router = APIRouter()

def get_task_service(db: Session = Depends(get_db)):
    return TaskService(db)

@router.post("/tasks/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, service: TaskService = Depends(get_task_service)):
    return service.create_task(task)

@router.get("/tasks/", response_model=List[TaskRead])
def list_tasks(
    property_id: Optional[int] = Query(None),
    status: Optional[TaskStatusEnum] = Query(None),
    assigned_to: Optional[int] = Query(None),
    service: TaskService = Depends(get_task_service)
):
    return service.list_tasks(property_id=property_id, status=status, assigned_to=assigned_to)

@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, service: TaskService = Depends(get_task_service)):
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/tasks/{task_id}", response_model=TaskRead)
def update_task(task_id: int, update: TaskUpdate, service: TaskService = Depends(get_task_service)):
    task = service.update_task(task_id, update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, service: TaskService = Depends(get_task_service)):
    if not service.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return None
