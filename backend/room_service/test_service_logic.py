import pytest
from backend.room_service.models import Room, RoomType
from backend.room_service.service import RoomService, RoomTypeService
from backend.room_service.repository import RoomRepository, RoomTypeRepository
from backend.room_service.exceptions import InvalidStatusTransition, NoAvailableRoom
from backend.core.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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

@pytest.fixture
def room_type_service(db_session):
    return RoomTypeService(db_session)

@pytest.fixture
def room_service(db_session):
    return RoomService(db_session)

# --- RoomService.mark_room_status ---
def test_mark_room_status_valid_transitions(room_service, room_type_service):
    # Setup
    rt = room_type_service.repo.create(type('obj', (object,), {'property_id': 1, 'name': 'Test', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'Test', 'base_rate': 1.0}})())
    room = room_service.repo.create(type('obj', (object,), {'property_id': 1, 'number': '1', 'type_id': rt.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 1, 'number': '1', 'type_id': rt.id, 'floor': None, 'amenities': None}})())
    # AVAILABLE -> OCCUPIED
    updated = room_service.mark_room_status(room.id, 'OCCUPIED')
    assert updated.status == 'OCCUPIED'
    # OCCUPIED -> CLEANING
    updated = room_service.mark_room_status(room.id, 'CLEANING')
    assert updated.status == 'CLEANING'
    # CLEANING -> AVAILABLE
    updated = room_service.mark_room_status(room.id, 'AVAILABLE')

def test_mark_room_status_invalid_transition(room_service, room_type_service):
    rt = room_type_service.repo.create(type('obj', (object,), {'property_id': 1, 'name': 'Test', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'Test', 'base_rate': 1.0}})())
    room = room_service.repo.create(type('obj', (object,), {'property_id': 1, 'number': '2', 'type_id': rt.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 1, 'number': '2', 'type_id': rt.id, 'floor': None, 'amenities': None}})())
    # AVAILABLE -> AVAILABLE (should fail)
    with pytest.raises(InvalidStatusTransition):
        room_service.mark_room_status(room.id, 'AVAILABLE')
    # Non-existent room
    with pytest.raises(InvalidStatusTransition):
        room_service.mark_room_status(999, 'OCCUPIED')

# --- RoomService.allocate_room ---
def test_allocate_room_success(room_service, room_type_service):
    rt = room_type_service.repo.create(type('obj', (object,), {'property_id': 1, 'name': 'Test', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'Test', 'base_rate': 1.0}})())
    room = room_service.repo.create(type('obj', (object,), {'property_id': 1, 'number': '3', 'type_id': rt.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 1, 'number': '3', 'type_id': rt.id, 'floor': None, 'amenities': None}})())
    allocated = room_service.allocate_room(1, rt.id)
    assert allocated.id == room.id
    assert allocated.status == 'AVAILABLE'

def test_allocate_room_no_available(room_service, room_type_service):
    rt = room_type_service.repo.create(type('obj', (object,), {'property_id': 1, 'name': 'Test', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'Test', 'base_rate': 1.0}})())
    room = room_service.repo.create(type('obj', (object,), {'property_id': 1, 'number': '4', 'type_id': rt.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 1, 'number': '4', 'type_id': rt.id, 'floor': None, 'amenities': None}})())
    # Mark as OCCUPIED
    room_service.mark_room_status(room.id, 'OCCUPIED')
    with pytest.raises(NoAvailableRoom):
        room_service.allocate_room(1, rt.id)

# --- RoomTypeService basic CRUD ---
def test_room_type_crud(room_type_service, db_session):
    # Create
    data = type('obj', (object,), {'property_id': 1, 'name': 'CRUD', 'base_rate': 10.0, 'dict': lambda self: {'property_id': 1, 'name': 'CRUD', 'base_rate': 10.0}})()
    created = room_type_service.repo.create(data)
    assert created.id is not None
    # Read
    found = db_session.query(RoomType).filter_by(id=created.id).first()
    assert found is not None
    # Update
    update_obj = type('obj', (object,), {'name': 'CRUD2', 'dict': lambda self, exclude_unset=False: {'name': 'CRUD2'}})()
    updated = room_type_service.repo.update(created.id, update_obj)
    assert updated.name == 'CRUD2'
    # Delete
    room_type_service.repo.delete(created.id)
    assert db_session.query(RoomType).filter_by(id=created.id).first() is None

