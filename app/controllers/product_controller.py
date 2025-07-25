from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.product import Product
from app.models.category import Category
from app.schemas.product_schema import ProductCreate, ProductUpdate
from typing import Optional

def create_product(db: Session, product: ProductCreate):
    # Check if category exists
    category = db.query(Category).filter(Category.id == product.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found"
        )
    
    # Check if SKU already exists
    existing_product = db.query(Product).filter(Product.sku == product.sku).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this SKU already exists"
        )
    
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products(db: Session, skip: int = 0, limit: int = 100, 
                category_id: Optional[int] = None, active_only: bool = True):
    query = db.query(Product).options(joinedload(Product.category))
    
    if active_only:
        query = query.filter(Product.is_active == True)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    return query.offset(skip).limit(limit).all()

def get_product_by_id(db: Session, product_id: int):
    product = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.reviews)
    ).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

def get_product_by_sku(db: Session, sku: str):
    product = db.query(Product).filter(Product.sku == sku).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

def update_product(db: Session, product_id: int, product_update: ProductUpdate):
    product = get_product_by_id(db, product_id)
    
    # If updating category, check if it exists
    if product_update.category_id:
        category = db.query(Category).filter(Category.id == product_update.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )
    
    # If updating SKU, check if it's unique
    if product_update.sku and product_update.sku != product.sku:
        existing_product = db.query(Product).filter(Product.sku == product_update.sku).first()
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this SKU already exists"
            )
    
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product

def delete_product(db: Session, product_id: int):
    product = get_product_by_id(db, product_id)
    
    # Soft delete by setting is_active to False
    product.is_active = False
    db.commit()
    return {"message": "Product deleted successfully"}

def search_products(db: Session, query: str, skip: int = 0, limit: int = 100):
    products = db.query(Product).options(joinedload(Product.category)).filter(
        Product.is_active == True,
        (Product.name.ilike(f"%{query}%") | 
         Product.description.ilike(f"%{query}%"))
    ).offset(skip).limit(limit).all()
    
    return products
