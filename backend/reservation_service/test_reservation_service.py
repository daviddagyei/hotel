import pytest
from backend.reservation_service.models import Reservation, ReservationStatusEnum
from backend.reservation_service.repository import ReservationRepository
from backend.reservation_service.service import ReservationService
from backend.room_service.service import RoomService
from backend.room_service.models import RoomType, Room
from backend.core.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer

# Minimal Guest model for test DB setup
class Guest(Base):
    __tablename__ = 'guests'
    id = Column(Integer, primary_key=True)

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
def room_service(db_session):
    return RoomService(db_session)

@pytest.fixture
def reservation_service(db_session, room_service):
    return ReservationService(db_session, room_service)

def test_create_reservation_and_room_allocation(reservation_service, room_service, db_session):
    # Setup: create RoomType and Room
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="101", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    # Create reservation
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1,
        guest_id=1,
        room_type_id=rt.id,
        check_in=check_in,
        check_out=check_out,
        price=200.0
    )
    assert reservation.id is not None
    assert reservation.room_id == room.id
    assert reservation.status == ReservationStatusEnum.BOOKED
    # Room should be marked OCCUPIED
    updated_room = room_service.repo.get(room.id)
    assert updated_room.status == "OCCUPIED"

def test_cancel_reservation_frees_room(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="102", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1,
        guest_id=2,
        room_type_id=rt.id,
        check_in=check_in,
        check_out=check_out,
        price=200.0
    )
    reservation_service.cancel_reservation(reservation.id)
    updated = reservation_service.repo.get(reservation.id)
    assert updated.status == ReservationStatusEnum.CANCELED
    # Room should be marked AVAILABLE
    updated_room = room_service.repo.get(room.id)
    assert updated_room.status == "AVAILABLE"

def test_check_in_and_check_out(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Suite", base_rate=200.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="201", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1,
        guest_id=3,
        room_type_id=rt.id,
        check_in=check_in,
        check_out=check_out,
        price=400.0
    )
    reservation_service.check_in(reservation.id)
    updated = reservation_service.repo.get(reservation.id)
    assert updated.status == ReservationStatusEnum.CHECKED_IN
    reservation_service.check_out(reservation.id)
    updated = reservation_service.repo.get(reservation.id)
    assert updated.status == ReservationStatusEnum.CHECKED_OUT
    # Room should be marked AVAILABLE after check-out
    updated_room = room_service.repo.get(room.id)
    assert updated_room.status == "AVAILABLE"

def test_no_double_booking(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Economy", base_rate=50.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="301", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1,
        guest_id=4,
        room_type_id=rt.id,
        check_in=check_in,
        check_out=check_out,
        price=100.0
    )
    # Try to book again for same room type and property (should fail)
    with pytest.raises(Exception):
        reservation_service.create_reservation(
            property_id=1,
            guest_id=5,
            room_type_id=rt.id,
            check_in=check_in,
            check_out=check_out,
            price=100.0
        )

def test_create_reservation_invalid_dates(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="103", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=2)
    check_out = datetime.now() + timedelta(days=1)  # check_out before check_in
    with pytest.raises(Exception):
        reservation_service.create_reservation(
            property_id=1,
            guest_id=6,
            room_type_id=rt.id,
            check_in=check_in,
            check_out=check_out,
            price=100.0
        )
    # Same day check-in/check-out
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in
    with pytest.raises(Exception):
        reservation_service.create_reservation(
            property_id=1,
            guest_id=7,
            room_type_id=rt.id,
            check_in=check_in,
            check_out=check_out,
            price=100.0
        )