# --- RoomRepository.list property filter ---
def test_room_repository_list_property_filter(room_service, room_type_service):
    rt1 = room_type_service.repo.create(type('obj', (object,), {'property_id': 1, 'name': 'A', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'A', 'base_rate': 1.0}})())
    rt2 = room_type_service.repo.create(type('obj', (object,), {'property_id': 2, 'name': 'B', 'base_rate': 2.0, 'dict': lambda self: {'property_id': 2, 'name': 'B', 'base_rate': 2.0}})())
    room1 = room_service.repo.create(type('obj', (object,), {'property_id': 1, 'number': '10', 'type_id': rt1.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 1, 'number': '10', 'type_id': rt1.id, 'floor': None, 'amenities': None}})())
    room2 = room_service.repo.create(type('obj', (object,), {'property_id': 2, 'number': '20', 'type_id': rt2.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 2, 'number': '20', 'type_id': rt2.id, 'floor': None, 'amenities': None}})())
    all_rooms = room_service.repo.list()
    assert len(all_rooms) == 2
    prop1_rooms = room_service.repo.list(property_id=1)
    assert len(prop1_rooms) == 1
    assert prop1_rooms[0].property_id == 1

# --- Additional Robustness Tests ---

def test_mark_room_status_to_maintenance(room_service, room_type_service):
    rt = room_type_service.repo.create(type('obj', (object,), {'property_id': 1, 'name': 'Maint', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'Maint', 'base_rate': 1.0}})())
    room = room_service.repo.create(type('obj', (object,), {'property_id': 1, 'number': '5', 'type_id': rt.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 1, 'number': '5', 'type_id': rt.id, 'floor': None, 'amenities': None}})())
    updated = room_service.mark_room_status(room.id, 'MAINTENANCE')
    assert updated.status == 'MAINTENANCE'

def test_mark_room_status_to_cleaning_from_maintenance(room_service, room_type_service):
    rt = room_type_service.repo.create(type('obj', (object,), {'property_id': 1, 'name': 'Clean', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'Clean', 'base_rate': 1.0}})())
    room = room_service.repo.create(type('obj', (object,), {'property_id': 1, 'number': '6', 'type_id': rt.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 1, 'number': '6', 'type_id': rt.id, 'floor': None, 'amenities': None}})())
    room_service.mark_room_status(room.id, 'MAINTENANCE')
    updated = room_service.mark_room_status(room.id, 'CLEANING')
    assert updated.status == 'CLEANING'

def test_mark_room_status_invalid_status(room_service, room_type_service):
    rt = room_type_service.repo.create(type('obj', (object,), {'property_id': 1, 'name': 'Invalid', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'Invalid', 'base_rate': 1.0}})())
    room = room_service.repo.create(type('obj', (object,), {'property_id': 1, 'number': '7', 'type_id': rt.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 1, 'number': '7', 'type_id': rt.id, 'floor': None, 'amenities': None}})())
    with pytest.raises(Exception):
        room_service.mark_room_status(room.id, 'NOT_A_STATUS')

def test_mark_room_status_case_sensitivity(room_service, room_type_service):
    rt = room_type_service.repo.create(type('obj', (object,), {'property_id': 1, 'name': 'Case', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'Case', 'base_rate': 1.0}})())
    room = room_service.repo.create(type('obj', (object,), {'property_id': 1, 'number': '8', 'type_id': rt.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 1, 'number': '8', 'type_id': rt.id, 'floor': None, 'amenities': None}})())
    with pytest.raises(Exception):
        room_service.mark_room_status(room.id, 'available')

