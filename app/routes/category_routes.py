from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.controllers import category_controller
from app.schemas.category_schema import CategoryCreate, CategoryUpdate, CategoryOut
from app.utils.auth_dependency import get_current_user, get_current_admin_user
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=CategoryOut, dependencies=[Depends(get_current_admin_user)])
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    return category_controller.create_category(db, category)

@router.get("/", response_model=List[CategoryOut])
def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    return category_controller.get_categories(db, skip, limit, active_only)

@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return category_controller.get_category_by_id(db, category_id)

@router.put("/{category_id}", response_model=CategoryOut, dependencies=[Depends(get_current_admin_user)])
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db)
):
    return category_controller.update_category(db, category_id, category_update)

@router.delete("/{category_id}", dependencies=[Depends(get_current_admin_user)])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    return category_controller.delete_category(db, category_id)
