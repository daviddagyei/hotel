import httpx
from typing import Optional

ROOM_SERVICE_URL = "http://localhost:8001/api/v1/room-service/rooms"
RESERVATION_SERVICE_URL = "http://localhost:8002/api/v1/reservations"
HOUSEKEEPING_SERVICE_URL = "http://localhost:8003/api/v1/tasks"

async def fetch_rooms(property_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{ROOM_SERVICE_URL}?property_id={property_id}")
        resp.raise_for_status()
        return resp.json()

async def fetch_reservations(property_id: int, start_date: Optional[str], end_date: Optional[str]):
    async with httpx.AsyncClient() as client:
        params = {"property_id": property_id}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        resp = await client.get(RESERVATION_SERVICE_URL, params=params)
        resp.raise_for_status()
        return resp.json()

async def fetch_tasks(property_id: int, start_date: Optional[str], end_date: Optional[str]):
    async with httpx.AsyncClient() as client:
        params = {"property_id": property_id}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        resp = await client.get(HOUSEKEEPING_SERVICE_URL, params=params)
        resp.raise_for_status()
        return resp.json()
