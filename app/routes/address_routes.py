from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.controllers import address_controller
from app.schemas.address_schema import AddressCreate, AddressUpdate, AddressOut
from app.utils.auth_dependency import get_current_user
from app.models.user import User
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=AddressOut)
def create_address(
    address: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return address_controller.create_address(db, current_user.id, address)

@router.get("/", response_model=List[AddressOut])
def get_addresses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return address_controller.get_addresses(db, current_user.id)

@router.get("/{address_id}", response_model=AddressOut)
def get_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return address_controller.get_address_by_id(db, address_id, current_user.id)

@router.put("/{address_id}", response_model=AddressOut)
def update_address(
    address_id: int,
    address_update: AddressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return address_controller.update_address(db, address_id, current_user.id, address_update)

@router.delete("/{address_id}")
def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return address_controller.delete_address(db, address_id, current_user.id)
