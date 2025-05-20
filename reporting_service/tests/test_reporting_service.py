import pytest
from reporting_service.app.services import reporting_service
import asyncio

@pytest.mark.asyncio
async def test_occupancy_report():
    async def mock_fetch_rooms(property_id):
        return [
            {"id": 1, "status": "OCCUPIED"},
            {"id": 2, "status": "AVAILABLE"},
            {"id": 3, "status": "OCCUPIED"},
        ]
    result = await reporting_service.get_occupancy_report(1, None, None, fetch_rooms=mock_fetch_rooms)
    assert result.total_rooms == 3
    assert result.occupied_rooms == 2
    assert 0.66 < result.occupancy_rate < 0.67

@pytest.mark.asyncio
@pytest.mark.parametrize("rooms,expected_total,expected_occupied,expected_rate", [
    ([], 0, 0, 0.0),
    ([{"id": 1, "status": "OCCUPIED"}], 1, 1, 1.0),
    ([{"id": 1, "status": "AVAILABLE"}], 1, 0, 0.0),
    ([{"id": 1, "status": "OCCUPIED"}, {"id": 2, "status": "OCCUPIED"}], 2, 2, 1.0),
    ([{"id": 1, "status": "OCCUPIED"}, {"id": 2, "status": "AVAILABLE"}], 2, 1, 0.5),
    ([{"id": 1, "status": "OCCUPIED"}, {"id": 2, "status": "OCCUPIED"}, {"id": 3, "status": "AVAILABLE"}], 3, 2, 2/3),
    ([{"id": 1, "status": "DIRTY"}], 1, 0, 0.0),
    ([{"id": 1, "status": "OCCUPIED"}, {"id": 2, "status": "DIRTY"}], 2, 1, 0.5),
    ([{"id": 1, "status": "OCCUPIED"}, {"id": 2, "status": "OCCUPIED"}, {"id": 3, "status": "OCCUPIED"}], 3, 3, 1.0),
    ([{"id": 1, "status": "AVAILABLE"}, {"id": 2, "status": "AVAILABLE"}], 2, 0, 0.0),
    ([{"id": 1, "status": "OCCUPIED"}, {"id": 2, "status": "OCCUPIED"}, {"id": 3, "status": "AVAILABLE"}, {"id": 4, "status": "DIRTY"}], 4, 2, 0.5),
    ([{"id": 1, "status": "OCCUPIED"}, {"id": 2, "status": "OCCUPIED"}, {"id": 3, "status": "OCCUPIED"}, {"id": 4, "status": "OCCUPIED"}], 4, 4, 1.0),
    ([{"id": 1, "status": "AVAILABLE"}, {"id": 2, "status": "DIRTY"}, {"id": 3, "status": "OCCUPIED"}], 3, 1, 1/3),
    ([{"id": 1, "status": "OCCUPIED"}, {"id": 2, "status": "AVAILABLE"}, {"id": 3, "status": "AVAILABLE"}], 3, 1, 1/3),
    ([{"id": 1, "status": "OCCUPIED"}, {"id": 2, "status": "OCCUPIED"}, {"id": 3, "status": "DIRTY"}, {"id": 4, "status": "AVAILABLE"}], 4, 2, 0.5),
    ([{"id": 1, "status": "OCCUPIED"}, {"id": 2, "status": "OCCUPIED"}, {"id": 3, "status": "OCCUPIED"}, {"id": 4, "status": "AVAILABLE"}], 4, 3, 0.75),
    ([{"id": 1, "status": "DIRTY"}, {"id": 2, "status": "DIRTY"}], 2, 0, 0.0),
    ([{"id": 1, "status": "OCCUPIED"}, {"id": 2, "status": "DIRTY"}, {"id": 3, "status": "AVAILABLE"}], 3, 1, 1/3),
    ([{"id": 1, "status": "OCCUPIED"}, {"id": 2, "status": "OCCUPIED"}, {"id": 3, "status": "OCCUPIED"}, {"id": 4, "status": "DIRTY"}, {"id": 5, "status": "AVAILABLE"}], 5, 3, 0.6),
    ([{"id": 1, "status": "OCCUPIED"}, {"id": 2, "status": "OCCUPIED"}, {"id": 3, "status": "AVAILABLE"}, {"id": 4, "status": "AVAILABLE"}, {"id": 5, "status": "DIRTY"}], 5, 2, 0.4),
])
async def test_occupancy_report_cases(rooms, expected_total, expected_occupied, expected_rate):
    async def mock_fetch_rooms(property_id):
        return rooms
    result = await reporting_service.get_occupancy_report(1, None, None, fetch_rooms=mock_fetch_rooms)
    assert result.total_rooms == expected_total
    assert result.occupied_rooms == expected_occupied
    assert pytest.approx(result.occupancy_rate, 0.01) == expected_rate

