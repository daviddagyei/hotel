from backend.housekeeping_service.models import test_stubs  # Ensure FK tables exist for tests
import pytest
from fastapi.testclient import TestClient
from backend.housekeeping_service.main import app
from backend.housekeeping_service.db import get_db
from backend.core.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile

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

def test_create_task():
    data = {
        "property_id": 1,
        "task_type": "HOUSEKEEPING",
        "room_id": 101,
        "description": "Clean Room 101",
        "assigned_to": 1
    }
    response = client.post("/api/v1/tasks/", json=data)
    assert response.status_code == 201
    task = response.json()
    assert task["task_type"] == "HOUSEKEEPING"
    assert task["description"] == "Clean Room 101"

def test_create_task_missing_property_id():
    data = {
        "task_type": "HOUSEKEEPING",
        "room_id": 101,
        "description": "Clean Room 101",
        "assigned_to": 1
    }
    response = client.post("/api/v1/tasks/", json=data)
    assert response.status_code == 422

def test_create_task_invalid_task_type():
    data = {
        "property_id": 1,
        "task_type": "INVALID",
        "room_id": 101,
        "description": "Invalid type",
        "assigned_to": 1
    }
    response = client.post("/api/v1/tasks/", json=data)
    assert response.status_code == 422

def test_create_task_long_description():
    data = {
        "property_id": 1,
        "task_type": "HOUSEKEEPING",
        "room_id": 101,
        "description": "A"*1000,
        "assigned_to": 1
    }
    response = client.post("/api/v1/tasks/", json=data)
    assert response.status_code == 201
    assert response.json()["description"] == "A"*1000

def test_create_task_empty_description():
    data = {
        "property_id": 1,
        "task_type": "HOUSEKEEPING",
        "room_id": 101,
        "description": "",
        "assigned_to": 1
    }
    response = client.post("/api/v1/tasks/", json=data)
    assert response.status_code == 201
    assert response.json()["description"] == ""

def test_create_task_null_room_id():
    data = {
        "property_id": 1,
        "task_type": "MAINTENANCE",
        "room_id": None,
        "description": "General maintenance",
        "assigned_to": 1
    }
    response = client.post("/api/v1/tasks/", json=data)
    assert response.status_code == 201
    assert response.json()["room_id"] is None

def test_create_task_future_scheduled_time():
    from datetime import datetime, timedelta
    future_time = (datetime.utcnow() + timedelta(days=1)).isoformat()
    data = {
        "property_id": 1,
        "task_type": "HOUSEKEEPING",
        "room_id": 101,
        "description": "Scheduled cleaning",
        "assigned_to": 1,
        "scheduled_time": future_time
    }
    response = client.post("/api/v1/tasks/", json=data)
    assert response.status_code == 201
    assert "scheduled_time" in response.json()

def test_create_task_past_scheduled_time():
    from datetime import datetime, timedelta
    past_time = (datetime.utcnow() - timedelta(days=1)).isoformat()
    data = {
        "property_id": 1,
        "task_type": "HOUSEKEEPING",
        "room_id": 101,
        "description": "Past cleaning",
        "assigned_to": 1,
        "scheduled_time": past_time
    }
    response = client.post("/api/v1/tasks/", json=data)
    assert response.status_code == 201
    assert "scheduled_time" in response.json()

def test_create_task_invalid_status():
    data = {
        "property_id": 1,
        "task_type": "HOUSEKEEPING",
        "room_id": 101,
        "description": "Invalid status",
        "assigned_to": 1,
        "status": "INVALID"
    }
    response = client.post("/api/v1/tasks/", json=data)
    assert response.status_code == 422

def test_create_task_missing_task_type():
    data = {
        "property_id": 1,
        "room_id": 101,
        "description": "No type",
        "assigned_to": 1
    }
    response = client.post("/api/v1/tasks/", json=data)
    assert response.status_code == 422

