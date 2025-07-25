from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.utils.payment_service import PaymentService
from app.controllers import order_controller
from app.utils.auth_dependency import get_current_user
from app.models.user import User
from app.models.order import OrderStatus
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PaymentIntentRequest(BaseModel):
    order_id: int

class PaymentConfirmRequest(BaseModel):
    payment_intent_id: str
    order_id: int

class RefundRequest(BaseModel):
    payment_intent_id: str
    amount: Optional[Decimal] = None

@router.post("/create-payment-intent")
def create_payment_intent(
    request: PaymentIntentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a payment intent for an order
    """
    # Get the order
    order = order_controller.get_order_by_id(db, request.order_id, current_user.id)
    
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order cannot be paid"
        )
    
    # Create payment intent
    metadata = {
        "order_id": str(order.id),
        "user_id": str(current_user.id)
    }
    
    payment_intent = PaymentService.create_payment_intent(
        amount=order.total_amount,
        metadata=metadata
    )
    
    return payment_intent

@router.post("/confirm-payment")
def confirm_payment(
    request: PaymentConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Confirm payment and update order status
    """
    # Verify payment
    is_paid = PaymentService.confirm_payment(request.payment_intent_id)
    
    if not is_paid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment not successful"
        )
    
    # Update order
    from app.schemas.order_schema import OrderUpdate
    order_update = OrderUpdate(
        status=OrderStatus.CONFIRMED,
        payment_status="paid"
    )
    
    updated_order = order_controller.update_order(db, request.order_id, order_update)
    
    return {
        "message": "Payment confirmed successfully",
        "order": updated_order
    }

@router.post("/refund")
def refund_payment(
    request: RefundRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Refund a payment (admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    refund = PaymentService.refund_payment(
        request.payment_intent_id,
        request.amount
    )
    
    return {
        "message": "Refund processed successfully",
        "refund": refund
    }