@pytest.mark.asyncio
async def test_task_history_report():
    async def mock_fetch_tasks(property_id, start_date, end_date):
        return [
            {"id": 1, "status": "COMPLETED"},
            {"id": 2, "status": "PENDING"},
        ]
    result = await reporting_service.get_task_history_report(1, None, None, fetch_tasks=mock_fetch_tasks)
    assert result.total_tasks == 2
    assert result.completed_tasks == 1
    assert result.pending_tasks == 1

@pytest.mark.asyncio
@pytest.mark.parametrize("tasks,expected_total,expected_completed,expected_pending", [
    ([], 0, 0, 0),
    ([{"id": 1, "status": "COMPLETED"}], 1, 1, 0),
    ([{"id": 1, "status": "PENDING"}], 1, 0, 1),
    ([{"id": 1, "status": "COMPLETED"}, {"id": 2, "status": "COMPLETED"}], 2, 2, 0),
    ([{"id": 1, "status": "PENDING"}, {"id": 2, "status": "PENDING"}], 2, 0, 2),
    ([{"id": 1, "status": "COMPLETED"}, {"id": 2, "status": "PENDING"}], 2, 1, 1),
    ([{"id": 1, "status": "COMPLETED"}, {"id": 2, "status": "IN_PROGRESS"}], 2, 1, 1),
    ([{"id": 1, "status": "IN_PROGRESS"}, {"id": 2, "status": "PENDING"}], 2, 0, 2),
    ([{"id": 1, "status": "COMPLETED"}, {"id": 2, "status": "COMPLETED"}, {"id": 3, "status": "PENDING"}], 3, 2, 1),
    ([{"id": 1, "status": "COMPLETED"}, {"id": 2, "status": "COMPLETED"}, {"id": 3, "status": "COMPLETED"}], 3, 3, 0),
    ([{"id": 1, "status": "PENDING"}, {"id": 2, "status": "IN_PROGRESS"}, {"id": 3, "status": "COMPLETED"}], 3, 1, 2),
    ([{"id": 1, "status": "IN_PROGRESS"}, {"id": 2, "status": "IN_PROGRESS"}], 2, 0, 2),
    ([{"id": 1, "status": "COMPLETED"}, {"id": 2, "status": "PENDING"}, {"id": 3, "status": "IN_PROGRESS"}], 3, 1, 2),
    ([{"id": 1, "status": "COMPLETED"}, {"id": 2, "status": "PENDING"}, {"id": 3, "status": "PENDING"}], 3, 1, 2),
    ([{"id": 1, "status": "PENDING"}, {"id": 2, "status": "PENDING"}, {"id": 3, "status": "PENDING"}], 3, 0, 3),
    ([{"id": 1, "status": "COMPLETED"}, {"id": 2, "status": "IN_PROGRESS"}, {"id": 3, "status": "IN_PROGRESS"}], 3, 1, 2),
    ([{"id": 1, "status": "IN_PROGRESS"}, {"id": 2, "status": "IN_PROGRESS"}, {"id": 3, "status": "IN_PROGRESS"}], 3, 0, 3),
    ([{"id": 1, "status": "COMPLETED"}, {"id": 2, "status": "COMPLETED"}, {"id": 3, "status": "IN_PROGRESS"}], 3, 2, 1),
    ([{"id": 1, "status": "COMPLETED"}, {"id": 2, "status": "PENDING"}, {"id": 3, "status": "COMPLETED"}], 3, 2, 1),
    ([{"id": 1, "status": "IN_PROGRESS"}, {"id": 2, "status": "COMPLETED"}, {"id": 3, "status": "PENDING"}], 3, 1, 2),
])
async def test_task_history_report_cases(tasks, expected_total, expected_completed, expected_pending):
    async def mock_fetch_tasks(property_id, start_date, end_date):
        return tasks
    result = await reporting_service.get_task_history_report(1, None, None, fetch_tasks=mock_fetch_tasks)
    assert result.total_tasks == expected_total
    assert result.completed_tasks == expected_completed
    assert result.pending_tasks == expected_pending

