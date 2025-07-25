from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum

class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price: Decimal

class OrderItemOut(OrderItemBase):
    id: int
    order_id: int
    created_at: datetime
    product: Optional[dict] = None

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    shipping_address: str
    billing_address: str
    payment_method: str
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[OrderStatusEnum] = None
    payment_status: Optional[str] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None

class OrderOut(OrderBase):
    id: int
    user_id: int
    total_amount: Decimal
    status: OrderStatusEnum
    payment_status: str
    tracking_number: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    order_items: List[OrderItemOut] = []

    class Config:
        from_attributes = True
