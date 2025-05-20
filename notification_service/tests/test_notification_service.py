import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from notification_service.app.main import app
from backend.core.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import Depends
from backend.auth_service.db import get_db

TEST_DB_FD, TEST_DB_PATH = tempfile.mkstemp(suffix='.db')
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True, scope="function")
def setup_and_teardown_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def override_get_db_fixture(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

client = TestClient(app)

def test_create_notification():
    data = {
        "property_id": 1,
        "type": "INFO",
        "message": "Room 101 cleaned",
        "recipient": "staff_1"
    }
    resp = client.post("/api/v1/notifications/", json=data)
    assert resp.status_code == 201
    notif = resp.json()
    assert notif["message"] == "Room 101 cleaned"
    assert notif["recipient"] == "staff_1"
    assert notif["is_read"] is False

def test_get_notification(db_session):
    data = {
        "property_id": 1,
        "type": "ALERT",
        "message": "VIP guest arrived",
        "recipient": "manager"
    }
    post = client.post("/api/v1/notifications/", json=data)
    notif_id = post.json()["id"]
    resp = client.get(f"/api/v1/notifications/{notif_id}")
    assert resp.status_code == 200
    notif = resp.json()
    assert notif["type"] == "ALERT"
    assert notif["recipient"] == "manager"

def test_list_notifications(db_session):
    data1 = {"property_id": 1, "type": "INFO", "message": "Task done", "recipient": "staff_2"}
    data2 = {"property_id": 1, "type": "ALERT", "message": "Fire drill", "recipient": "staff_2"}
    client.post("/api/v1/notifications/", json=data1)
    client.post("/api/v1/notifications/", json=data2)
    resp = client.get("/api/v1/notifications/?recipient=staff_2")
    assert resp.status_code == 200
    notifs = resp.json()
    assert len(notifs) >= 2
    assert any(n["message"] == "Task done" for n in notifs)
    assert any(n["message"] == "Fire drill" for n in notifs)

def test_mark_as_read(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "Check-in complete", "recipient": "frontdesk"}
    post = client.post("/api/v1/notifications/", json=data)
    notif_id = post.json()["id"]
    resp = client.patch(f"/api/v1/notifications/{notif_id}/read")
    assert resp.status_code == 200
    notif = resp.json()
    assert notif["is_read"] is True

def test_get_notification_not_found():
    resp = client.get("/api/v1/notifications/9999")
    assert resp.status_code == 404

def test_mark_as_read_not_found():
    resp = client.patch("/api/v1/notifications/9999/read")
    assert resp.status_code == 404

def teardown_module(module):
    os.close(TEST_DB_FD)
    os.unlink(TEST_DB_PATH)
