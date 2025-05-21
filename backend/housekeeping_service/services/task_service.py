import requests
from backend.housekeeping_service.repositories.task_repository import TaskRepository
from backend.housekeeping_service.models.task import Task, TaskStatusEnum, TaskTypeEnum
from backend.housekeeping_service.schemas.task import TaskCreate, TaskUpdate
from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException

ROOM_SERVICE_URL = "http://localhost:8001/api/v1/room-service/rooms"

class TaskService:
    def __init__(self, db: Session):
        self.repo = TaskRepository(db)

    def _verify_room_exists(self, room_id: int):
        if room_id is None:
            return
        try:
            resp = requests.get(f"{ROOM_SERVICE_URL}/{room_id}", timeout=2)
            if resp.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Room {room_id} does not exist")
        except Exception:
            raise HTTPException(status_code=400, detail=f"Room {room_id} does not exist or room service unavailable")

    def create_task(self, data: TaskCreate) -> Task:
        if data.room_id is not None:
            self._verify_room_exists(data.room_id)
        task = Task(**data.dict())
        return self.repo.create(task)

    def update_task(self, task_id: int, data: TaskUpdate) -> Optional[Task]:
        task = self.repo.get(task_id)
        if not task:
            return None
        # If updating room_id, verify existence
        if data.room_id is not None:
            self._verify_room_exists(data.room_id)
        updated_task = self.repo.update(task, data.dict(exclude_unset=True))
        # If marking as DONE and task has a room, update room status to CLEAN
        if data.status == TaskStatusEnum.DONE and updated_task.room_id:
            try:
                requests.patch(f"{ROOM_SERVICE_URL}/{updated_task.room_id}", json={"status": "CLEAN"}, timeout=2)
            except Exception:
                pass  # Log or handle error in production
        return updated_task

    def list_tasks(self, property_id: Optional[int] = None, status: Optional[TaskStatusEnum] = None, assigned_to: Optional[int] = None) -> List[Task]:
        return self.repo.list(property_id=property_id, status=status, assigned_to=assigned_to)

    def get_task(self, task_id: int) -> Optional[Task]:
        return self.repo.get(task_id)

    def delete_task(self, task_id: int) -> bool:
        task = self.repo.get(task_id)
        if not task:
            return False
        self.repo.delete(task)
        return True
