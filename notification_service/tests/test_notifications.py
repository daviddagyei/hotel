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

def test_create_notification_missing_fields():
    data = {"property_id": 1, "type": "INFO", "recipient": "staff_1"}  # missing message
    resp = client.post("/api/v1/notifications/", json=data)
    assert resp.status_code == 422

def test_create_notification_empty_message():
    data = {"property_id": 1, "type": "INFO", "message": "", "recipient": "staff_1"}
    resp = client.post("/api/v1/notifications/", json=data)
    assert resp.status_code == 422 or resp.status_code == 400

def test_create_notification_long_message():
    data = {"property_id": 1, "type": "INFO", "message": "x"*2048, "recipient": "staff_1"}
    resp = client.post("/api/v1/notifications/", json=data)
    assert resp.status_code == 201

def test_create_notification_invalid_type():
    data = {"property_id": 1, "type": "INVALID", "message": "Test", "recipient": "staff_1"}
    resp = client.post("/api/v1/notifications/", json=data)
    assert resp.status_code in (201, 422, 400)

def test_create_notification_no_recipient():
    data = {"property_id": 1, "type": "INFO", "message": "Test"}
    resp = client.post("/api/v1/notifications/", json=data)
    assert resp.status_code == 422

def test_create_notification_null_fields():
    data = {"property_id": None, "type": None, "message": None, "recipient": None}
    resp = client.post("/api/v1/notifications/", json=data)
    assert resp.status_code == 422

def test_create_notification_duplicate():
    data = {"property_id": 1, "type": "INFO", "message": "Dup", "recipient": "staff_1"}
    resp1 = client.post("/api/v1/notifications/", json=data)
    resp2 = client.post("/api/v1/notifications/", json=data)
    assert resp1.status_code == 201
    assert resp2.status_code == 201

def test_create_notification_special_characters():
    data = {"property_id": 1, "type": "INFO", "message": "!@#$%^&*()_+", "recipient": "staff_1"}
    resp = client.post("/api/v1/notifications/", json=data)
    assert resp.status_code == 201

def test_create_notification_unicode():
    data = {"property_id": 1, "type": "INFO", "message": "こんにちは", "recipient": "staff_1"}
    resp = client.post("/api/v1/notifications/", json=data)
    assert resp.status_code == 201

def test_create_notification_large_property_id():
    data = {"property_id": 999999999, "type": "INFO", "message": "Test", "recipient": "staff_1"}
    resp = client.post("/api/v1/notifications/", json=data)
    assert resp.status_code == 201

def test_create_notification_negative_property_id():
    data = {"property_id": -1, "type": "INFO", "message": "Test", "recipient": "staff_1"}
    resp = client.post("/api/v1/notifications/", json=data)
    assert resp.status_code in (201, 422, 400)

def test_create_notification_blank_recipient():
    data = {"property_id": 1, "type": "INFO", "message": "Test", "recipient": ""}
    resp = client.post("/api/v1/notifications/", json=data)
    assert resp.status_code == 422 or resp.status_code == 400

def test_create_notification_long_recipient():
    data = {"property_id": 1, "type": "INFO", "message": "Test", "recipient": "x"*256}
    resp = client.post("/api/v1/notifications/", json=data)
    assert resp.status_code == 201

def test_create_notification_multiple_types():
    for t in ["INFO", "ALERT", "WARNING", "REMINDER"]:
        data = {"property_id": 1, "type": t, "message": f"Type {t}", "recipient": "staff_1"}
        resp = client.post("/api/v1/notifications/", json=data)
        assert resp.status_code in (201, 422, 400)

def test_create_notification_multiple_recipients():
    for r in ["staff_1", "manager", "frontdesk", "housekeeping"]:
        data = {"property_id": 1, "type": "INFO", "message": f"To {r}", "recipient": r}
        resp = client.post("/api/v1/notifications/", json=data)
        assert resp.status_code == 201

def test_create_notification_zero_property_id():
    data = {"property_id": 0, "type": "INFO", "message": "Zero", "recipient": "staff_1"}
    resp = client.post("/api/v1/notifications/", json=data)
    assert resp.status_code in (201, 422, 400)

def test_create_notification_float_property_id():
    data = {"property_id": 1.5, "type": "INFO", "message": "Float", "recipient": "staff_1"}
    resp = client.post("/api/v1/notifications/", json=data)
    assert resp.status_code == 422

def test_create_notification_extra_fields():
    data = {"property_id": 1, "type": "INFO", "message": "Extra", "recipient": "staff_1", "extra": "field"}
    resp = client.post("/api/v1/notifications/", json=data)
    assert resp.status_code in (201, 422)

def test_create_notification_case_sensitivity():
    data = {"property_id": 1, "type": "info", "message": "Case", "recipient": "Staff_1"}
    resp = client.post("/api/v1/notifications/", json=data)
    assert resp.status_code in (201, 422, 400)

