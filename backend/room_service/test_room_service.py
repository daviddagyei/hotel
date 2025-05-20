import pytest
from backend.room_service import models  # This ensures all models are registered
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.room_service import models  # Ensure all models are registered
from backend.core.base import Base  # Use shared Base
from backend.room_service.models import RoomType, Room, RatePlan
from backend.room_service.repository import RoomTypeRepository, RoomRepository, RatePlanRepository
from backend.room_service.service import RoomService, RoomTypeService, RatePlanService
from backend.room_service.exceptions import InvalidStatusTransition, NoAvailableRoom
from sqlalchemy.orm import Session

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

@pytest.fixture
def rate_plan_service(db_session):
    return RatePlanService(db_session)

def test_create_room_type(room_type_service, db_session):
    data = type('obj', (object,), {'property_id': 1, 'name': 'Deluxe', 'base_rate': 100.0, 'dict': lambda self: {'property_id': 1, 'name': 'Deluxe', 'base_rate': 100.0}})()
    room_type = room_type_service.repo.create(data)
    assert room_type.id is not None
    assert room_type.name == 'Deluxe'
    assert db_session.query(RoomType).filter_by(name='Deluxe').first() is not None

def test_create_room_default_status(room_service, db_session, room_type_service):
    # Create RoomType first
    rt_data = type('obj', (object,), {'property_id': 1, 'name': 'Standard', 'base_rate': 80.0, 'dict': lambda self: {'property_id': 1, 'name': 'Standard', 'base_rate': 80.0}})()
    room_type = room_type_service.repo.create(rt_data)
    data = type('obj', (object,), {'property_id': 1, 'number': '101', 'type_id': room_type.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 1, 'number': '101', 'type_id': room_type.id, 'floor': None, 'amenities': None}})()
    room = room_service.repo.create(data)
    assert room.status == 'AVAILABLE'
    assert db_session.query(Room).filter_by(number='101').first().status == 'AVAILABLE'

def test_mark_room_status_transitions(room_service, db_session, room_type_service):
    rt_data = type('obj', (object,), {'property_id': 1, 'name': 'Suite', 'base_rate': 200.0, 'dict': lambda self: {'property_id': 1, 'name': 'Suite', 'base_rate': 200.0}})()
    room_type = room_type_service.repo.create(rt_data)
    data = type('obj', (object,), {'property_id': 1, 'number': '201', 'type_id': room_type.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 1, 'number': '201', 'type_id': room_type.id, 'floor': None, 'amenities': None}})()
    room = room_service.repo.create(data)
    # AVAILABLE -> OCCUPIED
    room = room_service.mark_room_status(room.id, 'OCCUPIED')
    assert room.status == 'OCCUPIED'
    # OCCUPIED -> CLEANING
    room = room_service.mark_room_status(room.id, 'CLEANING')
    assert room.status == 'CLEANING'
    # CLEANING -> AVAILABLE
    room = room_service.mark_room_status(room.id, 'AVAILABLE')
    assert room.status == 'AVAILABLE'
    # Invalid: AVAILABLE -> AVAILABLE
    with pytest.raises(Exception):
        room_service.mark_room_status(room.id, 'AVAILABLE')

def test_availability_query(room_service, db_session, room_type_service):
    rt_data = type('obj', (object,), {'property_id': 1, 'name': 'Economy', 'base_rate': 50.0, 'dict': lambda self: {'property_id': 1, 'name': 'Economy', 'base_rate': 50.0}})()
    room_type = room_type_service.repo.create(rt_data)
    # Create two rooms, one AVAILABLE, one OCCUPIED
    data1 = type('obj', (object,), {'property_id': 1, 'number': '301', 'type_id': room_type.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 1, 'number': '301', 'type_id': room_type.id, 'floor': None, 'amenities': None}})()
    data2 = type('obj', (object,), {'property_id': 1, 'number': '302', 'type_id': room_type.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 1, 'number': '302', 'type_id': room_type.id, 'floor': None, 'amenities': None}})()
    room1 = room_service.repo.create(data1)
    room2 = room_service.repo.create(data2)
    room_service.mark_room_status(room2.id, 'OCCUPIED')
    available_rooms = [r for r in room_service.repo.list() if r.status == 'AVAILABLE']
    assert len(available_rooms) == 1
    assert available_rooms[0].number == '301'

def test_allocation_logic(room_service, db_session, room_type_service):
    rt_data = type('obj', (object,), {'property_id': 1, 'name': 'Family', 'base_rate': 120.0, 'dict': lambda self: {'property_id': 1, 'name': 'Family', 'base_rate': 120.0}})()
    room_type = room_type_service.repo.create(rt_data)
    # Create two available rooms
    data1 = type('obj', (object,), {'property_id': 1, 'number': '401', 'type_id': room_type.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 1, 'number': '401', 'type_id': room_type.id, 'floor': None, 'amenities': None}})()
    data2 = type('obj', (object,), {'property_id': 1, 'number': '402', 'type_id': room_type.id, 'floor': None, 'amenities': None, 'dict': lambda self: {'property_id': 1, 'number': '402', 'type_id': room_type.id, 'floor': None, 'amenities': None}})()
    room1 = room_service.repo.create(data1)
    room2 = room_service.repo.create(data2)
    # Allocate a room
    allocated = room_service.allocate_room(1, room_type.id)
    assert allocated.status == 'AVAILABLE'  # Before marking
    room_service.mark_room_status(allocated.id, 'OCCUPIED')
    # Next allocation
    allocated2 = room_service.allocate_room(1, room_type.id)
    assert allocated2.id != allocated.id
    room_service.mark_room_status(allocated2.id, 'OCCUPIED')
    # No available rooms left
    with pytest.raises(Exception):
        room_service.allocate_room(1, room_type.id)

def test_rate_lookup(rate_plan_service, room_type_service, db_session):
    rt_data = type('obj', (object,), {'property_id': 1, 'name': 'Penthouse', 'base_rate': 500.0, 'dict': lambda self: {'property_id': 1, 'name': 'Penthouse', 'base_rate': 500.0}})()
    room_type = room_type_service.repo.create(rt_data)
    rp_data = type('obj', (object,), {'property_id': 1, 'room_type_id': room_type.id, 'name': 'Standard Rate', 'daily_rate': 500.0, 'start_date': None, 'end_date': None, 'dict': lambda self: {'property_id': 1, 'room_type_id': room_type.id, 'name': 'Standard Rate', 'daily_rate': 500.0, 'start_date': None, 'end_date': None}})()
    rate_plan = rate_plan_service.repo.create(rp_data)
    # Simulate get_rate_for_type
    found = rate_plan_service.repo.list(property_id=1)
    assert any(r.room_type_id == room_type.id and r.daily_rate == 500.0 for r in found)
