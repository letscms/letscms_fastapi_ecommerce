import stripe
import os
from decimal import Decimal
from fastapi import HTTPException, status
from typing import Dict, Any

# Initialize Stripe (you'll need to set your Stripe keys in environment variables)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_your_stripe_secret_key")

class PaymentService:
    @staticmethod
    def create_payment_intent(amount: Decimal, currency: str = "usd", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a Stripe payment intent
        """
        try:
            # Convert amount to cents (Stripe uses cents)
            amount_cents = int(amount * 100)
            
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            
            return {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "amount": amount,
                "currency": currency
            }
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment processing error: {str(e)}"
            )
    
    @staticmethod
    def confirm_payment(payment_intent_id: str) -> bool:
        """
        Confirm a payment intent
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return intent.status == "succeeded"
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment confirmation error: {str(e)}"
            )
    
    @staticmethod
    def refund_payment(payment_intent_id: str, amount: Decimal = None) -> Dict[str, Any]:
        """
        Refund a payment
        """
        try:
            refund_data = {"payment_intent": payment_intent_id}
            if amount:
                refund_data["amount"] = int(amount * 100)  # Convert to cents
            
            refund = stripe.Refund.create(**refund_data)
            
            return {
                "refund_id": refund.id,
                "amount": Decimal(refund.amount) / 100,  # Convert back from cents
                "status": refund.status
            }
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Refund processing error: {str(e)}"
            )
