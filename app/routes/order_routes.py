from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.controllers import order_controller
from app.schemas.order_schema import OrderCreate, OrderUpdate, OrderOut
from app.utils.auth_dependency import get_current_user, get_current_admin_user
from app.models.user import User
from typing import List, Optional

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=OrderOut)
def create_order(
    order: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return order_controller.create_order(db, current_user.id, order)

@router.get("/", response_model=List[OrderOut])
def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return order_controller.get_orders(db, current_user.id, skip, limit)

@router.get("/admin", response_model=List[OrderOut], dependencies=[Depends(get_current_admin_user)])
def get_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    return order_controller.get_orders(db, user_id, skip, limit)

@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return order_controller.get_order_by_id(db, order_id, current_user.id)

@router.get("/admin/{order_id}", response_model=OrderOut, dependencies=[Depends(get_current_admin_user)])
def get_order_admin(order_id: int, db: Session = Depends(get_db)):
    return order_controller.get_order_by_id(db, order_id)

@router.put("/{order_id}", response_model=OrderOut, dependencies=[Depends(get_current_admin_user)])
def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db)
):
    return order_controller.update_order(db, order_id, order_update)

@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return order_controller.cancel_order(db, order_id, current_user.id)
