import httpx
from backend.reservation_service.repository import ReservationRepository
from backend.reservation_service.models import ReservationStatusEnum
from backend.room_service.service import RoomService
from sqlalchemy.orm import Session
from datetime import datetime
from backend.reservation_service.exceptions import ReservationError, RoomUnavailableError, InvalidReservationStatus

ROOM_SERVICE_URL = "http://localhost:8001/api/v1/room-service/rooms"

class ReservationService:
    def __init__(self, db: Session, room_service: RoomService):
        self.repo = ReservationRepository(db)
        self.room_service = room_service

    async def get_room_http(self, room_id):
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{ROOM_SERVICE_URL}?property_id=1")
            resp.raise_for_status()
            rooms = resp.json()
            for room in rooms:
                if room["id"] == room_id:
                    return room
            return None

    async def mark_room_status_http(self, room_id, status):
        async with httpx.AsyncClient() as client:
            resp = await client.patch(f"{ROOM_SERVICE_URL}/{room_id}", json={"status": status})
            resp.raise_for_status()
            return resp.json()

    def create_reservation(self, property_id, guest_id, room_type_id, check_in, check_out, price=None, payment_status=None, room_id=None):
        import asyncio
        now = datetime.now()
        if check_in >= check_out:
            raise ReservationError("Check-in date must be before check-out date.")
        if check_in < now or check_out < now:
            raise ReservationError("Cannot create reservation in the past.")
        if price is not None and price < 0:
            raise ReservationError("Price cannot be negative.")
        # Use provided room_id if given, else allocate by type
        if room_id:
            room = asyncio.run(self.get_room_http(room_id))
            if not room:
                raise RoomUnavailableError(f"Room {room_id} not found.")
            if room["status"] != "AVAILABLE":
                raise RoomUnavailableError(f"Room {room_id} is not available.")
            asyncio.run(self.mark_room_status_http(room_id, "OCCUPIED"))
        else:
            raise RoomUnavailableError("room_id is required for reservation in microservice mode.")
        reservation = self.repo.create(type('obj', (object,), {
            'property_id': property_id,
            'guest_id': guest_id,
            'room_id': room_id,
            'check_in': check_in,
            'check_out': check_out,
            'price': price,
            'payment_status': payment_status,
            'dict': lambda self: {
                'property_id': property_id,
                'guest_id': guest_id,
                'room_id': room_id,
                'check_in': check_in,
                'check_out': check_out,
                'price': price,
                'payment_status': payment_status
            }
        })())
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

    def list_reservations(self, property_id=None, guest_id=None, start_date=None, end_date=None):
        return self.repo.list_reservations(property_id, guest_id, start_date, end_date)
