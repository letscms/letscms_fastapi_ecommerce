from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database import SessionLocal
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem, OrderStatus
from app.models.category import Category
from app.utils.auth_dependency import get_current_admin_user
from datetime import datetime, timedelta
from typing import Dict, List, Any

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/stats")
def get_dashboard_stats(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get dashboard statistics for admin
    """
    # Total users
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # Total products
    total_products = db.query(Product).count()
    active_products = db.query(Product).filter(Product.is_active == True).count()
    
    # Total orders
    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).count()
    confirmed_orders = db.query(Order).filter(Order.status == OrderStatus.CONFIRMED).count()
    shipped_orders = db.query(Order).filter(Order.status == OrderStatus.SHIPPED).count()
    delivered_orders = db.query(Order).filter(Order.status == OrderStatus.DELIVERED).count()
    
    # Revenue
    total_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.DELIVERED])
    ).scalar() or 0
    
    # This month's revenue
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.created_at >= current_month_start,
        Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.DELIVERED])
    ).scalar() or 0
    
    # Categories
    total_categories = db.query(Category).count()
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users
        },
        "products": {
            "total": total_products,
            "active": active_products,
            "inactive": total_products - active_products
        },
        "orders": {
            "total": total_orders,
            "pending": pending_orders,
            "confirmed": confirmed_orders,
            "shipped": shipped_orders,
            "delivered": delivered_orders
        },
        "revenue": {
            "total": float(total_revenue),
            "monthly": float(monthly_revenue)
        },
        "categories": total_categories
    }

@router.get("/recent-orders")
def get_recent_orders(
    limit: int = Query(10, ge=1, le=50),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get recent orders for admin dashboard
    """
    orders = db.query(Order).order_by(desc(Order.created_at)).limit(limit).all()
    
    return [
        {
            "id": order.id,
            "user_id": order.user_id,
            "total_amount": float(order.total_amount),
            "status": order.status.value,
            "created_at": order.created_at,
            "user_email": order.user.email if order.user else None
        }
        for order in orders
    ]

@router.get("/top-products")
def get_top_products(
    limit: int = Query(10, ge=1, le=50),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get top selling products
    """
    top_products = db.query(
        Product.id,
        Product.name,
        Product.price,
        func.sum(OrderItem.quantity).label('total_sold')
    ).join(OrderItem).join(Order).filter(
        Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.DELIVERED])
    ).group_by(Product.id, Product.name, Product.price).order_by(
        desc(func.sum(OrderItem.quantity))
    ).limit(limit).all()
    
    return [
        {
            "id": product.id,
            "name": product.name,
            "price": float(product.price),
            "total_sold": product.total_sold
        }
        for product in top_products
    ]

@router.get("/low-stock-products")
def get_low_stock_products(
    threshold: int = Query(10, ge=1),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get products with low stock
    """
    low_stock_products = db.query(Product).filter(
        Product.stock_quantity <= threshold,
        Product.is_active == True
    ).order_by(Product.stock_quantity).all()
    
    return [
        {
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "stock_quantity": product.stock_quantity,
            "price": float(product.price)
        }
        for product in low_stock_products
    ]

@router.get("/revenue-chart")
def get_revenue_chart(
    days: int = Query(30, ge=7, le=365),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get revenue data for chart
    """
    start_date = datetime.now() - timedelta(days=days)
    
    # Daily revenue for the specified period
    daily_revenue = db.query(
        func.date(Order.created_at).label('date'),
        func.sum(Order.total_amount).label('revenue')
    ).filter(
        Order.created_at >= start_date,
        Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.DELIVERED])
    ).group_by(func.date(Order.created_at)).order_by(func.date(Order.created_at)).all()
    
    return {
        "period_days": days,
        "data": [
            {
                "date": revenue.date.isoformat(),
                "revenue": float(revenue.revenue)
            }
            for revenue in daily_revenue
        ]
    }
