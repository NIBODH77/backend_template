from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, dashboard, users, servers, plans, orders, 
    invoices, billing, referrals, support, settings
    )

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(plans.router, prefix="/plans", tags=["plans"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
# api_router.include_router(payment.router, prefix="/payments", tags=["payments"])

api_router.include_router(servers.router, prefix="/servers", tags=["servers"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
api_router.include_router(referrals.router, prefix="/referrals", tags=["referrals"])
api_router.include_router(support.router, prefix="/support", tags=["support"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
