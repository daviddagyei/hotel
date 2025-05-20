from backend.reservation_service.repository import ReservationRepository
from backend.reservation_service.models import ReservationStatusEnum
from backend.room_service.service import RoomService
from sqlalchemy.orm import Session
from datetime import datetime
from backend.reservation_service.exceptions import ReservationError, RoomUnavailableError, InvalidReservationStatus

class ReservationService:
    def __init__(self, db: Session, room_service: RoomService):
        self.repo = ReservationRepository(db)
        self.room_service = room_service

    def create_reservation(self, property_id, guest_id, room_type_id, check_in, check_out, price=None, payment_status=None):
        # Rigorous business logic: check dates
        now = datetime.now()
        if check_in >= check_out:
            raise ReservationError("Check-in date must be before check-out date.")
        if check_in < now or check_out < now:
            raise ReservationError("Cannot create reservation in the past.")
        if price is not None and price < 0:
            raise ReservationError("Price cannot be negative.")
        # Optionally: check for overlapping reservations for the same room type/property
        # Allocate room via RoomService
        room = self.room_service.allocate_room(property_id, room_type_id)
        reservation = self.repo.create(type('obj', (object,), {
            'property_id': property_id,
            'guest_id': guest_id,
            'room_id': room.id,
            'check_in': check_in,
            'check_out': check_out,
            'price': price,
            'payment_status': payment_status,
            'dict': lambda self: {
                'property_id': property_id,
                'guest_id': guest_id,
                'room_id': room.id,
                'check_in': check_in,
                'check_out': check_out,
                'price': price,
                'payment_status': payment_status
            }
        })())
        # Mark room as OCCUPIED/BOOKED
        self.room_service.mark_room_status(room.id, 'OCCUPIED')
        return reservation

    def cancel_reservation(self, reservation_id):
        reservation = self.repo.get(reservation_id)
        if not reservation:
            raise AttributeError(f"Reservation {reservation_id} not found")
        if reservation.status == ReservationStatusEnum.CANCELED:
            raise InvalidReservationStatus("Reservation is already canceled.")
        if reservation.status == ReservationStatusEnum.CHECKED_IN:
            raise InvalidReservationStatus("Cannot cancel a checked-in reservation.")
        if reservation.status == ReservationStatusEnum.CHECKED_OUT:
            raise InvalidReservationStatus("Cannot cancel a checked-out reservation.")
        reservation.status = ReservationStatusEnum.CANCELED
        self.repo.db.commit()
        # Free up the room
        if reservation.room_id:
            self.room_service.mark_room_status(reservation.room_id, 'AVAILABLE')
        return reservation

    def check_in(self, reservation_id):
        reservation = self.repo.get(reservation_id)
        if not reservation:
            raise AttributeError(f"Reservation {reservation_id} not found")
        if reservation.status != ReservationStatusEnum.BOOKED:
            raise InvalidReservationStatus("Can only check in a BOOKED reservation.")
        reservation.status = ReservationStatusEnum.CHECKED_IN
        self.repo.db.commit()
        return reservation

    def check_out(self, reservation_id):
        reservation = self.repo.get(reservation_id)
        if not reservation:
            raise AttributeError(f"Reservation {reservation_id} not found")
        if reservation.status != ReservationStatusEnum.CHECKED_IN:
            raise InvalidReservationStatus("Can only check out a CHECKED_IN reservation.")
        reservation.status = ReservationStatusEnum.CHECKED_OUT
        self.repo.db.commit()
        # Free up the room
        if reservation.room_id:
            self.room_service.mark_room_status(reservation.room_id, 'AVAILABLE')
        return reservation
