from fastapi import APIRouter, Query
from typing import Optional
from reporting_service.app.services.reporting_service import (
    get_occupancy_report,
    get_task_history_report,
    get_night_audit_report,
)
from reporting_service.app.schemas.reports import (
    OccupancyReport,
    TaskHistoryReport,
    NightAuditReport,
)

router = APIRouter()

@router.get("/occupancy", response_model=OccupancyReport)
async def occupancy_report(
    property_id: int,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    return await get_occupancy_report(property_id, start_date, end_date)

@router.get("/task-history", response_model=TaskHistoryReport)
async def task_history_report(
    property_id: int,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    return await get_task_history_report(property_id, start_date, end_date)

@router.get("/night-audit", response_model=NightAuditReport)
async def night_audit_report(
    property_id: int,
    date: Optional[str] = Query(None),
):
    return await get_night_audit_report(property_id, date)