def test_mark_room_status_multiple_transitions(room_service, room_type_service):
    rt = room_type_service.repo.create(type('obj', (object,), {'property_id': 1, 'name': 'Multi', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'Multi', 'base_rate': 1.0}})())
    room = room_service.repo.create(type('obj', (object,), {'property_id': 1, 'number': '9', 'type_id': rt.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 1, 'number': '9', 'type_id': rt.id, 'floor': None, 'amenities': None}})())
    for status in ['OCCUPIED', 'CLEANING', 'AVAILABLE', 'MAINTENANCE', 'AVAILABLE']:
        updated = room_service.mark_room_status(room.id, status)
        assert updated.status == status

def test_allocate_room_multiple_available(room_service, room_type_service):
    rt = room_type_service.repo.create(type('obj', (object,), {'property_id': 1, 'name': 'MultiAvail', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'MultiAvail', 'base_rate': 1.0}})())
    room1 = room_service.repo.create(type('obj', (object,), {'property_id': 1, 'number': '11', 'type_id': rt.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 1, 'number': '11', 'type_id': rt.id, 'floor': None, 'amenities': None}})())
    room2 = room_service.repo.create(type('obj', (object,), {'property_id': 1, 'number': '12', 'type_id': rt.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 1, 'number': '12', 'type_id': rt.id, 'floor': None, 'amenities': None}})())
    allocated = room_service.allocate_room(1, rt.id)
    assert allocated.status == 'AVAILABLE'
    assert allocated.id in [room1.id, room2.id]

def test_allocate_room_different_property(room_service, room_type_service):
    rt1 = room_type_service.repo.create(type('obj', (object,), {'property_id': 1, 'name': 'A', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'A', 'base_rate': 1.0}})())
    rt2 = room_type_service.repo.create(type('obj', (object,), {'property_id': 2, 'name': 'B', 'base_rate': 2.0, 'dict': lambda self: {'property_id': 2, 'name': 'B', 'base_rate': 2.0}})())
    room1 = room_service.repo.create(type('obj', (object,), {'property_id': 1, 'number': '13', 'type_id': rt1.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 1, 'number': '13', 'type_id': rt1.id, 'floor': None, 'amenities': None}})())
    room2 = room_service.repo.create(type('obj', (object,), {'property_id': 2, 'number': '14', 'type_id': rt2.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 2, 'number': '14', 'type_id': rt2.id, 'floor': None, 'amenities': None}})())
    allocated = room_service.allocate_room(2, rt2.id)
    assert allocated.id == room2.id

def test_allocate_room_type_mismatch(room_service, room_type_service):
    rt1 = room_type_service.repo.create(type('obj', (object,), {'property_id': 1, 'name': 'A', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'A', 'base_rate': 1.0}})())
    rt2 = room_type_service.repo.create(type('obj', (object,), {'property_id': 1, 'name': 'B', 'base_rate': 2.0, 'dict': lambda self: {'property_id': 1, 'name': 'B', 'base_rate': 2.0}})())
    room = room_service.repo.create(type('obj', (object,), {'property_id': 1, 'number': '15', 'type_id': rt1.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 1, 'number': '15', 'type_id': rt1.id, 'floor': None, 'amenities': None}})())
    with pytest.raises(NoAvailableRoom):
        room_service.allocate_room(1, rt2.id)

def test_allocate_room_after_status_change(room_service, room_type_service):
    rt = room_type_service.repo.create(type('obj', (object,), {'property_id': 1, 'name': 'Switch', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'Switch', 'base_rate': 1.0}})())
    room = room_service.repo.create(type('obj', (object,), {'property_id': 1, 'number': '16', 'type_id': rt.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 1, 'number': '16', 'type_id': rt.id, 'floor': None, 'amenities': None}})())
    room_service.mark_room_status(room.id, 'OCCUPIED')
    with pytest.raises(NoAvailableRoom):
        room_service.allocate_room(1, rt.id)
    room_service.mark_room_status(room.id, 'AVAILABLE')
    allocated = room_service.allocate_room(1, rt.id)
    assert allocated.id == room.id

