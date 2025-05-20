from sqlalchemy.orm import Session
from backend.housekeeping_service.models.task import Task, TaskStatusEnum
from typing import List, Optional

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, task_id: int) -> Optional[Task]:
        return self.db.query(Task).filter(Task.id == task_id).first()

    def list(self, property_id: Optional[int] = None, status: Optional[TaskStatusEnum] = None, assigned_to: Optional[int] = None) -> List[Task]:
        query = self.db.query(Task)
        if property_id:
            query = query.filter(Task.property_id == property_id)
        if status:
            query = query.filter(Task.status == status)
        if assigned_to:
            query = query.filter(Task.assigned_to == assigned_to)
        return query.all()

    def create(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update(self, task: Task, data: dict) -> Task:
        for key, value in data.items():
            setattr(task, key, value)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task):
        self.db.delete(task)
        self.db.commit()
