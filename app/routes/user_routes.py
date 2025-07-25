from fastapi import APIRouter, Depends, Body, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.controllers import user_controller
from app.schemas.user_schema import UserCreate, UserLogin, UserOut, UserUpdate
from app.utils.auth_dependency import get_current_user, get_current_admin_user
from app.models.user import User
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return user_controller.create_user(db, user)

@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    return user_controller.login_user(db, data.email, data.password)

@router.get("/", response_model=List[UserOut], dependencies=[Depends(get_current_admin_user)])
def all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return user_controller.get_users(db, skip, limit)

@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=UserOut, dependencies=[Depends(get_current_admin_user)])
def one_user(user_id: int, db: Session = Depends(get_db)):
    return user_controller.get_user_by_id(db, user_id)

@router.put("/me", response_model=UserOut)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return user_controller.update_user(db, current_user.id, user_update)

@router.put("/{user_id}", response_model=UserOut, dependencies=[Depends(get_current_admin_user)])
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    return user_controller.update_user(db, user_id, user_update)

@router.delete("/{user_id}", dependencies=[Depends(get_current_admin_user)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return user_controller.delete_user(db, user_id)

@router.post("/{user_id}/activate", response_model=UserOut, dependencies=[Depends(get_current_admin_user)])
def activate_user(user_id: int, db: Session = Depends(get_db)):
    return user_controller.activate_user(db, user_id)

@router.post("/{user_id}/make-admin", response_model=UserOut, dependencies=[Depends(get_current_admin_user)])
def make_admin(user_id: int, db: Session = Depends(get_db)):
    return user_controller.make_admin(db, user_id)
