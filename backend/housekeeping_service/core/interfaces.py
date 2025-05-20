from abc import ABC, abstractmethod
from typing import List, Optional
from backend.housekeeping_service.models.task import Task, TaskStatusEnum
from backend.housekeeping_service.schemas.task import TaskCreate, TaskUpdate

class ITaskService(ABC):
    @abstractmethod
    def create_task(self, data: TaskCreate) -> Task:
        pass

    @abstractmethod
    def update_task(self, task_id: int, data: TaskUpdate) -> Optional[Task]:
        pass

    @abstractmethod
    def list_tasks(self, property_id: Optional[int] = None, status: Optional[TaskStatusEnum] = None, assigned_to: Optional[int] = None) -> List[Task]:
        pass

    @abstractmethod
    def get_task(self, task_id: int) -> Optional[Task]:
        pass

    @abstractmethod
    def delete_task(self, task_id: int) -> bool:
        pass
