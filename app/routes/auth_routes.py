from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.controllers import auth_controller
from app.schemas.user_schema import UserCreate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    return auth_controller.create_user(db, user)

@router.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    return auth_controller.login_user(db, data["email"], data["password"])