def test_create_task_missing_all_fields():
    data = {}
    response = client.post("/api/v1/tasks/", json=data)
    assert response.status_code == 422

def test_create_task_minimal():
    data = {
        "property_id": 1,
        "task_type": "HOUSEKEEPING"
    }
    response = client.post("/api/v1/tasks/", json=data)
    assert response.status_code == 201
    assert response.json()["property_id"] == 1
    assert response.json()["task_type"] == "HOUSEKEEPING"

def test_create_task_max_int_property_id():
    data = {
        "property_id": 2**31-1,
        "task_type": "MAINTENANCE"
    }
    response = client.post("/api/v1/tasks/", json=data)
    assert response.status_code == 201
    assert response.json()["property_id"] == 2**31-1

def test_create_task_zero_property_id():
    data = {
        "property_id": 0,
        "task_type": "MAINTENANCE"
    }
    response = client.post("/api/v1/tasks/", json=data)
    assert response.status_code == 201
    assert response.json()["property_id"] == 0

def test_create_task_negative_property_id():
    data = {
        "property_id": -1,
        "task_type": "MAINTENANCE"
    }
    response = client.post("/api/v1/tasks/", json=data)
    assert response.status_code == 201
    assert response.json()["property_id"] == -1

def test_create_task_unicode_description():
    data = {
        "property_id": 1,
        "task_type": "HOUSEKEEPING",
        "description": "清洁房间"
    }
    response = client.post("/api/v1/tasks/", json=data)
    assert response.status_code == 201
    assert response.json()["description"] == "清洁房间"

def test_create_task_large_room_id():
    data = {
        "property_id": 1,
        "task_type": "HOUSEKEEPING",
        "room_id": 999999999,
        "description": "Big room id"
    }
    response = client.post("/api/v1/tasks/", json=data)
    assert response.status_code == 201
    assert response.json()["room_id"] == 999999999

def test_create_task_duplicate():
    data = {
        "property_id": 1,
        "task_type": "HOUSEKEEPING",
        "room_id": 101,
        "description": "Duplicate",
        "assigned_to": 1
    }
    response1 = client.post("/api/v1/tasks/", json=data)
    response2 = client.post("/api/v1/tasks/", json=data)
    assert response1.status_code == 201
    assert response2.status_code == 201

def test_create_task_with_all_fields():
    from datetime import datetime
    data = {
        "property_id": 1,
        "task_type": "MAINTENANCE",
        "room_id": 101,
        "description": "All fields",
        "assigned_to": 1,
        "scheduled_time": datetime.utcnow().isoformat()
    }
    response = client.post("/api/v1/tasks/", json=data)
    assert response.status_code == 201
    assert response.json()["task_type"] == "MAINTENANCE"

def test_list_tasks():
    data = {
        "property_id": 1,
        "task_type": "HOUSEKEEPING",
        "room_id": 101,
        "description": "Clean Room 101",
        "assigned_to": 1
    }
    client.post("/api/v1/tasks/", json=data)
    resp = client.get("/api/v1/tasks/")
    assert resp.status_code == 200
    tasks = resp.json()
    assert len(tasks) >= 1

def test_list_tasks_empty():
    resp = client.get("/api/v1/tasks/")
    assert resp.status_code == 200
    assert resp.json() == []

def test_list_tasks_by_property():
    data1 = {"property_id": 1, "task_type": "HOUSEKEEPING"}
    data2 = {"property_id": 2, "task_type": "MAINTENANCE"}
    client.post("/api/v1/tasks/", json=data1)
    client.post("/api/v1/tasks/", json=data2)
    resp = client.get("/api/v1/tasks/?property_id=1")
    assert resp.status_code == 200
    assert all(t["property_id"] == 1 for t in resp.json())

