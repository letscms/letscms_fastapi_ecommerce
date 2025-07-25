from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.controllers import product_controller
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductOut, ProductWithCategory
from app.utils.auth_dependency import get_current_user, get_current_admin_user
from typing import List, Optional

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ProductOut, dependencies=[Depends(get_current_admin_user)])
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    return product_controller.create_product(db, product)

@router.get("/", response_model=List[ProductWithCategory])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category_id: Optional[int] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    return product_controller.get_products(db, skip, limit, category_id, active_only)

@router.get("/search", response_model=List[ProductWithCategory])
def search_products(
    q: str = Query(..., min_length=2),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return product_controller.search_products(db, q, skip, limit)

@router.get("/{product_id}", response_model=ProductWithCategory)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return product_controller.get_product_by_id(db, product_id)

@router.get("/sku/{sku}", response_model=ProductOut)
def get_product_by_sku(sku: str, db: Session = Depends(get_db)):
    return product_controller.get_product_by_sku(db, sku)

@router.put("/{product_id}", response_model=ProductOut, dependencies=[Depends(get_current_admin_user)])
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
):
    return product_controller.update_product(db, product_id, product_update)

@router.delete("/{product_id}", dependencies=[Depends(get_current_admin_user)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    return product_controller.delete_product(db, product_id)
