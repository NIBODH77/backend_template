# # from fastapi import APIRouter, Depends, HTTPException
# # from sqlalchemy.ext.asyncio import AsyncSession
# # from typing import List

# # from app.core.database import get_db
# # from app.core.security import get_current_user, get_current_admin_user
# # from app.services.invoice_service import InvoiceService
# # from app.schemas.invoice import Invoice, InvoiceWithUser
# # from app.schemas.users import User

# # router = APIRouter()

# # @router.get("/", response_model=List[Invoice])
# # async def get_invoices(
# #     db: AsyncSession = Depends(get_db),
# #     current_user: User = Depends(get_current_user),
# #     invoice_service: InvoiceService = Depends()
# # ):
# #     """
# #     Get user's invoices
# #     """
# #     return invoice_service.get_user_invoices(db, current_user.id)

# # @router.get("/admin", response_model=List[InvoiceWithUser])
# # async def get_all_invoices(
# #     db: AsyncSession = Depends(get_db),
# #     current_user: User = Depends(get_current_admin_user),
# #     invoice_service: InvoiceService = Depends()
# # ):
# #     """
# #     Get all invoices (Admin only)
# #     """
# #     return invoice_service.get_all_invoices(db)

# # @router.get("/{invoice_id}", response_model=Invoice)
# # async def get_invoice(
# #     invoice_id: int,
# #     db: AsyncSession = Depends(get_db),
# #     current_user: User = Depends(get_current_user),
# #     invoice_service: InvoiceService = Depends()
# # ):
# #     """
# #     Get invoice by ID
# #     """
# #     invoice = invoice_service.get_user_invoice(db, current_user.id, invoice_id)
# #     if not invoice:
# #         raise HTTPException(status_code=404, detail="Invoice not found")
# #     return invoice

# # @router.get("/{invoice_id}/download")
# # async def download_invoice(
# #     invoice_id: int,
# #     db: AsyncSession = Depends(get_db),
# #     current_user: User = Depends(get_current_user),
# #     invoice_service: InvoiceService = Depends()
# # ):
# #     """
# #     Download invoice as PDF
# #     """
# #     invoice = invoice_service.get_user_invoice(db, current_user.id, invoice_id)
# #     if not invoice:
# #         raise HTTPException(status_code=404, detail="Invoice not found")
    
# #     # Generate PDF (mock implementation)
# #     pdf_content = f"Invoice {invoice.invoice_number} for {invoice.total_amount}"
    
# #     return {
# #         "filename": f"invoice_{invoice.invoice_number}.pdf",
# #         "content": pdf_content,
# #         "content_type": "application/pdf"
# #     }

# # @router.post("/{invoice_id}/pay")
# # async def pay_invoice(
# #     invoice_id: int,
# #     payment_method: str,
# #     db: AsyncSession = Depends(get_db),
# #     current_user: User = Depends(get_current_user),
# #     invoice_service: InvoiceService = Depends()
# # ):
# #     """
# #     Pay invoice
# #     """
# #     success = invoice_service.pay_invoice(db, current_user.id, invoice_id, payment_method)
# #     if not success:
# #         raise HTTPException(status_code=404, detail="Invoice not found or already paid")
# #     return {"message": "Invoice paid successfully"}

# # @router.get("/current/balance")
# # async def get_current_balance(
# #     db: AsyncSession = Depends(get_db),
# #     current_user: User = Depends(get_current_user),
# #     invoice_service: InvoiceService = Depends()
# # ):
# #     """
# #     Get current balance
# #     """
# #     balance = invoice_service.get_user_current_balance(db, current_user.id)
# #     return {"balance": float(balance), "currency": "INR"}

# # @router.get("/stats/summary")
# # async def get_invoice_stats(
# #     db: AsyncSession = Depends(get_db),
# #     current_user: User = Depends(get_current_admin_user),
# #     invoice_service: InvoiceService = Depends()
# # ):
# #     """
# #     Get invoice statistics (Admin only)
# #     """
# #     return invoice_service.get_invoice_stats(db)







# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from typing import List

# from app.core.database import get_db
# from app.core.security import get_current_user, get_current_admin_user
# from app.services.invoice_service import InvoiceService
# from app.schemas.invoice import Invoice, InvoiceWithUser
# from app.schemas.users import User

# router = APIRouter()

# # ---------------- USER INVOICES ----------------

# @router.get("/", response_model=List[Invoice])
# async def get_invoices(
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
#     invoice_service: InvoiceService = Depends()
# ):
#     """Get user's invoices"""
#     return await invoice_service.get_user_invoices(db, current_user.id)


# # ---------------- ADMIN INVOICES ----------------

# @router.get("/admin", response_model=List[InvoiceWithUser])
# async def get_all_invoices(
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_admin_user),
#     invoice_service: InvoiceService = Depends()
# ):
#     """Get all invoices (Admin only)"""
#     return await invoice_service.get_all_invoices(db)


