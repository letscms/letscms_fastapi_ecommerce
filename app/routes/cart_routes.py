from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.controllers import cart_controller
from app.schemas.cart_schema import CartItemCreate, CartItemUpdate, CartItemOut, CartOut
from app.utils.auth_dependency import get_current_user
from app.models.user import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/add", response_model=CartItemOut)
def add_to_cart(
    cart_item: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return cart_controller.add_to_cart(db, current_user.id, cart_item)

@router.get("/", response_model=CartOut)
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return cart_controller.get_cart(db, current_user.id)

@router.put("/items/{item_id}", response_model=CartItemOut)
def update_cart_item(
    item_id: int,
    cart_update: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return cart_controller.update_cart_item(db, current_user.id, item_id, cart_update)

@router.delete("/items/{item_id}")
def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return cart_controller.remove_from_cart(db, current_user.id, item_id)

@router.delete("/clear")
def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return cart_controller.clear_cart(db, current_user.id)
