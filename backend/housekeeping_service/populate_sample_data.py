# Script to populate sample data for housekeeping_service using SQLAlchemy models
import os
import sys
from datetime import datetime, timedelta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.housekeeping_service.db import get_db
from backend.housekeeping_service.models.task import Task, TaskStatusEnum, TaskTypeEnum
from sqlalchemy.orm import Session

def reset_and_populate():
    db: Session = next(get_db())
    # Delete all existing tasks
    db.query(Task).delete()
    db.commit()

    now = datetime.utcnow()
    sample_tasks = [
        Task(
            property_id=1,
            task_type=TaskTypeEnum.HOUSEKEEPING,
            room_id=1,
            description="Clean Room 101",
            status=TaskStatusEnum.PENDING,
            assigned_to=1,
            scheduled_time=now + timedelta(days=1),
            created_at=now,
            updated_at=now
        ),
        Task(
            property_id=1,
            task_type=TaskTypeEnum.MAINTENANCE,
            room_id=2,
            description="Fix AC in Room 102",
            status=TaskStatusEnum.IN_PROGRESS,
            assigned_to=2,
            scheduled_time=now + timedelta(days=2),
            created_at=now,
            updated_at=now
        ),
        Task(
            property_id=2,
            task_type=TaskTypeEnum.HOUSEKEEPING,
            room_id=4,
            description="Laundry for Room 104",
            status=TaskStatusEnum.DONE,
            assigned_to=None,
            scheduled_time=now + timedelta(days=3),
            created_at=now,
            updated_at=now
        ),
    ]
    db.add_all(sample_tasks)
    db.commit()
    print('Sample housekeeping tasks inserted.')

if __name__ == "__main__":
    reset_and_populate()