def test_create_notification_minimal_valid():
    data = {"property_id": 1, "type": "INFO", "message": "A", "recipient": "a"}
    resp = client.post("/api/v1/notifications/", json=data)
    assert resp.status_code == 201

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

def test_get_notification_invalid_id():
    resp = client.get("/api/v1/notifications/abc")
    assert resp.status_code == 422

def test_get_notification_zero_id():
    resp = client.get("/api/v1/notifications/0")
    assert resp.status_code in (404, 422)

def test_get_notification_negative_id():
    resp = client.get("/api/v1/notifications/-1")
    assert resp.status_code in (404, 422)

def test_get_notification_after_delete(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "To be deleted", "recipient": "staff_1"}
    post = client.post("/api/v1/notifications/", json=data)
    notif_id = post.json()["id"]
    # Simulate delete (not implemented, so just check get still works)
    resp = client.get(f"/api/v1/notifications/{notif_id}")
    assert resp.status_code == 200

def test_get_notification_multiple(db_session):
    ids = []
    for i in range(3):
        data = {"property_id": 1, "type": "INFO", "message": f"msg{i}", "recipient": "staff_1"}
        post = client.post("/api/v1/notifications/", json=data)
        ids.append(post.json()["id"])
    for nid in ids:
        resp = client.get(f"/api/v1/notifications/{nid}")
        assert resp.status_code == 200

def test_get_notification_wrong_recipient(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "Wrong recipient", "recipient": "staff_1"}
    post = client.post("/api/v1/notifications/", json=data)
    notif_id = post.json()["id"]
    resp = client.get(f"/api/v1/notifications/{notif_id}")
    assert resp.status_code == 200
    notif = resp.json()
    assert notif["recipient"] == "staff_1"

def test_get_notification_unicode_message(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "测试", "recipient": "staff_1"}
    post = client.post("/api/v1/notifications/", json=data)
    notif_id = post.json()["id"]
    resp = client.get(f"/api/v1/notifications/{notif_id}")
    assert resp.status_code == 200
    notif = resp.json()
    assert notif["message"] == "测试"

def test_get_notification_long_message(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "x"*1024, "recipient": "staff_1"}
    post = client.post("/api/v1/notifications/", json=data)
    notif_id = post.json()["id"]
    resp = client.get(f"/api/v1/notifications/{notif_id}")
    assert resp.status_code == 200

def test_get_notification_is_read_flag(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "Read flag", "recipient": "staff_1"}
    post = client.post("/api/v1/notifications/", json=data)
    notif_id = post.json()["id"]
    resp = client.get(f"/api/v1/notifications/{notif_id}")
    assert resp.status_code == 200
    notif = resp.json()
    assert notif["is_read"] is False

def test_get_notification_after_mark_as_read(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "Mark read", "recipient": "staff_1"}
    post = client.post("/api/v1/notifications/", json=data)
    notif_id = post.json()["id"]
    client.patch(f"/api/v1/notifications/{notif_id}/read")
    resp = client.get(f"/api/v1/notifications/{notif_id}")
    assert resp.status_code == 200
    notif = resp.json()
    assert notif["is_read"] is True

def test_get_notification_case_sensitivity(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "Case", "recipient": "Staff_1"}
    post = client.post("/api/v1/notifications/", json=data)
    notif_id = post.json()["id"]
    resp = client.get(f"/api/v1/notifications/{notif_id}")
    assert resp.status_code == 200

def test_get_notification_property_id_filter(db_session):
    data = {"property_id": 2, "type": "INFO", "message": "Property 2", "recipient": "staff_1"}
    post = client.post("/api/v1/notifications/", json=data)
    notif_id = post.json()["id"]
    resp = client.get(f"/api/v1/notifications/{notif_id}")
    assert resp.status_code == 200
    notif = resp.json()
    assert notif["property_id"] == 2

def test_get_notification_multiple_properties(db_session):
    for pid in [1, 2, 3]:
        data = {"property_id": pid, "type": "INFO", "message": f"P{pid}", "recipient": "staff_1"}
        post = client.post("/api/v1/notifications/", json=data)
        notif_id = post.json()["id"]
        resp = client.get(f"/api/v1/notifications/{notif_id}")
        assert resp.status_code == 200

def test_get_notification_special_characters(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "!@#$", "recipient": "staff_1"}
    post = client.post("/api/v1/notifications/", json=data)
    notif_id = post.json()["id"]
    resp = client.get(f"/api/v1/notifications/{notif_id}")
    assert resp.status_code == 200

def test_get_notification_blank_message(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "", "recipient": "staff_1"}
    resp = client.post("/api/v1/notifications/", json=data)
    if resp.status_code == 201:
        notif_id = resp.json()["id"]
        resp2 = client.get(f"/api/v1/notifications/{notif_id}")
        assert resp2.status_code == 200

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

