import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.room_service.models import Base, Room
from backend.room_service.repository import RoomRepository
from types import SimpleNamespace

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def repo(db_session):
    return RoomRepository(db_session)

def make_room_obj(property_id=1, number="101", type_id=1, status="AVAILABLE", floor="1", amenities="TV,WiFi"):
    return {
        "property_id": property_id,
        "number": number,
        "type_id": type_id,
        "status": status,
        "floor": floor,
        "amenities": amenities
    }

def test_create_room_success(repo):
    room = make_room_obj()
    created = repo.create(room)
    assert created.id is not None
    assert created.number == "101"

def test_create_room_duplicate_number(repo):
    room1 = make_room_obj()
    room2 = make_room_obj()
    repo.create(room1)
    with pytest.raises(ValueError):
        repo.create(room2)

def test_update_room_number_to_duplicate(repo):
    room1 = make_room_obj(number="101")
    room2 = make_room_obj(number="102")
    r1 = repo.create(room1)
    r2 = repo.create(room2)
    # Try to update r2's number to r1's number
    update_obj = make_room_obj(number="101")
    with pytest.raises(ValueError):
        repo.update(r2.id, update_obj)

def test_update_room_success(repo):
    room = make_room_obj()
    created = repo.create(room)
    update_obj = make_room_obj(number="201", floor="2")
    updated = repo.update(created.id, update_obj)
    assert updated.number == "201"
    assert updated.floor == "2"

def test_delete_room(repo):
    room = make_room_obj()
    created = repo.create(room)
    repo.delete(created.id)
    assert repo.get(created.id) is None

def test_list_rooms(repo):
    repo.create(make_room_obj(number="101"))
    repo.create(make_room_obj(number="102"))
    rooms = repo.list()
    assert len(rooms) == 2

def test_get_room(repo):
    created = repo.create(make_room_obj(number="101"))
    fetched = repo.get(created.id)
    assert fetched.id == created.id
    assert fetched.number == "101"

def test_create_same_number_different_properties(repo):
    room1 = make_room_obj(property_id=1, number="101")
    room2 = make_room_obj(property_id=2, number="101")
    r1 = repo.create(room1)
    r2 = repo.create(room2)
    assert r1.number == r2.number == "101"
    assert r1.property_id != r2.property_id

def test_create_room_empty_fields(repo):
    # Should fail if required fields are missing
    with pytest.raises(ValueError):
        repo.create({})
    with pytest.raises(ValueError):
        repo.create({"number": ""})

def test_partial_update_room(repo):
    room = make_room_obj(number="105", floor="1")
    created = repo.create(room)
    update_obj = {"floor": "3"}
    updated = repo.update(created.id, update_obj)
    assert updated.floor == "3"
    assert updated.number == "105"

def test_update_nonexistent_room(repo):
    update_obj = make_room_obj(number="999")
    with pytest.raises(AttributeError):
        repo.update(9999, update_obj)

def test_delete_nonexistent_room(repo):
    # Should not raise
    repo.delete(9999)

def test_list_rooms_by_property(repo):
    repo.create(make_room_obj(property_id=1, number="201"))
    repo.create(make_room_obj(property_id=2, number="202"))
    rooms1 = repo.list(property_id=1)
    rooms2 = repo.list(property_id=2)
    assert all(r.property_id == 1 for r in rooms1)
    assert all(r.property_id == 2 for r in rooms2)

def test_create_room_long_strings(repo):
    long_str = "x" * 255
    room = make_room_obj(number=long_str, floor=long_str, amenities=long_str)
    created = repo.create(room)
    assert created.number == long_str
    assert created.floor == long_str
    assert created.amenities == long_str

def test_create_room_special_characters(repo):
    special = "!@#$%^&*()_+-=|\\/,.<>?"
    room = make_room_obj(number=special, floor=special, amenities=special)
    created = repo.create(room)
    assert created.number == special
    assert created.floor == special
    assert created.amenities == special

def test_create_room_null_amenities(repo):
    room = make_room_obj(amenities=None)
    created = repo.create(room)
    assert created.amenities is None

def test_create_duplicate_number_different_properties(repo):
    repo.create(make_room_obj(property_id=1, number="X"))
    repo.create(make_room_obj(property_id=2, number="X"))
    assert len(repo.list()) == 2

def test_update_room_to_number_in_other_property(repo):
    r1 = repo.create(make_room_obj(property_id=1, number="A"))
    r2 = repo.create(make_room_obj(property_id=2, number="B"))
    # Update r2 to number "A" (should succeed, different property)
    update_obj = {"number": "A"}
    updated = repo.update(r2.id, update_obj)
    assert updated.number == "A"
    assert updated.property_id == 2

def test_create_many_rooms_stress(repo):
    for i in range(100):
        repo.create(make_room_obj(number=str(i)))
    assert len(repo.list()) >= 100
