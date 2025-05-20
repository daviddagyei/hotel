from backend.auth_service.models.staff import Staff
from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

class StaffRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, staff_id: int) -> Optional[Staff]:
        return self.db.query(Staff).filter(Staff.id == staff_id).first()

    def get_by_username(self, username: str) -> Optional[Staff]:
        return self.db.query(Staff).filter(Staff.username == username).first()

    def get_by_email(self, email: str) -> Optional[Staff]:
        # Case-insensitive email search
        return self.db.query(Staff).filter(func.lower(Staff.email) == email.lower()).first()

    def list(self, property_id: Optional[int] = None) -> list[Staff]:
        query = self.db.query(Staff)
        if property_id:
            query = query.filter(Staff.property_id == property_id)
        return query.all()

    def create(self, staff: Staff) -> Staff:
        try:
            # Check for case-insensitive email and username uniqueness
            if self.get_by_email(staff.email):
                raise ValueError('Email already exists')
            if self.get_by_username(staff.username):
                raise ValueError('Username already exists')
            self.db.add(staff)
            self.db.commit()
            self.db.refresh(staff)
            return staff
        except IntegrityError as e:
            self.db.rollback()
            if 'UNIQUE constraint failed: staff.email' in str(e.orig):
                raise ValueError('Email already exists')
            if 'UNIQUE constraint failed: staff.username' in str(e.orig):
                raise ValueError('Username already exists')
            raise

    def update(self, staff: Staff, data: dict) -> Staff:
        # Prevent updating to a duplicate email or username (case-insensitive)
        if 'email' in data:
            existing = self.get_by_email(data['email'])
            if existing and existing.id != staff.id:
                raise ValueError('Email already exists')
        if 'username' in data:
            existing = self.get_by_username(data['username'])
            if existing and existing.id != staff.id:
                raise ValueError('Username already exists')
        for key, value in data.items():
            if key == 'password':
                continue  # Password should be handled at the service layer
            setattr(staff, key, value)
        self.db.commit()
        self.db.refresh(staff)
        return staff

    def delete(self, staff: Staff):
        self.db.delete(staff)
        self.db.commit()