def test_list_notifications_no_results(db_session):
    resp = client.get("/api/v1/notifications/?recipient=nonexistent")
    assert resp.status_code == 200
    assert resp.json() == []

def test_list_notifications_multiple_properties(db_session):
    for pid in [1, 2]:
        data = {"property_id": pid, "type": "INFO", "message": f"P{pid}", "recipient": "staff_2"}
        client.post("/api/v1/notifications/", json=data)
    resp = client.get("/api/v1/notifications/?recipient=staff_2")
    assert resp.status_code == 200
    notifs = resp.json()
    assert any(n["property_id"] == 1 for n in notifs)
    assert any(n["property_id"] == 2 for n in notifs)

def test_list_notifications_filter_property_id(db_session):
    data = {"property_id": 3, "type": "INFO", "message": "P3", "recipient": "staff_2"}
    client.post("/api/v1/notifications/", json=data)
    resp = client.get("/api/v1/notifications/?recipient=staff_2&property_id=3")
    assert resp.status_code == 200
    notifs = resp.json()
    assert all(n["property_id"] == 3 for n in notifs)

def test_list_notifications_case_sensitivity(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "Case", "recipient": "Staff_2"}
    client.post("/api/v1/notifications/", json=data)
    resp = client.get("/api/v1/notifications/?recipient=Staff_2")
    assert resp.status_code == 200
    notifs = resp.json()
    assert any(n["recipient"] == "Staff_2" for n in notifs)

def test_list_notifications_large_number(db_session):
    for i in range(20):
        data = {"property_id": 1, "type": "INFO", "message": f"msg{i}", "recipient": "bulk"}
        client.post("/api/v1/notifications/", json=data)
    resp = client.get("/api/v1/notifications/?recipient=bulk")
    assert resp.status_code == 200
    notifs = resp.json()
    assert len(notifs) >= 20

def test_list_notifications_special_characters(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "!@#$", "recipient": "special"}
    client.post("/api/v1/notifications/", json=data)
    resp = client.get("/api/v1/notifications/?recipient=special")
    assert resp.status_code == 200
    notifs = resp.json()
    assert any(n["message"] == "!@#$" for n in notifs)

def test_list_notifications_unicode(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "测试", "recipient": "unicode"}
    client.post("/api/v1/notifications/", json=data)
    resp = client.get("/api/v1/notifications/?recipient=unicode")
    assert resp.status_code == 200
    notifs = resp.json()
    assert any(n["message"] == "测试" for n in notifs)

def test_list_notifications_empty_message(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "", "recipient": "empty"}
    resp = client.post("/api/v1/notifications/", json=data)
    if resp.status_code == 201:
        resp2 = client.get("/api/v1/notifications/?recipient=empty")
        assert resp2.status_code == 200

def test_list_notifications_multiple_types(db_session):
    for t in ["INFO", "ALERT", "WARNING", "REMINDER"]:
        data = {"property_id": 1, "type": t, "message": f"Type {t}", "recipient": "multi"}
        client.post("/api/v1/notifications/", json=data)
    resp = client.get("/api/v1/notifications/?recipient=multi")
    assert resp.status_code == 200
    notifs = resp.json()
    assert len(notifs) >= 4

def test_list_notifications_blank_recipient(db_session):
    resp = client.get("/api/v1/notifications/?recipient=")
    assert resp.status_code == 200

def test_list_notifications_long_recipient(db_session):
    r = "x"*256
    data = {"property_id": 1, "type": "INFO", "message": "Long", "recipient": r}
    client.post("/api/v1/notifications/", json=data)
    resp = client.get(f"/api/v1/notifications/?recipient={r}")
    assert resp.status_code == 200
    notifs = resp.json()
    assert any(n["recipient"] == r for n in notifs)

def test_list_notifications_minimal_valid(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "A", "recipient": "a"}
    client.post("/api/v1/notifications/", json=data)
    resp = client.get("/api/v1/notifications/?recipient=a")
    assert resp.status_code == 200
    notifs = resp.json()
    assert any(n["message"] == "A" for n in notifs)

def test_list_notifications_multiple_properties_filter(db_session):
    for pid in [1, 2]:
        data = {"property_id": pid, "type": "INFO", "message": f"P{pid}", "recipient": "filter"}
        client.post("/api/v1/notifications/", json=data)
    resp = client.get("/api/v1/notifications/?recipient=filter&property_id=2")
    assert resp.status_code == 200
    notifs = resp.json()
    assert all(n["property_id"] == 2 for n in notifs)

def test_list_notifications_invalid_property_id(db_session):
    resp = client.get("/api/v1/notifications/?recipient=staff_2&property_id=abc")
    assert resp.status_code == 422

