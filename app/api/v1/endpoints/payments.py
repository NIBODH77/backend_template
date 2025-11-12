from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.payment_service import PaymentService
from app.services.commission_service import CommissionService
from app.services.order_service import OrderService
from app.services.plan_service import PlanService
from app.schemas.users import User
from app.models.payment import PaymentType, PaymentStatus
from pydantic import BaseModel


router = APIRouter()


# --------------------------------------------------------
# Request/Response Schemas
# --------------------------------------------------------
class CreatePaymentRequest(BaseModel):
    """
    Unified payment creation request for both subscription and server payments
    """
    payment_type: str  # 'subscription' or 'server'
    plan_id: int
    billing_cycle: Optional[str] = 'one_time'  # For subscription: 'one_time', 'monthly', 'quarterly', etc.
    server_config: Optional[Dict[str, Any]] = None  # For server purchase


class VerifyPaymentRequest(BaseModel):
    """Payment verification request"""
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


# --------------------------------------------------------
# ✅ Create Payment Order (Subscription or Server)
# --------------------------------------------------------
@router.post("/create-order")
async def create_payment_order(
    payment_request: CreatePaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create Razorpay payment order for subscription (499 plan) or server purchase
    
    This endpoint:
    1. Creates a PaymentTransaction record
    2. Calculates user-specific discount
    3. Creates Razorpay order
    4. Returns order details for frontend payment
    """
    payment_service = PaymentService()
    plan_service = PlanService()

    # Validate payment type
    if payment_request.payment_type not in ['subscription', 'server']:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment_type. Must be 'subscription' or 'server'"
        )

    # Get plan details
    plan = await plan_service.get_plan_by_id(db, payment_request.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Determine amount based on payment type
    if payment_request.payment_type == 'subscription':
        # For one-time premium subscription (₹499)
        if payment_request.billing_cycle == 'one_time' or not payment_request.billing_cycle:
            amount = plan.monthly_price  # Use monthly_price as one-time premium amount (₹499)
            billing_cycle = 'one_time'
        else:
            # For recurring subscriptions
            price_map = {
                'monthly': plan.monthly_price,
                'quarterly': plan.quarterly_price,
                'annual': plan.annual_price,
                'biennial': plan.biennial_price,
                'triennial': plan.triennial_price
            }
            amount = price_map.get(payment_request.billing_cycle)
            billing_cycle = payment_request.billing_cycle
            
        if not amount:
            raise HTTPException(status_code=400, detail="Invalid billing cycle or amount")
        
        metadata = {
            'plan_id': payment_request.plan_id,
            'billing_cycle': billing_cycle,
            'plan_name': plan.name,
            'subscription_type': 'one_time_premium' if billing_cycle == 'one_time' else 'recurring'
        }
    else:
        # For server purchase
        amount = plan.monthly_price  # Base server cost
        metadata = {
            'plan_id': payment_request.plan_id,
            'server_config': payment_request.server_config,
            'plan_name': plan.name
        }

    try:
        # Create payment transaction with Razorpay order
        payment_type = PaymentType.SUBSCRIPTION if payment_request.payment_type == 'subscription' else PaymentType.SERVER
        
        payment_transaction = await payment_service.create_payment_transaction(
            db=db,
            user_id=current_user.id,
            payment_type=payment_type,
            amount=amount,
            plan_id=payment_request.plan_id,
            billing_cycle=payment_request.billing_cycle,
            metadata=metadata
        )

        # print("response is",type(payment_transaction))
        # print("response is",payment_transaction.json())

        return {
            "success": True,
            "message": "Payment order created successfully",
            "payment": {
                "transaction_id": payment_transaction.id,
                "razorpay_order_id": payment_transaction.razorpay_order_id,
                "amount": float(payment_transaction.subtotal),
                "discount": float(payment_transaction.discount_applied),
                "tax": float(payment_transaction.tax_amount),
                "total_amount": float(payment_transaction.total_amount),
                "currency": payment_transaction.currency,
                "payment_type": payment_transaction.payment_type.value,
                "activation_type": payment_transaction.activation_type.value
            },
            "plan": {
                "id": plan.id,
                "name": plan.name,
                "billing_cycle": payment_request.billing_cycle
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create payment order: {str(e)}"
        )


# --------------------------------------------------------
# ✅ Verify Payment and Complete Transaction
# --------------------------------------------------------
@router.post("/verify-payment")
async def verify_payment(
    payment_data: VerifyPaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify Razorpay payment and complete the transaction
    
    This endpoint:
    1. Verifies Razorpay payment signature
    2. Updates PaymentTransaction to PAID status
    3. Creates Order in database
    4. Distributes commission (if user activated via referral)
    5. Updates user subscription status (for subscription payments)
    """
    payment_service = PaymentService()
    commission_service = CommissionService()
    order_service = OrderService()

    try:
        # Verify and complete payment
        payment_transaction = await payment_service.verify_and_complete_payment(
            db=db,
            razorpay_order_id=payment_data.razorpay_order_id,
            razorpay_payment_id=payment_data.razorpay_payment_id,
            razorpay_signature=payment_data.razorpay_signature
        )

        # Create order record
        from app.schemas.order import OrderCreate
        order_create = OrderCreate(
            plan_id=payment_transaction.payment_metadata.get('plan_id'),
            billing_cycle=payment_transaction.payment_metadata.get('billing_cycle', 'monthly'),
            status='active',
            payment_method='razorpay',
            payment_status='paid'
        )

        order = await order_service.create_order(db, current_user.id, order_create)

        # Link payment to order
        await payment_service.link_payment_to_order(
            db=db,
            payment_transaction_id=payment_transaction.id,
            order_id=order.id
        )

        # Update order with payment details
        order.payment_type = payment_transaction.payment_type.value
        order.activation_type = payment_transaction.activation_type.value
        order.razorpay_order_id = payment_data.razorpay_order_id
        order.razorpay_payment_id = payment_data.razorpay_payment_id
        order.paid_at = payment_transaction.paid_at
        await db.commit()

        # Distribute commission if applicable
        commission_earnings = []
        if payment_transaction.requires_commission():
            commission_earnings = await commission_service.distribute_commission(
                db=db,
                payment_transaction_id=payment_transaction.id
            )

        # Update user subscription status for subscription payments
        if payment_transaction.payment_type == PaymentType.SUBSCRIPTION:
            from sqlalchemy import select
            from app.models.users import UserProfile
            
            result = await db.execute(
                select(UserProfile).where(UserProfile.id == current_user.id)
            )
            user = result.scalars().first()
            if user:
                user.subscription_status = 'active'
                user.subscription_start = datetime.utcnow()
                # Calculate end date based on billing cycle
                # You can implement this based on billing cycle
                await db.commit()

        return {
            "success": True,
            "message": "Payment verified and processed successfully",
            "payment": {
                "transaction_id": payment_transaction.id,
                "payment_id": payment_data.razorpay_payment_id,
                "amount": float(payment_transaction.total_amount),
                "status": payment_transaction.payment_status.value,
                "payment_type": payment_transaction.payment_type.value,
                "payment_method": payment_transaction.payment_method
            },
            "order": {
                "id": order.id,
                "order_number": order.order_number,
                "status": order.order_status
            },
            "commission": {
                "distributed": payment_transaction.commission_distributed,
                "earnings_count": len(commission_earnings),
                "total_distributed": sum(float(e.commission_amount) for e in commission_earnings)
            }
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Payment verification failed: {str(e)}"
        )


# --------------------------------------------------------
# ✅ Razorpay Webhook Handler
# --------------------------------------------------------
@router.post("/razorpay-webhook")
async def razorpay_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_razorpay_signature: Optional[str] = Header(None)
):
    """
    Handle Razorpay webhooks for payment events
    
    This is called by Razorpay for events like:
    - payment.authorized
    - payment.captured
    - payment.failed
    - order.paid
    """
    payment_service = PaymentService()
    commission_service = CommissionService()

    try:
        # Get webhook payload
        payload = await request.json()
        
        # Verify webhook signature
        from app.services.razorpay_service import RazorpayService
        razorpay_service = RazorpayService()
        
        is_valid = await razorpay_service.process_webhook(
            payload=payload,
            signature=x_razorpay_signature
        )

        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

        # Process webhook event
        event = payload.get('event')
        
        if event == 'payment.captured':
            # Payment was successful
            payment_entity = payload.get('payload', {}).get('payment', {}).get('entity', {})
            order_id = payment_entity.get('order_id')
            payment_id = payment_entity.get('id')

            # Find and update payment transaction
            payment_transaction = await payment_service.get_payment_by_razorpay_order_id(
                db=db,
                razorpay_order_id=order_id
            )

            if payment_transaction and payment_transaction.payment_status == PaymentStatus.INITIATED:
                payment_transaction.razorpay_payment_id = payment_id
                payment_transaction.payment_status = PaymentStatus.PAID
                payment_transaction.paid_at = datetime.utcnow()
                await db.commit()

                # Trigger commission distribution if needed
                if payment_transaction.requires_commission():
                    await commission_service.distribute_commission(
                        db=db,
                        payment_transaction_id=payment_transaction.id
                    )

        elif event == 'payment.failed':
            # Payment failed
            payment_entity = payload.get('payload', {}).get('payment', {}).get('entity', {})
            order_id = payment_entity.get('order_id')
            error_description = payment_entity.get('error_description', 'Payment failed')

            await payment_service.mark_payment_failed(
                db=db,
                razorpay_order_id=order_id,
                reason=error_description
            )

        return {"status": "success", "event": event}

    except Exception as e:
        print(f"❌ Webhook processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------------------------
# ✅ Get Payment Status
# --------------------------------------------------------
@router.get("/payment-status/{razorpay_order_id}")
async def get_payment_status(
    razorpay_order_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get payment transaction status
    """
    payment_service = PaymentService()

    payment_transaction = await payment_service.get_payment_by_razorpay_order_id(
        db=db,
        razorpay_order_id=razorpay_order_id
    )

    if not payment_transaction:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Verify user owns this payment
    if payment_transaction.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "success": True,
        "payment": {
            "id": payment_transaction.id,
            "razorpay_order_id": payment_transaction.razorpay_order_id,
            "razorpay_payment_id": payment_transaction.razorpay_payment_id,
            "amount": float(payment_transaction.total_amount),
            "status": payment_transaction.payment_status.value,
            "payment_type": payment_transaction.payment_type.value,
            "activation_type": payment_transaction.activation_type.value,
            "commission_distributed": payment_transaction.commission_distributed,
            "created_at": payment_transaction.created_at.isoformat(),
            "paid_at": payment_transaction.paid_at.isoformat() if payment_transaction.paid_at else None
        }
    }