def test_create_reservation_no_available_rooms(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    # No rooms added
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    with pytest.raises(Exception):
        reservation_service.create_reservation(
            property_id=1,
            guest_id=8,
            room_type_id=rt.id,
            check_in=check_in,
            check_out=check_out,
            price=100.0
        )

def test_cancel_already_canceled_reservation(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="104", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1,
        guest_id=9,
        room_type_id=rt.id,
        check_in=check_in,
        check_out=check_out,
        price=100.0
    )
    reservation_service.cancel_reservation(reservation.id)
    with pytest.raises(Exception):
        reservation_service.cancel_reservation(reservation.id)

def test_check_in_wrong_status(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="105", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1,
        guest_id=10,
        room_type_id=rt.id,
        check_in=check_in,
        check_out=check_out,
        price=100.0
    )
    reservation_service.cancel_reservation(reservation.id)
    with pytest.raises(Exception):
        reservation_service.check_in(reservation.id)

def test_check_out_wrong_status(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="106", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1,
        guest_id=11,
        room_type_id=rt.id,
        check_in=check_in,
        check_out=check_out,
        price=100.0
    )
    # Try to check out before check-in
    with pytest.raises(Exception):
        reservation_service.check_out(reservation.id)

def test_cancel_nonexistent_reservation(reservation_service):
    with pytest.raises(Exception):
        reservation_service.cancel_reservation(9999)

def test_check_in_nonexistent_reservation(reservation_service):
    with pytest.raises(Exception):
        reservation_service.check_in(9999)

def test_check_out_nonexistent_reservation(reservation_service):
    with pytest.raises(Exception):
        reservation_service.check_out(9999)

def test_overlapping_reservations_different_room_types(reservation_service, room_service, db_session):
    rt1 = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    rt2 = RoomType(property_id=1, name="Suite", base_rate=200.0)
    db_session.add_all([rt1, rt2])
    db_session.commit()
    room1 = Room(property_id=1, number="201", type_id=rt1.id, status="AVAILABLE")
    room2 = Room(property_id=1, number="202", type_id=rt2.id, status="AVAILABLE")
    db_session.add_all([room1, room2])
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    res1 = reservation_service.create_reservation(
        property_id=1,
        guest_id=12,
        room_type_id=rt1.id,
        check_in=check_in,
        check_out=check_out,
        price=100.0
    )
    res2 = reservation_service.create_reservation(
        property_id=1,
        guest_id=13,
        room_type_id=rt2.id,
        check_in=check_in,
        check_out=check_out,
        price=200.0
    )
    assert res1.id is not None and res2.id is not None

def test_create_reservation_nonexistent_room_type(reservation_service):
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    with pytest.raises(Exception):
        reservation_service.create_reservation(
            property_id=1,
            guest_id=14,
            room_type_id=9999,  # Non-existent
            check_in=check_in,
            check_out=check_out,
            price=100.0
        )

def test_create_reservation_nonexistent_property(reservation_service, room_service, db_session):
    # RoomType with property_id=2, but no rooms for property_id=2
    rt = RoomType(property_id=2, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    with pytest.raises(Exception):
        reservation_service.create_reservation(
            property_id=2,
            guest_id=15,
            room_type_id=rt.id,
            check_in=check_in,
            check_out=check_out,
            price=100.0
        )

def test_create_reservation_no_available_room(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    # No room added
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    with pytest.raises(Exception):
        reservation_service.create_reservation(
            property_id=1,
            guest_id=7,
            room_type_id=rt.id,
            check_in=check_in,
            check_out=check_out,
            price=100.0
        )

def test_cancel_reservation_already_canceled(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="104", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1,
        guest_id=9,
        room_type_id=rt.id,
        check_in=check_in,
        check_out=check_out,
        price=100.0
    )
    reservation_service.cancel_reservation(reservation.id)
    with pytest.raises(Exception):
        reservation_service.cancel_reservation(reservation.id)

def test_cancel_reservation_checked_in(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="105", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1,
        guest_id=10,
        room_type_id=rt.id,
        check_in=check_in,
        check_out=check_out,
        price=100.0
    )
    reservation_service.check_in(reservation.id)
    with pytest.raises(Exception):
        reservation_service.cancel_reservation(reservation.id)

def test_check_out_without_check_in(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="107", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1,
        guest_id=12,
        room_type_id=rt.id,
        check_in=check_in,
        check_out=check_out,
        price=100.0
    )
    with pytest.raises(Exception):
        reservation_service.check_out(reservation.id)

def test_check_out_twice(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="108", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1,
        guest_id=13,
        room_type_id=rt.id,
        check_in=check_in,
        check_out=check_out,
        price=100.0
    )
    reservation_service.check_in(reservation.id)
    reservation_service.check_out(reservation.id)
    with pytest.raises(Exception):
        reservation_service.check_out(reservation.id)

def test_double_booking_overlapping_dates(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Economy", base_rate=50.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="401", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in1 = datetime.now() + timedelta(days=1)
    check_out1 = check_in1 + timedelta(days=2)
    reservation_service.create_reservation(
        property_id=1,
        guest_id=14,
        room_type_id=rt.id,
        check_in=check_in1,
        check_out=check_out1,
        price=100.0
    )
    # Overlapping reservation
    check_in2 = check_in1 + timedelta(days=1)
    check_out2 = check_in2 + timedelta(days=2)
    with pytest.raises(Exception):
        reservation_service.create_reservation(
            property_id=1,
            guest_id=15,
            room_type_id=rt.id,
            check_in=check_in2,
            check_out=check_out2,
            price=100.0
        )

def test_double_booking_different_properties(reservation_service, room_service, db_session):
    rt1 = RoomType(property_id=1, name="Economy", base_rate=50.0)
    rt2 = RoomType(property_id=2, name="Economy", base_rate=50.0)
    db_session.add_all([rt1, rt2])
    db_session.commit()
    room1 = Room(property_id=1, number="501", type_id=rt1.id, status="AVAILABLE")
    room2 = Room(property_id=2, number="601", type_id=rt2.id, status="AVAILABLE")
    db_session.add_all([room1, room2])
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation1 = reservation_service.create_reservation(
        property_id=1,
        guest_id=16,
        room_type_id=rt1.id,
        check_in=check_in,
        check_out=check_out,
        price=100.0
    )
    # Should succeed for different property
    reservation2 = reservation_service.create_reservation(
        property_id=2,
        guest_id=17,
        room_type_id=rt2.id,
        check_in=check_in,
        check_out=check_out,
        price=100.0
    )
    assert reservation2.id is not None
    assert reservation2.room_id == room2.id
    assert reservation2.status == ReservationStatusEnum.BOOKED

def test_create_reservation_far_future_dates(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="999", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime(2100, 1, 1)
    check_out = datetime(2100, 1, 10)
    reservation = reservation_service.create_reservation(
        property_id=1, guest_id=1, room_type_id=rt.id, check_in=check_in, check_out=check_out, price=1000.0
    )
    assert reservation.check_in == check_in
    assert reservation.check_out == check_out

def test_create_reservation_past_dates_raises(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="998", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime(2000, 1, 1)
    check_out = datetime(2000, 1, 2)
    with pytest.raises(Exception):
        reservation_service.create_reservation(
            property_id=1, guest_id=1, room_type_id=rt.id, check_in=check_in, check_out=check_out, price=100.0
        )

def test_create_reservation_zero_price(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=0.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="997", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=1)
    reservation = reservation_service.create_reservation(
        property_id=1, guest_id=1, room_type_id=rt.id, check_in=check_in, check_out=check_out, price=0.0
    )
    assert reservation.price == 0.0

def test_create_reservation_negative_price_raises(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="996", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=1)
    with pytest.raises(Exception):
        reservation_service.create_reservation(
            property_id=1, guest_id=1, room_type_id=rt.id, check_in=check_in, check_out=check_out, price=-10.0
        )

def test_create_reservation_duplicate_room_number_different_type(reservation_service, room_service, db_session):
    rt1 = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    rt2 = RoomType(property_id=1, name="Suite", base_rate=200.0)
    db_session.add_all([rt1, rt2])
    db_session.commit()
    room1 = Room(property_id=1, number="500", type_id=rt1.id, status="AVAILABLE")
    room2 = Room(property_id=1, number="500", type_id=rt2.id, status="AVAILABLE")
    db_session.add_all([room1, room2])
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    res1 = reservation_service.create_reservation(
        property_id=1, guest_id=1, room_type_id=rt1.id, check_in=check_in, check_out=check_out, price=100.0
    )
    res2 = reservation_service.create_reservation(
        property_id=1, guest_id=2, room_type_id=rt2.id, check_in=check_in, check_out=check_out, price=200.0
    )
    assert res1.room_id != res2.room_id

def test_create_reservation_multiple_properties(reservation_service, room_service, db_session):
    rt1 = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    rt2 = RoomType(property_id=2, name="Suite", base_rate=200.0)
    db_session.add_all([rt1, rt2])
    db_session.commit()
    room1 = Room(property_id=1, number="100", type_id=rt1.id, status="AVAILABLE")
    room2 = Room(property_id=2, number="200", type_id=rt2.id, status="AVAILABLE")
    db_session.add_all([room1, room2])
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    res1 = reservation_service.create_reservation(
        property_id=1, guest_id=1, room_type_id=rt1.id, check_in=check_in, check_out=check_out, price=100.0
    )
    res2 = reservation_service.create_reservation(
        property_id=2, guest_id=2, room_type_id=rt2.id, check_in=check_in, check_out=check_out, price=200.0
    )
    assert res1.property_id != res2.property_id

def test_create_reservation_room_unavailable_after_booking(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="300", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation_service.create_reservation(
        property_id=1, guest_id=1, room_type_id=rt.id, check_in=check_in, check_out=check_out, price=100.0
    )
    # Room should now be unavailable
    with pytest.raises(Exception):
        reservation_service.create_reservation(
            property_id=1, guest_id=2, room_type_id=rt.id, check_in=check_in, check_out=check_out, price=100.0
        )

def test_cancel_reservation_frees_room_status(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="400", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1, guest_id=1, room_type_id=rt.id, check_in=check_in, check_out=check_out, price=100.0
    )
    reservation_service.cancel_reservation(reservation.id)
    updated_room = room_service.repo.get(room.id)
    assert updated_room.status == "AVAILABLE"

def test_cancel_reservation_twice_raises(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="401", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1, guest_id=1, room_type_id=rt.id, check_in=check_in, check_out=check_out, price=100.0
    )
    reservation_service.cancel_reservation(reservation.id)
    with pytest.raises(Exception):
        reservation_service.cancel_reservation(reservation.id)

def test_cancel_reservation_checked_out_raises(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="402", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1, guest_id=1, room_type_id=rt.id, check_in=check_in, check_out=check_out, price=100.0
    )
    reservation_service.check_in(reservation.id)
    reservation_service.check_out(reservation.id)
    with pytest.raises(Exception):
        reservation_service.cancel_reservation(reservation.id)

def test_check_in_already_checked_in_raises(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="403", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1, guest_id=1, room_type_id=rt.id, check_in=check_in, check_out=check_out, price=100.0
    )
    reservation_service.check_in(reservation.id)
    with pytest.raises(Exception):
        reservation_service.check_in(reservation.id)

def test_check_in_canceled_raises(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="404", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1, guest_id=1, room_type_id=rt.id, check_in=check_in, check_out=check_out, price=100.0
    )
    reservation_service.cancel_reservation(reservation.id)
    with pytest.raises(Exception):
        reservation_service.check_in(reservation.id)

def test_check_out_without_check_in_raises(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="405", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1, guest_id=1, room_type_id=rt.id, check_in=check_in, check_out=check_out, price=100.0
    )
    with pytest.raises(Exception):
        reservation_service.check_out(reservation.id)

def test_check_out_twice_raises(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="406", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1, guest_id=1, room_type_id=rt.id, check_in=check_in, check_out=check_out, price=100.0
    )
    reservation_service.check_in(reservation.id)
    reservation_service.check_out(reservation.id)
    with pytest.raises(Exception):
        reservation_service.check_out(reservation.id)

def test_check_out_canceled_raises(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="407", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1, guest_id=1, room_type_id=rt.id, check_in=check_in, check_out=check_out, price=100.0
    )
    reservation_service.cancel_reservation(reservation.id)
    with pytest.raises(Exception):
        reservation_service.check_out(reservation.id)

def test_check_out_checked_out_raises(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="408", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1, guest_id=1, room_type_id=rt.id, check_in=check_in, check_out=check_out, price=100.0
    )
    reservation_service.check_in(reservation.id)
    reservation_service.check_out(reservation.id)
    with pytest.raises(Exception):
        reservation_service.check_out(reservation.id)

def test_check_in_checked_out_raises(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="409", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1, guest_id=1, room_type_id=rt.id, check_in=check_in, check_out=check_out, price=100.0
    )
    reservation_service.check_in(reservation.id)
    reservation_service.check_out(reservation.id)
    with pytest.raises(Exception):
        reservation_service.check_in(reservation.id)

def test_create_reservation_with_payment_status(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="410", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1, guest_id=1, room_type_id=rt.id, check_in=check_in, check_out=check_out, price=100.0, payment_status="PAID"
    )
    assert reservation.payment_status == "PAID"

def test_create_reservation_with_null_payment_status(reservation_service, room_service, db_session):
    rt = RoomType(property_id=1, name="Deluxe", base_rate=100.0)
    db_session.add(rt)
    db_session.commit()
    room = Room(property_id=1, number="411", type_id=rt.id, status="AVAILABLE")
    db_session.add(room)
    db_session.commit()
    check_in = datetime.now() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    reservation = reservation_service.create_reservation(
        property_id=1, guest_id=1, room_type_id=rt.id, check_in=check_in, check_out=check_out, price=100.0, payment_status=None
    )
    assert reservation.payment_status is None
