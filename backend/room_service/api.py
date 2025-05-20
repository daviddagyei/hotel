from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from .config import SessionLocal
from .schemas import (
    PropertyCreate, PropertyRead, RoomTypeCreate, RoomTypeRead, RoomCreate, RoomRead, RatePlanCreate, RatePlanRead, RoomStatusLogRead, RoomUpdate
)
from .service import (
    PropertyService, RoomService, RoomTypeService, RatePlanService, RoomStatusLogService
)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Property endpoints
@router.get("/properties", response_model=list[PropertyRead])
def list_properties(db: Session = Depends(get_db)):
    return PropertyService(db).repo.list()

@router.post("/properties", response_model=PropertyRead)
def create_property(data: PropertyCreate, db: Session = Depends(get_db)):
    return PropertyService(db).repo.create(data)

# RoomType endpoints
@router.get("/room-types", response_model=list[RoomTypeRead])
def list_room_types(db: Session = Depends(get_db)):
    return RoomTypeService(db).repo.list()

@router.post("/room-types", response_model=RoomTypeRead)
def create_room_type(data: RoomTypeCreate, db: Session = Depends(get_db)):
    return RoomTypeService(db).repo.create(data)

# Room endpoints
@router.get("/rooms", response_model=list[RoomRead])
def list_rooms(db: Session = Depends(get_db)):
    return RoomService(db).repo.list()

@router.post("/rooms", response_model=RoomRead)
def create_room(data: RoomCreate, db: Session = Depends(get_db)):
    try:
        return RoomService(db).repo.create(data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.patch("/rooms/{room_id}", response_model=RoomRead)
def update_room(room_id: int, update: RoomUpdate = Body(...), db: Session = Depends(get_db)):
    room = RoomService(db).repo.get(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    try:
        updated = RoomService(db).repo.update(room_id, update)
        return updated
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.delete("/rooms/{room_id}", response_model=None)
def delete_room(room_id: int, db: Session = Depends(get_db)):
    room = RoomService(db).repo.get(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    RoomService(db).repo.delete(room_id)
    return {"detail": "Room deleted"}

# RatePlan endpoints
@router.get("/rate-plans", response_model=list[RatePlanRead])
def list_rate_plans(db: Session = Depends(get_db)):
    return RatePlanService(db).repo.list()

@router.post("/rate-plans", response_model=RatePlanRead)
def create_rate_plan(data: RatePlanCreate, db: Session = Depends(get_db)):
    return RatePlanService(db).repo.create(data)

# RoomStatusLog endpoints
@router.get("/room-status-logs", response_model=list[RoomStatusLogRead])
def list_room_status_logs(db: Session = Depends(get_db)):
    return RoomStatusLogService(db).repo.list()
