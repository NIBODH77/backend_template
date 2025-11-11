from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.razorpay_service import RazorpayService
from app.services.order_service import OrderService
from app.services.referral_service import ReferralService
from app.services.plan_service import PlanService
from app.schemas.users import User
from pydantic import BaseModel


router = APIRouter()


# --------------------------------------------------------
# Request/Response Schemas
# --------------------------------------------------------
class CreateOrderRequest(BaseModel):
    plan_id: int
    billing_cycle: str  # monthly, quarterly, annual, biennial, triennial
    referral_code: Optional[str] = None


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    plan_id: int
    billing_cycle: str


# --------------------------------------------------------
# ✅ Create Razorpay Order
# --------------------------------------------------------
@router.post("/create-order")
async def create_payment_order(
    order_data: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    razorpay_service: RazorpayService = Depends(),
    plan_service: PlanService = Depends()
):
    """
    Create Razorpay order for subscription payment
    User can optionally provide referral code
    """
    # Get plan details
    plan = await plan_service.get_plan_by_id(db, order_data.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Get price based on billing cycle
    price_map = {
        'monthly': plan.monthly_price,
        'quarterly': plan.quarterly_price,
        'annual': plan.annual_price,
        'biennial': plan.biennial_price,
        'triennial': plan.triennial_price
    }

    amount = price_map.get(order_data.billing_cycle)
    if not amount:
        raise HTTPException(status_code=400, detail="Invalid billing cycle")

    # Create Razorpay order
    try:
        order = await razorpay_service.create_order(
            db=db,
            user_id=current_user.id,
            plan_id=order_data.plan_id,
            billing_cycle=order_data.billing_cycle,
            amount=amount,
            referral_code=order_data.referral_code
        )

        return {
            "success": True,
            "order": order,
            "plan_name": plan.name,
            "billing_cycle": order_data.billing_cycle,
            "amount": float(amount)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")


# --------------------------------------------------------
# ✅ Verify Payment and Process Order
# --------------------------------------------------------
@router.post("/verify-payment")
async def verify_payment(
    payment_data: VerifyPaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    razorpay_service: RazorpayService = Depends(),
    order_service: OrderService = Depends(),
    referral_service: ReferralService = Depends(),
    plan_service: PlanService = Depends()
):
    """
    Verify Razorpay payment and create order with referral commission
    """
    # Verify payment signature
    is_valid = await razorpay_service.verify_payment(
        payment_data.razorpay_order_id,
        payment_data.razorpay_payment_id,
        payment_data.razorpay_signature
    )

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid payment signature")

    # Fetch payment details
    payment_details = await razorpay_service.fetch_payment_details(
        payment_data.razorpay_payment_id
    )

    if 'error' in payment_details:
        raise HTTPException(status_code=400, detail="Payment verification failed")

    # Get plan details
    plan = await plan_service.get_plan_by_id(db, payment_data.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Get amount based on billing cycle
    price_map = {
        'monthly': plan.monthly_price,
        'quarterly': plan.quarterly_price,
        'annual': plan.annual_price,
        'biennial': plan.biennial_price,
        'triennial': plan.triennial_price
    }
    amount = price_map.get(payment_data.billing_cycle, plan.monthly_price)

    # Create order in database
    from app.schemas.order import OrderCreate
    order_create = OrderCreate(
        plan_id=payment_data.plan_id,
        billing_cycle=payment_data.billing_cycle,
        status='active',
        payment_method='razorpay',
        payment_status='paid'
    )

    order = await order_service.create_order(db, current_user.id, order_create)

    # Determine plan type for commission calculation
    plan_type = 'longterm' if payment_data.billing_cycle in ['annual', 'biennial', 'triennial'] else 'recurring'

    # Record referral commission if user has referrer
    try:
        await referral_service.record_commission_earnings(
            db=db,
            user_id=current_user.id,
            order_id=order.id,
            plan_amount=amount,
            plan_type=plan_type
        )
    except Exception as e:
        print(f"⚠️ Failed to record referral commission: {str(e)}")

    return {
        "success": True,
        "message": "Payment verified and order created successfully",
        "order_id": order.id,
        "order_number": order.order_number,
        "payment_id": payment_data.razorpay_payment_id,
        "amount": float(amount),
        "plan_type": plan_type
    }


# --------------------------------------------------------
# ✅ Razorpay Webhook Handler
# --------------------------------------------------------
@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_razorpay_signature: str = Header(None),
    razorpay_service: RazorpayService = Depends(),
    order_service: OrderService = Depends(),
    referral_service: ReferralService = Depends()
):
    """
    Handle Razorpay webhook events
    """
    try:
        payload = await request.json()

        # Verify webhook signature
        is_valid = await razorpay_service.process_webhook(
            payload,
            x_razorpay_signature
        )

        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

        event = payload.get('event')
        payment_entity = payload.get('payload', {}).get('payment', {}).get('entity', {})

        # Handle payment success event
        if event == 'payment.captured':
            notes = payment_entity.get('notes', {})
            user_id = notes.get('user_id')
            plan_id = notes.get('plan_id')
            billing_cycle = notes.get('billing_cycle')
            referrer_id = notes.get('referrer_id')

            if user_id and plan_id and billing_cycle:
                # Process order and commissions
                print(f"✅ Payment captured for user {user_id}, plan {plan_id}")

        return {"status": "success"}

    except Exception as e:
        print(f"❌ Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------------------------
# ✅ Get Razorpay Key (for frontend)
# --------------------------------------------------------
@router.get("/config")
async def get_razorpay_config():
    """
    Get Razorpay configuration for frontend
    """
    from app.core.config import settings
    return {
        "key_id": settings.RAZORPAY_KEY_ID,
        "currency": "INR"
    }