def test_list_tasks_by_status():
    data = {"property_id": 1, "task_type": "HOUSEKEEPING"}
    post = client.post("/api/v1/tasks/", json=data)
    task_id = post.json()["id"]
    client.patch(f"/api/v1/tasks/{task_id}", json={"status": "DONE"})
    resp = client.get("/api/v1/tasks/?status=DONE")
    assert resp.status_code == 200
    assert any(t["status"] == "DONE" for t in resp.json())

def test_list_tasks_by_assigned_to():
    data = {"property_id": 1, "task_type": "HOUSEKEEPING", "assigned_to": 42}
    client.post("/api/v1/tasks/", json=data)
    resp = client.get("/api/v1/tasks/?assigned_to=42")
    assert resp.status_code == 200
    assert all(t["assigned_to"] == 42 for t in resp.json())

def test_list_tasks_multiple_filters():
    data = {"property_id": 1, "task_type": "HOUSEKEEPING", "assigned_to": 99}
    client.post("/api/v1/tasks/", json=data)
    resp = client.get("/api/v1/tasks/?property_id=1&assigned_to=99")
    assert resp.status_code == 200
    assert all(t["property_id"] == 1 and t["assigned_to"] == 99 for t in resp.json())

def test_list_tasks_large_set():
    for i in range(20):
        client.post("/api/v1/tasks/", json={"property_id": 1, "task_type": "HOUSEKEEPING", "room_id": i})
    resp = client.get("/api/v1/tasks/")
    assert resp.status_code == 200
    assert len(resp.json()) >= 20

def test_list_tasks_status_pending():
    client.post("/api/v1/tasks/", json={"property_id": 1, "task_type": "HOUSEKEEPING"})
    resp = client.get("/api/v1/tasks/?status=PENDING")
    assert resp.status_code == 200
    assert all(t["status"] == "PENDING" for t in resp.json())

def test_list_tasks_status_done_none():
    resp = client.get("/api/v1/tasks/?status=DONE")
    assert resp.status_code == 200
    assert resp.json() == []

def test_list_tasks_by_nonexistent_property():
    resp = client.get("/api/v1/tasks/?property_id=9999")
    assert resp.status_code == 200
    assert resp.json() == []

def test_list_tasks_by_nonexistent_assigned_to():
    resp = client.get("/api/v1/tasks/?assigned_to=9999")
    assert resp.status_code == 200
    assert resp.json() == []

def test_list_tasks_by_nonexistent_status():
    resp = client.get("/api/v1/tasks/?status=IN_PROGRESS")
    assert resp.status_code == 200
    assert resp.json() == []

def test_list_tasks_combined_filters_none():
    resp = client.get("/api/v1/tasks/?property_id=1&assigned_to=9999&status=DONE")
    assert resp.status_code == 200
    assert resp.json() == []

def test_list_tasks_unicode_description():
    client.post("/api/v1/tasks/", json={"property_id": 1, "task_type": "HOUSEKEEPING", "description": "清洁"})
    resp = client.get("/api/v1/tasks/")
    assert resp.status_code == 200
    assert any("清洁" in t["description"] for t in resp.json() if t["description"])

def test_list_tasks_long_description():
    desc = "A"*500
    client.post("/api/v1/tasks/", json={"property_id": 1, "task_type": "HOUSEKEEPING", "description": desc})
    resp = client.get("/api/v1/tasks/")
    assert resp.status_code == 200
    assert any(t["description"] == desc for t in resp.json())

def test_list_tasks_room_id():
    client.post("/api/v1/tasks/", json={"property_id": 1, "task_type": "HOUSEKEEPING", "room_id": 123})
    resp = client.get("/api/v1/tasks/")
    assert resp.status_code == 200
    assert any(t["room_id"] == 123 for t in resp.json())

def test_list_tasks_no_room_id():
    client.post("/api/v1/tasks/", json={"property_id": 1, "task_type": "MAINTENANCE"})
    resp = client.get("/api/v1/tasks/")
    assert resp.status_code == 200
    assert any(t["room_id"] is None for t in resp.json())