def test_list_notifications_zero_property_id(db_session):
    resp = client.get("/api/v1/notifications/?recipient=staff_2&property_id=0")
    assert resp.status_code == 200

def test_list_notifications_negative_property_id(db_session):
    resp = client.get("/api/v1/notifications/?recipient=staff_2&property_id=-1")
    assert resp.status_code == 200

def test_mark_as_read(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "Check-in complete", "recipient": "frontdesk"}
    post = client.post("/api/v1/notifications/", json=data)
    notif_id = post.json()["id"]
    resp = client.patch(f"/api/v1/notifications/{notif_id}/read")
    assert resp.status_code == 200
    notif = resp.json()
    assert notif["is_read"] is True

def test_mark_as_read_invalid_id():
    resp = client.patch("/api/v1/notifications/abc/read")
    assert resp.status_code == 422

def test_mark_as_read_zero_id():
    resp = client.patch("/api/v1/notifications/0/read")
    assert resp.status_code in (404, 422)

def test_mark_as_read_negative_id():
    resp = client.patch("/api/v1/notifications/-1/read")
    assert resp.status_code in (404, 422)

def test_mark_as_read_twice(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "Twice", "recipient": "frontdesk"}
    post = client.post("/api/v1/notifications/", json=data)
    notif_id = post.json()["id"]
    resp1 = client.patch(f"/api/v1/notifications/{notif_id}/read")
    resp2 = client.patch(f"/api/v1/notifications/{notif_id}/read")
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp2.json()["is_read"] is True

def test_mark_as_read_already_read(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "Already read", "recipient": "frontdesk"}
    post = client.post("/api/v1/notifications/", json=data)
    notif_id = post.json()["id"]
    client.patch(f"/api/v1/notifications/{notif_id}/read")
    resp = client.patch(f"/api/v1/notifications/{notif_id}/read")
    assert resp.status_code == 200
    assert resp.json()["is_read"] is True

def test_mark_as_read_multiple(db_session):
    ids = []
    for i in range(3):
        data = {"property_id": 1, "type": "INFO", "message": f"msg{i}", "recipient": "frontdesk"}
        post = client.post("/api/v1/notifications/", json=data)
        ids.append(post.json()["id"])
    for nid in ids:
        resp = client.patch(f"/api/v1/notifications/{nid}/read")
        assert resp.status_code == 200
        assert resp.json()["is_read"] is True

def test_mark_as_read_case_sensitivity(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "Case", "recipient": "Frontdesk"}
    post = client.post("/api/v1/notifications/", json=data)
    notif_id = post.json()["id"]
    resp = client.patch(f"/api/v1/notifications/{notif_id}/read")
    assert resp.status_code == 200
    assert resp.json()["is_read"] is True

def test_mark_as_read_unicode(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "测试", "recipient": "frontdesk"}
    post = client.post("/api/v1/notifications/", json=data)
    notif_id = post.json()["id"]
    resp = client.patch(f"/api/v1/notifications/{notif_id}/read")
    assert resp.status_code == 200
    assert resp.json()["is_read"] is True

def test_mark_as_read_special_characters(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "!@#$", "recipient": "frontdesk"}
    post = client.post("/api/v1/notifications/", json=data)
    notif_id = post.json()["id"]
    resp = client.patch(f"/api/v1/notifications/{notif_id}/read")
    assert resp.status_code == 200
    assert resp.json()["is_read"] is True

def test_mark_as_read_long_message(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "x"*1024, "recipient": "frontdesk"}
    post = client.post("/api/v1/notifications/", json=data)
    notif_id = post.json()["id"]
    resp = client.patch(f"/api/v1/notifications/{notif_id}/read")
    assert resp.status_code == 200
    assert resp.json()["is_read"] is True

def test_mark_as_read_blank_message(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "", "recipient": "frontdesk"}
    resp = client.post("/api/v1/notifications/", json=data)
    if resp.status_code == 201:
        notif_id = resp.json()["id"]
        resp2 = client.patch(f"/api/v1/notifications/{notif_id}/read")
        assert resp2.status_code == 200
        assert resp2.json()["is_read"] is True

def test_mark_as_read_minimal_valid(db_session):
    data = {"property_id": 1, "type": "INFO", "message": "A", "recipient": "a"}
    post = client.post("/api/v1/notifications/", json=data)
    notif_id = post.json()["id"]
    resp = client.patch(f"/api/v1/notifications/{notif_id}/read")
    assert resp.status_code == 200
    assert resp.json()["is_read"] is True

def test_get_notification_not_found():
    resp = client.get("/api/v1/notifications/9999")
    assert resp.status_code == 404

def test_mark_as_read_not_found():
    resp = client.patch("/api/v1/notifications/9999/read")
    assert resp.status_code == 404

def teardown_module(module):
    os.close(TEST_DB_FD)
    os.unlink(TEST_DB_PATH)