# # ---------------- SINGLE INVOICE ----------------

# @router.get("/{invoice_id}", response_model=Invoice)
# async def get_invoice(
#     invoice_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
#     invoice_service: InvoiceService = Depends()
# ):
#     """Get invoice by ID"""
#     invoice = await invoice_service.get_user_invoice(db, current_user.id, invoice_id)
#     if not invoice:
#         raise HTTPException(status_code=404, detail="Invoice not found")
#     return invoice


# @router.get("/{invoice_id}/download")
# async def download_invoice(
#     invoice_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
#     invoice_service: InvoiceService = Depends()
# ):
#     """Download invoice as PDF"""
#     invoice = await invoice_service.get_user_invoice(db, current_user.id, invoice_id)
#     if not invoice:
#         raise HTTPException(status_code=404, detail="Invoice not found")

#     # Example PDF generation (replace with real PDF builder)
#     pdf_content = f"Invoice {invoice.invoice_number} for {invoice.total_amount}"

#     return {
#         "filename": f"invoice_{invoice.invoice_number}.pdf",
#         "content": pdf_content,
#         "content_type": "application/pdf"
#     }


# # ---------------- PAYMENT ----------------

# @router.post("/{invoice_id}/pay")
# async def pay_invoice(
#     invoice_id: int,
#     payment_method: str,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
#     invoice_service: InvoiceService = Depends()
# ):
#     """Pay invoice"""
#     success = await invoice_service.pay_invoice(db, current_user.id, invoice_id, payment_method)
#     if not success:
#         raise HTTPException(status_code=404, detail="Invoice not found or already paid")
#     return {"message": "Invoice paid successfully"}


# # ---------------- BALANCE ----------------

# @router.get("/current/balance")
# async def get_current_balance(
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
#     invoice_service: InvoiceService = Depends()
# ):
#     """Get current balance"""
#     balance = await invoice_service.get_user_current_balance(db, current_user.id)
#     return {"balance": float(balance), "currency": "INR"}


# # ---------------- STATS ----------------

# @router.get("/stats/summary")
# async def get_invoice_stats(
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_admin_user),
#     invoice_service: InvoiceService = Depends()
# ):
#     """Get invoice statistics (Admin only)"""
#     return await invoice_service.get_invoice_stats(db)





from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy import select
import logging

from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin_user
from app.services.invoice_service import InvoiceService
from app.schemas.invoice import Invoice, InvoiceWithUser
from app.schemas.users import User
from app.models.invoice import Invoice as InvoiceModel

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------- USER INVOICES ----------------

@router.get("/", response_model=List[Invoice])
async def get_invoices(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    invoice_service: InvoiceService = Depends()
):
    """Get user's invoices"""
    return await invoice_service.get_user_invoices(db, current_user.id)


# ---------------- ADMIN INVOICES ----------------

@router.get("/admin", response_model=List[InvoiceWithUser])
async def get_all_invoices(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    invoice_service: InvoiceService = Depends()
):
    """Get all invoices (Admin only)"""
    return await invoice_service.get_all_invoices(db)


# ---------------- SINGLE INVOICE ----------------

@router.get("/{invoice_id}", response_model=Invoice)
async def get_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    invoice_service: InvoiceService = Depends()
):
    """Get invoice by ID"""
    invoice = await invoice_service.get_user_invoice(db, current_user.id, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.get("/{invoice_id}/download")
async def download_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    invoice_service: InvoiceService = Depends()
):
    """Download invoice as PDF"""
    invoice = await invoice_service.get_user_invoice(db, current_user.id, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Example PDF generation (replace with real PDF builder)
    pdf_content = f"Invoice {invoice.invoice_number} for {invoice.total_amount}"

    return {
        "filename": f"invoice_{invoice.invoice_number}.pdf",
        "content": pdf_content,
        "content_type": "application/pdf"
    }


# ---------------- PAYMENT ----------------

@router.post("/{invoice_id}/pay")
async def pay_invoice(
    invoice_id: int,
    payment_method: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    invoice_service: InvoiceService = Depends()
):
    """Pay invoice"""
    success = await invoice_service.pay_invoice(db, current_user.id, invoice_id, payment_method)
    if not success:
        raise HTTPException(status_code=404, detail="Invoice not found or already paid")
    return {"message": "Invoice paid successfully"}


# ---------------- BALANCE ----------------

@router.get("/current/balance")
async def get_current_balance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    invoice_service: InvoiceService = Depends()
):
    """Get current balance"""
    balance = await invoice_service.get_user_current_balance(db, current_user.id)
    return {"balance": float(balance), "currency": "INR"}


# ---------------- STATS ----------------

@router.get("/stats/summary")
async def get_invoice_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    invoice_service: InvoiceService = Depends()
):
    """Get invoice statistics (Admin only)"""
    return await invoice_service.get_invoice_stats(db)