def test_list_tasks_all_fields():
    from datetime import datetime
    client.post("/api/v1/tasks/", json={"property_id": 1, "task_type": "MAINTENANCE", "room_id": 1, "description": "desc", "assigned_to": 1, "scheduled_time": datetime.utcnow().isoformat()})
    resp = client.get("/api/v1/tasks/")
    assert resp.status_code == 200
    assert any(t["task_type"] == "MAINTENANCE" and t["assigned_to"] == 1 for t in resp.json())

def test_update_task():
    data = {
        "property_id": 1,
        "task_type": "HOUSEKEEPING",
        "room_id": 101,
        "description": "Clean Room 101",
        "assigned_to": 1
    }
    post = client.post("/api/v1/tasks/", json=data)
    task_id = post.json()["id"]
    update = {"status": "DONE"}
    resp = client.patch(f"/api/v1/tasks/{task_id}", json=update)
    assert resp.status_code == 200
    task = resp.json()
    assert task["status"] == "DONE"

def test_update_task_status_in_progress():
    data = {"property_id": 1, "task_type": "HOUSEKEEPING"}
    post = client.post("/api/v1/tasks/", json=data)
    task_id = post.json()["id"]
    resp = client.patch(f"/api/v1/tasks/{task_id}", json={"status": "IN_PROGRESS"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "IN_PROGRESS"

def test_update_task_status_done():
    data = {"property_id": 1, "task_type": "HOUSEKEEPING"}
    post = client.post("/api/v1/tasks/", json=data)
    task_id = post.json()["id"]
    resp = client.patch(f"/api/v1/tasks/{task_id}", json={"status": "DONE"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "DONE"

def test_update_task_description():
    data = {"property_id": 1, "task_type": "HOUSEKEEPING", "description": "old"}
    post = client.post("/api/v1/tasks/", json=data)
    task_id = post.json()["id"]
    resp = client.patch(f"/api/v1/tasks/{task_id}", json={"description": "new desc"})
    assert resp.status_code == 200
    assert resp.json()["description"] == "new desc"

def test_update_task_assigned_to():
    data = {"property_id": 1, "task_type": "HOUSEKEEPING"}
    post = client.post("/api/v1/tasks/", json=data)
    task_id = post.json()["id"]
    resp = client.patch(f"/api/v1/tasks/{task_id}", json={"assigned_to": 123})
    assert resp.status_code == 200
    assert resp.json()["assigned_to"] == 123

def test_update_task_scheduled_time():
    from datetime import datetime, timedelta
    data = {"property_id": 1, "task_type": "HOUSEKEEPING"}
    post = client.post("/api/v1/tasks/", json=data)
    task_id = post.json()["id"]
    new_time = (datetime.utcnow() + timedelta(days=2)).isoformat()
    resp = client.patch(f"/api/v1/tasks/{task_id}", json={"scheduled_time": new_time})
    assert resp.status_code == 200
    assert "scheduled_time" in resp.json()

def test_update_task_multiple_fields():
    data = {"property_id": 1, "task_type": "HOUSEKEEPING"}
    post = client.post("/api/v1/tasks/", json=data)
    task_id = post.json()["id"]
    resp = client.patch(f"/api/v1/tasks/{task_id}", json={"status": "DONE", "description": "done desc"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "DONE"
    assert resp.json()["description"] == "done desc"

def test_update_task_noop():
    data = {"property_id": 1, "task_type": "HOUSEKEEPING"}
    post = client.post("/api/v1/tasks/", json=data)
    task_id = post.json()["id"]
    resp = client.patch(f"/api/v1/tasks/{task_id}", json={})
    assert resp.status_code == 200

def test_update_task_not_found():
    resp = client.patch(f"/api/v1/tasks/9999", json={"status": "DONE"})
    assert resp.status_code == 404

def test_update_task_invalid_status():
    data = {"property_id": 1, "task_type": "HOUSEKEEPING"}
    post = client.post("/api/v1/tasks/", json=data)
    task_id = post.json()["id"]
    resp = client.patch(f"/api/v1/tasks/{task_id}", json={"status": "INVALID"})
    assert resp.status_code == 422

def test_update_task_invalid_field():
    data = {"property_id": 1, "task_type": "HOUSEKEEPING"}
    post = client.post("/api/v1/tasks/", json=data)
    task_id = post.json()["id"]
    resp = client.patch(f"/api/v1/tasks/{task_id}", json={"not_a_field": "value"})
    assert resp.status_code == 200

def test_update_task_long_description():
    data = {"property_id": 1, "task_type": "HOUSEKEEPING"}
    post = client.post("/api/v1/tasks/", json=data)
    task_id = post.json()["id"]
    desc = "A"*1000
    resp = client.patch(f"/api/v1/tasks/{task_id}", json={"description": desc})
    assert resp.status_code == 200
    assert resp.json()["description"] == desc

def test_update_task_unicode_description():
    data = {"property_id": 1, "task_type": "HOUSEKEEPING"}
    post = client.post("/api/v1/tasks/", json=data)
    task_id = post.json()["id"]
    resp = client.patch(f"/api/v1/tasks/{task_id}", json={"description": "清洁"})
    assert resp.status_code == 200
    assert resp.json()["description"] == "清洁"

def test_update_task_assigned_to_none():
    data = {"property_id": 1, "task_type": "HOUSEKEEPING", "assigned_to": 1}
    post = client.post("/api/v1/tasks/", json=data)
    task_id = post.json()["id"]
    resp = client.patch(f"/api/v1/tasks/{task_id}", json={"assigned_to": None})
    assert resp.status_code == 200
    assert resp.json()["assigned_to"] is None

def test_update_task_room_id():
    data = {"property_id": 1, "task_type": "HOUSEKEEPING", "room_id": 1}
    post = client.post("/api/v1/tasks/", json=data)
    task_id = post.json()["id"]
    resp = client.patch(f"/api/v1/tasks/{task_id}", json={"room_id": 2})
    assert resp.status_code == 200
    assert resp.json()["room_id"] == 2

def test_update_task_room_id_none():
    data = {"property_id": 1, "task_type": "HOUSEKEEPING", "room_id": 1}
    post = client.post("/api/v1/tasks/", json=data)
    task_id = post.json()["id"]
    resp = client.patch(f"/api/v1/tasks/{task_id}", json={"room_id": None})
    assert resp.status_code == 200
    assert resp.json()["room_id"] is None

def test_update_task_all_fields():
    from datetime import datetime
    data = {"property_id": 1, "task_type": "MAINTENANCE"}
    post = client.post("/api/v1/tasks/", json=data)
    task_id = post.json()["id"]
    resp = client.patch(f"/api/v1/tasks/{task_id}", json={"status": "DONE", "description": "desc", "assigned_to": 1, "scheduled_time": datetime.utcnow().isoformat()})
    assert resp.status_code == 200
    assert resp.json()["status"] == "DONE"
    assert resp.json()["assigned_to"] == 1

def test_delete_task():
    data = {
        "property_id": 1,
        "task_type": "HOUSEKEEPING",
        "room_id": 101,
        "description": "Clean Room 101",
        "assigned_to": 1
    }
    post = client.post("/api/v1/tasks/", json=data)
    task_id = post.json()["id"]
    resp = client.delete(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 204

def test_delete_task_not_found():
    resp = client.delete("/api/v1/tasks/9999")
    assert resp.status_code == 404

def test_delete_task_twice():
    data = {"property_id": 1, "task_type": "HOUSEKEEPING"}
    post = client.post("/api/v1/tasks/", json=data)
    task_id = post.json()["id"]
    resp1 = client.delete(f"/api/v1/tasks/{task_id}")
    resp2 = client.delete(f"/api/v1/tasks/{task_id}")
    assert resp1.status_code == 204
    assert resp2.status_code == 404

def test_delete_task_and_recreate():
    data = {"property_id": 1, "task_type": "HOUSEKEEPING"}
    post = client.post("/api/v1/tasks/", json=data)
    task_id = post.json()["id"]
    resp = client.delete(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 204
    # Recreate
    post2 = client.post("/api/v1/tasks/", json=data)
    assert post2.status_code == 201

def test_delete_task_with_all_fields():
    from datetime import datetime
    data = {"property_id": 1, "task_type": "MAINTENANCE", "room_id": 1, "description": "desc", "assigned_to": 1, "scheduled_time": datetime.utcnow().isoformat()}
    post = client.post("/api/v1/tasks/", json=data)
    task_id = post.json()["id"]
    resp = client.delete(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 204

def test_delete_task_multiple():
    ids = []
    for i in range(5):
        post = client.post("/api/v1/tasks/", json={"property_id": 1, "task_type": "HOUSEKEEPING", "room_id": i})
        ids.append(post.json()["id"])
    for task_id in ids:
        resp = client.delete(f"/api/v1/tasks/{task_id}")
        assert resp.status_code == 204

def test_delete_task_then_list():
    post = client.post("/api/v1/tasks/", json={"property_id": 1, "task_type": "HOUSEKEEPING"})
    task_id = post.json()["id"]
    client.delete(f"/api/v1/tasks/{task_id}")
    resp = client.get("/api/v1/tasks/")
    assert all(t["id"] != task_id for t in resp.json())

def test_delete_task_unicode():
    post = client.post("/api/v1/tasks/", json={"property_id": 1, "task_type": "HOUSEKEEPING", "description": "清洁"})
    task_id = post.json()["id"]
    resp = client.delete(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 204

def test_delete_task_long_description():
    desc = "A"*1000
    post = client.post("/api/v1/tasks/", json={"property_id": 1, "task_type": "HOUSEKEEPING", "description": desc})
    task_id = post.json()["id"]
    resp = client.delete(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 204

def test_delete_task_with_room_id():
    post = client.post("/api/v1/tasks/", json={"property_id": 1, "task_type": "HOUSEKEEPING", "room_id": 123})
    task_id = post.json()["id"]
    resp = client.delete(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 204

def test_delete_task_with_assigned_to():
    post = client.post("/api/v1/tasks/", json={"property_id": 1, "task_type": "HOUSEKEEPING", "assigned_to": 42})
    task_id = post.json()["id"]
    resp = client.delete(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 204

def test_delete_task_with_scheduled_time():
    from datetime import datetime
    post = client.post("/api/v1/tasks/", json={"property_id": 1, "task_type": "HOUSEKEEPING", "scheduled_time": datetime.utcnow().isoformat()})
    task_id = post.json()["id"]
    resp = client.delete(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 204

def test_delete_task_and_readd():
    post = client.post("/api/v1/tasks/", json={"property_id": 1, "task_type": "HOUSEKEEPING"})
    task_id = post.json()["id"]
    client.delete(f"/api/v1/tasks/{task_id}")
    post2 = client.post("/api/v1/tasks/", json={"property_id": 1, "task_type": "HOUSEKEEPING"})
    assert post2.status_code == 201

def test_delete_task_edge_id():
    post = client.post("/api/v1/tasks/", json={"property_id": 1, "task_type": "HOUSEKEEPING"})
    task_id = post.json()["id"]
    resp = client.delete(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 204

def test_delete_task_zero_id():
    resp = client.delete(f"/api/v1/tasks/0")
    assert resp.status_code in (204, 404)

def test_delete_task_negative_id():
    resp = client.delete(f"/api/v1/tasks/-1")
    assert resp.status_code in (204, 404)

def teardown_module(module):
    import os
    os.close(TEST_DB_FD)
    os.unlink(TEST_DB_PATH)
