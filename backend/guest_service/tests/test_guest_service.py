import pytest
from fastapi.testclient import TestClient
from backend.guest_service.main import app
from backend.guest_service.models.guest import Guest
from backend.guest_service.schemas.guest import GuestCreate
from backend.core.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from backend.room_service.models import Property

client = TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_create_guest():
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "1234567890"
    }
    response = client.post("/api/v1/guests/", json=data)
    assert response.status_code == 201
    guest = response.json()
    assert guest["first_name"] == "John"
    assert guest["email"] == "john@example.com"

def test_get_guest():
    data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@example.com",
        "phone": "5555555555"
    }
    response = client.post("/api/v1/guests/", json=data)
    guest_id = response.json()["id"]
    get_resp = client.get(f"/api/v1/guests/{guest_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["email"] == "jane@example.com"

def test_search_guest():
    data = {
        "first_name": "Alice",
        "last_name": "Wonderland",
        "email": "alice@wonder.com",
        "phone": "1112223333"
    }
    client.post("/api/v1/guests/", json=data)
    resp = client.get("/api/v1/guests/search/?q=alice")
    assert resp.status_code == 200
    results = resp.json()
    assert any(g["email"] == "alice@wonder.com" for g in results)

def test_create_guest_valid(db_session):
    data = {
        "first_name": "Valid",
        "last_name": "User",
        "email": "valid@example.com",
        "phone": "1234567890"
    }
    response = client.post("/api/v1/guests/", json=data)
    assert response.status_code == 201
    guest = response.json()
    assert guest["first_name"] == "Valid"
    assert guest["email"] == "valid@example.com"

def test_create_guest_duplicate_email(db_session):
    data = {
        "first_name": "Dup",
        "last_name": "User",
        "email": "dup@example.com",
        "phone": "1234567890"
    }
    client.post("/api/v1/guests/", json=data)
    response = client.post("/api/v1/guests/", json=data)
    assert response.status_code == 201
    guest = response.json()
    assert guest["email"] == "dup@example.com"

def test_create_guest_invalid_email(db_session):
    data = {
        "first_name": "Bad",
        "last_name": "Email",
        "email": "not-an-email",
        "phone": "1234567890"
    }
    response = client.post("/api/v1/guests/", json=data)
    assert response.status_code == 422

def test_create_guest_missing_first_name(db_session):
    data = {
        "last_name": "NoFirst",
        "email": "nofirst@example.com",
        "phone": "1234567890"
    }
    response = client.post("/api/v1/guests/", json=data)
    assert response.status_code == 422

def test_create_guest_missing_last_name(db_session):
    data = {
        "first_name": "NoLast",
        "email": "nolast@example.com",
        "phone": "1234567890"
    }
    response = client.post("/api/v1/guests/", json=data)
    assert response.status_code == 422

def test_create_guest_missing_email(db_session):
    data = {
        "first_name": "NoEmail",
        "last_name": "User",
        "phone": "1234567890"
    }
    response = client.post("/api/v1/guests/", json=data)
    assert response.status_code == 422

def test_create_guest_long_names(db_session):
    data = {
        "first_name": "A"*100,
        "last_name": "B"*100,
        "email": "longname@example.com",
        "phone": "1234567890"
    }
    response = client.post("/api/v1/guests/", json=data)
    assert response.status_code == 201
    guest = response.json()
    assert guest["first_name"] == "A"*100

def test_create_guest_empty_phone(db_session):
    data = {
        "first_name": "NoPhone",
        "last_name": "User",
        "email": "nophone@example.com",
        "phone": ""
    }
    response = client.post("/api/v1/guests/", json=data)
    assert response.status_code == 201
    guest = response.json()
    assert guest["phone"] == ""

def test_create_guest_address_optional(db_session):
    data = {
        "first_name": "Addr",
        "last_name": "Opt",
        "email": "addr@example.com"
    }
    response = client.post("/api/v1/guests/", json=data)
    assert response.status_code == 201
    guest = response.json()
    assert guest["address"] is None

def test_create_guest_with_address(db_session):
    data = {
        "first_name": "Addr",
        "last_name": "Set",
        "email": "addrset@example.com",
        "address": "123 Main St"
    }
    response = client.post("/api/v1/guests/", json=data)
    assert response.status_code == 201
    guest = response.json()
    assert guest["address"] == "123 Main St"

def test_create_guest_invalid_phone_type(db_session):
    data = {
        "first_name": "Bad",
        "last_name": "Phone",
        "email": "badphone@example.com",
        "phone": 1234567890
    }
    response = client.post("/api/v1/guests/", json=data)
    assert response.status_code == 422

def test_create_guest_extra_fields_ignored(db_session):
    data = {
        "first_name": "Extra",
        "last_name": "Field",
        "email": "extrafield@example.com",
        "phone": "1234567890",
        "foo": "bar"
    }
    response = client.post("/api/v1/guests/", json=data)
    assert response.status_code == 201
    guest = response.json()
    assert "foo" not in guest

def test_create_guest_case_insensitive_email(db_session):
    data1 = {
        "first_name": "Case",
        "last_name": "Insensitive",
        "email": "case@example.com",
        "phone": "1234567890"
    }
    data2 = {
        "first_name": "Case",
        "last_name": "Insensitive",
        "email": "CASE@EXAMPLE.COM",
        "phone": "1234567890"
    }
    client.post("/api/v1/guests/", json=data1)
    response = client.post("/api/v1/guests/", json=data2)
    assert response.status_code == 201
    guest = response.json()
    assert guest["email"].lower() == "case@example.com"

def test_create_guest_unicode_names(db_session):
    data = {
        "first_name": "测试",
        "last_name": "用户",
        "email": "unicode@example.com",
        "phone": "1234567890"
    }
    response = client.post("/api/v1/guests/", json=data)
    assert response.status_code == 201
    guest = response.json()
    assert guest["first_name"] == "测试"

def test_create_guest_whitespace_names(db_session):
    data = {
        "first_name": " ",
        "last_name": " ",
        "email": "whitespace@example.com",
        "phone": "1234567890"
    }
    response = client.post("/api/v1/guests/", json=data)
    assert response.status_code == 201
    guest = response.json()
    assert guest["first_name"].strip() == ""

def test_create_guest_max_length_email(db_session):
    email = "a"*64 + "@example.com"
    data = {
        "first_name": "Max",
        "last_name": "Email",
        "email": email,
        "phone": "1234567890"
    }
    response = client.post("/api/v1/guests/", json=data)
    assert response.status_code == 201
    guest = response.json()
    assert guest["email"] == email

def test_create_guest_minimal_valid(db_session):
    data = {
        "first_name": "Min",
        "last_name": "User",
        "email": "min@example.com"
    }
    response = client.post("/api/v1/guests/", json=data)
    assert response.status_code == 201
    guest = response.json()
    assert guest["first_name"] == "Min"

# --- GET GUEST TESTS ---

def test_get_guest_valid(db_session):
    data = {
        "first_name": "Get",
        "last_name": "Valid",
        "email": "getvalid@example.com"
    }
    post = client.post("/api/v1/guests/", json=data)
    guest_id = post.json()["id"]
    get_resp = client.get(f"/api/v1/guests/{guest_id}")
    assert get_resp.status_code == 200
    guest = get_resp.json()
    assert guest["email"] == "getvalid@example.com"

def test_get_guest_not_found(db_session):
    resp = client.get("/api/v1/guests/9999")
    assert resp.status_code == 404

def test_get_guest_invalid_id(db_session):
    resp = client.get("/api/v1/guests/abc")
    assert resp.status_code == 422

def test_get_guest_after_multiple_creates(db_session):
    emails = [f"multi{i}@example.com" for i in range(5)]
    ids = []
    for email in emails:
        data = {"first_name": "Multi", "last_name": "User", "email": email}
        post = client.post("/api/v1/guests/", json=data)
        ids.append(post.json()["id"])
    for i, guest_id in enumerate(ids):
        get_resp = client.get(f"/api/v1/guests/{guest_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["email"] == emails[i]

def test_get_guest_case_insensitive_email(db_session):
    data = {
        "first_name": "Case",
        "last_name": "Insensitive",
        "email": "caseget@example.com"
    }
    post = client.post("/api/v1/guests/", json=data)
    guest_id = post.json()["id"]
    get_resp = client.get(f"/api/v1/guests/{guest_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["email"].lower() == "caseget@example.com"

def test_get_guest_unicode_id(db_session):
    resp = client.get("/api/v1/guests/测试")
    assert resp.status_code == 422

def test_get_guest_with_address(db_session):
    data = {
        "first_name": "Addr",
        "last_name": "Get",
        "email": "addrget@example.com",
        "address": "456 Main St"
    }
    post = client.post("/api/v1/guests/", json=data)
    guest_id = post.json()["id"]
    get_resp = client.get(f"/api/v1/guests/{guest_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["address"] == "456 Main St"

def test_get_guest_minimal(db_session):
    data = {
        "first_name": "Min",
        "last_name": "Get",
        "email": "minget@example.com"
    }
    post = client.post("/api/v1/guests/", json=data)
    guest_id = post.json()["id"]
    get_resp = client.get(f"/api/v1/guests/{guest_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["first_name"] == "Min"

def test_get_guest_long_id(db_session):
    data = {
        "first_name": "Long",
        "last_name": "Id",
        "email": "longid@example.com"
    }
    post = client.post("/api/v1/guests/", json=data)
    guest_id = post.json()["id"]
    get_resp = client.get(f"/api/v1/guests/{guest_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["email"] == "longid@example.com"

def test_get_guest_after_search(db_session):
    data = {
        "first_name": "Search",
        "last_name": "Get",
        "email": "searchget@example.com"
    }
    post = client.post("/api/v1/guests/", json=data)
    guest_id = post.json()["id"]
    # Search first
    resp = client.get("/api/v1/guests/search/?q=searchget")
    assert resp.status_code == 200
    # Then get
    get_resp = client.get(f"/api/v1/guests/{guest_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["email"] == "searchget@example.com"

def test_get_guest_with_empty_address(db_session):
    data = {
        "first_name": "Empty",
        "last_name": "Addr",
        "email": "emptyaddr@example.com",
        "address": ""
    }
    post = client.post("/api/v1/guests/", json=data)
    guest_id = post.json()["id"]
    get_resp = client.get(f"/api/v1/guests/{guest_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["address"] == ""

# --- SEARCH GUEST TESTS ---

def test_search_guest_by_first_name(db_session):
    data = {
        "first_name": "SearchFirst",
        "last_name": "User",
        "email": "searchfirst@example.com"
    }
    client.post("/api/v1/guests/", json=data)
    resp = client.get("/api/v1/guests/search/?q=searchfirst")
    assert resp.status_code == 200
    results = resp.json()
    assert any(g["email"] == "searchfirst@example.com" for g in results)

def test_search_guest_by_last_name(db_session):
    data = {
        "first_name": "User",
        "last_name": "SearchLast",
        "email": "searchlast@example.com"
    }
    client.post("/api/v1/guests/", json=data)
    resp = client.get("/api/v1/guests/search/?q=searchlast")
    assert resp.status_code == 200
    results = resp.json()
    assert any(g["email"] == "searchlast@example.com" for g in results)

def test_search_guest_by_email(db_session):
    data = {
        "first_name": "User",
        "last_name": "SearchEmail",
        "email": "searchemail@example.com"
    }
    client.post("/api/v1/guests/", json=data)
    resp = client.get("/api/v1/guests/search/?q=searchemail")
    assert resp.status_code == 200
    results = resp.json()
    assert any(g["email"] == "searchemail@example.com" for g in results)

def test_search_guest_case_insensitive(db_session):
    data = {
        "first_name": "Case",
        "last_name": "Insensitive",
        "email": "searchcase@example.com"
    }
    client.post("/api/v1/guests/", json=data)
    resp = client.get("/api/v1/guests/search/?q=SEARCHCASE")
    assert resp.status_code == 200
    results = resp.json()
    assert any(g["email"] == "searchcase@example.com" for g in results)

def test_search_guest_partial_match(db_session):
    data = {
        "first_name": "Partial",
        "last_name": "Match",
        "email": "partialmatch@example.com"
    }
    client.post("/api/v1/guests/", json=data)
    resp = client.get("/api/v1/guests/search/?q=part")
    assert resp.status_code == 200
    results = resp.json()
    assert any(g["email"] == "partialmatch@example.com" for g in results)

def test_search_guest_no_results(db_session):
    resp = client.get("/api/v1/guests/search/?q=notfound")
    assert resp.status_code == 200
    results = resp.json()
    assert results == []

def test_search_guest_multiple_results(db_session):
    emails = [f"multi{i}@search.com" for i in range(3)]
    for email in emails:
        data = {"first_name": "Multi", "last_name": "Search", "email": email}
        client.post("/api/v1/guests/", json=data)
    resp = client.get("/api/v1/guests/search/?q=multi")
    assert resp.status_code == 200
    results = resp.json()
    found = [g["email"] for g in results]
    for email in emails:
        assert email in found

def test_search_guest_unicode(db_session):
    data = {
        "first_name": "查找",
        "last_name": "用户",
        "email": "searchunicode@example.com"
    }
    client.post("/api/v1/guests/", json=data)
    resp = client.get("/api/v1/guests/search/?q=查找")
    assert resp.status_code == 200
    results = resp.json()
    assert any(g["email"] == "searchunicode@example.com" for g in results)

def test_search_guest_whitespace_query(db_session):
    data = {
        "first_name": "White",
        "last_name": "Space",
        "email": "whitespaceq@example.com"
    }
    client.post("/api/v1/guests/", json=data)
    resp = client.get("/api/v1/guests/search/?q= ")
    assert resp.status_code == 200
    results = resp.json()
    assert results == []  # Whitespace query should return empty list

def test_search_guest_empty_query(db_session):
    resp = client.get("/api/v1/guests/search/?q=")
    assert resp.status_code == 200
    results = resp.json()
    assert results == []

def test_search_guest_after_create_and_get(db_session):
    data = {
        "first_name": "After",
        "last_name": "Get",
        "email": "afterget@example.com"
    }
    client.post("/api/v1/guests/", json=data)
    resp = client.get("/api/v1/guests/search/?q=afterget")
    assert resp.status_code == 200
    results = resp.json()
    assert any(g["email"] == "afterget@example.com" for g in results)

def test_search_guest_special_characters(db_session):
    data = {
        "first_name": "Special",
        "last_name": "Char",
        "email": "specialchar@example.com"
    }
    client.post("/api/v1/guests/", json=data)
    resp = client.get("/api/v1/guests/search/?q=specialchar@example.com")
    assert resp.status_code == 200
    results = resp.json()
    assert any(g["email"] == "specialchar@example.com" for g in results)
