import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from backend.auth_service.main import app
from backend.core.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.room_service.models import Property  # Use Property from room_service
from fastapi import Depends
from backend.auth_service.db import get_db

# Use a temporary file-based SQLite DB for all test connections
TEST_DB_FD, TEST_DB_PATH = tempfile.mkstemp(suffix='.db')
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True, scope="function")
def setup_and_teardown_db():
    # Drop and recreate all tables before each test for isolation
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # No teardown needed per test (file removed at end)

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

def test_create_staff():
    data = {
        "username": "admin1",  # Use unique username/email
        "email": "admin1@example.com",
        "password": "secret123"
    }
    response = client.post("/api/v1/staff/", json=data)
    assert response.status_code == 201
    staff = response.json()
    assert staff["username"] == "admin1"
    assert staff["email"] == "admin1@example.com"

def test_create_duplicate_staff():
    data = {
        "username": "admin2",
        "email": "admin2@example.com",
        "password": "secret123"
    }
    client.post("/api/v1/staff/", json=data)
    response = client.post("/api/v1/staff/", json=data)
    assert response.status_code == 409

def test_login_success():
    data = {
        "username": "admin2",
        "email": "admin2@example.com",
        "password": "secret123"
    }
    client.post("/api/v1/staff/", json=data)
    login = {"username": "admin2", "password": "secret123"}
    resp = client.post("/api/v1/login/", json=login)
    assert resp.status_code == 200
    assert resp.json()["username"] == "admin2"

def test_login_fail():
    login = {"username": "notfound", "password": "badpass"}
    resp = client.post("/api/v1/login/", json=login)
    assert resp.status_code == 401

def test_create_staff_missing_username():
    data = {"email": "nouser@example.com", "password": "secret123"}
    response = client.post("/api/v1/staff/", json=data)
    assert response.status_code == 422

def test_create_staff_missing_email():
    data = {"username": "nouser", "password": "secret123"}
    response = client.post("/api/v1/staff/", json=data)
    assert response.status_code == 422

def test_create_staff_missing_password():
    data = {"username": "nopass", "email": "nopass@example.com"}
    response = client.post("/api/v1/staff/", json=data)
    assert response.status_code == 422

def test_create_staff_invalid_email():
    data = {"username": "bademail", "email": "notanemail", "password": "secret123"}
    response = client.post("/api/v1/staff/", json=data)
    assert response.status_code == 422

def test_create_staff_long_username(db_session):
    data = {"username": "a"*100, "email": "longuser2@example.com", "password": "secret123"}
    response = client.post("/api/v1/staff/", json=data)
    assert response.status_code == 201
    staff = response.json()
    assert staff["username"] == "a"*100

def test_create_staff_unicode_username(db_session):
    data = {"username": "测试2", "email": "unicode2@example.com", "password": "secret123"}
    response = client.post("/api/v1/staff/", json=data)
    assert response.status_code == 201
    staff = response.json()
    assert staff["username"] == "测试2"

def test_create_staff_duplicate_email():
    data1 = {"username": "user3", "email": "dup1@example.com", "password": "secret123"}
    data2 = {"username": "user4", "email": "dup1@example.com", "password": "secret123"}
    client.post("/api/v1/staff/", json=data1)
    response = client.post("/api/v1/staff/", json=data2)
    assert response.status_code == 409

def test_create_staff_case_insensitive_email(db_session):
    data1 = {"username": "case3", "email": "case2@example.com", "password": "secret123"}
    data2 = {"username": "case4", "email": "CASE2@EXAMPLE.COM", "password": "secret123"}
    client.post("/api/v1/staff/", json=data1)
    response = client.post("/api/v1/staff/", json=data2)
    assert response.status_code == 409

def test_get_staff(db_session):
    data = {"username": "getuser2", "email": "getuser2@example.com", "password": "secret123"}
    post = client.post("/api/v1/staff/", json=data)
    assert post.status_code == 201
    staff_id = post.json()["id"]
    resp = client.get(f"/api/v1/staff/{staff_id}")
    assert resp.status_code == 200
    staff = resp.json()
    assert staff["email"] == "getuser2@example.com"

def test_get_staff_not_found():
    resp = client.get("/api/v1/staff/9999")
    assert resp.status_code == 404

def test_update_staff(db_session):
    data = {"username": "upd2", "email": "upd2@example.com", "password": "secret123"}
    post = client.post("/api/v1/staff/", json=data)
    assert post.status_code == 201
    staff_id = post.json()["id"]
    update = {"username": "updated2"}
    resp = client.patch(f"/api/v1/staff/{staff_id}", json=update)
    assert resp.status_code == 200
    staff = resp.json()
    assert staff["username"] == "updated2"