@pytest.mark.asyncio
async def test_night_audit_report():
    async def mock_fetch_reservations(property_id, start_date, end_date):
        return [
            {"id": 1, "status": "CHECKED_IN"},
            {"id": 2, "status": "CHECKED_OUT"},
            {"id": 3, "status": "CANCELLED"},
            {"id": 4, "status": "NO_SHOW"},
        ]
    result = await reporting_service.get_night_audit_report(1, "2025-05-19", fetch_reservations=mock_fetch_reservations)
    assert result.total_bookings == 4
    assert result.check_ins == 1
    assert result.check_outs == 1
    assert result.cancellations == 1
    assert result.no_shows == 1

@pytest.mark.asyncio
@pytest.mark.parametrize("reservations,expected_total,expected_checkins,expected_checkouts,expected_cancels,expected_noshows", [
    ([], 0, 0, 0, 0, 0),
    ([{"id": 1, "status": "CHECKED_IN"}], 1, 1, 0, 0, 0),
    ([{"id": 1, "status": "CHECKED_OUT"}], 1, 0, 1, 0, 0),
    ([{"id": 1, "status": "CANCELLED"}], 1, 0, 0, 1, 0),
    ([{"id": 1, "status": "NO_SHOW"}], 1, 0, 0, 0, 1),
    ([{"id": 1, "status": "CHECKED_IN"}, {"id": 2, "status": "CHECKED_OUT"}], 2, 1, 1, 0, 0),
    ([{"id": 1, "status": "CHECKED_IN"}, {"id": 2, "status": "CANCELLED"}], 2, 1, 0, 1, 0),
    ([{"id": 1, "status": "CHECKED_IN"}, {"id": 2, "status": "NO_SHOW"}], 2, 1, 0, 0, 1),
    ([{"id": 1, "status": "CHECKED_OUT"}, {"id": 2, "status": "CANCELLED"}], 2, 0, 1, 1, 0),
    ([{"id": 1, "status": "CHECKED_OUT"}, {"id": 2, "status": "NO_SHOW"}], 2, 0, 1, 0, 1),
    ([{"id": 1, "status": "CANCELLED"}, {"id": 2, "status": "NO_SHOW"}], 2, 0, 0, 1, 1),
    ([{"id": 1, "status": "CHECKED_IN"}, {"id": 2, "status": "CHECKED_OUT"}, {"id": 3, "status": "CANCELLED"}], 3, 1, 1, 1, 0),
    ([{"id": 1, "status": "CHECKED_IN"}, {"id": 2, "status": "CHECKED_OUT"}, {"id": 3, "status": "NO_SHOW"}], 3, 1, 1, 0, 1),
    ([{"id": 1, "status": "CHECKED_IN"}, {"id": 2, "status": "CANCELLED"}, {"id": 3, "status": "NO_SHOW"}], 3, 1, 0, 1, 1),
    ([{"id": 1, "status": "CHECKED_OUT"}, {"id": 2, "status": "CANCELLED"}, {"id": 3, "status": "NO_SHOW"}], 3, 0, 1, 1, 1),
    ([{"id": 1, "status": "CHECKED_IN"}, {"id": 2, "status": "CHECKED_OUT"}, {"id": 3, "status": "CANCELLED"}, {"id": 4, "status": "NO_SHOW"}], 4, 1, 1, 1, 1),
    ([{"id": 1, "status": "CHECKED_IN"}, {"id": 2, "status": "CHECKED_IN"}], 2, 2, 0, 0, 0),
    ([{"id": 1, "status": "CHECKED_OUT"}, {"id": 2, "status": "CHECKED_OUT"}], 2, 0, 2, 0, 0),
    ([{"id": 1, "status": "CANCELLED"}, {"id": 2, "status": "CANCELLED"}], 2, 0, 0, 2, 0),
    ([{"id": 1, "status": "NO_SHOW"}, {"id": 2, "status": "NO_SHOW"}], 2, 0, 0, 0, 2),
    ([{"id": 1, "status": "CHECKED_IN"}, {"id": 2, "status": "CHECKED_OUT"}, {"id": 3, "status": "CANCELLED"}, {"id": 4, "status": "NO_SHOW"}, {"id": 5, "status": "CHECKED_IN"}], 5, 2, 1, 1, 1),
])
async def test_night_audit_report_cases(reservations, expected_total, expected_checkins, expected_checkouts, expected_cancels, expected_noshows):
    async def mock_fetch_reservations(property_id, start_date, end_date):
        return reservations
    result = await reporting_service.get_night_audit_report(1, "2025-05-19", fetch_reservations=mock_fetch_reservations)
    assert result.total_bookings == expected_total
    assert result.check_ins == expected_checkins
    assert result.check_outs == expected_checkouts
    assert result.cancellations == expected_cancels
    assert result.no_shows == expected_noshows
