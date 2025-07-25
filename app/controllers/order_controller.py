from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.order import Order, OrderItem, OrderStatus
from app.models.cart import CartItem
from app.models.product import Product
from app.schemas.order_schema import OrderCreate, OrderUpdate
from decimal import Decimal
from typing import List, Optional

def create_order(db: Session, user_id: int, order: OrderCreate):
    # Get cart items
    cart_items = db.query(CartItem).options(
        joinedload(CartItem.product)
    ).filter(CartItem.user_id == user_id).all()
    
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )
    
    # Check stock availability for all items
    for cart_item in cart_items:
        if cart_item.product.stock_quantity < cart_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {cart_item.product.name}"
            )
    
    # Calculate total amount
    total_amount = sum(
        Decimal(str(cart_item.product.price)) * cart_item.quantity 
        for cart_item in cart_items
    )
    
    # Create order
    db_order = Order(
        user_id=user_id,
        total_amount=total_amount,
        shipping_address=order.shipping_address,
        billing_address=order.billing_address,
        payment_method=order.payment_method,
        notes=order.notes
    )
    db.add(db_order)
    db.flush()  # Get the order ID
    
    # Create order items and update stock
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=db_order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )
        db.add(order_item)
        
        # Update product stock
        cart_item.product.stock_quantity -= cart_item.quantity
    
    # Clear cart
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders(db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    query = db.query(Order).options(
        joinedload(Order.order_items).joinedload(OrderItem.product),
        joinedload(Order.user)
    )
    
    if user_id:
        query = query.filter(Order.user_id == user_id)
    
    return query.offset(skip).limit(limit).all()

def get_order_by_id(db: Session, order_id: int, user_id: Optional[int] = None):
    query = db.query(Order).options(
        joinedload(Order.order_items).joinedload(OrderItem.product),
        joinedload(Order.user)
    ).filter(Order.id == order_id)
    
    if user_id:
        query = query.filter(Order.user_id == user_id)
    
    order = query.first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order

def update_order(db: Session, order_id: int, order_update: OrderUpdate):
    order = get_order_by_id(db, order_id)
    
    update_data = order_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    return order

def cancel_order(db: Session, order_id: int, user_id: Optional[int] = None):
    order = get_order_by_id(db, order_id, user_id)
    
    if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel order that is already shipped or delivered"
        )
    
    # Restore stock
    for order_item in order.order_items:
        product = db.query(Product).filter(Product.id == order_item.product_id).first()
        if product:
            product.stock_quantity += order_item.quantity
    
    order.status = OrderStatus.CANCELLED
    db.commit()
    db.refresh(order)
    return order
