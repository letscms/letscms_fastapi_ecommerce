from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.controllers import review_controller
from app.schemas.review_schema import ReviewCreate, ReviewUpdate, ReviewOut
from app.utils.auth_dependency import get_current_user
from app.models.user import User
from typing import List, Optional

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ReviewOut)
def create_review(
    review: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return review_controller.create_review(db, current_user.id, review)

@router.get("/", response_model=List[ReviewOut])
def get_reviews(
    product_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return review_controller.get_reviews(db, product_id, None, skip, limit)

@router.get("/my", response_model=List[ReviewOut])
def get_my_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return review_controller.get_reviews(db, None, current_user.id, skip, limit)

@router.get("/{review_id}", response_model=ReviewOut)
def get_review(review_id: int, db: Session = Depends(get_db)):
    return review_controller.get_review_by_id(db, review_id)

@router.put("/{review_id}", response_model=ReviewOut)
def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return review_controller.update_review(db, review_id, current_user.id, review_update)

@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return review_controller.delete_review(db, review_id, current_user.id)