def test_room_type_create_duplicate_name(room_type_service):
    data1 = type('obj', (object,), {'property_id': 1, 'name': 'Dup', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'Dup', 'base_rate': 1.0}})()
    data2 = type('obj', (object,), {'property_id': 1, 'name': 'Dup', 'base_rate': 2.0, 'dict': lambda self: {'property_id': 1, 'name': 'Dup', 'base_rate': 2.0}})()
    rt1 = room_type_service.repo.create(data1)
    rt2 = room_type_service.repo.create(data2)
    assert rt1.name == rt2.name
    assert rt1.id != rt2.id

def test_room_type_update_base_rate(room_type_service, db_session):
    data = type('obj', (object,), {'property_id': 1, 'name': 'Rate', 'base_rate': 10.0, 'dict': lambda self: {'property_id': 1, 'name': 'Rate', 'base_rate': 10.0}})()
    created = room_type_service.repo.create(data)
    update_obj = type('obj', (object,), {'base_rate': 20.0, 'dict': lambda self, exclude_unset=False: {'base_rate': 20.0}})()
    updated = room_type_service.repo.update(created.id, update_obj)
    assert updated.base_rate == 20.0

def test_room_type_update_partial(room_type_service, db_session):
    data = type('obj', (object,), {'property_id': 1, 'name': 'Partial', 'base_rate': 10.0, 'dict': lambda self: {'property_id': 1, 'name': 'Partial', 'base_rate': 10.0}})()
    created = room_type_service.repo.create(data)
    update_obj = type('obj', (object,), {'dict': lambda self, exclude_unset=False: {}})()
    updated = room_type_service.repo.update(created.id, update_obj)
    assert updated.name == 'Partial'
    assert updated.base_rate == 10.0

def test_room_type_delete_nonexistent(room_type_service):
    # Should not raise
    room_type_service.repo.delete(999)

def test_room_type_list_by_property(room_type_service):
    data1 = type('obj', (object,), {'property_id': 1, 'name': 'ListA', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'ListA', 'base_rate': 1.0}})()
    data2 = type('obj', (object,), {'property_id': 2, 'name': 'ListB', 'base_rate': 2.0, 'dict': lambda self: {'property_id': 2, 'name': 'ListB', 'base_rate': 2.0}})()
    rt1 = room_type_service.repo.create(data1)
    rt2 = room_type_service.repo.create(data2)
    all_types = room_type_service.repo.list()
    assert len(all_types) >= 2
    prop1_types = room_type_service.repo.list(property_id=1)
    assert all(rt.property_id == 1 for rt in prop1_types)

def test_room_type_update_nonexistent(room_type_service):
    update_obj = type('obj', (object,), {'name': 'Nope', 'dict': lambda self, exclude_unset=False: {'name': 'Nope'}})()
    with pytest.raises(AttributeError):
        room_type_service.repo.update(999, update_obj)

def test_room_type_get(room_type_service):
    data = type('obj', (object,), {'property_id': 1, 'name': 'Get', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'Get', 'base_rate': 1.0}})()
    created = room_type_service.repo.create(data)
    found = room_type_service.repo.get(created.id)
    assert found is not None
    assert found.id == created.id

def test_room_type_get_nonexistent(room_type_service):
    found = room_type_service.repo.get(999)
    assert found is None

def test_room_type_create_with_null_name(room_type_service):
    from sqlalchemy.exc import IntegrityError
    data = type('obj', (object,), {'property_id': 1, 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'base_rate': 1.0}})()
    with pytest.raises(IntegrityError):
        room_type_service.repo.create(data)

def test_room_type_create_with_negative_base_rate(room_type_service):
    data = type('obj', (object,), {'property_id': 1, 'name': 'NegRate', 'base_rate': -10.0, 'dict': lambda self: {'property_id': 1, 'name': 'NegRate', 'base_rate': -10.0}})()
    created = room_type_service.repo.create(data)
    assert created.base_rate == -10.0  # Business logic may allow or disallow; test current behavior

