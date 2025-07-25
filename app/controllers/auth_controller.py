from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from app import models
from app.schemas.user_schema import UserCreate
from app.utils.jwt_handler import create_access_token

def create_user(db: Session, user: UserCreate):
    existing_user = db.query(models.user.User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = bcrypt.hash(user.password)
    new_user = models.user.User(
        username=user.username, email=user.email, hashed_password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def login_user(db: Session, email: str, password: str):
    user = db.query(models.user.User).filter_by(email=email).first()
    if not user or not bcrypt.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user.email})
    return {"access_token": token}
