import pytest
from fastapi.testclient import TestClient
from backend.reservation_service.main import app
import requests

ROOM_SERVICE_URL = "http://localhost:8001/api/v1/room-service/rooms/"

@pytest.fixture(autouse=True)
def ensure_rooms_available():
    # Set test rooms to AVAILABLE before each test
    for room_id in [8, 9]:
        try:
            requests.patch(f"{ROOM_SERVICE_URL}{room_id}", json={"status": "AVAILABLE"}, timeout=2)
        except Exception:
            pass  # Ignore errors if room doesn't exist or service is down

client = TestClient(app)

# Helper: create a reservation payload

def make_payload(room_id, check_in, check_out, property_id=1, guest_id=1, price=100.0, payment_status="PAID"):
    return {
        "property_id": property_id,
        "guest_id": guest_id,
        "room_id": room_id,
        "check_in": check_in,
        "check_out": check_out,
        "price": price,
        "payment_status": payment_status
    }

def test_create_reservation_success():
    # Use a known available room (update room_id as needed)
    payload = make_payload(room_id=8, check_in="2025-05-21T14:00:00", check_out="2025-05-22T14:00:00")
    response = client.post("/api/v1/reservations", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["room_id"] == 8
    assert data["status"] == "BOOKED" or data["status"] == "OCCUPIED"

def test_create_reservation_room_not_available():
    # Reserve the room first
    payload = make_payload(room_id=8, check_in="2025-05-23T14:00:00", check_out="2025-05-24T14:00:00")
    client.post("/api/v1/reservations", json=payload)
    # Try to reserve again (should fail)
    response = client.post("/api/v1/reservations", json=payload)
    assert response.status_code == 400
    assert "not available" in response.json()["detail"].lower() or "not found" in response.json()["detail"].lower()

def test_create_reservation_room_not_found():
    payload = make_payload(room_id=9999, check_in="2025-05-21T14:00:00", check_out="2025-05-22T14:00:00")
    response = client.post("/api/v1/reservations", json=payload)
    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower()

def test_create_reservation_invalid_dates():
    payload = make_payload(room_id=8, check_in="2025-05-22T14:00:00", check_out="2025-05-21T14:00:00")
    response = client.post("/api/v1/reservations", json=payload)
    assert response.status_code == 400
    assert "check-in date must be before check-out date" in response.json()["detail"].lower()

def test_delete_reservation_sets_room_available():
    # Create a reservation
    payload = make_payload(room_id=9, check_in="2025-05-25T14:00:00", check_out="2025-05-26T14:00:00")
    response = client.post("/api/v1/reservations", json=payload)
    assert response.status_code == 200
    reservation_id = response.json()["id"]
    # Delete the reservation
    del_response = client.delete(f"/api/v1/reservations/{reservation_id}")
    assert del_response.status_code == 200
    # Try to reserve again (should succeed)
    response2 = client.post("/api/v1/reservations", json=payload)
    assert response2.status_code == 200

def test_create_reservation_past_dates():
    payload = make_payload(room_id=8, check_in="2020-01-01T14:00:00", check_out="2020-01-02T14:00:00")
    response = client.post("/api/v1/reservations", json=payload)
    assert response.status_code == 400
    assert "in the past" in response.json()["detail"].lower()

# Add more tests as needed for edge cases
