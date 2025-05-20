from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.reservation_service.schemas import ReservationCreate, ReservationRead, ReservationUpdate
from backend.reservation_service.repository import ReservationRepository
from backend.reservation_service.service import ReservationService
from backend.room_service.service import RoomService
from backend.room_service.config import SessionLocal

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
            payment_status=reservation.payment_status
        )
        return res
    except Exception as e:
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