def test_update_staff_not_found():
    update = {"username": "nope"}
    resp = client.patch("/api/v1/staff/9999", json=update)
    assert resp.status_code == 404

def test_delete_staff():
    data = {"username": "del", "email": "del@example.com", "password": "secret123"}
    post = client.post("/api/v1/staff/", json=data)
    staff_id = post.json()["id"]
    resp = client.delete(f"/api/v1/staff/{staff_id}")
    assert resp.status_code == 204

def test_delete_staff_not_found():
    resp = client.delete("/api/v1/staff/9999")
    assert resp.status_code == 404

def test_assign_role():
    # Create staff
    staff_data = {"username": "roleuser", "email": "roleuser@example.com", "password": "secret123"}
    staff_post = client.post("/api/v1/staff/", json=staff_data)
    staff_id = staff_post.json()["id"]
    # Create role
    role_data = {"name": "manager"}
    role_post = client.post("/api/v1/roles/", json=role_data)
    role_id = role_post.json()["id"]
    # Assign role
    resp = client.post(f"/api/v1/staff/{staff_id}/roles/{role_id}")
    assert resp.status_code == 200
    result = resp.json()
    assert result["staff_id"] == staff_id
    assert result["role_id"] == role_id

def test_assign_role_staff_not_found():
    role_data = {"name": "missingrole"}
    role_post = client.post("/api/v1/roles/", json=role_data)
    role_id = role_post.json()["id"]
    resp = client.post(f"/api/v1/staff/9999/roles/{role_id}")
    assert resp.status_code == 404

def test_create_role():
    data = {"name": "admin", "description": "Administrator"}
    resp = client.post("/api/v1/roles/", json=data)
    assert resp.status_code == 201
    role = resp.json()
    assert role["name"] == "admin"
    assert role["description"] == "Administrator"

def test_get_role():
    data = {"name": "getrole"}
    post = client.post("/api/v1/roles/", json=data)
    role_id = post.json()["id"]
    resp = client.get(f"/api/v1/roles/{role_id}")
    assert resp.status_code == 200
    role = resp.json()
    assert role["name"] == "getrole"

def test_get_role_not_found():
    resp = client.get("/api/v1/roles/9999")
    assert resp.status_code == 404

def test_update_role():
    data = {"name": "updaterole"}
    post = client.post("/api/v1/roles/", json=data)
    role_id = post.json()["id"]
    update = {"name": "updatedrole", "description": "Updated desc"}
    resp = client.patch(f"/api/v1/roles/{role_id}", json=update)
    assert resp.status_code == 200
    role = resp.json()
    assert role["name"] == "updatedrole"
    assert role["description"] == "Updated desc"

def test_update_role_not_found():
    update = {"name": "nope"}
    resp = client.patch("/api/v1/roles/9999", json=update)
    assert resp.status_code == 404

def test_delete_role():
    data = {"name": "delrole"}
    post = client.post("/api/v1/roles/", json=data)
    role_id = post.json()["id"]
    resp = client.delete(f"/api/v1/roles/{role_id}")
    assert resp.status_code == 204

def test_delete_role_not_found():
    resp = client.delete("/api/v1/roles/9999")
    assert resp.status_code == 404

def test_list_roles():
    client.post("/api/v1/roles/", json={"name": "role1"})
    client.post("/api/v1/roles/", json={"name": "role2"})
    resp = client.get("/api/v1/roles/")
    assert resp.status_code == 200
    roles = resp.json()
    assert any(r["name"] == "role1" for r in roles)
    assert any(r["name"] == "role2" for r in roles)

def test_login_wrong_password():
    data = {"username": "wrongpass", "email": "wrongpass@example.com", "password": "secret123"}
    client.post("/api/v1/staff/", json=data)
    login = {"username": "wrongpass", "password": "badpass"}
    resp = client.post("/api/v1/login/", json=login)
    assert resp.status_code == 401

def test_login_missing_username():
    login = {"password": "secret123"}
    resp = client.post("/api/v1/login/", json=login)
    assert resp.status_code == 422

def test_login_missing_password():
    login = {"username": "admin"}
    resp = client.post("/api/v1/login/", json=login)
    assert resp.status_code == 422

def teardown_module(module):
    os.close(TEST_DB_FD)
    os.unlink(TEST_DB_PATH)