def test_room_type_update_to_null_name(room_type_service, db_session):
    data = type('obj', (object,), {'property_id': 1, 'name': 'ToNull', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'ToNull', 'base_rate': 1.0}})()
    created = room_type_service.repo.create(data)
    update_obj = type('obj', (object,), {'dict': lambda self, exclude_unset=False: {'name': None}})()
    with pytest.raises(Exception):
        room_type_service.repo.update(created.id, update_obj)

def test_room_type_update_to_empty_name(room_type_service, db_session):
    data = type('obj', (object,), {'property_id': 1, 'name': 'ToEmpty', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'ToEmpty', 'base_rate': 1.0}})()
    created = room_type_service.repo.create(data)
    update_obj = type('obj', (object,), {'dict': lambda self, exclude_unset=False: {'name': ''}})()
    updated = room_type_service.repo.update(created.id, update_obj)
    assert updated.name == ''

def test_room_type_update_to_negative_base_rate(room_type_service, db_session):
    data = type('obj', (object,), {'property_id': 1, 'name': 'ToNeg', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'ToNeg', 'base_rate': 1.0}})()
    created = room_type_service.repo.create(data)
    update_obj = type('obj', (object,), {'dict': lambda self, exclude_unset=False: {'base_rate': -5.0}})()
    updated = room_type_service.repo.update(created.id, update_obj)
    assert updated.base_rate == -5.0

def test_room_type_update_with_no_fields(room_type_service, db_session):
    data = type('obj', (object,), {'property_id': 1, 'name': 'NoFields', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'NoFields', 'base_rate': 1.0}})()
    created = room_type_service.repo.create(data)
    update_obj = type('obj', (object,), {'dict': lambda self, exclude_unset=False: {}})()
    updated = room_type_service.repo.update(created.id, update_obj)
    assert updated.name == 'NoFields'
    assert updated.base_rate == 1.0

def test_room_type_update_with_extra_fields(room_type_service, db_session):
    data = type('obj', (object,), {'property_id': 1, 'name': 'Extra', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'Extra', 'base_rate': 1.0}})()
    created = room_type_service.repo.create(data)
    update_obj = type('obj', (object,), {'dict': lambda self, exclude_unset=False: {'base_rate': 2.0, 'foo': 'bar'}})()
    updated = room_type_service.repo.update(created.id, update_obj)
    assert updated.base_rate == 2.0
    assert not hasattr(updated, 'foo')

def test_room_type_delete_twice(room_type_service, db_session):
    data = type('obj', (object,), {'property_id': 1, 'name': 'Twice', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'Twice', 'base_rate': 1.0}})()
    created = room_type_service.repo.create(data)
    room_type_service.repo.delete(created.id)
    # Second delete should not raise
    room_type_service.repo.delete(created.id)

def test_room_type_list_empty(room_type_service):
    types = room_type_service.repo.list(property_id=999)
    assert types == []

def test_room_type_list_large(room_type_service):
    for i in range(50):
        data = type('obj', (object,), {'property_id': 1, 'name': f'Bulk{i}', 'base_rate': i, 'dict': lambda self: {'property_id': 1, 'name': f'Bulk{i}', 'base_rate': i}})()
        room_type_service.repo.create(data)
    types = room_type_service.repo.list(property_id=1)
    assert len(types) >= 50

def test_room_type_list_mixed_properties(room_type_service):
    for i in range(10):
        data1 = type('obj', (object,), {'property_id': 1, 'name': f'MixA{i}', 'base_rate': i, 'dict': lambda self: {'property_id': 1, 'name': f'MixA{i}', 'base_rate': i}})()
        data2 = type('obj', (object,), {'property_id': 2, 'name': f'MixB{i}', 'base_rate': i, 'dict': lambda self: {'property_id': 2, 'name': f'MixB{i}', 'base_rate': i}})()
        room_type_service.repo.create(data1)
        room_type_service.repo.create(data2)
    types1 = room_type_service.repo.list(property_id=1)
    types2 = room_type_service.repo.list(property_id=2)
    assert all(rt.property_id == 1 for rt in types1)
    assert all(rt.property_id == 2 for rt in types2)

