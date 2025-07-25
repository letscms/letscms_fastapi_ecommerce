from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemOut(CartItemBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    product: Optional[dict] = None

    class Config:
        from_attributes = True

class CartOut(BaseModel):
    items: List[CartItemOut]
    total_items: int
    total_amount: float
