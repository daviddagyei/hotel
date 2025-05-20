from pydantic import BaseModel, Field
from typing import List, Optional

class OccupancyReport(BaseModel):
    property_id: int
    start_date: Optional[str]
    end_date: Optional[str]
    total_rooms: int
    occupied_rooms: int
    occupancy_rate: float  # 0.0 - 1.0

class TaskHistoryReport(BaseModel):
    property_id: int
    start_date: Optional[str]
    end_date: Optional[str]
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    tasks: Optional[List[dict]] = None  # Optionally detailed

class NightAuditReport(BaseModel):
    property_id: int
    date: str
    total_bookings: int
    check_ins: int
    check_outs: int
    cancellations: int
    no_shows: int
    # Optionally add revenue, etc.
