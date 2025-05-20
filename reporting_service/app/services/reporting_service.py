from typing import Optional, Callable
from reporting_service.app.schemas.reports import OccupancyReport, TaskHistoryReport, NightAuditReport
from reporting_service.app.core import clients

# Dependency injection for easier testing
async def get_occupancy_report(property_id: int, start_date: Optional[str], end_date: Optional[str], fetch_rooms: Callable = clients.fetch_rooms) -> OccupancyReport:
    rooms = await fetch_rooms(property_id)
    total_rooms = len(rooms)
    occupied_rooms = sum(1 for r in rooms if r.get("status") == "OCCUPIED")
    occupancy_rate = occupied_rooms / total_rooms if total_rooms else 0.0
    return OccupancyReport(
        property_id=property_id,
        start_date=start_date,
        end_date=end_date,
        total_rooms=total_rooms,
        occupied_rooms=occupied_rooms,
        occupancy_rate=occupancy_rate,
    )

async def get_task_history_report(property_id: int, start_date: Optional[str], end_date: Optional[str], fetch_tasks: Callable = clients.fetch_tasks) -> TaskHistoryReport:
    tasks = await fetch_tasks(property_id, start_date, end_date)
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.get("status") == "COMPLETED")
    pending_tasks = sum(1 for t in tasks if t.get("status") != "COMPLETED")
    return TaskHistoryReport(
        property_id=property_id,
        start_date=start_date,
        end_date=end_date,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        tasks=tasks,
    )

async def get_night_audit_report(property_id: int, date: Optional[str], fetch_reservations: Callable = clients.fetch_reservations) -> NightAuditReport:
    reservations = await fetch_reservations(property_id, date, date)
    total_bookings = len(reservations)
    check_ins = sum(1 for r in reservations if r.get("status") == "CHECKED_IN")
    check_outs = sum(1 for r in reservations if r.get("status") == "CHECKED_OUT")
    cancellations = sum(1 for r in reservations if r.get("status") == "CANCELLED")
    no_shows = sum(1 for r in reservations if r.get("status") == "NO_SHOW")
    return NightAuditReport(
        property_id=property_id,
        date=date,
        total_bookings=total_bookings,
        check_ins=check_ins,
        check_outs=check_outs,
        cancellations=cancellations,
        no_shows=no_shows,
    )
