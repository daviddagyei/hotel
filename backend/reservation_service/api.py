from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.reservation_service.schemas import ReservationCreate, ReservationRead, ReservationUpdate
from backend.reservation_service.repository import ReservationRepository
from backend.reservation_service.service import ReservationService
from backend.room_service.service import RoomService
from backend.reservation_service.config import SessionLocal
from backend.reservation_service.exceptions import ReservationError, RoomUnavailableError

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_room_service(db: Session = Depends(get_db)):
    return RoomService(db)

def get_reservation_service(db: Session = Depends(get_db), room_service: RoomService = Depends(get_room_service)):
    return ReservationService(db, room_service)

@router.post("/reservations", response_model=ReservationRead)
@router.post("/reservations/", response_model=ReservationRead)
def create_reservation(reservation: ReservationCreate, service: ReservationService = Depends(get_reservation_service)):
    try:
        res = service.create_reservation(
            property_id=reservation.property_id,
            guest_id=reservation.guest_id,
            room_type_id=None,  # For MVP, assume room_id is provided directly
            check_in=reservation.check_in,
            check_out=reservation.check_out,
            price=reservation.price,
            payment_status=reservation.payment_status,
            room_id=reservation.room_id
        )
        return res
    except (ReservationError, RoomUnavailableError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/reservations/{reservation_id}", response_model=ReservationRead)
def update_reservation(reservation_id: int, update: ReservationUpdate, service: ReservationService = Depends(get_reservation_service)):
    res = service.repo.update(reservation_id, update)
    return res

@router.post("/reservations/{reservation_id}/cancel", response_model=ReservationRead)
def cancel_reservation(reservation_id: int, service: ReservationService = Depends(get_reservation_service)):
    return service.cancel_reservation(reservation_id)

@router.post("/reservations/{reservation_id}/checkin", response_model=ReservationRead)
def check_in(reservation_id: int, service: ReservationService = Depends(get_reservation_service)):
    return service.check_in(reservation_id)

@router.post("/reservations/{reservation_id}/checkout", response_model=ReservationRead)
def check_out(reservation_id: int, service: ReservationService = Depends(get_reservation_service)):
    return service.check_out(reservation_id)

@router.get("/reservations/{reservation_id}", response_model=ReservationRead)
def get_reservation(reservation_id: int, service: ReservationService = Depends(get_reservation_service)):
    res = service.repo.get(reservation_id)
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return res

@router.get("/reservations", response_model=List[ReservationRead])
def list_reservations(
    property_id: Optional[int] = Query(None),
    guest_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    service: ReservationService = Depends(get_reservation_service)
):
    # This assumes ReservationService has a method to filter reservations
    return service.repo.list_reservations(
        property_id=property_id,
        guest_id=guest_id,
        start_date=start_date,
        end_date=end_date
    )

@router.delete("/reservations/{reservation_id}", response_model=None)
def delete_reservation(reservation_id: int, service: ReservationService = Depends(get_reservation_service)):
    res = service.repo.get(reservation_id)
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")
    # Set room status to AVAILABLE via HTTP if reservation has a room_id
    if res.room_id:
        import httpx
        ROOM_SERVICE_URL = "http://localhost:8001/api/v1/room-service/rooms"
        try:
            with httpx.Client() as client:
                client.patch(f"{ROOM_SERVICE_URL}/{res.room_id}", json={"status": "AVAILABLE"})
        except Exception:
            pass  # Ignore if room is already available or not found
    service.repo.delete(reservation_id)
    return {"detail": "Reservation deleted"}
