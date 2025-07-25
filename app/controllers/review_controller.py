from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.review import Review
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.schemas.review_schema import ReviewCreate, ReviewUpdate

def create_review(db: Session, user_id: int, review: ReviewCreate):
    # Check if product exists
    product = db.query(Product).filter(Product.id == review.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if user has purchased this product
    order_item = db.query(OrderItem).join(Order).filter(
        Order.user_id == user_id,
        OrderItem.product_id == review.product_id
    ).first()
    
    if not order_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only review products you have purchased"
        )
    
    # Check if user has already reviewed this product
    existing_review = db.query(Review).filter(
        Review.user_id == user_id,
        Review.product_id == review.product_id
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this product"
        )
    
    # Validate rating
    if not 1 <= review.rating <= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    
    db_review = Review(user_id=user_id, **review.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_reviews(db: Session, product_id: int = None, user_id: int = None, 
                skip: int = 0, limit: int = 100):
    query = db.query(Review).options(
        joinedload(Review.user),
        joinedload(Review.product)
    )
    
    if product_id:
        query = query.filter(Review.product_id == product_id)
    
    if user_id:
        query = query.filter(Review.user_id == user_id)
    
    return query.offset(skip).limit(limit).all()

def get_review_by_id(db: Session, review_id: int):
    review = db.query(Review).options(
        joinedload(Review.user),
        joinedload(Review.product)
    ).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    return review

def update_review(db: Session, review_id: int, user_id: int, review_update: ReviewUpdate):
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == user_id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Validate rating if provided
    if review_update.rating and not 1 <= review_update.rating <= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    
    update_data = review_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)
    
    db.commit()
    db.refresh(review)
    return review

def delete_review(db: Session, review_id: int, user_id: int):
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == user_id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    db.delete(review)
    db.commit()
    return {"message": "Review deleted successfully"}
