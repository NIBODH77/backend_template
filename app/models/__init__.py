# Import all models to register them with SQLAlchemy
from app.models.users import UserProfile
from app.models.plan import HostingPlan
from app.models.server import Server
from app.models.order import Order
from app.models.invoice import Invoice
from app.models.referrals import ReferralPayout, ReferralEarning
from app.models.billing import PaymentMethod, BillingSettings
from app.models.settings import UserSettings
from app.models.support import SupportTicket
from app.models.payment import PaymentTransaction, ReferralCommissionRate, PaymentType, ActivationType, PaymentStatus

__all__ = [
    "UserProfile",
    "HostingPlan",
    "Server",
    "Order",
    "Invoice",
    "ReferralPayout",
    "ReferralEarning",
    "PaymentMethod",
    "BillingSettings",
    "UserSettings",
    "SupportTicket",
    "PaymentTransaction",
    "ReferralCommissionRate",
    "PaymentType",
    "ActivationType",
    "PaymentStatus",
]
