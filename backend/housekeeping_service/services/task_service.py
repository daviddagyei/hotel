from backend.housekeeping_service.repositories.task_repository import TaskRepository
from backend.housekeeping_service.models.task import Task, TaskStatusEnum, TaskTypeEnum
from backend.housekeeping_service.schemas.task import TaskCreate, TaskUpdate
from sqlalchemy.orm import Session
from typing import Optional, List

class TaskService:
    def __init__(self, db: Session):
        self.repo = TaskRepository(db)

    def create_task(self, data: TaskCreate) -> Task:
        task = Task(**data.dict())
        return self.repo.create(task)

    def update_task(self, task_id: int, data: TaskUpdate) -> Optional[Task]:
        task = self.repo.get(task_id)
        if not task:
            return None
        return self.repo.update(task, data.dict(exclude_unset=True))

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