def test_room_type_get_after_delete(room_type_service):
    data = type('obj', (object,), {'property_id': 1, 'name': 'DelGet', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'DelGet', 'base_rate': 1.0}})()
    created = room_type_service.repo.create(data)
    room_type_service.repo.delete(created.id)
    found = room_type_service.repo.get(created.id)
    assert found is None

def test_room_type_update_deleted(room_type_service):
    data = type('obj', (object,), {'property_id': 1, 'name': 'UpdDel', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'UpdDel', 'base_rate': 1.0}})()
    created = room_type_service.repo.create(data)
    room_type_service.repo.delete(created.id)
    update_obj = type('obj', (object,), {'dict': lambda self, exclude_unset=False: {'name': 'StillUpd'}})()
    with pytest.raises(AttributeError):
        room_type_service.repo.update(created.id, update_obj)

def test_room_type_update_with_property_change(room_type_service, db_session):
    data = type('obj', (object,), {'property_id': 1, 'name': 'PropChg', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'PropChg', 'base_rate': 1.0}})()
    created = room_type_service.repo.create(data)
    update_obj = type('obj', (object,), {'dict': lambda self, exclude_unset=False: {'property_id': 2}})()
    updated = room_type_service.repo.update(created.id, update_obj)
    assert updated.property_id == 2

def test_room_type_update_with_large_name(room_type_service, db_session):
    data = type('obj', (object,), {'property_id': 1, 'name': 'Short', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'Short', 'base_rate': 1.0}})()
    created = room_type_service.repo.create(data)
    long_name = 'A' * 1000
    update_obj = type('obj', (object,), {'dict': lambda self, exclude_unset=False: {'name': long_name}})()
    updated = room_type_service.repo.update(created.id, update_obj)
    assert updated.name == long_name

def test_room_type_update_with_special_characters(room_type_service, db_session):
    data = type('obj', (object,), {'property_id': 1, 'name': 'Special', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'Special', 'base_rate': 1.0}})()
    created = room_type_service.repo.create(data)
    special_name = '!@#$%^&*()_+-=[]{}|;:,.<>?/~`'
    update_obj = type('obj', (object,), {'dict': lambda self, exclude_unset=False: {'name': special_name}})()
    updated = room_type_service.repo.update(created.id, update_obj)
    assert updated.name == special_name

def test_room_type_update_with_float_base_rate(room_type_service, db_session):
    data = type('obj', (object,), {'property_id': 1, 'name': 'Float', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'Float', 'base_rate': 1.0}})()
    created = room_type_service.repo.create(data)
    update_obj = type('obj', (object,), {'dict': lambda self, exclude_unset=False: {'base_rate': 3.14159}})()
    updated = room_type_service.repo.update(created.id, update_obj)
    assert abs(updated.base_rate - 3.14159) < 1e-6

def test_room_type_update_with_zero_base_rate(room_type_service, db_session):
    data = type('obj', (object,), {'property_id': 1, 'name': 'Zero', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'Zero', 'base_rate': 1.0}})()
    created = room_type_service.repo.create(data)
    update_obj = type('obj', (object,), {'dict': lambda self, exclude_unset=False: {'base_rate': 0.0}})()
    updated = room_type_service.repo.update(created.id, update_obj)
    assert updated.base_rate == 0.0

def test_room_type_update_with_string_base_rate(room_type_service, db_session):
    data = type('obj', (object,), {'property_id': 1, 'name': 'StrRate', 'base_rate': 1.0, 'dict': lambda self: {'property_id': 1, 'name': 'StrRate', 'base_rate': 1.0}})()
    created = room_type_service.repo.create(data)
    update_obj = type('obj', (object,), {'dict': lambda self, exclude_unset=False: {'base_rate': 'not-a-float'}})()
    with pytest.raises(Exception):
        room_type_service.repo.update(created.id, update_obj)
