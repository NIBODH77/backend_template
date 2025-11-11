# # # # from sqlalchemy.ext.asyncio import AsyncSession
# # # # from sqlalchemy import func, and_, select
# # # # from typing import List, Optional, Dict, Any
# # # # from datetime import datetime, timedelta
# # # # from decimal import Decimal
# # # # import secrets
# # # # import string

# # # # from app.models.order import Order
# # # # from app.models.plan import HostingPlan
# # # # from app.models.users import UserProfile
# # # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary

# # # # class OrderService:
# # # #     async def get_user_orders(self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100, 
# # # #                             status: Optional[str] = None) -> List[Order]:
# # # #         query = select(Order).where(Order.user_id == user_id)
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()
    
# # # #     async def get_all_orders(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
# # # #                            status: Optional[str] = None) -> List[Order]:
# # # #         query = select(Order)
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()
    
# # # #     async def get_orders_with_plan(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
# # # #                                  status: Optional[str] = None, payment_status: Optional[str] = None) -> List[Dict[str, Any]]:
# # # #         query = select(Order, HostingPlan, UserProfile).join(
# # # #             HostingPlan, Order.plan_id == HostingPlan.id
# # # #         ).join(
# # # #             UserProfile, Order.user_id == UserProfile.id
# # # #         )
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         if payment_status and payment_status != "all":
# # # #             query = query.where(Order.payment_status == payment_status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         orders_with_details = result.all()
        
# # # #         orders_list = []
# # # #         for order, plan, user in orders_with_details:
# # # #             order_dict = {
# # # #                 "id": order.id,
# # # #                 "user_id": order.user_id,
# # # #                 "plan_id": order.plan_id,
# # # #                 "order_number": order.order_number,
# # # #                 "order_status": order.order_status,
# # # #                 "total_amount": order.total_amount,
# # # #                 "payment_status": order.payment_status,
# # # #                 "billing_cycle": order.billing_cycle,
# # # #                 "server_details": order.server_details,
# # # #                 "payment_method": order.payment_method,
# # # #                 "payment_reference": order.payment_reference,
# # # #                 "payment_date": order.payment_date,
# # # #                 "created_at": order.created_at,
# # # #                 "updated_at": order.updated_at,
# # # #                 "plan_name": plan.name,
# # # #                 "plan_type": plan.plan_type,
# # # #                 "user_email": user.email
# # # #             }
# # # #             orders_list.append(order_dict)
        
# # # #         return orders_list
    
# # # #     async def get_order_by_id(self, db: AsyncSession, order_id: int) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(Order.id == order_id)
# # # #         )
# # # #         return result.scalar_one_or_none()
    
# # # #     async def get_user_order(self, db: AsyncSession, user_id: int, order_id: int) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(
# # # #                 Order.id == order_id,
# # # #                 Order.user_id == user_id
# # # #             )
# # # #         )
# # # #         return result.scalar_one_or_none()
    
# # # #     async def create_order(self, db: AsyncSession, user_id: int, order_data: OrderCreate) -> Order:
# # # #         # Get plan details
# # # #         result = await db.execute(
# # # #             select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # # #         )
# # # #         plan = result.scalar_one_or_none()
        
# # # #         if not plan:
# # # #             raise ValueError("Plan not found")
        
# # # #         # Generate order number
# # # #         order_number = await self._generate_order_number(db)
        
# # # #         db_order = Order(
# # # #             user_id=user_id,
# # # #             plan_id=order_data.plan_id,
# # # #             order_number=order_number,
# # # #             billing_cycle=order_data.billing_cycle,
# # # #             total_amount=order_data.total_amount,
# # # #             server_details=order_data.server_details
# # # #         )
        
# # # #         db.add(db_order)
# # # #         await db.commit()
# # # #         await db.refresh(db_order)
# # # #         return db_order
    
# # # #     async def update_order(self, db: AsyncSession, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return None
            
# # # #         update_data = order_update.dict(exclude_unset=True)
# # # #         for field, value in update_data.items():
# # # #             setattr(order, field, value)
            
# # # #         await db.commit()
# # # #         await db.refresh(order)
# # # #         return order
    
# # # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "cancelled"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def cancel_user_order(self, db: AsyncSession, user_id: int, order_id: int) -> bool:
# # # #         order = await self.get_user_order(db, user_id, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "cancelled"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "completed"
# # # #         order.payment_status = "paid"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # # #         result = await db.execute(select(func.count(Order.id)))
# # # #         return result.scalar()
    
# # # #     async def get_recent_orders(self, db: AsyncSession, limit: int = 5) -> List[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # # #         )
# # # #         return result.scalars().all()
    
# # # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # # #         total_orders = await self.get_total_orders(db)
        
# # # #         pending_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # # #         )
# # # #         pending_orders = pending_result.scalar()
        
# # # #         completed_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # # #         )
# # # #         completed_orders = completed_result.scalar()
        
# # # #         cancelled_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # # #         )
# # # #         cancelled_orders = cancelled_result.scalar()
        
# # # #         # Calculate revenue
# # # #         total_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # # #         )
# # # #         total_revenue = total_revenue_result.scalar() or Decimal('0.0')
        
# # # #         # Calculate monthly revenue
# # # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # # #         monthly_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(
# # # #                 Order.payment_status == "paid",
# # # #                 Order.created_at >= start_of_month
# # # #             )
# # # #         )
# # # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal('0.0')
        
# # # #         return OrderSummary(
# # # #             total_orders=total_orders,
# # # #             pending_orders=pending_orders,
# # # #             completed_orders=completed_orders,
# # # #             cancelled_orders=cancelled_orders,
# # # #             total_revenue=total_revenue,
# # # #             monthly_revenue=monthly_revenue
# # # #         )
    
# # # #     async def _generate_order_number(self, db: AsyncSession, length: int = 10) -> str:
# # # #         """Generate a unique order number"""
# # # #         characters = string.ascii_uppercase + string.digits
# # # #         while True:
# # # #             number = 'ORD-' + ''.join(secrets.choice(characters) for _ in range(length))
# # # #             # Check if order number already exists
# # # #             result = await db.execute(
# # # #                 select(Order).where(Order.order_number == number)
# # # #             )
# # # #             existing_order = result.scalar_one_or_none()
# # # #             if not existing_order:
# # # #                 return number




# # # # from sqlalchemy.ext.asyncio import AsyncSession
# # # # from sqlalchemy import func, select
# # # # from typing import List, Optional, Dict, Any
# # # # from datetime import datetime
# # # # from decimal import Decimal
# # # # import secrets
# # # # import string

# # # # from app.models.order import Order
# # # # from app.models.plan import HostingPlan
# # # # from app.models.users import UserProfile
# # # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary


# # # # class OrderService:
# # # #     # -----------------------------
# # # #     # 🔹 USER-SPECIFIC QUERIES
# # # #     # -----------------------------
# # # #     async def get_user_orders(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         user_id: int,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #     ) -> List[Order]:
# # # #         query = select(Order).where(Order.user_id == user_id)

# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()

# # # #     async def get_user_order(
# # # #         self, db: AsyncSession, user_id: int, order_id: int
# # # #     ) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(Order.id == order_id, Order.user_id == user_id)
# # # #         )
# # # #         return result.scalar_one_or_none()

# # # #     # -----------------------------
# # # #     # 🔹 ADMIN / GLOBAL QUERIES
# # # #     # -----------------------------
# # # #     async def get_all_orders(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #     ) -> List[Order]:
# # # #         query = select(Order)
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()

# # # #     async def get_orders_with_plan(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #         payment_status: Optional[str] = None,
# # # #     ) -> List[Dict[str, Any]]:
# # # #         query = (
# # # #             select(Order, HostingPlan, UserProfile)
# # # #             .join(HostingPlan, Order.plan_id == HostingPlan.id)
# # # #             .join(UserProfile, Order.user_id == UserProfile.id)
# # # #         )

# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
# # # #         if payment_status and payment_status != "all":
# # # #             query = query.where(Order.payment_status == payment_status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         rows = result.all()

# # # #         orders_list = []
# # # #         for order, plan, user in rows:
# # # #             orders_list.append(
# # # #                 {
# # # #                     "id": order.id,
# # # #                     "user_id": order.user_id,
# # # #                     "plan_id": order.plan_id,
# # # #                     "order_number": order.order_number,
# # # #                     "order_status": order.order_status,
# # # #                     "total_amount": order.total_amount,
# # # #                     "payment_status": order.payment_status,
# # # #                     "billing_cycle": order.billing_cycle,
# # # #                     "server_details": order.server_details,
# # # #                     "payment_method": order.payment_method,
# # # #                     "payment_reference": order.payment_reference,
# # # #                     "payment_date": order.payment_date,
# # # #                     "created_at": order.created_at,
# # # #                     "updated_at": order.updated_at,
# # # #                     "plan_name": plan.name,
# # # #                     "plan_type": plan.plan_type,
# # # #                     "user_email": user.email,
# # # #                 }
# # # #             )
# # # #         return orders_list

# # # #     # -----------------------------
# # # #     # 🔹 CRUD OPERATIONS
# # # #     # -----------------------------
# # # #     async def get_order_by_id(
# # # #         self, db: AsyncSession, order_id: int
# # # #     ) -> Optional[Order]:
# # # #         result = await db.execute(select(Order).where(Order.id == order_id))
# # # #         return result.scalar_one_or_none()

# # # #     async def create_order(
# # # #         self, db: AsyncSession, user_id: int, order_data: OrderCreate
# # # #     ) -> Order:
# # # #         # Get plan details
# # # #         result = await db.execute(
# # # #             select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # # #         )
# # # #         plan = result.scalar_one_or_none()
# # # #         if not plan:
# # # #             raise ValueError("Plan not found")

# # # #         # Generate unique order number
# # # #         order_number = await self._generate_order_number(db)

# # # #         new_order = Order(
# # # #             user_id=user_id,
# # # #             plan_id=order_data.plan_id,
# # # #             order_number=order_number,
# # # #             billing_cycle=order_data.billing_cycle,
# # # #             total_amount=order_data.total_amount,
# # # #             server_details=order_data.server_details,
# # # #         )

# # # #         async with db.begin():
# # # #             db.add(new_order)

# # # #         await db.refresh(new_order)
# # # #         return new_order

# # # #     async def update_order(
# # # #         self, db: AsyncSession, order_id: int, order_update: OrderUpdate
# # # #     ) -> Optional[Order]:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return None

# # # #         update_data = order_update.dict(exclude_unset=True)
# # # #         for field, value in update_data.items():
# # # #             setattr(order, field, value)

# # # #         async with db.begin():
# # # #             db.add(order)

# # # #         await db.refresh(order)
# # # #         return order

# # # #     # -----------------------------
# # # #     # 🔹 ORDER STATUS ACTIONS
# # # #     # -----------------------------

# # # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "cancelled"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     async def cancel_user_order(
# # # #         self, db: AsyncSession, user_id: int, order_id: int
# # # #     ) -> bool:
# # # #         order = await self.get_user_order(db, user_id, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "cancelled"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "completed"
# # # #         order.payment_status = "paid"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     # -----------------------------
# # # #     # 🔹 ANALYTICS / STATS
# # # #     # -----------------------------
# # # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # # #         result = await db.execute(select(func.count(Order.id)))
# # # #         return result.scalar() or 0

# # # #     async def get_recent_orders(
# # # #         self, db: AsyncSession, limit: int = 5
# # # #     ) -> List[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # # #         )
# # # #         return result.scalars().all()

# # # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # # #         total_orders = await self.get_total_orders(db)

# # # #         pending = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # # #         )
# # # #         completed = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # # #         )
# # # #         cancelled = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # # #         )

# # # #         total_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # # #         )
# # # #         total_revenue = total_revenue_result.scalar() or Decimal("0.0")

# # # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # # #         monthly_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(
# # # #                 Order.payment_status == "paid", Order.created_at >= start_of_month
# # # #             )
# # # #         )
# # # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal("0.0")

# # # #         return OrderSummary(
# # # #             total_orders=total_orders,
# # # #             pending_orders=pending.scalar() or 0,
# # # #             completed_orders=completed.scalar() or 0,
# # # #             cancelled_orders=cancelled.scalar() or 0,
# # # #             total_revenue=total_revenue,
# # # #             monthly_revenue=monthly_revenue,
# # # #         )

# # # #     # -----------------------------
# # # #     # 🔹 PRIVATE HELPERS
# # # #     # -----------------------------
# # # #     async def _generate_order_number(
# # # #         self, db: AsyncSession, length: int = 10
# # # #     ) -> str:
# # # #         """Generate a unique order number"""
# # # #         chars = string.ascii_uppercase + string.digits
# # # #         while True:
# # # #             number = "ORD-" + "".join(secrets.choice(chars) for _ in range(length))
# # # #             result = await db.execute(
# # # #                 select(Order).where(Order.order_number == number)
# # # #             )
# # # #             if not result.scalar_one_or_none():
# # # #                 return number


# # # # from sqlalchemy.ext.asyncio import AsyncSession
# # # # from sqlalchemy import func, and_, select
# # # # from typing import List, Optional, Dict, Any
# # # # from datetime import datetime, timedelta
# # # # from decimal import Decimal
# # # # import secrets
# # # # import string

# # # # from app.models.order import Order
# # # # from app.models.plan import HostingPlan
# # # # from app.models.users import UserProfile
# # # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary

# # # # class OrderService:
# # # #     async def get_user_orders(self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100, 
# # # #                             status: Optional[str] = None) -> List[Order]:
# # # #         query = select(Order).where(Order.user_id == user_id)
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()
    
# # # #     async def get_all_orders(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
# # # #                            status: Optional[str] = None) -> List[Order]:
# # # #         query = select(Order)
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()
    
# # # #     async def get_orders_with_plan(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
# # # #                                  status: Optional[str] = None, payment_status: Optional[str] = None) -> List[Dict[str, Any]]:
# # # #         query = select(Order, HostingPlan, UserProfile).join(
# # # #             HostingPlan, Order.plan_id == HostingPlan.id
# # # #         ).join(
# # # #             UserProfile, Order.user_id == UserProfile.id
# # # #         )
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         if payment_status and payment_status != "all":
# # # #             query = query.where(Order.payment_status == payment_status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         orders_with_details = result.all()
        
# # # #         orders_list = []
# # # #         for order, plan, user in orders_with_details:
# # # #             order_dict = {
# # # #                 "id": order.id,
# # # #                 "user_id": order.user_id,
# # # #                 "plan_id": order.plan_id,
# # # #                 "order_number": order.order_number,
# # # #                 "order_status": order.order_status,
# # # #                 "total_amount": order.total_amount,
# # # #                 "payment_status": order.payment_status,
# # # #                 "billing_cycle": order.billing_cycle,
# # # #                 "server_details": order.server_details,
# # # #                 "payment_method": order.payment_method,
# # # #                 "payment_reference": order.payment_reference,
# # # #                 "payment_date": order.payment_date,
# # # #                 "created_at": order.created_at,
# # # #                 "updated_at": order.updated_at,
# # # #                 "plan_name": plan.name,
# # # #                 "plan_type": plan.plan_type,
# # # #                 "user_email": user.email
# # # #             }
# # # #             orders_list.append(order_dict)
        
# # # #         return orders_list
    
# # # #     async def get_order_by_id(self, db: AsyncSession, order_id: int) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(Order.id == order_id)
# # # #         )
# # # #         return result.scalar_one_or_none()
    
# # # #     async def get_user_order(self, db: AsyncSession, user_id: int, order_id: int) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(
# # # #                 Order.id == order_id,
# # # #                 Order.user_id == user_id
# # # #             )
# # # #         )
# # # #         return result.scalar_one_or_none()
    
# # # #     async def create_order(self, db: AsyncSession, user_id: int, order_data: OrderCreate) -> Order:
# # # #         # Get plan details
# # # #         result = await db.execute(
# # # #             select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # # #         )
# # # #         plan = result.scalar_one_or_none()
        
# # # #         if not plan:
# # # #             raise ValueError("Plan not found")
        
# # # #         # Generate order number
# # # #         order_number = await self._generate_order_number(db)
        
# # # #         db_order = Order(
# # # #             user_id=user_id,
# # # #             plan_id=order_data.plan_id,
# # # #             order_number=order_number,
# # # #             billing_cycle=order_data.billing_cycle,
# # # #             total_amount=order_data.total_amount,
# # # #             server_details=order_data.server_details
# # # #         )
        
# # # #         db.add(db_order)
# # # #         await db.commit()
# # # #         await db.refresh(db_order)
# # # #         return db_order
    
# # # #     async def update_order(self, db: AsyncSession, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return None
            
# # # #         update_data = order_update.dict(exclude_unset=True)
# # # #         for field, value in update_data.items():
# # # #             setattr(order, field, value)
            
# # # #         await db.commit()
# # # #         await db.refresh(order)
# # # #         return order
    
# # # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "cancelled"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def cancel_user_order(self, db: AsyncSession, user_id: int, order_id: int) -> bool:
# # # #         order = await self.get_user_order(db, user_id, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "cancelled"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "completed"
# # # #         order.payment_status = "paid"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # # #         result = await db.execute(select(func.count(Order.id)))
# # # #         return result.scalar()
    
# # # #     async def get_recent_orders(self, db: AsyncSession, limit: int = 5) -> List[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # # #         )
# # # #         return result.scalars().all()
    
# # # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # # #         total_orders = await self.get_total_orders(db)
        
# # # #         pending_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # # #         )
# # # #         pending_orders = pending_result.scalar()
        
# # # #         completed_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # # #         )
# # # #         completed_orders = completed_result.scalar()
        
# # # #         cancelled_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # # #         )
# # # #         cancelled_orders = cancelled_result.scalar()
        
# # # #         # Calculate revenue
# # # #         total_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # # #         )
# # # #         total_revenue = total_revenue_result.scalar() or Decimal('0.0')
        
# # # #         # Calculate monthly revenue
# # # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # # #         monthly_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(
# # # #                 Order.payment_status == "paid",
# # # #                 Order.created_at >= start_of_month
# # # #             )
# # # #         )
# # # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal('0.0')
        
# # # #         return OrderSummary(
# # # #             total_orders=total_orders,
# # # #             pending_orders=pending_orders,
# # # #             completed_orders=completed_orders,
# # # #             cancelled_orders=cancelled_orders,
# # # #             total_revenue=total_revenue,
# # # #             monthly_revenue=monthly_revenue
# # # #         )
    
# # # #     async def _generate_order_number(self, db: AsyncSession, length: int = 10) -> str:
# # # #         """Generate a unique order number"""
# # # #         characters = string.ascii_uppercase + string.digits
# # # #         while True:
# # # #             number = 'ORD-' + ''.join(secrets.choice(characters) for _ in range(length))
# # # #             # Check if order number already exists
# # # #             result = await db.execute(
# # # #                 select(Order).where(Order.order_number == number)
# # # #             )
# # # #             existing_order = result.scalar_one_or_none()
# # # #             if not existing_order:
# # # #                 return number




# # # # from sqlalchemy.ext.asyncio import AsyncSession
# # # # from sqlalchemy import func, select
# # # # from typing import List, Optional, Dict, Any
# # # # from datetime import datetime
# # # # from decimal import Decimal
# # # # import secrets
# # # # import string

# # # # from app.models.order import Order
# # # # from app.models.plan import HostingPlan
# # # # from app.models.users import UserProfile
# # # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary


# # # # class OrderService:
# # # #     # -----------------------------
# # # #     # 🔹 USER-SPECIFIC QUERIES
# # # #     # -----------------------------
# # # #     async def get_user_orders(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         user_id: int,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #     ) -> List[Order]:
# # # #         query = select(Order).where(Order.user_id == user_id)

# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()

# # # #     async def get_user_order(
# # # #         self, db: AsyncSession, user_id: int, order_id: int
# # # #     ) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(Order.id == order_id, Order.user_id == user_id)
# # # #         )
# # # #         return result.scalar_one_or_none()

# # # #     # -----------------------------
# # # #     # 🔹 ADMIN / GLOBAL QUERIES
# # # #     # -----------------------------
# # # #     async def get_all_orders(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #     ) -> List[Order]:
# # # #         query = select(Order)
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()

# # # #     async def get_orders_with_plan(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #         payment_status: Optional[str] = None,
# # # #     ) -> List[Dict[str, Any]]:
# # # #         query = (
# # # #             select(Order, HostingPlan, UserProfile)
# # # #             .join(HostingPlan, Order.plan_id == HostingPlan.id)
# # # #             .join(UserProfile, Order.user_id == UserProfile.id)
# # # #         )

# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
# # # #         if payment_status and payment_status != "all":
# # # #             query = query.where(Order.payment_status == payment_status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         rows = result.all()

# # # #         orders_list = []
# # # #         for order, plan, user in rows:
# # # #             orders_list.append(
# # # #                 {
# # # #                     "id": order.id,
# # # #                     "user_id": order.user_id,
# # # #                     "plan_id": order.plan_id,
# # # #                     "order_number": order.order_number,
# # # #                     "order_status": order.order_status,
# # # #                     "total_amount": order.total_amount,
# # # #                     "payment_status": order.payment_status,
# # # #                     "billing_cycle": order.billing_cycle,
# # # #                     "server_details": order.server_details,
# # # #                     "payment_method": order.payment_method,
# # # #                     "payment_reference": order.payment_reference,
# # # #                     "payment_date": order.payment_date,
# # # #                     "created_at": order.created_at,
# # # #                     "updated_at": order.updated_at,
# # # #                     "plan_name": plan.name,
# # # #                     "plan_type": plan.plan_type,
# # # #                     "user_email": user.email,
# # # #                 }
# # # #             )
# # # #         return orders_list

# # # #     # -----------------------------
# # # #     # 🔹 CRUD OPERATIONS
# # # #     # -----------------------------
# # # #     async def get_order_by_id(
# # # #         self, db: AsyncSession, order_id: int
# # # #     ) -> Optional[Order]:
# # # #         result = await db.execute(select(Order).where(Order.id == order_id))
# # # #         return result.scalar_one_or_none()

# # # #     async def create_order(
# # # #         self, db: AsyncSession, user_id: int, order_data: OrderCreate
# # # #     ) -> Order:
# # # #         # Get plan details
# # # #         result = await db.execute(
# # # #             select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # # #         )
# # # #         plan = result.scalar_one_or_none()
# # # #         if not plan:
# # # #             raise ValueError("Plan not found")

# # # #         # Generate unique order number
# # # #         order_number = await self._generate_order_number(db)

# # # #         new_order = Order(
# # # #             user_id=user_id,
# # # #             plan_id=order_data.plan_id,
# # # #             order_number=order_number,
# # # #             billing_cycle=order_data.billing_cycle,
# # # #             total_amount=order_data.total_amount,
# # # #             server_details=order_data.server_details,
# # # #         )

# # # #         async with db.begin():
# # # #             db.add(new_order)

# # # #         await db.refresh(new_order)
# # # #         return new_order

# # # #     async def update_order(
# # # #         self, db: AsyncSession, order_id: int, order_update: OrderUpdate
# # # #     ) -> Optional[Order]:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return None

# # # #         update_data = order_update.dict(exclude_unset=True)
# # # #         for field, value in update_data.items():
# # # #             setattr(order, field, value)

# # # #         async with db.begin():
# # # #             db.add(order)

# # # #         await db.refresh(order)
# # # #         return order

# # # #     # -----------------------------
# # # #     # 🔹 ORDER STATUS ACTIONS
# # # #     # -----------------------------

# # # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "cancelled"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     async def cancel_user_order(
# # # #         self, db: AsyncSession, user_id: int, order_id: int
# # # #     ) -> bool:
# # # #         order = await self.get_user_order(db, user_id, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "cancelled"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "completed"
# # # #         order.payment_status = "paid"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     # -----------------------------
# # # #     # 🔹 ANALYTICS / STATS
# # # #     # -----------------------------
# # # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # # #         result = await db.execute(select(func.count(Order.id)))
# # # #         return result.scalar() or 0

# # # #     async def get_recent_orders(
# # # #         self, db: AsyncSession, limit: int = 5
# # # #     ) -> List[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # # #         )
# # # #         return result.scalars().all()

# # # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # # #         total_orders = await self.get_total_orders(db)

# # # #         pending = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # # #         )
# # # #         completed = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # # #         )
# # # #         cancelled = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # # #         )

# # # #         total_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # # #         )
# # # #         total_revenue = total_revenue_result.scalar() or Decimal("0.0")

# # # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # # #         monthly_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(
# # # #                 Order.payment_status == "paid", Order.created_at >= start_of_month
# # # #             )
# # # #         )
# # # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal("0.0")

# # # #         return OrderSummary(
# # # #             total_orders=total_orders,
# # # #             pending_orders=pending.scalar() or 0,
# # # #             completed_orders=completed.scalar() or 0,
# # # #             cancelled_orders=cancelled.scalar() or 0,
# # # #             total_revenue=total_revenue,
# # # #             monthly_revenue=monthly_revenue,
# # # #         )

# # # #     # -----------------------------
# # # #     # 🔹 PRIVATE HELPERS
# # # #     # -----------------------------
# # # #     async def _generate_order_number(
# # # #         self, db: AsyncSession, length: int = 10
# # # #     ) -> str:
# # # #         """Generate a unique order number"""
# # # #         chars = string.ascii_uppercase + string.digits
# # # #         while True:
# # # #             number = "ORD-" + "".join(secrets.choice(chars) for _ in range(length))
# # # #             result = await db.execute(
# # # #                 select(Order).where(Order.order_number == number)
# # # #             )
# # # #             if not result.scalar_one_or_none():
# # # #                 return number





# # # from sqlalchemy.ext.asyncio import AsyncSession
# # # from sqlalchemy import func, select
# # # from typing import List, Optional, Dict, Any
# # # from datetime import datetime
# # # from decimal import Decimal
# # # import secrets
# # # import string

# # # from app.models.order import Order
# # # from app.models.plan import HostingPlan
# # # from app.models.users import UserProfile
# # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary


# # # class OrderService:
# # #     # -----------------------------
# # #     # 🔹 USER-SPECIFIC QUERIES
# # #     # -----------------------------
# # #     async def get_user_orders(
# # #         self,
# # #         db: AsyncSession,
# # #         user_id: int,
# # #         skip: int = 0,
# # #         limit: int = 100,
# # #         status: Optional[str] = None,
# # #     ) -> List[Order]:
# # #         query = select(Order).where(Order.user_id == user_id)
# # #         if status and status != "all":
# # #             query = query.where(Order.order_status == status)
# # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

# # #         result = await db.execute(query)
# # #         return result.scalars().all()

# # #     async def get_user_order(
# # #         self, db: AsyncSession, user_id: int, order_id: int
# # #     ) -> Optional[Order]:
# # #         result = await db.execute(
# # #             select(Order).where(Order.id == order_id, Order.user_id == user_id)
# # #         )
# # #         return result.scalar_one_or_none()

# # #     # -----------------------------
# # #     # 🔹 ADMIN / GLOBAL QUERIES
# # #     # -----------------------------
# # #     async def get_all_orders(
# # #         self,
# # #         db: AsyncSession,
# # #         skip: int = 0,
# # #         limit: int = 100,
# # #         status: Optional[str] = None,
# # #     ) -> List[Order]:
# # #         query = select(Order)
# # #         if status and status != "all":
# # #             query = query.where(Order.order_status == status)
# # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

# # #         result = await db.execute(query)
# # #         return result.scalars().all()

# # #     async def get_orders_with_plan(
# # #         self,
# # #         db: AsyncSession,
# # #         skip: int = 0,
# # #         limit: int = 100,
# # #         status: Optional[str] = None,
# # #         payment_status: Optional[str] = None,
# # #     ) -> List[Dict[str, Any]]:
# # #         query = (
# # #             select(Order, HostingPlan, UserProfile)
# # #             .join(HostingPlan, Order.plan_id == HostingPlan.id)
# # #             .join(UserProfile, Order.user_id == UserProfile.id)
# # #         )

# # #         if status and status != "all":
# # #             query = query.where(Order.order_status == status)
# # #         if payment_status and payment_status != "all":
# # #             query = query.where(Order.payment_status == payment_status)

# # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # #         result = await db.execute(query)
# # #         rows = result.all()

# # #         return [
# # #             {
# # #                 "id": order.id,
# # #                 "user_id": order.user_id,
# # #                 "plan_id": order.plan_id,
# # #                 "order_number": order.order_number,
# # #                 "order_status": order.order_status,
# # #                 "total_amount": order.total_amount,
# # #                 "payment_status": order.payment_status,
# # #                 "billing_cycle": order.billing_cycle,
# # #                 "server_details": order.server_details,
# # #                 "payment_method": order.payment_method,
# # #                 "payment_reference": order.payment_reference,
# # #                 "payment_date": order.payment_date,
# # #                 "created_at": order.created_at,
# # #                 "updated_at": order.updated_at,
# # #                 "plan_name": plan.name,
# # #                 "plan_type": plan.plan_type,
# # #                 "user_email": user.email,
# # #             }
# # #             for order, plan, user in rows
# # #         ]

# # #     # -----------------------------
# # #     # 🔹 CRUD OPERATIONS
# # #     # -----------------------------
# # #     async def get_order_by_id(self, db: AsyncSession, order_id: int) -> Optional[Order]:
# # #         result = await db.execute(select(Order).where(Order.id == order_id))
# # #         return result.scalar_one_or_none()

# # #     async def create_order(
# # #         self, db: AsyncSession, user_id: int, order_data: OrderCreate
# # #     ) -> Order:
# # #         try:
# # #             # ✅ 1. Get plan details
# # #             result = await db.execute(
# # #                 select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # #             )
# # #             plan = result.scalar_one_or_none()
# # #             if not plan:
# # #                 raise ValueError("Plan not found")

# # #             # ✅ 2. Generate unique order number
# # #             order_number = await self._generate_order_number(db)

# # #             # ✅ 3. Create order instance
# # #             new_order = Order(
# # #                 user_id=user_id,
# # #                 plan_id=order_data.plan_id,
# # #                 order_number=order_number,
# # #                 billing_cycle=order_data.billing_cycle,
# # #                 total_amount=order_data.total_amount,
# # #                 server_details=order_data.server_details,
# # #                 created_at=datetime.utcnow(),
# # #                 updated_at=datetime.utcnow(),
# # #             )

# # #             db.add(new_order)
# # #             await db.commit()
# # #             await db.refresh(new_order)
# # #             return new_order

# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     async def update_order(
# # #         self, db: AsyncSession, order_id: int, order_update: OrderUpdate
# # #     ) -> Optional[Order]:
# # #         order = await self.get_order_by_id(db, order_id)
# # #         if not order:
# # #             return None

# # #         update_data = order_update.dict(exclude_unset=True)
# # #         for field, value in update_data.items():
# # #             setattr(order, field, value)

# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             await db.refresh(order)
# # #             return order
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     # -----------------------------
# # #     # 🔹 ORDER STATUS ACTIONS
# # #     # -----------------------------
# # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # #         order = await self.get_order_by_id(db, order_id)
# # #         if not order:
# # #             return False

# # #         order.order_status = "cancelled"
# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             return True
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     async def cancel_user_order(
# # #         self, db: AsyncSession, user_id: int, order_id: int
# # #     ) -> bool:
# # #         order = await self.get_user_order(db, user_id, order_id)
# # #         if not order:
# # #             return False

# # #         order.order_status = "cancelled"
# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             return True
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # #         order = await self.get_order_by_id(db, order_id)
# # #         if not order:
# # #             return False

# # #         order.order_status = "completed"
# # #         order.payment_status = "paid"
# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             return True
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     # -----------------------------
# # #     # 🔹 ANALYTICS / STATS
# # #     # -----------------------------
    
# # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # #         result = await db.execute(select(func.count(Order.id)))
# # #         return result.scalar() or 0

# # #     async def get_recent_orders(self, db: AsyncSession, limit: int = 5) -> List[Order]:
# # #         result = await db.execute(
# # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # #         )
# # #         return result.scalars().all()

# # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # #         total_orders = await self.get_total_orders(db)

# # #         pending = await db.execute(
# # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # #         )
# # #         completed = await db.execute(
# # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # #         )
# # #         cancelled = await db.execute(
# # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # #         )

# # #         total_revenue_result = await db.execute(
# # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # #         )
# # #         total_revenue = total_revenue_result.scalar() or Decimal("0.0")

# # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # #         monthly_revenue_result = await db.execute(
# # #             select(func.sum(Order.total_amount)).where(
# # #                 Order.payment_status == "paid", Order.created_at >= start_of_month
# # #             )
# # #         )
# # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal("0.0")

# # #         return OrderSummary(
# # #             total_orders=total_orders,
# # #             pending_orders=pending.scalar() or 0,
# # #             completed_orders=completed.scalar() or 0,
# # #             cancelled_orders=cancelled.scalar() or 0,
# # #             total_revenue=total_revenue,
# # #             monthly_revenue=monthly_revenue,
# # #         )

# # #     # -----------------------------
# # #     # 🔹 PRIVATE HELPERS
# # #     # -----------------------------
# # #     async def _generate_order_number(self, db: AsyncSession, length: int = 10) -> str:
# # #         chars = string.ascii_uppercase + string.digits
# # #         while True:
# # #             number = "ORD-" + "".join(secrets.choice(chars) for _ in range(length))
# # #             result = await db.execute(
# # #                 select(Order).where(Order.order_number == number)
# # #             )
# # #             if not result.scalar_one_or_none():
# # #                 return number
# # # # from sqlalchemy.ext.asyncio import AsyncSession
# # # # from sqlalchemy import func, and_, select
# # # # from typing import List, Optional, Dict, Any
# # # # from datetime import datetime, timedelta
# # # # from decimal import Decimal
# # # # import secrets
# # # # import string

# # # # from app.models.order import Order
# # # # from app.models.plan import HostingPlan
# # # # from app.models.users import UserProfile
# # # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary

# # # # class OrderService:
# # # #     async def get_user_orders(self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100, 
# # # #                             status: Optional[str] = None) -> List[Order]:
# # # #         query = select(Order).where(Order.user_id == user_id)
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()
    
# # # #     async def get_all_orders(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
# # # #                            status: Optional[str] = None) -> List[Order]:
# # # #         query = select(Order)
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()
    
# # # #     async def get_orders_with_plan(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
# # # #                                  status: Optional[str] = None, payment_status: Optional[str] = None) -> List[Dict[str, Any]]:
# # # #         query = select(Order, HostingPlan, UserProfile).join(
# # # #             HostingPlan, Order.plan_id == HostingPlan.id
# # # #         ).join(
# # # #             UserProfile, Order.user_id == UserProfile.id
# # # #         )
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         if payment_status and payment_status != "all":
# # # #             query = query.where(Order.payment_status == payment_status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         orders_with_details = result.all()
        
# # # #         orders_list = []
# # # #         for order, plan, user in orders_with_details:
# # # #             order_dict = {
# # # #                 "id": order.id,
# # # #                 "user_id": order.user_id,
# # # #                 "plan_id": order.plan_id,
# # # #                 "order_number": order.order_number,
# # # #                 "order_status": order.order_status,
# # # #                 "total_amount": order.total_amount,
# # # #                 "payment_status": order.payment_status,
# # # #                 "billing_cycle": order.billing_cycle,
# # # #                 "server_details": order.server_details,
# # # #                 "payment_method": order.payment_method,
# # # #                 "payment_reference": order.payment_reference,
# # # #                 "payment_date": order.payment_date,
# # # #                 "created_at": order.created_at,
# # # #                 "updated_at": order.updated_at,
# # # #                 "plan_name": plan.name,
# # # #                 "plan_type": plan.plan_type,
# # # #                 "user_email": user.email
# # # #             }
# # # #             orders_list.append(order_dict)
        
# # # #         return orders_list
    
# # # #     async def get_order_by_id(self, db: AsyncSession, order_id: int) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(Order.id == order_id)
# # # #         )
# # # #         return result.scalar_one_or_none()
    
# # # #     async def get_user_order(self, db: AsyncSession, user_id: int, order_id: int) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(
# # # #                 Order.id == order_id,
# # # #                 Order.user_id == user_id
# # # #             )
# # # #         )
# # # #         return result.scalar_one_or_none()
    
# # # #     async def create_order(self, db: AsyncSession, user_id: int, order_data: OrderCreate) -> Order:
# # # #         # Get plan details
# # # #         result = await db.execute(
# # # #             select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # # #         )
# # # #         plan = result.scalar_one_or_none()
        
# # # #         if not plan:
# # # #             raise ValueError("Plan not found")
        
# # # #         # Generate order number
# # # #         order_number = await self._generate_order_number(db)
        
# # # #         db_order = Order(
# # # #             user_id=user_id,
# # # #             plan_id=order_data.plan_id,
# # # #             order_number=order_number,
# # # #             billing_cycle=order_data.billing_cycle,
# # # #             total_amount=order_data.total_amount,
# # # #             server_details=order_data.server_details
# # # #         )
        
# # # #         db.add(db_order)
# # # #         await db.commit()
# # # #         await db.refresh(db_order)
# # # #         return db_order
    
# # # #     async def update_order(self, db: AsyncSession, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return None
            
# # # #         update_data = order_update.dict(exclude_unset=True)
# # # #         for field, value in update_data.items():
# # # #             setattr(order, field, value)
            
# # # #         await db.commit()
# # # #         await db.refresh(order)
# # # #         return order
    
# # # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "cancelled"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def cancel_user_order(self, db: AsyncSession, user_id: int, order_id: int) -> bool:
# # # #         order = await self.get_user_order(db, user_id, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "cancelled"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "completed"
# # # #         order.payment_status = "paid"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # # #         result = await db.execute(select(func.count(Order.id)))
# # # #         return result.scalar()
    
# # # #     async def get_recent_orders(self, db: AsyncSession, limit: int = 5) -> List[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # # #         )
# # # #         return result.scalars().all()
    
# # # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # # #         total_orders = await self.get_total_orders(db)
        
# # # #         pending_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # # #         )
# # # #         pending_orders = pending_result.scalar()
        
# # # #         completed_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # # #         )
# # # #         completed_orders = completed_result.scalar()
        
# # # #         cancelled_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # # #         )
# # # #         cancelled_orders = cancelled_result.scalar()
        
# # # #         # Calculate revenue
# # # #         total_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # # #         )
# # # #         total_revenue = total_revenue_result.scalar() or Decimal('0.0')
        
# # # #         # Calculate monthly revenue
# # # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # # #         monthly_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(
# # # #                 Order.payment_status == "paid",
# # # #                 Order.created_at >= start_of_month
# # # #             )
# # # #         )
# # # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal('0.0')
        
# # # #         return OrderSummary(
# # # #             total_orders=total_orders,
# # # #             pending_orders=pending_orders,
# # # #             completed_orders=completed_orders,
# # # #             cancelled_orders=cancelled_orders,
# # # #             total_revenue=total_revenue,
# # # #             monthly_revenue=monthly_revenue
# # # #         )
    
# # # #     async def _generate_order_number(self, db: AsyncSession, length: int = 10) -> str:
# # # #         """Generate a unique order number"""
# # # #         characters = string.ascii_uppercase + string.digits
# # # #         while True:
# # # #             number = 'ORD-' + ''.join(secrets.choice(characters) for _ in range(length))
# # # #             # Check if order number already exists
# # # #             result = await db.execute(
# # # #                 select(Order).where(Order.order_number == number)
# # # #             )
# # # #             existing_order = result.scalar_one_or_none()
# # # #             if not existing_order:
# # # #                 return number




# # # # from sqlalchemy.ext.asyncio import AsyncSession
# # # # from sqlalchemy import func, select
# # # # from typing import List, Optional, Dict, Any
# # # # from datetime import datetime
# # # # from decimal import Decimal
# # # # import secrets
# # # # import string

# # # # from app.models.order import Order
# # # # from app.models.plan import HostingPlan
# # # # from app.models.users import UserProfile
# # # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary


# # # # class OrderService:
# # # #     # -----------------------------
# # # #     # 🔹 USER-SPECIFIC QUERIES
# # # #     # -----------------------------
# # # #     async def get_user_orders(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         user_id: int,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #     ) -> List[Order]:
# # # #         query = select(Order).where(Order.user_id == user_id)

# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()

# # # #     async def get_user_order(
# # # #         self, db: AsyncSession, user_id: int, order_id: int
# # # #     ) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(Order.id == order_id, Order.user_id == user_id)
# # # #         )
# # # #         return result.scalar_one_or_none()

# # # #     # -----------------------------
# # # #     # 🔹 ADMIN / GLOBAL QUERIES
# # # #     # -----------------------------
# # # #     async def get_all_orders(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #     ) -> List[Order]:
# # # #         query = select(Order)
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()

# # # #     async def get_orders_with_plan(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #         payment_status: Optional[str] = None,
# # # #     ) -> List[Dict[str, Any]]:
# # # #         query = (
# # # #             select(Order, HostingPlan, UserProfile)
# # # #             .join(HostingPlan, Order.plan_id == HostingPlan.id)
# # # #             .join(UserProfile, Order.user_id == UserProfile.id)
# # # #         )

# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
# # # #         if payment_status and payment_status != "all":
# # # #             query = query.where(Order.payment_status == payment_status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         rows = result.all()

# # # #         orders_list = []
# # # #         for order, plan, user in rows:
# # # #             orders_list.append(
# # # #                 {
# # # #                     "id": order.id,
# # # #                     "user_id": order.user_id,
# # # #                     "plan_id": order.plan_id,
# # # #                     "order_number": order.order_number,
# # # #                     "order_status": order.order_status,
# # # #                     "total_amount": order.total_amount,
# # # #                     "payment_status": order.payment_status,
# # # #                     "billing_cycle": order.billing_cycle,
# # # #                     "server_details": order.server_details,
# # # #                     "payment_method": order.payment_method,
# # # #                     "payment_reference": order.payment_reference,
# # # #                     "payment_date": order.payment_date,
# # # #                     "created_at": order.created_at,
# # # #                     "updated_at": order.updated_at,
# # # #                     "plan_name": plan.name,
# # # #                     "plan_type": plan.plan_type,
# # # #                     "user_email": user.email,
# # # #                 }
# # # #             )
# # # #         return orders_list

# # # #     # -----------------------------
# # # #     # 🔹 CRUD OPERATIONS
# # # #     # -----------------------------
# # # #     async def get_order_by_id(
# # # #         self, db: AsyncSession, order_id: int
# # # #     ) -> Optional[Order]:
# # # #         result = await db.execute(select(Order).where(Order.id == order_id))
# # # #         return result.scalar_one_or_none()

# # # #     async def create_order(
# # # #         self, db: AsyncSession, user_id: int, order_data: OrderCreate
# # # #     ) -> Order:
# # # #         # Get plan details
# # # #         result = await db.execute(
# # # #             select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # # #         )
# # # #         plan = result.scalar_one_or_none()
# # # #         if not plan:
# # # #             raise ValueError("Plan not found")

# # # #         # Generate unique order number
# # # #         order_number = await self._generate_order_number(db)

# # # #         new_order = Order(
# # # #             user_id=user_id,
# # # #             plan_id=order_data.plan_id,
# # # #             order_number=order_number,
# # # #             billing_cycle=order_data.billing_cycle,
# # # #             total_amount=order_data.total_amount,
# # # #             server_details=order_data.server_details,
# # # #         )

# # # #         async with db.begin():
# # # #             db.add(new_order)

# # # #         await db.refresh(new_order)
# # # #         return new_order

# # # #     async def update_order(
# # # #         self, db: AsyncSession, order_id: int, order_update: OrderUpdate
# # # #     ) -> Optional[Order]:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return None

# # # #         update_data = order_update.dict(exclude_unset=True)
# # # #         for field, value in update_data.items():
# # # #             setattr(order, field, value)

# # # #         async with db.begin():
# # # #             db.add(order)

# # # #         await db.refresh(order)
# # # #         return order

# # # #     # -----------------------------
# # # #     # 🔹 ORDER STATUS ACTIONS
# # # #     # -----------------------------

# # # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "cancelled"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     async def cancel_user_order(
# # # #         self, db: AsyncSession, user_id: int, order_id: int
# # # #     ) -> bool:
# # # #         order = await self.get_user_order(db, user_id, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "cancelled"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "completed"
# # # #         order.payment_status = "paid"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     # -----------------------------
# # # #     # 🔹 ANALYTICS / STATS
# # # #     # -----------------------------
# # # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # # #         result = await db.execute(select(func.count(Order.id)))
# # # #         return result.scalar() or 0

# # # #     async def get_recent_orders(
# # # #         self, db: AsyncSession, limit: int = 5
# # # #     ) -> List[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # # #         )
# # # #         return result.scalars().all()

# # # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # # #         total_orders = await self.get_total_orders(db)

# # # #         pending = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # # #         )
# # # #         completed = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # # #         )
# # # #         cancelled = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # # #         )

# # # #         total_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # # #         )
# # # #         total_revenue = total_revenue_result.scalar() or Decimal("0.0")

# # # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # # #         monthly_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(
# # # #                 Order.payment_status == "paid", Order.created_at >= start_of_month
# # # #             )
# # # #         )
# # # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal("0.0")

# # # #         return OrderSummary(
# # # #             total_orders=total_orders,
# # # #             pending_orders=pending.scalar() or 0,
# # # #             completed_orders=completed.scalar() or 0,
# # # #             cancelled_orders=cancelled.scalar() or 0,
# # # #             total_revenue=total_revenue,
# # # #             monthly_revenue=monthly_revenue,
# # # #         )

# # # #     # -----------------------------
# # # #     # 🔹 PRIVATE HELPERS
# # # #     # -----------------------------
# # # #     async def _generate_order_number(
# # # #         self, db: AsyncSession, length: int = 10
# # # #     ) -> str:
# # # #         """Generate a unique order number"""
# # # #         chars = string.ascii_uppercase + string.digits
# # # #         while True:
# # # #             number = "ORD-" + "".join(secrets.choice(chars) for _ in range(length))
# # # #             result = await db.execute(
# # # #                 select(Order).where(Order.order_number == number)
# # # #             )
# # # #             if not result.scalar_one_or_none():
# # # #                 return number





# # # from sqlalchemy.ext.asyncio import AsyncSession
# # # from sqlalchemy import func, select
# # # from typing import List, Optional, Dict, Any
# # # from datetime import datetime
# # # from decimal import Decimal
# # # import secrets
# # # import string

# # # from app.models.order import Order
# # # from app.models.plan import HostingPlan
# # # from app.models.users import UserProfile
# # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary


# # # class OrderService:
# # #     # -----------------------------
# # #     # 🔹 USER-SPECIFIC QUERIES
# # #     # -----------------------------
# # #     async def get_user_orders(
# # #         self,
# # #         db: AsyncSession,
# # #         user_id: int,
# # #         skip: int = 0,
# # #         limit: int = 100,
# # #         status: Optional[str] = None,
# # #     ) -> List[Order]:
# # #         query = select(Order).where(Order.user_id == user_id)
# # #         if status and status != "all":
# # #             query = query.where(Order.order_status == status)
# # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

# # #         result = await db.execute(query)
# # #         return result.scalars().all()

# # #     async def get_user_order(
# # #         self, db: AsyncSession, user_id: int, order_id: int
# # #     ) -> Optional[Order]:
# # #         result = await db.execute(
# # #             select(Order).where(Order.id == order_id, Order.user_id == user_id)
# # #         )
# # #         return result.scalar_one_or_none()

# # #     # -----------------------------
# # #     # 🔹 ADMIN / GLOBAL QUERIES
# # #     # -----------------------------
# # #     async def get_all_orders(
# # #         self,
# # #         db: AsyncSession,
# # #         skip: int = 0,
# # #         limit: int = 100,
# # #         status: Optional[str] = None,
# # #     ) -> List[Order]:
# # #         query = select(Order)
# # #         if status and status != "all":
# # #             query = query.where(Order.order_status == status)
# # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

# # #         result = await db.execute(query)
# # #         return result.scalars().all()

# # #     async def get_orders_with_plan(
# # #         self,
# # #         db: AsyncSession,
# # #         skip: int = 0,
# # #         limit: int = 100,
# # #         status: Optional[str] = None,
# # #         payment_status: Optional[str] = None,
# # #     ) -> List[Dict[str, Any]]:
# # #         query = (
# # #             select(Order, HostingPlan, UserProfile)
# # #             .join(HostingPlan, Order.plan_id == HostingPlan.id)
# # #             .join(UserProfile, Order.user_id == UserProfile.id)
# # #         )

# # #         if status and status != "all":
# # #             query = query.where(Order.order_status == status)
# # #         if payment_status and payment_status != "all":
# # #             query = query.where(Order.payment_status == payment_status)

# # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # #         result = await db.execute(query)
# # #         rows = result.all()

# # #         return [
# # #             {
# # #                 "id": order.id,
# # #                 "user_id": order.user_id,
# # #                 "plan_id": order.plan_id,
# # #                 "order_number": order.order_number,
# # #                 "order_status": order.order_status,
# # #                 "total_amount": order.total_amount,
# # #                 "payment_status": order.payment_status,
# # #                 "billing_cycle": order.billing_cycle,
# # #                 "server_details": order.server_details,
# # #                 "payment_method": order.payment_method,
# # #                 "payment_reference": order.payment_reference,
# # #                 "payment_date": order.payment_date,
# # #                 "created_at": order.created_at,
# # #                 "updated_at": order.updated_at,
# # #                 "plan_name": plan.name,
# # #                 "plan_type": plan.plan_type,
# # #                 "user_email": user.email,
# # #             }
# # #             for order, plan, user in rows
# # #         ]

# # #     # -----------------------------
# # #     # 🔹 CRUD OPERATIONS
# # #     # -----------------------------
# # #     async def get_order_by_id(self, db: AsyncSession, order_id: int) -> Optional[Order]:
# # #         result = await db.execute(select(Order).where(Order.id == order_id))
# # #         return result.scalar_one_or_none()

# # #     async def create_order(
# # #         self, db: AsyncSession, user_id: int, order_data: OrderCreate
# # #     ) -> Order:
# # #         try:
# # #             # ✅ 1. Get plan details
# # #             result = await db.execute(
# # #                 select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # #             )
# # #             plan = result.scalar_one_or_none()
# # #             if not plan:
# # #                 raise ValueError("Plan not found")

# # #             # ✅ 2. Generate unique order number
# # #             order_number = await self._generate_order_number(db)

# # #             # ✅ 3. Create order instance
# # #             new_order = Order(
# # #                 user_id=user_id,
# # #                 plan_id=order_data.plan_id,
# # #                 order_number=order_number,
# # #                 billing_cycle=order_data.billing_cycle,
# # #                 total_amount=order_data.total_amount,
# # #                 server_details=order_data.server_details,
# # #                 created_at=datetime.utcnow(),
# # #                 updated_at=datetime.utcnow(),
# # #             )

# # #             db.add(new_order)
# # #             await db.commit()
# # #             await db.refresh(new_order)
# # #             return new_order

# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     async def update_order(
# # #         self, db: AsyncSession, order_id: int, order_update: OrderUpdate
# # #     ) -> Optional[Order]:
# # #         order = await self.get_order_by_id(db, order_id)
# # #         if not order:
# # #             return None

# # #         update_data = order_update.dict(exclude_unset=True)
# # #         for field, value in update_data.items():
# # #             setattr(order, field, value)

# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             await db.refresh(order)
# # #             return order
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     # -----------------------------
# # #     # 🔹 ORDER STATUS ACTIONS
# # #     # -----------------------------
# # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # #         order = await self.get_order_by_id(db, order_id)
# # #         if not order:
# # #             return False

# # #         order.order_status = "cancelled"
# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             return True
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     async def cancel_user_order(
# # #         self, db: AsyncSession, user_id: int, order_id: int
# # #     ) -> bool:
# # #         order = await self.get_user_order(db, user_id, order_id)
# # #         if not order:
# # #             return False

# # #         order.order_status = "cancelled"
# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             return True
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # #         order = await self.get_order_by_id(db, order_id)
# # #         if not order:
# # #             return False

# # #         order.order_status = "completed"
# # #         order.payment_status = "paid"
# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             return True
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     # -----------------------------
# # #     # 🔹 ANALYTICS / STATS
# # #     # -----------------------------
    
# # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # #         result = await db.execute(select(func.count(Order.id)))
# # #         return result.scalar() or 0

# # #     async def get_recent_orders(self, db: AsyncSession, limit: int = 5) -> List[Order]:
# # #         result = await db.execute(
# # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # #         )
# # #         return result.scalars().all()

# # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # #         total_orders = await self.get_total_orders(db)

# # #         pending = await db.execute(
# # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # #         )
# # #         completed = await db.execute(
# # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # #         )
# # #         cancelled = await db.execute(
# # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # #         )

# # #         total_revenue_result = await db.execute(
# # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # #         )
# # #         total_revenue = total_revenue_result.scalar() or Decimal("0.0")

# # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # #         monthly_revenue_result = await db.execute(
# # #             select(func.sum(Order.total_amount)).where(
# # #                 Order.payment_status == "paid", Order.created_at >= start_of_month
# # #             )
# # #         )
# # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal("0.0")

# # #         return OrderSummary(
# # #             total_orders=total_orders,
# # #             pending_orders=pending.scalar() or 0,
# # #             completed_orders=completed.scalar() or 0,
# # #             cancelled_orders=cancelled.scalar() or 0,
# # #             total_revenue=total_revenue,
# # #             monthly_revenue=monthly_revenue,
# # #         )

# # #     # -----------------------------
# # #     # 🔹 PRIVATE HELPERS
# # #     # -----------------------------
# # #     async def _generate_order_number(self, db: AsyncSession, length: int = 10) -> str:
# # #         chars = string.ascii_uppercase + string.digits
# # #         while True:
# # #             number = "ORD-" + "".join(secrets.choice(chars) for _ in range(length))
# # #             result = await db.execute(
# # #                 select(Order).where(Order.order_number == number)
# # #             )
# # #             if not result.scalar_one_or_none():
# # #                 return number
# # # # from sqlalchemy.ext.asyncio import AsyncSession
# # # # from sqlalchemy import func, and_, select
# # # # from typing import List, Optional, Dict, Any
# # # # from datetime import datetime, timedelta
# # # # from decimal import Decimal
# # # # import secrets
# # # # import string

# # # # from app.models.order import Order
# # # # from app.models.plan import HostingPlan
# # # # from app.models.users import UserProfile
# # # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary

# # # # class OrderService:
# # # #     async def get_user_orders(self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100, 
# # # #                             status: Optional[str] = None) -> List[Order]:
# # # #         query = select(Order).where(Order.user_id == user_id)
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()
    
# # # #     async def get_all_orders(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
# # # #                            status: Optional[str] = None) -> List[Order]:
# # # #         query = select(Order)
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()
    
# # # #     async def get_orders_with_plan(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
# # # #                                  status: Optional[str] = None, payment_status: Optional[str] = None) -> List[Dict[str, Any]]:
# # # #         query = select(Order, HostingPlan, UserProfile).join(
# # # #             HostingPlan, Order.plan_id == HostingPlan.id
# # # #         ).join(
# # # #             UserProfile, Order.user_id == UserProfile.id
# # # #         )
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         if payment_status and payment_status != "all":
# # # #             query = query.where(Order.payment_status == payment_status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         orders_with_details = result.all()
        
# # # #         orders_list = []
# # # #         for order, plan, user in orders_with_details:
# # # #             order_dict = {
# # # #                 "id": order.id,
# # # #                 "user_id": order.user_id,
# # # #                 "plan_id": order.plan_id,
# # # #                 "order_number": order.order_number,
# # # #                 "order_status": order.order_status,
# # # #                 "total_amount": order.total_amount,
# # # #                 "payment_status": order.payment_status,
# # # #                 "billing_cycle": order.billing_cycle,
# # # #                 "server_details": order.server_details,
# # # #                 "payment_method": order.payment_method,
# # # #                 "payment_reference": order.payment_reference,
# # # #                 "payment_date": order.payment_date,
# # # #                 "created_at": order.created_at,
# # # #                 "updated_at": order.updated_at,
# # # #                 "plan_name": plan.name,
# # # #                 "plan_type": plan.plan_type,
# # # #                 "user_email": user.email
# # # #             }
# # # #             orders_list.append(order_dict)
        
# # # #         return orders_list
    
# # # #     async def get_order_by_id(self, db: AsyncSession, order_id: int) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(Order.id == order_id)
# # # #         )
# # # #         return result.scalar_one_or_none()
    
# # # #     async def get_user_order(self, db: AsyncSession, user_id: int, order_id: int) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(
# # # #                 Order.id == order_id,
# # # #                 Order.user_id == user_id
# # # #             )
# # # #         )
# # # #         return result.scalar_one_or_none()
    
# # # #     async def create_order(self, db: AsyncSession, user_id: int, order_data: OrderCreate) -> Order:
# # # #         # Get plan details
# # # #         result = await db.execute(
# # # #             select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # # #         )
# # # #         plan = result.scalar_one_or_none()
        
# # # #         if not plan:
# # # #             raise ValueError("Plan not found")
        
# # # #         # Generate order number
# # # #         order_number = await self._generate_order_number(db)
        
# # # #         db_order = Order(
# # # #             user_id=user_id,
# # # #             plan_id=order_data.plan_id,
# # # #             order_number=order_number,
# # # #             billing_cycle=order_data.billing_cycle,
# # # #             total_amount=order_data.total_amount,
# # # #             server_details=order_data.server_details
# # # #         )
        
# # # #         db.add(db_order)
# # # #         await db.commit()
# # # #         await db.refresh(db_order)
# # # #         return db_order
    
# # # #     async def update_order(self, db: AsyncSession, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return None
            
# # # #         update_data = order_update.dict(exclude_unset=True)
# # # #         for field, value in update_data.items():
# # # #             setattr(order, field, value)
            
# # # #         await db.commit()
# # # #         await db.refresh(order)
# # # #         return order
    
# # # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "cancelled"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def cancel_user_order(self, db: AsyncSession, user_id: int, order_id: int) -> bool:
# # # #         order = await self.get_user_order(db, user_id, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "cancelled"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "completed"
# # # #         order.payment_status = "paid"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # # #         result = await db.execute(select(func.count(Order.id)))
# # # #         return result.scalar()
    
# # # #     async def get_recent_orders(self, db: AsyncSession, limit: int = 5) -> List[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # # #         )
# # # #         return result.scalars().all()
    
# # # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # # #         total_orders = await self.get_total_orders(db)
        
# # # #         pending_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # # #         )
# # # #         pending_orders = pending_result.scalar()
        
# # # #         completed_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # # #         )
# # # #         completed_orders = completed_result.scalar()
        
# # # #         cancelled_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # # #         )
# # # #         cancelled_orders = cancelled_result.scalar()
        
# # # #         # Calculate revenue
# # # #         total_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # # #         )
# # # #         total_revenue = total_revenue_result.scalar() or Decimal('0.0')
        
# # # #         # Calculate monthly revenue
# # # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # # #         monthly_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(
# # # #                 Order.payment_status == "paid",
# # # #                 Order.created_at >= start_of_month
# # # #             )
# # # #         )
# # # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal('0.0')
        
# # # #         return OrderSummary(
# # # #             total_orders=total_orders,
# # # #             pending_orders=pending_orders,
# # # #             completed_orders=completed_orders,
# # # #             cancelled_orders=cancelled_orders,
# # # #             total_revenue=total_revenue,
# # # #             monthly_revenue=monthly_revenue
# # # #         )
    
# # # #     async def _generate_order_number(self, db: AsyncSession, length: int = 10) -> str:
# # # #         """Generate a unique order number"""
# # # #         characters = string.ascii_uppercase + string.digits
# # # #         while True:
# # # #             number = 'ORD-' + ''.join(secrets.choice(characters) for _ in range(length))
# # # #             # Check if order number already exists
# # # #             result = await db.execute(
# # # #                 select(Order).where(Order.order_number == number)
# # # #             )
# # # #             existing_order = result.scalar_one_or_none()
# # # #             if not existing_order:
# # # #                 return number




# # # # from sqlalchemy.ext.asyncio import AsyncSession
# # # # from sqlalchemy import func, select
# # # # from typing import List, Optional, Dict, Any
# # # # from datetime import datetime
# # # # from decimal import Decimal
# # # # import secrets
# # # # import string

# # # # from app.models.order import Order
# # # # from app.models.plan import HostingPlan
# # # # from app.models.users import UserProfile
# # # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary


# # # # class OrderService:
# # # #     # -----------------------------
# # # #     # 🔹 USER-SPECIFIC QUERIES
# # # #     # -----------------------------
# # # #     async def get_user_orders(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         user_id: int,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #     ) -> List[Order]:
# # # #         query = select(Order).where(Order.user_id == user_id)

# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()

# # # #     async def get_user_order(
# # # #         self, db: AsyncSession, user_id: int, order_id: int
# # # #     ) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(Order.id == order_id, Order.user_id == user_id)
# # # #         )
# # # #         return result.scalar_one_or_none()

# # # #     # -----------------------------
# # # #     # 🔹 ADMIN / GLOBAL QUERIES
# # # #     # -----------------------------
# # # #     async def get_all_orders(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #     ) -> List[Order]:
# # # #         query = select(Order)
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()

# # # #     async def get_orders_with_plan(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #         payment_status: Optional[str] = None,
# # # #     ) -> List[Dict[str, Any]]:
# # # #         query = (
# # # #             select(Order, HostingPlan, UserProfile)
# # # #             .join(HostingPlan, Order.plan_id == HostingPlan.id)
# # # #             .join(UserProfile, Order.user_id == UserProfile.id)
# # # #         )

# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
# # # #         if payment_status and payment_status != "all":
# # # #             query = query.where(Order.payment_status == payment_status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         rows = result.all()

# # # #         orders_list = []
# # # #         for order, plan, user in rows:
# # # #             orders_list.append(
# # # #                 {
# # # #                     "id": order.id,
# # # #                     "user_id": order.user_id,
# # # #                     "plan_id": order.plan_id,
# # # #                     "order_number": order.order_number,
# # # #                     "order_status": order.order_status,
# # # #                     "total_amount": order.total_amount,
# # # #                     "payment_status": order.payment_status,
# # # #                     "billing_cycle": order.billing_cycle,
# # # #                     "server_details": order.server_details,
# # # #                     "payment_method": order.payment_method,
# # # #                     "payment_reference": order.payment_reference,
# # # #                     "payment_date": order.payment_date,
# # # #                     "created_at": order.created_at,
# # # #                     "updated_at": order.updated_at,
# # # #                     "plan_name": plan.name,
# # # #                     "plan_type": plan.plan_type,
# # # #                     "user_email": user.email,
# # # #                 }
# # # #             )
# # # #         return orders_list

# # # #     # -----------------------------
# # # #     # 🔹 CRUD OPERATIONS
# # # #     # -----------------------------
# # # #     async def get_order_by_id(
# # # #         self, db: AsyncSession, order_id: int
# # # #     ) -> Optional[Order]:
# # # #         result = await db.execute(select(Order).where(Order.id == order_id))
# # # #         return result.scalar_one_or_none()

# # # #     async def create_order(
# # # #         self, db: AsyncSession, user_id: int, order_data: OrderCreate
# # # #     ) -> Order:
# # # #         # Get plan details
# # # #         result = await db.execute(
# # # #             select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # # #         )
# # # #         plan = result.scalar_one_or_none()
# # # #         if not plan:
# # # #             raise ValueError("Plan not found")

# # # #         # Generate unique order number
# # # #         order_number = await self._generate_order_number(db)

# # # #         new_order = Order(
# # # #             user_id=user_id,
# # # #             plan_id=order_data.plan_id,
# # # #             order_number=order_number,
# # # #             billing_cycle=order_data.billing_cycle,
# # # #             total_amount=order_data.total_amount,
# # # #             server_details=order_data.server_details,
# # # #         )

# # # #         async with db.begin():
# # # #             db.add(new_order)

# # # #         await db.refresh(new_order)
# # # #         return new_order

# # # #     async def update_order(
# # # #         self, db: AsyncSession, order_id: int, order_update: OrderUpdate
# # # #     ) -> Optional[Order]:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return None

# # # #         update_data = order_update.dict(exclude_unset=True)
# # # #         for field, value in update_data.items():
# # # #             setattr(order, field, value)

# # # #         async with db.begin():
# # # #             db.add(order)

# # # #         await db.refresh(order)
# # # #         return order

# # # #     # -----------------------------
# # # #     # 🔹 ORDER STATUS ACTIONS
# # # #     # -----------------------------

# # # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "cancelled"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     async def cancel_user_order(
# # # #         self, db: AsyncSession, user_id: int, order_id: int
# # # #     ) -> bool:
# # # #         order = await self.get_user_order(db, user_id, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "cancelled"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "completed"
# # # #         order.payment_status = "paid"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     # -----------------------------
# # # #     # 🔹 ANALYTICS / STATS
# # # #     # -----------------------------
# # # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # # #         result = await db.execute(select(func.count(Order.id)))
# # # #         return result.scalar() or 0

# # # #     async def get_recent_orders(
# # # #         self, db: AsyncSession, limit: int = 5
# # # #     ) -> List[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # # #         )
# # # #         return result.scalars().all()

# # # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # # #         total_orders = await self.get_total_orders(db)

# # # #         pending = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # # #         )
# # # #         completed = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # # #         )
# # # #         cancelled = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # # #         )

# # # #         total_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # # #         )
# # # #         total_revenue = total_revenue_result.scalar() or Decimal("0.0")

# # # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # # #         monthly_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(
# # # #                 Order.payment_status == "paid", Order.created_at >= start_of_month
# # # #             )
# # # #         )
# # # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal("0.0")

# # # #         return OrderSummary(
# # # #             total_orders=total_orders,
# # # #             pending_orders=pending.scalar() or 0,
# # # #             completed_orders=completed.scalar() or 0,
# # # #             cancelled_orders=cancelled.scalar() or 0,
# # # #             total_revenue=total_revenue,
# # # #             monthly_revenue=monthly_revenue,
# # # #         )

# # # #     # -----------------------------
# # # #     # 🔹 PRIVATE HELPERS
# # # #     # -----------------------------
# # # #     async def _generate_order_number(
# # # #         self, db: AsyncSession, length: int = 10
# # # #     ) -> str:
# # # #         """Generate a unique order number"""
# # # #         chars = string.ascii_uppercase + string.digits
# # # #         while True:
# # # #             number = "ORD-" + "".join(secrets.choice(chars) for _ in range(length))
# # # #             result = await db.execute(
# # # #                 select(Order).where(Order.order_number == number)
# # # #             )
# # # #             if not result.scalar_one_or_none():
# # # #                 return number





# # # from sqlalchemy.ext.asyncio import AsyncSession
# # # from sqlalchemy import func, select
# # # from typing import List, Optional, Dict, Any
# # # from datetime import datetime
# # # from decimal import Decimal
# # # import secrets
# # # import string

# # # from app.models.order import Order
# # # from app.models.plan import HostingPlan
# # # from app.models.users import UserProfile
# # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary


# # # class OrderService:
# # #     # -----------------------------
# # #     # 🔹 USER-SPECIFIC QUERIES
# # #     # -----------------------------
# # #     async def get_user_orders(
# # #         self,
# # #         db: AsyncSession,
# # #         user_id: int,
# # #         skip: int = 0,
# # #         limit: int = 100,
# # #         status: Optional[str] = None,
# # #     ) -> List[Order]:
# # #         query = select(Order).where(Order.user_id == user_id)
# # #         if status and status != "all":
# # #             query = query.where(Order.order_status == status)
# # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

# # #         result = await db.execute(query)
# # #         return result.scalars().all()

# # #     async def get_user_order(
# # #         self, db: AsyncSession, user_id: int, order_id: int
# # #     ) -> Optional[Order]:
# # #         result = await db.execute(
# # #             select(Order).where(Order.id == order_id, Order.user_id == user_id)
# # #         )
# # #         return result.scalar_one_or_none()

# # #     # -----------------------------
# # #     # 🔹 ADMIN / GLOBAL QUERIES
# # #     # -----------------------------
# # #     async def get_all_orders(
# # #         self,
# # #         db: AsyncSession,
# # #         skip: int = 0,
# # #         limit: int = 100,
# # #         status: Optional[str] = None,
# # #     ) -> List[Order]:
# # #         query = select(Order)
# # #         if status and status != "all":
# # #             query = query.where(Order.order_status == status)
# # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

# # #         result = await db.execute(query)
# # #         return result.scalars().all()

# # #     async def get_orders_with_plan(
# # #         self,
# # #         db: AsyncSession,
# # #         skip: int = 0,
# # #         limit: int = 100,
# # #         status: Optional[str] = None,
# # #         payment_status: Optional[str] = None,
# # #     ) -> List[Dict[str, Any]]:
# # #         query = (
# # #             select(Order, HostingPlan, UserProfile)
# # #             .join(HostingPlan, Order.plan_id == HostingPlan.id)
# # #             .join(UserProfile, Order.user_id == UserProfile.id)
# # #         )

# # #         if status and status != "all":
# # #             query = query.where(Order.order_status == status)
# # #         if payment_status and payment_status != "all":
# # #             query = query.where(Order.payment_status == payment_status)

# # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # #         result = await db.execute(query)
# # #         rows = result.all()

# # #         return [
# # #             {
# # #                 "id": order.id,
# # #                 "user_id": order.user_id,
# # #                 "plan_id": order.plan_id,
# # #                 "order_number": order.order_number,
# # #                 "order_status": order.order_status,
# # #                 "total_amount": order.total_amount,
# # #                 "payment_status": order.payment_status,
# # #                 "billing_cycle": order.billing_cycle,
# # #                 "server_details": order.server_details,
# # #                 "payment_method": order.payment_method,
# # #                 "payment_reference": order.payment_reference,
# # #                 "payment_date": order.payment_date,
# # #                 "created_at": order.created_at,
# # #                 "updated_at": order.updated_at,
# # #                 "plan_name": plan.name,
# # #                 "plan_type": plan.plan_type,
# # #                 "user_email": user.email,
# # #             }
# # #             for order, plan, user in rows
# # #         ]

# # #     # -----------------------------
# # #     # 🔹 CRUD OPERATIONS
# # #     # -----------------------------
# # #     async def get_order_by_id(self, db: AsyncSession, order_id: int) -> Optional[Order]:
# # #         result = await db.execute(select(Order).where(Order.id == order_id))
# # #         return result.scalar_one_or_none()

# # #     async def create_order(
# # #         self, db: AsyncSession, user_id: int, order_data: OrderCreate
# # #     ) -> Order:
# # #         try:
# # #             # ✅ 1. Get plan details
# # #             result = await db.execute(
# # #                 select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # #             )
# # #             plan = result.scalar_one_or_none()
# # #             if not plan:
# # #                 raise ValueError("Plan not found")

# # #             # ✅ 2. Generate unique order number
# # #             order_number = await self._generate_order_number(db)

# # #             # ✅ 3. Create order instance
# # #             new_order = Order(
# # #                 user_id=user_id,
# # #                 plan_id=order_data.plan_id,
# # #                 order_number=order_number,
# # #                 billing_cycle=order_data.billing_cycle,
# # #                 total_amount=order_data.total_amount,
# # #                 server_details=order_data.server_details,
# # #                 created_at=datetime.utcnow(),
# # #                 updated_at=datetime.utcnow(),
# # #             )

# # #             db.add(new_order)
# # #             await db.commit()
# # #             await db.refresh(new_order)
# # #             return new_order

# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     async def update_order(
# # #         self, db: AsyncSession, order_id: int, order_update: OrderUpdate
# # #     ) -> Optional[Order]:
# # #         order = await self.get_order_by_id(db, order_id)
# # #         if not order:
# # #             return None

# # #         update_data = order_update.dict(exclude_unset=True)
# # #         for field, value in update_data.items():
# # #             setattr(order, field, value)

# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             await db.refresh(order)
# # #             return order
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     # -----------------------------
# # #     # 🔹 ORDER STATUS ACTIONS
# # #     # -----------------------------
# # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # #         order = await self.get_order_by_id(db, order_id)
# # #         if not order:
# # #             return False

# # #         order.order_status = "cancelled"
# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             return True
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     async def cancel_user_order(
# # #         self, db: AsyncSession, user_id: int, order_id: int
# # #     ) -> bool:
# # #         order = await self.get_user_order(db, user_id, order_id)
# # #         if not order:
# # #             return False

# # #         order.order_status = "cancelled"
# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             return True
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # #         order = await self.get_order_by_id(db, order_id)
# # #         if not order:
# # #             return False

# # #         order.order_status = "completed"
# # #         order.payment_status = "paid"
# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             return True
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     # -----------------------------
# # #     # 🔹 ANALYTICS / STATS
# # #     # -----------------------------
    
# # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # #         result = await db.execute(select(func.count(Order.id)))
# # #         return result.scalar() or 0

# # #     async def get_recent_orders(self, db: AsyncSession, limit: int = 5) -> List[Order]:
# # #         result = await db.execute(
# # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # #         )
# # #         return result.scalars().all()

# # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # #         total_orders = await self.get_total_orders(db)

# # #         pending = await db.execute(
# # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # #         )
# # #         completed = await db.execute(
# # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # #         )
# # #         cancelled = await db.execute(
# # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # #         )

# # #         total_revenue_result = await db.execute(
# # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # #         )
# # #         total_revenue = total_revenue_result.scalar() or Decimal("0.0")

# # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # #         monthly_revenue_result = await db.execute(
# # #             select(func.sum(Order.total_amount)).where(
# # #                 Order.payment_status == "paid", Order.created_at >= start_of_month
# # #             )
# # #         )
# # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal("0.0")

# # #         return OrderSummary(
# # #             total_orders=total_orders,
# # #             pending_orders=pending.scalar() or 0,
# # #             completed_orders=completed.scalar() or 0,
# # #             cancelled_orders=cancelled.scalar() or 0,
# # #             total_revenue=total_revenue,
# # #             monthly_revenue=monthly_revenue,
# # #         )

# # #     # -----------------------------
# # #     # 🔹 PRIVATE HELPERS
# # #     # -----------------------------
# # #     async def _generate_order_number(self, db: AsyncSession, length: int = 10) -> str:
# # #         chars = string.ascii_uppercase + string.digits
# # #         while True:
# # #             number = "ORD-" + "".join(secrets.choice(chars) for _ in range(length))
# # #             result = await db.execute(
# # #                 select(Order).where(Order.order_number == number)
# # #             )
# # #             if not result.scalar_one_or_none():
# # #                 return number
# # # # from sqlalchemy.ext.asyncio import AsyncSession
# # # # from sqlalchemy import func, and_, select
# # # # from typing import List, Optional, Dict, Any
# # # # from datetime import datetime, timedelta
# # # # from decimal import Decimal
# # # # import secrets
# # # # import string

# # # # from app.models.order import Order
# # # # from app.models.plan import HostingPlan
# # # # from app.models.users import UserProfile
# # # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary

# # # # class OrderService:
# # # #     async def get_user_orders(self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100, 
# # # #                             status: Optional[str] = None) -> List[Order]:
# # # #         query = select(Order).where(Order.user_id == user_id)
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()
    
# # # #     async def get_all_orders(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
# # # #                            status: Optional[str] = None) -> List[Order]:
# # # #         query = select(Order)
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()
    
# # # #     async def get_orders_with_plan(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
# # # #                                  status: Optional[str] = None, payment_status: Optional[str] = None) -> List[Dict[str, Any]]:
# # # #         query = select(Order, HostingPlan, UserProfile).join(
# # # #             HostingPlan, Order.plan_id == HostingPlan.id
# # # #         ).join(
# # # #             UserProfile, Order.user_id == UserProfile.id
# # # #         )
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         if payment_status and payment_status != "all":
# # # #             query = query.where(Order.payment_status == payment_status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         orders_with_details = result.all()
        
# # # #         orders_list = []
# # # #         for order, plan, user in orders_with_details:
# # # #             order_dict = {
# # # #                 "id": order.id,
# # # #                 "user_id": order.user_id,
# # # #                 "plan_id": order.plan_id,
# # # #                 "order_number": order.order_number,
# # # #                 "order_status": order.order_status,
# # # #                 "total_amount": order.total_amount,
# # # #                 "payment_status": order.payment_status,
# # # #                 "billing_cycle": order.billing_cycle,
# # # #                 "server_details": order.server_details,
# # # #                 "payment_method": order.payment_method,
# # # #                 "payment_reference": order.payment_reference,
# # # #                 "payment_date": order.payment_date,
# # # #                 "created_at": order.created_at,
# # # #                 "updated_at": order.updated_at,
# # # #                 "plan_name": plan.name,
# # # #                 "plan_type": plan.plan_type,
# # # #                 "user_email": user.email
# # # #             }
# # # #             orders_list.append(order_dict)
        
# # # #         return orders_list
    
# # # #     async def get_order_by_id(self, db: AsyncSession, order_id: int) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(Order.id == order_id)
# # # #         )
# # # #         return result.scalar_one_or_none()
    
# # # #     async def get_user_order(self, db: AsyncSession, user_id: int, order_id: int) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(
# # # #                 Order.id == order_id,
# # # #                 Order.user_id == user_id
# # # #             )
# # # #         )
# # # #         return result.scalar_one_or_none()
    
# # # #     async def create_order(self, db: AsyncSession, user_id: int, order_data: OrderCreate) -> Order:
# # # #         # Get plan details
# # # #         result = await db.execute(
# # # #             select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # # #         )
# # # #         plan = result.scalar_one_or_none()
        
# # # #         if not plan:
# # # #             raise ValueError("Plan not found")
        
# # # #         # Generate order number
# # # #         order_number = await self._generate_order_number(db)
        
# # # #         db_order = Order(
# # # #             user_id=user_id,
# # # #             plan_id=order_data.plan_id,
# # # #             order_number=order_number,
# # # #             billing_cycle=order_data.billing_cycle,
# # # #             total_amount=order_data.total_amount,
# # # #             server_details=order_data.server_details
# # # #         )
        
# # # #         db.add(db_order)
# # # #         await db.commit()
# # # #         await db.refresh(db_order)
# # # #         return db_order
    
# # # #     async def update_order(self, db: AsyncSession, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return None
            
# # # #         update_data = order_update.dict(exclude_unset=True)
# # # #         for field, value in update_data.items():
# # # #             setattr(order, field, value)
            
# # # #         await db.commit()
# # # #         await db.refresh(order)
# # # #         return order
    
# # # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "cancelled"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def cancel_user_order(self, db: AsyncSession, user_id: int, order_id: int) -> bool:
# # # #         order = await self.get_user_order(db, user_id, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "cancelled"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "completed"
# # # #         order.payment_status = "paid"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # # #         result = await db.execute(select(func.count(Order.id)))
# # # #         return result.scalar()
    
# # # #     async def get_recent_orders(self, db: AsyncSession, limit: int = 5) -> List[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # # #         )
# # # #         return result.scalars().all()
    
# # # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # # #         total_orders = await self.get_total_orders(db)
        
# # # #         pending_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # # #         )
# # # #         pending_orders = pending_result.scalar()
        
# # # #         completed_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # # #         )
# # # #         completed_orders = completed_result.scalar()
        
# # # #         cancelled_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # # #         )
# # # #         cancelled_orders = cancelled_result.scalar()
        
# # # #         # Calculate revenue
# # # #         total_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # # #         )
# # # #         total_revenue = total_revenue_result.scalar() or Decimal('0.0')
        
# # # #         # Calculate monthly revenue
# # # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # # #         monthly_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(
# # # #                 Order.payment_status == "paid",
# # # #                 Order.created_at >= start_of_month
# # # #             )
# # # #         )
# # # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal('0.0')
        
# # # #         return OrderSummary(
# # # #             total_orders=total_orders,
# # # #             pending_orders=pending_orders,
# # # #             completed_orders=completed_orders,
# # # #             cancelled_orders=cancelled_orders,
# # # #             total_revenue=total_revenue,
# # # #             monthly_revenue=monthly_revenue
# # # #         )
    
# # # #     async def _generate_order_number(self, db: AsyncSession, length: int = 10) -> str:
# # # #         """Generate a unique order number"""
# # # #         characters = string.ascii_uppercase + string.digits
# # # #         while True:
# # # #             number = 'ORD-' + ''.join(secrets.choice(characters) for _ in range(length))
# # # #             # Check if order number already exists
# # # #             result = await db.execute(
# # # #                 select(Order).where(Order.order_number == number)
# # # #             )
# # # #             existing_order = result.scalar_one_or_none()
# # # #             if not existing_order:
# # # #                 return number




# # # # from sqlalchemy.ext.asyncio import AsyncSession
# # # # from sqlalchemy import func, select
# # # # from typing import List, Optional, Dict, Any
# # # # from datetime import datetime
# # # # from decimal import Decimal
# # # # import secrets
# # # # import string

# # # # from app.models.order import Order
# # # # from app.models.plan import HostingPlan
# # # # from app.models.users import UserProfile
# # # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary


# # # # class OrderService:
# # # #     # -----------------------------
# # # #     # 🔹 USER-SPECIFIC QUERIES
# # # #     # -----------------------------
# # # #     async def get_user_orders(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         user_id: int,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #     ) -> List[Order]:
# # # #         query = select(Order).where(Order.user_id == user_id)

# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()

# # # #     async def get_user_order(
# # # #         self, db: AsyncSession, user_id: int, order_id: int
# # # #     ) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(Order.id == order_id, Order.user_id == user_id)
# # # #         )
# # # #         return result.scalar_one_or_none()

# # # #     # -----------------------------
# # # #     # 🔹 ADMIN / GLOBAL QUERIES
# # # #     # -----------------------------
# # # #     async def get_all_orders(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #     ) -> List[Order]:
# # # #         query = select(Order)
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()

# # # #     async def get_orders_with_plan(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #         payment_status: Optional[str] = None,
# # # #     ) -> List[Dict[str, Any]]:
# # # #         query = (
# # # #             select(Order, HostingPlan, UserProfile)
# # # #             .join(HostingPlan, Order.plan_id == HostingPlan.id)
# # # #             .join(UserProfile, Order.user_id == UserProfile.id)
# # # #         )

# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
# # # #         if payment_status and payment_status != "all":
# # # #             query = query.where(Order.payment_status == payment_status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         rows = result.all()

# # # #         orders_list = []
# # # #         for order, plan, user in rows:
# # # #             orders_list.append(
# # # #                 {
# # # #                     "id": order.id,
# # # #                     "user_id": order.user_id,
# # # #                     "plan_id": order.plan_id,
# # # #                     "order_number": order.order_number,
# # # #                     "order_status": order.order_status,
# # # #                     "total_amount": order.total_amount,
# # # #                     "payment_status": order.payment_status,
# # # #                     "billing_cycle": order.billing_cycle,
# # # #                     "server_details": order.server_details,
# # # #                     "payment_method": order.payment_method,
# # # #                     "payment_reference": order.payment_reference,
# # # #                     "payment_date": order.payment_date,
# # # #                     "created_at": order.created_at,
# # # #                     "updated_at": order.updated_at,
# # # #                     "plan_name": plan.name,
# # # #                     "plan_type": plan.plan_type,
# # # #                     "user_email": user.email,
# # # #                 }
# # # #             )
# # # #         return orders_list

# # # #     # -----------------------------
# # # #     # 🔹 CRUD OPERATIONS
# # # #     # -----------------------------
# # # #     async def get_order_by_id(
# # # #         self, db: AsyncSession, order_id: int
# # # #     ) -> Optional[Order]:
# # # #         result = await db.execute(select(Order).where(Order.id == order_id))
# # # #         return result.scalar_one_or_none()

# # # #     async def create_order(
# # # #         self, db: AsyncSession, user_id: int, order_data: OrderCreate
# # # #     ) -> Order:
# # # #         # Get plan details
# # # #         result = await db.execute(
# # # #             select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # # #         )
# # # #         plan = result.scalar_one_or_none()
# # # #         if not plan:
# # # #             raise ValueError("Plan not found")

# # # #         # Generate unique order number
# # # #         order_number = await self._generate_order_number(db)

# # # #         new_order = Order(
# # # #             user_id=user_id,
# # # #             plan_id=order_data.plan_id,
# # # #             order_number=order_number,
# # # #             billing_cycle=order_data.billing_cycle,
# # # #             total_amount=order_data.total_amount,
# # # #             server_details=order_data.server_details,
# # # #         )

# # # #         async with db.begin():
# # # #             db.add(new_order)

# # # #         await db.refresh(new_order)
# # # #         return new_order

# # # #     async def update_order(
# # # #         self, db: AsyncSession, order_id: int, order_update: OrderUpdate
# # # #     ) -> Optional[Order]:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return None

# # # #         update_data = order_update.dict(exclude_unset=True)
# # # #         for field, value in update_data.items():
# # # #             setattr(order, field, value)

# # # #         async with db.begin():
# # # #             db.add(order)

# # # #         await db.refresh(order)
# # # #         return order

# # # #     # -----------------------------
# # # #     # 🔹 ORDER STATUS ACTIONS
# # # #     # -----------------------------

# # # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "cancelled"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     async def cancel_user_order(
# # # #         self, db: AsyncSession, user_id: int, order_id: int
# # # #     ) -> bool:
# # # #         order = await self.get_user_order(db, user_id, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "cancelled"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "completed"
# # # #         order.payment_status = "paid"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     # -----------------------------
# # # #     # 🔹 ANALYTICS / STATS
# # # #     # -----------------------------
# # # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # # #         result = await db.execute(select(func.count(Order.id)))
# # # #         return result.scalar() or 0

# # # #     async def get_recent_orders(
# # # #         self, db: AsyncSession, limit: int = 5
# # # #     ) -> List[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # # #         )
# # # #         return result.scalars().all()

# # # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # # #         total_orders = await self.get_total_orders(db)

# # # #         pending = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # # #         )
# # # #         completed = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # # #         )
# # # #         cancelled = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # # #         )

# # # #         total_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # # #         )
# # # #         total_revenue = total_revenue_result.scalar() or Decimal("0.0")

# # # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # # #         monthly_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(
# # # #                 Order.payment_status == "paid", Order.created_at >= start_of_month
# # # #             )
# # # #         )
# # # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal("0.0")

# # # #         return OrderSummary(
# # # #             total_orders=total_orders,
# # # #             pending_orders=pending.scalar() or 0,
# # # #             completed_orders=completed.scalar() or 0,
# # # #             cancelled_orders=cancelled.scalar() or 0,
# # # #             total_revenue=total_revenue,
# # # #             monthly_revenue=monthly_revenue,
# # # #         )

# # # #     # -----------------------------
# # # #     # 🔹 PRIVATE HELPERS
# # # #     # -----------------------------
# # # #     async def _generate_order_number(
# # # #         self, db: AsyncSession, length: int = 10
# # # #     ) -> str:
# # # #         """Generate a unique order number"""
# # # #         chars = string.ascii_uppercase + string.digits
# # # #         while True:
# # # #             number = "ORD-" + "".join(secrets.choice(chars) for _ in range(length))
# # # #             result = await db.execute(
# # # #                 select(Order).where(Order.order_number == number)
# # # #             )
# # # #             if not result.scalar_one_or_none():
# # # #                 return number





# # # from sqlalchemy.ext.asyncio import AsyncSession
# # # from sqlalchemy import func, select
# # # from typing import List, Optional, Dict, Any
# # # from datetime import datetime
# # # from decimal import Decimal
# # # import secrets
# # # import string

# # # from app.models.order import Order
# # # from app.models.plan import HostingPlan
# # # from app.models.users import UserProfile
# # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary


# # # class OrderService:
# # #     # -----------------------------
# # #     # 🔹 USER-SPECIFIC QUERIES
# # #     # -----------------------------
# # #     async def get_user_orders(
# # #         self,
# # #         db: AsyncSession,
# # #         user_id: int,
# # #         skip: int = 0,
# # #         limit: int = 100,
# # #         status: Optional[str] = None,
# # #     ) -> List[Order]:
# # #         query = select(Order).where(Order.user_id == user_id)
# # #         if status and status != "all":
# # #             query = query.where(Order.order_status == status)
# # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

# # #         result = await db.execute(query)
# # #         return result.scalars().all()

# # #     async def get_user_order(
# # #         self, db: AsyncSession, user_id: int, order_id: int
# # #     ) -> Optional[Order]:
# # #         result = await db.execute(
# # #             select(Order).where(Order.id == order_id, Order.user_id == user_id)
# # #         )
# # #         return result.scalar_one_or_none()

# # #     # -----------------------------
# # #     # 🔹 ADMIN / GLOBAL QUERIES
# # #     # -----------------------------
# # #     async def get_all_orders(
# # #         self,
# # #         db: AsyncSession,
# # #         skip: int = 0,
# # #         limit: int = 100,
# # #         status: Optional[str] = None,
# # #     ) -> List[Order]:
# # #         query = select(Order)
# # #         if status and status != "all":
# # #             query = query.where(Order.order_status == status)
# # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

# # #         result = await db.execute(query)
# # #         return result.scalars().all()

# # #     async def get_orders_with_plan(
# # #         self,
# # #         db: AsyncSession,
# # #         skip: int = 0,
# # #         limit: int = 100,
# # #         status: Optional[str] = None,
# # #         payment_status: Optional[str] = None,
# # #     ) -> List[Dict[str, Any]]:
# # #         query = (
# # #             select(Order, HostingPlan, UserProfile)
# # #             .join(HostingPlan, Order.plan_id == HostingPlan.id)
# # #             .join(UserProfile, Order.user_id == UserProfile.id)
# # #         )

# # #         if status and status != "all":
# # #             query = query.where(Order.order_status == status)
# # #         if payment_status and payment_status != "all":
# # #             query = query.where(Order.payment_status == payment_status)

# # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # #         result = await db.execute(query)
# # #         rows = result.all()

# # #         return [
# # #             {
# # #                 "id": order.id,
# # #                 "user_id": order.user_id,
# # #                 "plan_id": order.plan_id,
# # #                 "order_number": order.order_number,
# # #                 "order_status": order.order_status,
# # #                 "total_amount": order.total_amount,
# # #                 "payment_status": order.payment_status,
# # #                 "billing_cycle": order.billing_cycle,
# # #                 "server_details": order.server_details,
# # #                 "payment_method": order.payment_method,
# # #                 "payment_reference": order.payment_reference,
# # #                 "payment_date": order.payment_date,
# # #                 "created_at": order.created_at,
# # #                 "updated_at": order.updated_at,
# # #                 "plan_name": plan.name,
# # #                 "plan_type": plan.plan_type,
# # #                 "user_email": user.email,
# # #             }
# # #             for order, plan, user in rows
# # #         ]

# # #     # -----------------------------
# # #     # 🔹 CRUD OPERATIONS
# # #     # -----------------------------
# # #     async def get_order_by_id(self, db: AsyncSession, order_id: int) -> Optional[Order]:
# # #         result = await db.execute(select(Order).where(Order.id == order_id))
# # #         return result.scalar_one_or_none()

# # #     async def create_order(
# # #         self, db: AsyncSession, user_id: int, order_data: OrderCreate
# # #     ) -> Order:
# # #         try:
# # #             # ✅ 1. Get plan details
# # #             result = await db.execute(
# # #                 select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # #             )
# # #             plan = result.scalar_one_or_none()
# # #             if not plan:
# # #                 raise ValueError("Plan not found")

# # #             # ✅ 2. Generate unique order number
# # #             order_number = await self._generate_order_number(db)

# # #             # ✅ 3. Create order instance
# # #             new_order = Order(
# # #                 user_id=user_id,
# # #                 plan_id=order_data.plan_id,
# # #                 order_number=order_number,
# # #                 billing_cycle=order_data.billing_cycle,
# # #                 total_amount=order_data.total_amount,
# # #                 server_details=order_data.server_details,
# # #                 created_at=datetime.utcnow(),
# # #                 updated_at=datetime.utcnow(),
# # #             )

# # #             db.add(new_order)
# # #             await db.commit()
# # #             await db.refresh(new_order)
# # #             return new_order

# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     async def update_order(
# # #         self, db: AsyncSession, order_id: int, order_update: OrderUpdate
# # #     ) -> Optional[Order]:
# # #         order = await self.get_order_by_id(db, order_id)
# # #         if not order:
# # #             return None

# # #         update_data = order_update.dict(exclude_unset=True)
# # #         for field, value in update_data.items():
# # #             setattr(order, field, value)

# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             await db.refresh(order)
# # #             return order
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     # -----------------------------
# # #     # 🔹 ORDER STATUS ACTIONS
# # #     # -----------------------------
# # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # #         order = await self.get_order_by_id(db, order_id)
# # #         if not order:
# # #             return False

# # #         order.order_status = "cancelled"
# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             return True
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     async def cancel_user_order(
# # #         self, db: AsyncSession, user_id: int, order_id: int
# # #     ) -> bool:
# # #         order = await self.get_user_order(db, user_id, order_id)
# # #         if not order:
# # #             return False

# # #         order.order_status = "cancelled"
# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             return True
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # #         order = await self.get_order_by_id(db, order_id)
# # #         if not order:
# # #             return False

# # #         order.order_status = "completed"
# # #         order.payment_status = "paid"
# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             return True
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     # -----------------------------
# # #     # 🔹 ANALYTICS / STATS
# # #     # -----------------------------
    
# # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # #         result = await db.execute(select(func.count(Order.id)))
# # #         return result.scalar() or 0

# # #     async def get_recent_orders(self, db: AsyncSession, limit: int = 5) -> List[Order]:
# # #         result = await db.execute(
# # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # #         )
# # #         return result.scalars().all()

# # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # #         total_orders = await self.get_total_orders(db)

# # #         pending = await db.execute(
# # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # #         )
# # #         completed = await db.execute(
# # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # #         )
# # #         cancelled = await db.execute(
# # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # #         )

# # #         total_revenue_result = await db.execute(
# # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # #         )
# # #         total_revenue = total_revenue_result.scalar() or Decimal("0.0")

# # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # #         monthly_revenue_result = await db.execute(
# # #             select(func.sum(Order.total_amount)).where(
# # #                 Order.payment_status == "paid", Order.created_at >= start_of_month
# # #             )
# # #         )
# # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal("0.0")

# # #         return OrderSummary(
# # #             total_orders=total_orders,
# # #             pending_orders=pending.scalar() or 0,
# # #             completed_orders=completed.scalar() or 0,
# # #             cancelled_orders=cancelled.scalar() or 0,
# # #             total_revenue=total_revenue,
# # #             monthly_revenue=monthly_revenue,
# # #         )

# # #     # -----------------------------
# # #     # 🔹 PRIVATE HELPERS
# # #     # -----------------------------
# # #     async def _generate_order_number(self, db: AsyncSession, length: int = 10) -> str:
# # #         chars = string.ascii_uppercase + string.digits
# # #         while True:
# # #             number = "ORD-" + "".join(secrets.choice(chars) for _ in range(length))
# # #             result = await db.execute(
# # #                 select(Order).where(Order.order_number == number)
# # #             )
# # #             if not result.scalar_one_or_none():
# # #                 return number
# # # # from sqlalchemy.ext.asyncio import AsyncSession
# # # # from sqlalchemy import func, and_, select
# # # # from typing import List, Optional, Dict, Any
# # # # from datetime import datetime, timedelta
# # # # from decimal import Decimal
# # # # import secrets
# # # # import string

# # # # from app.models.order import Order
# # # # from app.models.plan import HostingPlan
# # # # from app.models.users import UserProfile
# # # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary

# # # # class OrderService:
# # # #     async def get_user_orders(self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100, 
# # # #                             status: Optional[str] = None) -> List[Order]:
# # # #         query = select(Order).where(Order.user_id == user_id)
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()
    
# # # #     async def get_all_orders(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
# # # #                            status: Optional[str] = None) -> List[Order]:
# # # #         query = select(Order)
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()
    
# # # #     async def get_orders_with_plan(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
# # # #                                  status: Optional[str] = None, payment_status: Optional[str] = None) -> List[Dict[str, Any]]:
# # # #         query = select(Order, HostingPlan, UserProfile).join(
# # # #             HostingPlan, Order.plan_id == HostingPlan.id
# # # #         ).join(
# # # #             UserProfile, Order.user_id == UserProfile.id
# # # #         )
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         if payment_status and payment_status != "all":
# # # #             query = query.where(Order.payment_status == payment_status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         orders_with_details = result.all()
        
# # # #         orders_list = []
# # # #         for order, plan, user in orders_with_details:
# # # #             order_dict = {
# # # #                 "id": order.id,
# # # #                 "user_id": order.user_id,
# # # #                 "plan_id": order.plan_id,
# # # #                 "order_number": order.order_number,
# # # #                 "order_status": order.order_status,
# # # #                 "total_amount": order.total_amount,
# # # #                 "payment_status": order.payment_status,
# # # #                 "billing_cycle": order.billing_cycle,
# # # #                 "server_details": order.server_details,
# # # #                 "payment_method": order.payment_method,
# # # #                 "payment_reference": order.payment_reference,
# # # #                 "payment_date": order.payment_date,
# # # #                 "created_at": order.created_at,
# # # #                 "updated_at": order.updated_at,
# # # #                 "plan_name": plan.name,
# # # #                 "plan_type": plan.plan_type,
# # # #                 "user_email": user.email
# # # #             }
# # # #             orders_list.append(order_dict)
        
# # # #         return orders_list
    
# # # #     async def get_order_by_id(self, db: AsyncSession, order_id: int) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(Order.id == order_id)
# # # #         )
# # # #         return result.scalar_one_or_none()
    
# # # #     async def get_user_order(self, db: AsyncSession, user_id: int, order_id: int) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(
# # # #                 Order.id == order_id,
# # # #                 Order.user_id == user_id
# # # #             )
# # # #         )
# # # #         return result.scalar_one_or_none()
    
# # # #     async def create_order(self, db: AsyncSession, user_id: int, order_data: OrderCreate) -> Order:
# # # #         # Get plan details
# # # #         result = await db.execute(
# # # #             select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # # #         )
# # # #         plan = result.scalar_one_or_none()
        
# # # #         if not plan:
# # # #             raise ValueError("Plan not found")
        
# # # #         # Generate order number
# # # #         order_number = await self._generate_order_number(db)
        
# # # #         db_order = Order(
# # # #             user_id=user_id,
# # # #             plan_id=order_data.plan_id,
# # # #             order_number=order_number,
# # # #             billing_cycle=order_data.billing_cycle,
# # # #             total_amount=order_data.total_amount,
# # # #             server_details=order_data.server_details
# # # #         )
        
# # # #         db.add(db_order)
# # # #         await db.commit()
# # # #         await db.refresh(db_order)
# # # #         return db_order
    
# # # #     async def update_order(self, db: AsyncSession, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return None
            
# # # #         update_data = order_update.dict(exclude_unset=True)
# # # #         for field, value in update_data.items():
# # # #             setattr(order, field, value)
            
# # # #         await db.commit()
# # # #         await db.refresh(order)
# # # #         return order
    
# # # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "cancelled"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def cancel_user_order(self, db: AsyncSession, user_id: int, order_id: int) -> bool:
# # # #         order = await self.get_user_order(db, user_id, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "cancelled"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "completed"
# # # #         order.payment_status = "paid"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # # #         result = await db.execute(select(func.count(Order.id)))
# # # #         return result.scalar()
    
# # # #     async def get_recent_orders(self, db: AsyncSession, limit: int = 5) -> List[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # # #         )
# # # #         return result.scalars().all()
    
# # # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # # #         total_orders = await self.get_total_orders(db)
        
# # # #         pending_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # # #         )
# # # #         pending_orders = pending_result.scalar()
        
# # # #         completed_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # # #         )
# # # #         completed_orders = completed_result.scalar()
        
# # # #         cancelled_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # # #         )
# # # #         cancelled_orders = cancelled_result.scalar()
        
# # # #         # Calculate revenue
# # # #         total_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # # #         )
# # # #         total_revenue = total_revenue_result.scalar() or Decimal('0.0')
        
# # # #         # Calculate monthly revenue
# # # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # # #         monthly_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(
# # # #                 Order.payment_status == "paid",
# # # #                 Order.created_at >= start_of_month
# # # #             )
# # # #         )
# # # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal('0.0')
        
# # # #         return OrderSummary(
# # # #             total_orders=total_orders,
# # # #             pending_orders=pending_orders,
# # # #             completed_orders=completed_orders,
# # # #             cancelled_orders=cancelled_orders,
# # # #             total_revenue=total_revenue,
# # # #             monthly_revenue=monthly_revenue
# # # #         )
    
# # # #     async def _generate_order_number(self, db: AsyncSession, length: int = 10) -> str:
# # # #         """Generate a unique order number"""
# # # #         characters = string.ascii_uppercase + string.digits
# # # #         while True:
# # # #             number = 'ORD-' + ''.join(secrets.choice(characters) for _ in range(length))
# # # #             # Check if order number already exists
# # # #             result = await db.execute(
# # # #                 select(Order).where(Order.order_number == number)
# # # #             )
# # # #             existing_order = result.scalar_one_or_none()
# # # #             if not existing_order:
# # # #                 return number




# # # # from sqlalchemy.ext.asyncio import AsyncSession
# # # # from sqlalchemy import func, select
# # # # from typing import List, Optional, Dict, Any
# # # # from datetime import datetime
# # # # from decimal import Decimal
# # # # import secrets
# # # # import string

# # # # from app.models.order import Order
# # # # from app.models.plan import HostingPlan
# # # # from app.models.users import UserProfile
# # # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary


# # # # class OrderService:
# # # #     # -----------------------------
# # # #     # 🔹 USER-SPECIFIC QUERIES
# # # #     # -----------------------------
# # # #     async def get_user_orders(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         user_id: int,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #     ) -> List[Order]:
# # # #         query = select(Order).where(Order.user_id == user_id)

# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()

# # # #     async def get_user_order(
# # # #         self, db: AsyncSession, user_id: int, order_id: int
# # # #     ) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(Order.id == order_id, Order.user_id == user_id)
# # # #         )
# # # #         return result.scalar_one_or_none()

# # # #     # -----------------------------
# # # #     # 🔹 ADMIN / GLOBAL QUERIES
# # # #     # -----------------------------
# # # #     async def get_all_orders(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #     ) -> List[Order]:
# # # #         query = select(Order)
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()

# # # #     async def get_orders_with_plan(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #         payment_status: Optional[str] = None,
# # # #     ) -> List[Dict[str, Any]]:
# # # #         query = (
# # # #             select(Order, HostingPlan, UserProfile)
# # # #             .join(HostingPlan, Order.plan_id == HostingPlan.id)
# # # #             .join(UserProfile, Order.user_id == UserProfile.id)
# # # #         )

# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
# # # #         if payment_status and payment_status != "all":
# # # #             query = query.where(Order.payment_status == payment_status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         rows = result.all()

# # # #         orders_list = []
# # # #         for order, plan, user in rows:
# # # #             orders_list.append(
# # # #                 {
# # # #                     "id": order.id,
# # # #                     "user_id": order.user_id,
# # # #                     "plan_id": order.plan_id,
# # # #                     "order_number": order.order_number,
# # # #                     "order_status": order.order_status,
# # # #                     "total_amount": order.total_amount,
# # # #                     "payment_status": order.payment_status,
# # # #                     "billing_cycle": order.billing_cycle,
# # # #                     "server_details": order.server_details,
# # # #                     "payment_method": order.payment_method,
# # # #                     "payment_reference": order.payment_reference,
# # # #                     "payment_date": order.payment_date,
# # # #                     "created_at": order.created_at,
# # # #                     "updated_at": order.updated_at,
# # # #                     "plan_name": plan.name,
# # # #                     "plan_type": plan.plan_type,
# # # #                     "user_email": user.email,
# # # #                 }
# # # #             )
# # # #         return orders_list

# # # #     # -----------------------------
# # # #     # 🔹 CRUD OPERATIONS
# # # #     # -----------------------------
# # # #     async def get_order_by_id(
# # # #         self, db: AsyncSession, order_id: int
# # # #     ) -> Optional[Order]:
# # # #         result = await db.execute(select(Order).where(Order.id == order_id))
# # # #         return result.scalar_one_or_none()

# # # #     async def create_order(
# # # #         self, db: AsyncSession, user_id: int, order_data: OrderCreate
# # # #     ) -> Order:
# # # #         # Get plan details
# # # #         result = await db.execute(
# # # #             select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # # #         )
# # # #         plan = result.scalar_one_or_none()
# # # #         if not plan:
# # # #             raise ValueError("Plan not found")

# # # #         # Generate unique order number
# # # #         order_number = await self._generate_order_number(db)

# # # #         new_order = Order(
# # # #             user_id=user_id,
# # # #             plan_id=order_data.plan_id,
# # # #             order_number=order_number,
# # # #             billing_cycle=order_data.billing_cycle,
# # # #             total_amount=order_data.total_amount,
# # # #             server_details=order_data.server_details,
# # # #         )

# # # #         async with db.begin():
# # # #             db.add(new_order)

# # # #         await db.refresh(new_order)
# # # #         return new_order

# # # #     async def update_order(
# # # #         self, db: AsyncSession, order_id: int, order_update: OrderUpdate
# # # #     ) -> Optional[Order]:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return None

# # # #         update_data = order_update.dict(exclude_unset=True)
# # # #         for field, value in update_data.items():
# # # #             setattr(order, field, value)

# # # #         async with db.begin():
# # # #             db.add(order)

# # # #         await db.refresh(order)
# # # #         return order

# # # #     # -----------------------------
# # # #     # 🔹 ORDER STATUS ACTIONS
# # # #     # -----------------------------

# # # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "cancelled"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     async def cancel_user_order(
# # # #         self, db: AsyncSession, user_id: int, order_id: int
# # # #     ) -> bool:
# # # #         order = await self.get_user_order(db, user_id, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "cancelled"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "completed"
# # # #         order.payment_status = "paid"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     # -----------------------------
# # # #     # 🔹 ANALYTICS / STATS
# # # #     # -----------------------------
# # # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # # #         result = await db.execute(select(func.count(Order.id)))
# # # #         return result.scalar() or 0

# # # #     async def get_recent_orders(
# # # #         self, db: AsyncSession, limit: int = 5
# # # #     ) -> List[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # # #         )
# # # #         return result.scalars().all()

# # # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # # #         total_orders = await self.get_total_orders(db)

# # # #         pending = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # # #         )
# # # #         completed = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # # #         )
# # # #         cancelled = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # # #         )

# # # #         total_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # # #         )
# # # #         total_revenue = total_revenue_result.scalar() or Decimal("0.0")

# # # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # # #         monthly_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(
# # # #                 Order.payment_status == "paid", Order.created_at >= start_of_month
# # # #             )
# # # #         )
# # # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal("0.0")

# # # #         return OrderSummary(
# # # #             total_orders=total_orders,
# # # #             pending_orders=pending.scalar() or 0,
# # # #             completed_orders=completed.scalar() or 0,
# # # #             cancelled_orders=cancelled.scalar() or 0,
# # # #             total_revenue=total_revenue,
# # # #             monthly_revenue=monthly_revenue,
# # # #         )

# # # #     # -----------------------------
# # # #     # 🔹 PRIVATE HELPERS
# # # #     # -----------------------------
# # # #     async def _generate_order_number(
# # # #         self, db: AsyncSession, length: int = 10
# # # #     ) -> str:
# # # #         """Generate a unique order number"""
# # # #         chars = string.ascii_uppercase + string.digits
# # # #         while True:
# # # #             number = "ORD-" + "".join(secrets.choice(chars) for _ in range(length))
# # # #             result = await db.execute(
# # # #                 select(Order).where(Order.order_number == number)
# # # #             )
# # # #             if not result.scalar_one_or_none():
# # # #                 return number





# # # from sqlalchemy.ext.asyncio import AsyncSession
# # # from sqlalchemy import func, select
# # # from typing import List, Optional, Dict, Any
# # # from datetime import datetime
# # # from decimal import Decimal
# # # import secrets
# # # import string

# # # from app.models.order import Order
# # # from app.models.plan import HostingPlan
# # # from app.models.users import UserProfile
# # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary


# # # class OrderService:
# # #     # -----------------------------
# # #     # 🔹 USER-SPECIFIC QUERIES
# # #     # -----------------------------
# # #     async def get_user_orders(
# # #         self,
# # #         db: AsyncSession,
# # #         user_id: int,
# # #         skip: int = 0,
# # #         limit: int = 100,
# # #         status: Optional[str] = None,
# # #     ) -> List[Order]:
# # #         query = select(Order).where(Order.user_id == user_id)
# # #         if status and status != "all":
# # #             query = query.where(Order.order_status == status)
# # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

# # #         result = await db.execute(query)
# # #         return result.scalars().all()

# # #     async def get_user_order(
# # #         self, db: AsyncSession, user_id: int, order_id: int
# # #     ) -> Optional[Order]:
# # #         result = await db.execute(
# # #             select(Order).where(Order.id == order_id, Order.user_id == user_id)
# # #         )
# # #         return result.scalar_one_or_none()

# # #     # -----------------------------
# # #     # 🔹 ADMIN / GLOBAL QUERIES
# # #     # -----------------------------
# # #     async def get_all_orders(
# # #         self,
# # #         db: AsyncSession,
# # #         skip: int = 0,
# # #         limit: int = 100,
# # #         status: Optional[str] = None,
# # #     ) -> List[Order]:
# # #         query = select(Order)
# # #         if status and status != "all":
# # #             query = query.where(Order.order_status == status)
# # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

# # #         result = await db.execute(query)
# # #         return result.scalars().all()

# # #     async def get_orders_with_plan(
# # #         self,
# # #         db: AsyncSession,
# # #         skip: int = 0,
# # #         limit: int = 100,
# # #         status: Optional[str] = None,
# # #         payment_status: Optional[str] = None,
# # #     ) -> List[Dict[str, Any]]:
# # #         query = (
# # #             select(Order, HostingPlan, UserProfile)
# # #             .join(HostingPlan, Order.plan_id == HostingPlan.id)
# # #             .join(UserProfile, Order.user_id == UserProfile.id)
# # #         )

# # #         if status and status != "all":
# # #             query = query.where(Order.order_status == status)
# # #         if payment_status and payment_status != "all":
# # #             query = query.where(Order.payment_status == payment_status)

# # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # #         result = await db.execute(query)
# # #         rows = result.all()

# # #         return [
# # #             {
# # #                 "id": order.id,
# # #                 "user_id": order.user_id,
# # #                 "plan_id": order.plan_id,
# # #                 "order_number": order.order_number,
# # #                 "order_status": order.order_status,
# # #                 "total_amount": order.total_amount,
# # #                 "payment_status": order.payment_status,
# # #                 "billing_cycle": order.billing_cycle,
# # #                 "server_details": order.server_details,
# # #                 "payment_method": order.payment_method,
# # #                 "payment_reference": order.payment_reference,
# # #                 "payment_date": order.payment_date,
# # #                 "created_at": order.created_at,
# # #                 "updated_at": order.updated_at,
# # #                 "plan_name": plan.name,
# # #                 "plan_type": plan.plan_type,
# # #                 "user_email": user.email,
# # #             }
# # #             for order, plan, user in rows
# # #         ]

# # #     # -----------------------------
# # #     # 🔹 CRUD OPERATIONS
# # #     # -----------------------------
# # #     async def get_order_by_id(self, db: AsyncSession, order_id: int) -> Optional[Order]:
# # #         result = await db.execute(select(Order).where(Order.id == order_id))
# # #         return result.scalar_one_or_none()

# # #     async def create_order(
# # #         self, db: AsyncSession, user_id: int, order_data: OrderCreate
# # #     ) -> Order:
# # #         try:
# # #             # ✅ 1. Get plan details
# # #             result = await db.execute(
# # #                 select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # #             )
# # #             plan = result.scalar_one_or_none()
# # #             if not plan:
# # #                 raise ValueError("Plan not found")

# # #             # ✅ 2. Generate unique order number
# # #             order_number = await self._generate_order_number(db)

# # #             # ✅ 3. Create order instance
# # #             new_order = Order(
# # #                 user_id=user_id,
# # #                 plan_id=order_data.plan_id,
# # #                 order_number=order_number,
# # #                 billing_cycle=order_data.billing_cycle,
# # #                 total_amount=order_data.total_amount,
# # #                 server_details=order_data.server_details,
# # #                 created_at=datetime.utcnow(),
# # #                 updated_at=datetime.utcnow(),
# # #             )

# # #             db.add(new_order)
# # #             await db.commit()
# # #             await db.refresh(new_order)
# # #             return new_order

# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     async def update_order(
# # #         self, db: AsyncSession, order_id: int, order_update: OrderUpdate
# # #     ) -> Optional[Order]:
# # #         order = await self.get_order_by_id(db, order_id)
# # #         if not order:
# # #             return None

# # #         update_data = order_update.dict(exclude_unset=True)
# # #         for field, value in update_data.items():
# # #             setattr(order, field, value)

# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             await db.refresh(order)
# # #             return order
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     # -----------------------------
# # #     # 🔹 ORDER STATUS ACTIONS
# # #     # -----------------------------
# # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # #         order = await self.get_order_by_id(db, order_id)
# # #         if not order:
# # #             return False

# # #         order.order_status = "cancelled"
# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             return True
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     async def cancel_user_order(
# # #         self, db: AsyncSession, user_id: int, order_id: int
# # #     ) -> bool:
# # #         order = await self.get_user_order(db, user_id, order_id)
# # #         if not order:
# # #             return False

# # #         order.order_status = "cancelled"
# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             return True
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # #         order = await self.get_order_by_id(db, order_id)
# # #         if not order:
# # #             return False

# # #         order.order_status = "completed"
# # #         order.payment_status = "paid"
# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             return True
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     # -----------------------------
# # #     # 🔹 ANALYTICS / STATS
# # #     # -----------------------------
    
# # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # #         result = await db.execute(select(func.count(Order.id)))
# # #         return result.scalar() or 0

# # #     async def get_recent_orders(self, db: AsyncSession, limit: int = 5) -> List[Order]:
# # #         result = await db.execute(
# # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # #         )
# # #         return result.scalars().all()

# # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # #         total_orders = await self.get_total_orders(db)

# # #         pending = await db.execute(
# # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # #         )
# # #         completed = await db.execute(
# # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # #         )
# # #         cancelled = await db.execute(
# # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # #         )

# # #         total_revenue_result = await db.execute(
# # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # #         )
# # #         total_revenue = total_revenue_result.scalar() or Decimal("0.0")

# # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # #         monthly_revenue_result = await db.execute(
# # #             select(func.sum(Order.total_amount)).where(
# # #                 Order.payment_status == "paid", Order.created_at >= start_of_month
# # #             )
# # #         )
# # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal("0.0")

# # #         return OrderSummary(
# # #             total_orders=total_orders,
# # #             pending_orders=pending.scalar() or 0,
# # #             completed_orders=completed.scalar() or 0,
# # #             cancelled_orders=cancelled.scalar() or 0,
# # #             total_revenue=total_revenue,
# # #             monthly_revenue=monthly_revenue,
# # #         )

# # #     # -----------------------------
# # #     # 🔹 PRIVATE HELPERS
# # #     # -----------------------------
# # #     async def _generate_order_number(self, db: AsyncSession, length: int = 10) -> str:
# # #         chars = string.ascii_uppercase + string.digits
# # #         while True:
# # #             number = "ORD-" + "".join(secrets.choice(chars) for _ in range(length))
# # #             result = await db.execute(
# # #                 select(Order).where(Order.order_number == number)
# # #             )
# # #             if not result.scalar_one_or_none():
# # #                 return number
# # # # from sqlalchemy.ext.asyncio import AsyncSession
# # # # from sqlalchemy import func, and_, select
# # # # from typing import List, Optional, Dict, Any
# # # # from datetime import datetime, timedelta
# # # # from decimal import Decimal
# # # # import secrets
# # # # import string

# # # # from app.models.order import Order
# # # # from app.models.plan import HostingPlan
# # # # from app.models.users import UserProfile
# # # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary

# # # # class OrderService:
# # # #     async def get_user_orders(self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100, 
# # # #                             status: Optional[str] = None) -> List[Order]:
# # # #         query = select(Order).where(Order.user_id == user_id)
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()
    
# # # #     async def get_all_orders(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
# # # #                            status: Optional[str] = None) -> List[Order]:
# # # #         query = select(Order)
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()
    
# # # #     async def get_orders_with_plan(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
# # # #                                  status: Optional[str] = None, payment_status: Optional[str] = None) -> List[Dict[str, Any]]:
# # # #         query = select(Order, HostingPlan, UserProfile).join(
# # # #             HostingPlan, Order.plan_id == HostingPlan.id
# # # #         ).join(
# # # #             UserProfile, Order.user_id == UserProfile.id
# # # #         )
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         if payment_status and payment_status != "all":
# # # #             query = query.where(Order.payment_status == payment_status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         orders_with_details = result.all()
        
# # # #         orders_list = []
# # # #         for order, plan, user in orders_with_details:
# # # #             order_dict = {
# # # #                 "id": order.id,
# # # #                 "user_id": order.user_id,
# # # #                 "plan_id": order.plan_id,
# # # #                 "order_number": order.order_number,
# # # #                 "order_status": order.order_status,
# # # #                 "total_amount": order.total_amount,
# # # #                 "payment_status": order.payment_status,
# # # #                 "billing_cycle": order.billing_cycle,
# # # #                 "server_details": order.server_details,
# # # #                 "payment_method": order.payment_method,
# # # #                 "payment_reference": order.payment_reference,
# # # #                 "payment_date": order.payment_date,
# # # #                 "created_at": order.created_at,
# # # #                 "updated_at": order.updated_at,
# # # #                 "plan_name": plan.name,
# # # #                 "plan_type": plan.plan_type,
# # # #                 "user_email": user.email
# # # #             }
# # # #             orders_list.append(order_dict)
        
# # # #         return orders_list
    
# # # #     async def get_order_by_id(self, db: AsyncSession, order_id: int) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(Order.id == order_id)
# # # #         )
# # # #         return result.scalar_one_or_none()
    
# # # #     async def get_user_order(self, db: AsyncSession, user_id: int, order_id: int) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(
# # # #                 Order.id == order_id,
# # # #                 Order.user_id == user_id
# # # #             )
# # # #         )
# # # #         return result.scalar_one_or_none()
    
# # # #     async def create_order(self, db: AsyncSession, user_id: int, order_data: OrderCreate) -> Order:
# # # #         # Get plan details
# # # #         result = await db.execute(
# # # #             select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # # #         )
# # # #         plan = result.scalar_one_or_none()
        
# # # #         if not plan:
# # # #             raise ValueError("Plan not found")
        
# # # #         # Generate order number
# # # #         order_number = await self._generate_order_number(db)
        
# # # #         db_order = Order(
# # # #             user_id=user_id,
# # # #             plan_id=order_data.plan_id,
# # # #             order_number=order_number,
# # # #             billing_cycle=order_data.billing_cycle,
# # # #             total_amount=order_data.total_amount,
# # # #             server_details=order_data.server_details
# # # #         )
        
# # # #         db.add(db_order)
# # # #         await db.commit()
# # # #         await db.refresh(db_order)
# # # #         return db_order
    
# # # #     async def update_order(self, db: AsyncSession, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return None
            
# # # #         update_data = order_update.dict(exclude_unset=True)
# # # #         for field, value in update_data.items():
# # # #             setattr(order, field, value)
            
# # # #         await db.commit()
# # # #         await db.refresh(order)
# # # #         return order
    
# # # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "cancelled"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def cancel_user_order(self, db: AsyncSession, user_id: int, order_id: int) -> bool:
# # # #         order = await self.get_user_order(db, user_id, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "cancelled"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "completed"
# # # #         order.payment_status = "paid"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # # #         result = await db.execute(select(func.count(Order.id)))
# # # #         return result.scalar()
    
# # # #     async def get_recent_orders(self, db: AsyncSession, limit: int = 5) -> List[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # # #         )
# # # #         return result.scalars().all()
    
# # # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # # #         total_orders = await self.get_total_orders(db)
        
# # # #         pending_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # # #         )
# # # #         pending_orders = pending_result.scalar()
        
# # # #         completed_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # # #         )
# # # #         completed_orders = completed_result.scalar()
        
# # # #         cancelled_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # # #         )
# # # #         cancelled_orders = cancelled_result.scalar()
        
# # # #         # Calculate revenue
# # # #         total_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # # #         )
# # # #         total_revenue = total_revenue_result.scalar() or Decimal('0.0')
        
# # # #         # Calculate monthly revenue
# # # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # # #         monthly_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(
# # # #                 Order.payment_status == "paid",
# # # #                 Order.created_at >= start_of_month
# # # #             )
# # # #         )
# # # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal('0.0')
        
# # # #         return OrderSummary(
# # # #             total_orders=total_orders,
# # # #             pending_orders=pending_orders,
# # # #             completed_orders=completed_orders,
# # # #             cancelled_orders=cancelled_orders,
# # # #             total_revenue=total_revenue,
# # # #             monthly_revenue=monthly_revenue
# # # #         )
    
# # # #     async def _generate_order_number(self, db: AsyncSession, length: int = 10) -> str:
# # # #         """Generate a unique order number"""
# # # #         characters = string.ascii_uppercase + string.digits
# # # #         while True:
# # # #             number = 'ORD-' + ''.join(secrets.choice(characters) for _ in range(length))
# # # #             # Check if order number already exists
# # # #             result = await db.execute(
# # # #                 select(Order).where(Order.order_number == number)
# # # #             )
# # # #             existing_order = result.scalar_one_or_none()
# # # #             if not existing_order:
# # # #                 return number




# # # # from sqlalchemy.ext.asyncio import AsyncSession
# # # # from sqlalchemy import func, select
# # # # from typing import List, Optional, Dict, Any
# # # # from datetime import datetime
# # # # from decimal import Decimal
# # # # import secrets
# # # # import string

# # # # from app.models.order import Order
# # # # from app.models.plan import HostingPlan
# # # # from app.models.users import UserProfile
# # # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary


# # # # class OrderService:
# # # #     # -----------------------------
# # # #     # 🔹 USER-SPECIFIC QUERIES
# # # #     # -----------------------------
# # # #     async def get_user_orders(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         user_id: int,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #     ) -> List[Order]:
# # # #         query = select(Order).where(Order.user_id == user_id)

# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()

# # # #     async def get_user_order(
# # # #         self, db: AsyncSession, user_id: int, order_id: int
# # # #     ) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(Order.id == order_id, Order.user_id == user_id)
# # # #         )
# # # #         return result.scalar_one_or_none()

# # # #     # -----------------------------
# # # #     # 🔹 ADMIN / GLOBAL QUERIES
# # # #     # -----------------------------
# # # #     async def get_all_orders(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #     ) -> List[Order]:
# # # #         query = select(Order)
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()

# # # #     async def get_orders_with_plan(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #         payment_status: Optional[str] = None,
# # # #     ) -> List[Dict[str, Any]]:
# # # #         query = (
# # # #             select(Order, HostingPlan, UserProfile)
# # # #             .join(HostingPlan, Order.plan_id == HostingPlan.id)
# # # #             .join(UserProfile, Order.user_id == UserProfile.id)
# # # #         )

# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
# # # #         if payment_status and payment_status != "all":
# # # #             query = query.where(Order.payment_status == payment_status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         rows = result.all()

# # # #         orders_list = []
# # # #         for order, plan, user in rows:
# # # #             orders_list.append(
# # # #                 {
# # # #                     "id": order.id,
# # # #                     "user_id": order.user_id,
# # # #                     "plan_id": order.plan_id,
# # # #                     "order_number": order.order_number,
# # # #                     "order_status": order.order_status,
# # # #                     "total_amount": order.total_amount,
# # # #                     "payment_status": order.payment_status,
# # # #                     "billing_cycle": order.billing_cycle,
# # # #                     "server_details": order.server_details,
# # # #                     "payment_method": order.payment_method,
# # # #                     "payment_reference": order.payment_reference,
# # # #                     "payment_date": order.payment_date,
# # # #                     "created_at": order.created_at,
# # # #                     "updated_at": order.updated_at,
# # # #                     "plan_name": plan.name,
# # # #                     "plan_type": plan.plan_type,
# # # #                     "user_email": user.email,
# # # #                 }
# # # #             )
# # # #         return orders_list

# # # #     # -----------------------------
# # # #     # 🔹 CRUD OPERATIONS
# # # #     # -----------------------------
# # # #     async def get_order_by_id(
# # # #         self, db: AsyncSession, order_id: int
# # # #     ) -> Optional[Order]:
# # # #         result = await db.execute(select(Order).where(Order.id == order_id))
# # # #         return result.scalar_one_or_none()

# # # #     async def create_order(
# # # #         self, db: AsyncSession, user_id: int, order_data: OrderCreate
# # # #     ) -> Order:
# # # #         # Get plan details
# # # #         result = await db.execute(
# # # #             select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # # #         )
# # # #         plan = result.scalar_one_or_none()
# # # #         if not plan:
# # # #             raise ValueError("Plan not found")

# # # #         # Generate unique order number
# # # #         order_number = await self._generate_order_number(db)

# # # #         new_order = Order(
# # # #             user_id=user_id,
# # # #             plan_id=order_data.plan_id,
# # # #             order_number=order_number,
# # # #             billing_cycle=order_data.billing_cycle,
# # # #             total_amount=order_data.total_amount,
# # # #             server_details=order_data.server_details,
# # # #         )

# # # #         async with db.begin():
# # # #             db.add(new_order)

# # # #         await db.refresh(new_order)
# # # #         return new_order

# # # #     async def update_order(
# # # #         self, db: AsyncSession, order_id: int, order_update: OrderUpdate
# # # #     ) -> Optional[Order]:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return None

# # # #         update_data = order_update.dict(exclude_unset=True)
# # # #         for field, value in update_data.items():
# # # #             setattr(order, field, value)

# # # #         async with db.begin():
# # # #             db.add(order)

# # # #         await db.refresh(order)
# # # #         return order

# # # #     # -----------------------------
# # # #     # 🔹 ORDER STATUS ACTIONS
# # # #     # -----------------------------

# # # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "cancelled"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     async def cancel_user_order(
# # # #         self, db: AsyncSession, user_id: int, order_id: int
# # # #     ) -> bool:
# # # #         order = await self.get_user_order(db, user_id, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "cancelled"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "completed"
# # # #         order.payment_status = "paid"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     # -----------------------------
# # # #     # 🔹 ANALYTICS / STATS
# # # #     # -----------------------------
# # # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # # #         result = await db.execute(select(func.count(Order.id)))
# # # #         return result.scalar() or 0

# # # #     async def get_recent_orders(
# # # #         self, db: AsyncSession, limit: int = 5
# # # #     ) -> List[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # # #         )
# # # #         return result.scalars().all()

# # # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # # #         total_orders = await self.get_total_orders(db)

# # # #         pending = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # # #         )
# # # #         completed = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # # #         )
# # # #         cancelled = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # # #         )

# # # #         total_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # # #         )
# # # #         total_revenue = total_revenue_result.scalar() or Decimal("0.0")

# # # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # # #         monthly_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(
# # # #                 Order.payment_status == "paid", Order.created_at >= start_of_month
# # # #             )
# # # #         )
# # # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal("0.0")

# # # #         return OrderSummary(
# # # #             total_orders=total_orders,
# # # #             pending_orders=pending.scalar() or 0,
# # # #             completed_orders=completed.scalar() or 0,
# # # #             cancelled_orders=cancelled.scalar() or 0,
# # # #             total_revenue=total_revenue,
# # # #             monthly_revenue=monthly_revenue,
# # # #         )

# # # #     # -----------------------------
# # # #     # 🔹 PRIVATE HELPERS
# # # #     # -----------------------------
# # # #     async def _generate_order_number(
# # # #         self, db: AsyncSession, length: int = 10
# # # #     ) -> str:
# # # #         """Generate a unique order number"""
# # # #         chars = string.ascii_uppercase + string.digits
# # # #         while True:
# # # #             number = "ORD-" + "".join(secrets.choice(chars) for _ in range(length))
# # # #             result = await db.execute(
# # # #                 select(Order).where(Order.order_number == number)
# # # #             )
# # # #             if not result.scalar_one_or_none():
# # # #                 return number





# # # from sqlalchemy.ext.asyncio import AsyncSession
# # # from sqlalchemy import func, select
# # # from typing import List, Optional, Dict, Any
# # # from datetime import datetime
# # # from decimal import Decimal
# # # import secrets
# # # import string

# # # from app.models.order import Order
# # # from app.models.plan import HostingPlan
# # # from app.models.users import UserProfile
# # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary


# # # class OrderService:
# # #     # -----------------------------
# # #     # 🔹 USER-SPECIFIC QUERIES
# # #     # -----------------------------
# # #     async def get_user_orders(
# # #         self,
# # #         db: AsyncSession,
# # #         user_id: int,
# # #         skip: int = 0,
# # #         limit: int = 100,
# # #         status: Optional[str] = None,
# # #     ) -> List[Order]:
# # #         query = select(Order).where(Order.user_id == user_id)
# # #         if status and status != "all":
# # #             query = query.where(Order.order_status == status)
# # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

# # #         result = await db.execute(query)
# # #         return result.scalars().all()

# # #     async def get_user_order(
# # #         self, db: AsyncSession, user_id: int, order_id: int
# # #     ) -> Optional[Order]:
# # #         result = await db.execute(
# # #             select(Order).where(Order.id == order_id, Order.user_id == user_id)
# # #         )
# # #         return result.scalar_one_or_none()

# # #     # -----------------------------
# # #     # 🔹 ADMIN / GLOBAL QUERIES
# # #     # -----------------------------
# # #     async def get_all_orders(
# # #         self,
# # #         db: AsyncSession,
# # #         skip: int = 0,
# # #         limit: int = 100,
# # #         status: Optional[str] = None,
# # #     ) -> List[Order]:
# # #         query = select(Order)
# # #         if status and status != "all":
# # #             query = query.where(Order.order_status == status)
# # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

# # #         result = await db.execute(query)
# # #         return result.scalars().all()

# # #     async def get_orders_with_plan(
# # #         self,
# # #         db: AsyncSession,
# # #         skip: int = 0,
# # #         limit: int = 100,
# # #         status: Optional[str] = None,
# # #         payment_status: Optional[str] = None,
# # #     ) -> List[Dict[str, Any]]:
# # #         query = (
# # #             select(Order, HostingPlan, UserProfile)
# # #             .join(HostingPlan, Order.plan_id == HostingPlan.id)
# # #             .join(UserProfile, Order.user_id == UserProfile.id)
# # #         )

# # #         if status and status != "all":
# # #             query = query.where(Order.order_status == status)
# # #         if payment_status and payment_status != "all":
# # #             query = query.where(Order.payment_status == payment_status)

# # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # #         result = await db.execute(query)
# # #         rows = result.all()

# # #         return [
# # #             {
# # #                 "id": order.id,
# # #                 "user_id": order.user_id,
# # #                 "plan_id": order.plan_id,
# # #                 "order_number": order.order_number,
# # #                 "order_status": order.order_status,
# # #                 "total_amount": order.total_amount,
# # #                 "payment_status": order.payment_status,
# # #                 "billing_cycle": order.billing_cycle,
# # #                 "server_details": order.server_details,
# # #                 "payment_method": order.payment_method,
# # #                 "payment_reference": order.payment_reference,
# # #                 "payment_date": order.payment_date,
# # #                 "created_at": order.created_at,
# # #                 "updated_at": order.updated_at,
# # #                 "plan_name": plan.name,
# # #                 "plan_type": plan.plan_type,
# # #                 "user_email": user.email,
# # #             }
# # #             for order, plan, user in rows
# # #         ]

# # #     # -----------------------------
# # #     # 🔹 CRUD OPERATIONS
# # #     # -----------------------------
# # #     async def get_order_by_id(self, db: AsyncSession, order_id: int) -> Optional[Order]:
# # #         result = await db.execute(select(Order).where(Order.id == order_id))
# # #         return result.scalar_one_or_none()

# # #     async def create_order(
# # #         self, db: AsyncSession, user_id: int, order_data: OrderCreate
# # #     ) -> Order:
# # #         try:
# # #             # ✅ 1. Get plan details
# # #             result = await db.execute(
# # #                 select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # #             )
# # #             plan = result.scalar_one_or_none()
# # #             if not plan:
# # #                 raise ValueError("Plan not found")

# # #             # ✅ 2. Generate unique order number
# # #             order_number = await self._generate_order_number(db)

# # #             # ✅ 3. Create order instance
# # #             new_order = Order(
# # #                 user_id=user_id,
# # #                 plan_id=order_data.plan_id,
# # #                 order_number=order_number,
# # #                 billing_cycle=order_data.billing_cycle,
# # #                 total_amount=order_data.total_amount,
# # #                 server_details=order_data.server_details,
# # #                 created_at=datetime.utcnow(),
# # #                 updated_at=datetime.utcnow(),
# # #             )

# # #             db.add(new_order)
# # #             await db.commit()
# # #             await db.refresh(new_order)
# # #             return new_order

# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     async def update_order(
# # #         self, db: AsyncSession, order_id: int, order_update: OrderUpdate
# # #     ) -> Optional[Order]:
# # #         order = await self.get_order_by_id(db, order_id)
# # #         if not order:
# # #             return None

# # #         update_data = order_update.dict(exclude_unset=True)
# # #         for field, value in update_data.items():
# # #             setattr(order, field, value)

# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             await db.refresh(order)
# # #             return order
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     # -----------------------------
# # #     # 🔹 ORDER STATUS ACTIONS
# # #     # -----------------------------
# # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # #         order = await self.get_order_by_id(db, order_id)
# # #         if not order:
# # #             return False

# # #         order.order_status = "cancelled"
# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             return True
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     async def cancel_user_order(
# # #         self, db: AsyncSession, user_id: int, order_id: int
# # #     ) -> bool:
# # #         order = await self.get_user_order(db, user_id, order_id)
# # #         if not order:
# # #             return False

# # #         order.order_status = "cancelled"
# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             return True
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # #         order = await self.get_order_by_id(db, order_id)
# # #         if not order:
# # #             return False

# # #         order.order_status = "completed"
# # #         order.payment_status = "paid"
# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             return True
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     # -----------------------------
# # #     # 🔹 ANALYTICS / STATS
# # #     # -----------------------------
    
# # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # #         result = await db.execute(select(func.count(Order.id)))
# # #         return result.scalar() or 0

# # #     async def get_recent_orders(self, db: AsyncSession, limit: int = 5) -> List[Order]:
# # #         result = await db.execute(
# # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # #         )
# # #         return result.scalars().all()

# # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # #         total_orders = await self.get_total_orders(db)

# # #         pending = await db.execute(
# # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # #         )
# # #         completed = await db.execute(
# # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # #         )
# # #         cancelled = await db.execute(
# # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # #         )

# # #         total_revenue_result = await db.execute(
# # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # #         )
# # #         total_revenue = total_revenue_result.scalar() or Decimal("0.0")

# # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # #         monthly_revenue_result = await db.execute(
# # #             select(func.sum(Order.total_amount)).where(
# # #                 Order.payment_status == "paid", Order.created_at >= start_of_month
# # #             )
# # #         )
# # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal("0.0")

# # #         return OrderSummary(
# # #             total_orders=total_orders,
# # #             pending_orders=pending.scalar() or 0,
# # #             completed_orders=completed.scalar() or 0,
# # #             cancelled_orders=cancelled.scalar() or 0,
# # #             total_revenue=total_revenue,
# # #             monthly_revenue=monthly_revenue,
# # #         )

# # #     # -----------------------------
# # #     # 🔹 PRIVATE HELPERS
# # #     # -----------------------------
# # #     async def _generate_order_number(self, db: AsyncSession, length: int = 10) -> str:
# # #         chars = string.ascii_uppercase + string.digits
# # #         while True:
# # #             number = "ORD-" + "".join(secrets.choice(chars) for _ in range(length))
# # #             result = await db.execute(
# # #                 select(Order).where(Order.order_number == number)
# # #             )
# # #             if not result.scalar_one_or_none():
# # #                 return number
# # # # from sqlalchemy.ext.asyncio import AsyncSession
# # # # from sqlalchemy import func, and_, select
# # # # from typing import List, Optional, Dict, Any
# # # # from datetime import datetime, timedelta
# # # # from decimal import Decimal
# # # # import secrets
# # # # import string

# # # # from app.models.order import Order
# # # # from app.models.plan import HostingPlan
# # # # from app.models.users import UserProfile
# # # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary

# # # # class OrderService:
# # # #     async def get_user_orders(self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100, 
# # # #                             status: Optional[str] = None) -> List[Order]:
# # # #         query = select(Order).where(Order.user_id == user_id)
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()
    
# # # #     async def get_all_orders(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
# # # #                            status: Optional[str] = None) -> List[Order]:
# # # #         query = select(Order)
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()
    
# # # #     async def get_orders_with_plan(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
# # # #                                  status: Optional[str] = None, payment_status: Optional[str] = None) -> List[Dict[str, Any]]:
# # # #         query = select(Order, HostingPlan, UserProfile).join(
# # # #             HostingPlan, Order.plan_id == HostingPlan.id
# # # #         ).join(
# # # #             UserProfile, Order.user_id == UserProfile.id
# # # #         )
        
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
            
# # # #         if payment_status and payment_status != "all":
# # # #             query = query.where(Order.payment_status == payment_status)
            
# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         orders_with_details = result.all()
        
# # # #         orders_list = []
# # # #         for order, plan, user in orders_with_details:
# # # #             order_dict = {
# # # #                 "id": order.id,
# # # #                 "user_id": order.user_id,
# # # #                 "plan_id": order.plan_id,
# # # #                 "order_number": order.order_number,
# # # #                 "order_status": order.order_status,
# # # #                 "total_amount": order.total_amount,
# # # #                 "payment_status": order.payment_status,
# # # #                 "billing_cycle": order.billing_cycle,
# # # #                 "server_details": order.server_details,
# # # #                 "payment_method": order.payment_method,
# # # #                 "payment_reference": order.payment_reference,
# # # #                 "payment_date": order.payment_date,
# # # #                 "created_at": order.created_at,
# # # #                 "updated_at": order.updated_at,
# # # #                 "plan_name": plan.name,
# # # #                 "plan_type": plan.plan_type,
# # # #                 "user_email": user.email
# # # #             }
# # # #             orders_list.append(order_dict)
        
# # # #         return orders_list
    
# # # #     async def get_order_by_id(self, db: AsyncSession, order_id: int) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(Order.id == order_id)
# # # #         )
# # # #         return result.scalar_one_or_none()
    
# # # #     async def get_user_order(self, db: AsyncSession, user_id: int, order_id: int) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(
# # # #                 Order.id == order_id,
# # # #                 Order.user_id == user_id
# # # #             )
# # # #         )
# # # #         return result.scalar_one_or_none()
    
# # # #     async def create_order(self, db: AsyncSession, user_id: int, order_data: OrderCreate) -> Order:
# # # #         # Get plan details
# # # #         result = await db.execute(
# # # #             select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # # #         )
# # # #         plan = result.scalar_one_or_none()
        
# # # #         if not plan:
# # # #             raise ValueError("Plan not found")
        
# # # #         # Generate order number
# # # #         order_number = await self._generate_order_number(db)
        
# # # #         db_order = Order(
# # # #             user_id=user_id,
# # # #             plan_id=order_data.plan_id,
# # # #             order_number=order_number,
# # # #             billing_cycle=order_data.billing_cycle,
# # # #             total_amount=order_data.total_amount,
# # # #             server_details=order_data.server_details
# # # #         )
        
# # # #         db.add(db_order)
# # # #         await db.commit()
# # # #         await db.refresh(db_order)
# # # #         return db_order
    
# # # #     async def update_order(self, db: AsyncSession, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return None
            
# # # #         update_data = order_update.dict(exclude_unset=True)
# # # #         for field, value in update_data.items():
# # # #             setattr(order, field, value)
            
# # # #         await db.commit()
# # # #         await db.refresh(order)
# # # #         return order
    
# # # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "cancelled"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def cancel_user_order(self, db: AsyncSession, user_id: int, order_id: int) -> bool:
# # # #         order = await self.get_user_order(db, user_id, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "cancelled"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False
            
# # # #         order.order_status = "completed"
# # # #         order.payment_status = "paid"
# # # #         await db.commit()
# # # #         return True
    
# # # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # # #         result = await db.execute(select(func.count(Order.id)))
# # # #         return result.scalar()
    
# # # #     async def get_recent_orders(self, db: AsyncSession, limit: int = 5) -> List[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # # #         )
# # # #         return result.scalars().all()
    
# # # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # # #         total_orders = await self.get_total_orders(db)
        
# # # #         pending_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # # #         )
# # # #         pending_orders = pending_result.scalar()
        
# # # #         completed_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # # #         )
# # # #         completed_orders = completed_result.scalar()
        
# # # #         cancelled_result = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # # #         )
# # # #         cancelled_orders = cancelled_result.scalar()
        
# # # #         # Calculate revenue
# # # #         total_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # # #         )
# # # #         total_revenue = total_revenue_result.scalar() or Decimal('0.0')
        
# # # #         # Calculate monthly revenue
# # # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # # #         monthly_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(
# # # #                 Order.payment_status == "paid",
# # # #                 Order.created_at >= start_of_month
# # # #             )
# # # #         )
# # # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal('0.0')
        
# # # #         return OrderSummary(
# # # #             total_orders=total_orders,
# # # #             pending_orders=pending_orders,
# # # #             completed_orders=completed_orders,
# # # #             cancelled_orders=cancelled_orders,
# # # #             total_revenue=total_revenue,
# # # #             monthly_revenue=monthly_revenue
# # # #         )
    
# # # #     async def _generate_order_number(self, db: AsyncSession, length: int = 10) -> str:
# # # #         """Generate a unique order number"""
# # # #         characters = string.ascii_uppercase + string.digits
# # # #         while True:
# # # #             number = 'ORD-' + ''.join(secrets.choice(characters) for _ in range(length))
# # # #             # Check if order number already exists
# # # #             result = await db.execute(
# # # #                 select(Order).where(Order.order_number == number)
# # # #             )
# # # #             existing_order = result.scalar_one_or_none()
# # # #             if not existing_order:
# # # #                 return number




# # # # from sqlalchemy.ext.asyncio import AsyncSession
# # # # from sqlalchemy import func, select
# # # # from typing import List, Optional, Dict, Any
# # # # from datetime import datetime
# # # # from decimal import Decimal
# # # # import secrets
# # # # import string

# # # # from app.models.order import Order
# # # # from app.models.plan import HostingPlan
# # # # from app.models.users import UserProfile
# # # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary


# # # # class OrderService:
# # # #     # -----------------------------
# # # #     # 🔹 USER-SPECIFIC QUERIES
# # # #     # -----------------------------
# # # #     async def get_user_orders(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         user_id: int,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #     ) -> List[Order]:
# # # #         query = select(Order).where(Order.user_id == user_id)

# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()

# # # #     async def get_user_order(
# # # #         self, db: AsyncSession, user_id: int, order_id: int
# # # #     ) -> Optional[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).where(Order.id == order_id, Order.user_id == user_id)
# # # #         )
# # # #         return result.scalar_one_or_none()

# # # #     # -----------------------------
# # # #     # 🔹 ADMIN / GLOBAL QUERIES
# # # #     # -----------------------------
# # # #     async def get_all_orders(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #     ) -> List[Order]:
# # # #         query = select(Order)
# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         return result.scalars().all()

# # # #     async def get_orders_with_plan(
# # # #         self,
# # # #         db: AsyncSession,
# # # #         skip: int = 0,
# # # #         limit: int = 100,
# # # #         status: Optional[str] = None,
# # # #         payment_status: Optional[str] = None,
# # # #     ) -> List[Dict[str, Any]]:
# # # #         query = (
# # # #             select(Order, HostingPlan, UserProfile)
# # # #             .join(HostingPlan, Order.plan_id == HostingPlan.id)
# # # #             .join(UserProfile, Order.user_id == UserProfile.id)
# # # #         )

# # # #         if status and status != "all":
# # # #             query = query.where(Order.order_status == status)
# # # #         if payment_status and payment_status != "all":
# # # #             query = query.where(Order.payment_status == payment_status)

# # # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # # #         result = await db.execute(query)
# # # #         rows = result.all()

# # # #         orders_list = []
# # # #         for order, plan, user in rows:
# # # #             orders_list.append(
# # # #                 {
# # # #                     "id": order.id,
# # # #                     "user_id": order.user_id,
# # # #                     "plan_id": order.plan_id,
# # # #                     "order_number": order.order_number,
# # # #                     "order_status": order.order_status,
# # # #                     "total_amount": order.total_amount,
# # # #                     "payment_status": order.payment_status,
# # # #                     "billing_cycle": order.billing_cycle,
# # # #                     "server_details": order.server_details,
# # # #                     "payment_method": order.payment_method,
# # # #                     "payment_reference": order.payment_reference,
# # # #                     "payment_date": order.payment_date,
# # # #                     "created_at": order.created_at,
# # # #                     "updated_at": order.updated_at,
# # # #                     "plan_name": plan.name,
# # # #                     "plan_type": plan.plan_type,
# # # #                     "user_email": user.email,
# # # #                 }
# # # #             )
# # # #         return orders_list

# # # #     # -----------------------------
# # # #     # 🔹 CRUD OPERATIONS
# # # #     # -----------------------------
# # # #     async def get_order_by_id(
# # # #         self, db: AsyncSession, order_id: int
# # # #     ) -> Optional[Order]:
# # # #         result = await db.execute(select(Order).where(Order.id == order_id))
# # # #         return result.scalar_one_or_none()

# # # #     async def create_order(
# # # #         self, db: AsyncSession, user_id: int, order_data: OrderCreate
# # # #     ) -> Order:
# # # #         # Get plan details
# # # #         result = await db.execute(
# # # #             select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # # #         )
# # # #         plan = result.scalar_one_or_none()
# # # #         if not plan:
# # # #             raise ValueError("Plan not found")

# # # #         # Generate unique order number
# # # #         order_number = await self._generate_order_number(db)

# # # #         new_order = Order(
# # # #             user_id=user_id,
# # # #             plan_id=order_data.plan_id,
# # # #             order_number=order_number,
# # # #             billing_cycle=order_data.billing_cycle,
# # # #             total_amount=order_data.total_amount,
# # # #             server_details=order_data.server_details,
# # # #         )

# # # #         async with db.begin():
# # # #             db.add(new_order)

# # # #         await db.refresh(new_order)
# # # #         return new_order

# # # #     async def update_order(
# # # #         self, db: AsyncSession, order_id: int, order_update: OrderUpdate
# # # #     ) -> Optional[Order]:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return None

# # # #         update_data = order_update.dict(exclude_unset=True)
# # # #         for field, value in update_data.items():
# # # #             setattr(order, field, value)

# # # #         async with db.begin():
# # # #             db.add(order)

# # # #         await db.refresh(order)
# # # #         return order

# # # #     # -----------------------------
# # # #     # 🔹 ORDER STATUS ACTIONS
# # # #     # -----------------------------

# # # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "cancelled"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     async def cancel_user_order(
# # # #         self, db: AsyncSession, user_id: int, order_id: int
# # # #     ) -> bool:
# # # #         order = await self.get_user_order(db, user_id, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "cancelled"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # # #         order = await self.get_order_by_id(db, order_id)
# # # #         if not order:
# # # #             return False

# # # #         order.order_status = "completed"
# # # #         order.payment_status = "paid"
# # # #         async with db.begin():
# # # #             db.add(order)
# # # #         return True

# # # #     # -----------------------------
# # # #     # 🔹 ANALYTICS / STATS
# # # #     # -----------------------------
# # # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # # #         result = await db.execute(select(func.count(Order.id)))
# # # #         return result.scalar() or 0

# # # #     async def get_recent_orders(
# # # #         self, db: AsyncSession, limit: int = 5
# # # #     ) -> List[Order]:
# # # #         result = await db.execute(
# # # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # # #         )
# # # #         return result.scalars().all()

# # # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # # #         total_orders = await self.get_total_orders(db)

# # # #         pending = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # # #         )
# # # #         completed = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # # #         )
# # # #         cancelled = await db.execute(
# # # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # # #         )

# # # #         total_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # # #         )
# # # #         total_revenue = total_revenue_result.scalar() or Decimal("0.0")

# # # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # # #         monthly_revenue_result = await db.execute(
# # # #             select(func.sum(Order.total_amount)).where(
# # # #                 Order.payment_status == "paid", Order.created_at >= start_of_month
# # # #             )
# # # #         )
# # # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal("0.0")

# # # #         return OrderSummary(
# # # #             total_orders=total_orders,
# # # #             pending_orders=pending.scalar() or 0,
# # # #             completed_orders=completed.scalar() or 0,
# # # #             cancelled_orders=cancelled.scalar() or 0,
# # # #             total_revenue=total_revenue,
# # # #             monthly_revenue=monthly_revenue,
# # # #         )

# # # #     # -----------------------------
# # # #     # 🔹 PRIVATE HELPERS
# # # #     # -----------------------------
# # # #     async def _generate_order_number(
# # # #         self, db: AsyncSession, length: int = 10
# # # #     ) -> str:
# # # #         """Generate a unique order number"""
# # # #         chars = string.ascii_uppercase + string.digits
# # # #         while True:
# # # #             number = "ORD-" + "".join(secrets.choice(chars) for _ in range(length))
# # # #             result = await db.execute(
# # # #                 select(Order).where(Order.order_number == number)
# # # #             )
# # # #             if not result.scalar_one_or_none():
# # # #                 return number





# # # from sqlalchemy.ext.asyncio import AsyncSession
# # # from sqlalchemy import func, select
# # # from typing import List, Optional, Dict, Any
# # # from datetime import datetime
# # # from decimal import Decimal
# # # import secrets
# # # import string

# # # from app.models.order import Order
# # # from app.models.plan import HostingPlan
# # # from app.models.users import UserProfile
# # # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary


# # # class OrderService:
# # #     # -----------------------------
# # #     # 🔹 USER-SPECIFIC QUERIES
# # #     # -----------------------------
# # #     async def get_user_orders(
# # #         self,
# # #         db: AsyncSession,
# # #         user_id: int,
# # #         skip: int = 0,
# # #         limit: int = 100,
# # #         status: Optional[str] = None,
# # #     ) -> List[Order]:
# # #         query = select(Order).where(Order.user_id == user_id)
# # #         if status and status != "all":
# # #             query = query.where(Order.order_status == status)
# # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

# # #         result = await db.execute(query)
# # #         return result.scalars().all()

# # #     async def get_user_order(
# # #         self, db: AsyncSession, user_id: int, order_id: int
# # #     ) -> Optional[Order]:
# # #         result = await db.execute(
# # #             select(Order).where(Order.id == order_id, Order.user_id == user_id)
# # #         )
# # #         return result.scalar_one_or_none()

# # #     # -----------------------------
# # #     # 🔹 ADMIN / GLOBAL QUERIES
# # #     # -----------------------------
# # #     async def get_all_orders(
# # #         self,
# # #         db: AsyncSession,
# # #         skip: int = 0,
# # #         limit: int = 100,
# # #         status: Optional[str] = None,
# # #     ) -> List[Order]:
# # #         query = select(Order)
# # #         if status and status != "all":
# # #             query = query.where(Order.order_status == status)
# # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

# # #         result = await db.execute(query)
# # #         return result.scalars().all()

# # #     async def get_orders_with_plan(
# # #         self,
# # #         db: AsyncSession,
# # #         skip: int = 0,
# # #         limit: int = 100,
# # #         status: Optional[str] = None,
# # #         payment_status: Optional[str] = None,
# # #     ) -> List[Dict[str, Any]]:
# # #         query = (
# # #             select(Order, HostingPlan, UserProfile)
# # #             .join(HostingPlan, Order.plan_id == HostingPlan.id)
# # #             .join(UserProfile, Order.user_id == UserProfile.id)
# # #         )

# # #         if status and status != "all":
# # #             query = query.where(Order.order_status == status)
# # #         if payment_status and payment_status != "all":
# # #             query = query.where(Order.payment_status == payment_status)

# # #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# # #         result = await db.execute(query)
# # #         rows = result.all()

# # #         return [
# # #             {
# # #                 "id": order.id,
# # #                 "user_id": order.user_id,
# # #                 "plan_id": order.plan_id,
# # #                 "order_number": order.order_number,
# # #                 "order_status": order.order_status,
# # #                 "total_amount": order.total_amount,
# # #                 "payment_status": order.payment_status,
# # #                 "billing_cycle": order.billing_cycle,
# # #                 "server_details": order.server_details,
# # #                 "payment_method": order.payment_method,
# # #                 "payment_reference": order.payment_reference,
# # #                 "payment_date": order.payment_date,
# # #                 "created_at": order.created_at,
# # #                 "updated_at": order.updated_at,
# # #                 "plan_name": plan.name,
# # #                 "plan_type": plan.plan_type,
# # #                 "user_email": user.email,
# # #             }
# # #             for order, plan, user in rows
# # #         ]

# # #     # -----------------------------
# # #     # 🔹 CRUD OPERATIONS
# # #     # -----------------------------
# # #     async def get_order_by_id(self, db: AsyncSession, order_id: int) -> Optional[Order]:
# # #         result = await db.execute(select(Order).where(Order.id == order_id))
# # #         return result.scalar_one_or_none()

# # #     async def create_order(
# # #         self, db: AsyncSession, user_id: int, order_data: OrderCreate
# # #     ) -> Order:
# # #         try:
# # #             # ✅ 1. Get plan details
# # #             result = await db.execute(
# # #                 select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# # #             )
# # #             plan = result.scalar_one_or_none()
# # #             if not plan:
# # #                 raise ValueError("Plan not found")

# # #             # ✅ 2. Generate unique order number
# # #             order_number = await self._generate_order_number(db)

# # #             # ✅ 3. Create order instance
# # #             new_order = Order(
# # #                 user_id=user_id,
# # #                 plan_id=order_data.plan_id,
# # #                 order_number=order_number,
# # #                 billing_cycle=order_data.billing_cycle,
# # #                 total_amount=order_data.total_amount,
# # #                 server_details=order_data.server_details,
# # #                 created_at=datetime.utcnow(),
# # #                 updated_at=datetime.utcnow(),
# # #             )

# # #             db.add(new_order)
# # #             await db.commit()
# # #             await db.refresh(new_order)
# # #             return new_order

# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     async def update_order(
# # #         self, db: AsyncSession, order_id: int, order_update: OrderUpdate
# # #     ) -> Optional[Order]:
# # #         order = await self.get_order_by_id(db, order_id)
# # #         if not order:
# # #             return None

# # #         update_data = order_update.dict(exclude_unset=True)
# # #         for field, value in update_data.items():
# # #             setattr(order, field, value)

# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             await db.refresh(order)
# # #             return order
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     # -----------------------------
# # #     # 🔹 ORDER STATUS ACTIONS
# # #     # -----------------------------
# # #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# # #         order = await self.get_order_by_id(db, order_id)
# # #         if not order:
# # #             return False

# # #         order.order_status = "cancelled"
# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             return True
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     async def cancel_user_order(
# # #         self, db: AsyncSession, user_id: int, order_id: int
# # #     ) -> bool:
# # #         order = await self.get_user_order(db, user_id, order_id)
# # #         if not order:
# # #             return False

# # #         order.order_status = "cancelled"
# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             return True
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# # #         order = await self.get_order_by_id(db, order_id)
# # #         if not order:
# # #             return False

# # #         order.order_status = "completed"
# # #         order.payment_status = "paid"
# # #         try:
# # #             db.add(order)
# # #             await db.commit()
# # #             return True
# # #         except Exception:
# # #             await db.rollback()
# # #             raise

# # #     # -----------------------------
# # #     # 🔹 ANALYTICS / STATS
# # #     # -----------------------------
    
# # #     async def get_total_orders(self, db: AsyncSession) -> int:
# # #         result = await db.execute(select(func.count(Order.id)))
# # #         return result.scalar() or 0

# # #     async def get_recent_orders(self, db: AsyncSession, limit: int = 5) -> List[Order]:
# # #         result = await db.execute(
# # #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# # #         )
# # #         return result.scalars().all()

# # #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# # #         total_orders = await self.get_total_orders(db)

# # #         pending = await db.execute(
# # #             select(func.count(Order.id)).where(Order.order_status == "pending")
# # #         )
# # #         completed = await db.execute(
# # #             select(func.count(Order.id)).where(Order.order_status == "completed")
# # #         )
# # #         cancelled = await db.execute(
# # #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# # #         )

# # #         total_revenue_result = await db.execute(
# # #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# # #         )
# # #         total_revenue = total_revenue_result.scalar() or Decimal("0.0")

# # #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# # #         monthly_revenue_result = await db.execute(
# # #             select(func.sum(Order.total_amount)).where(
# # #                 Order.payment_status == "paid", Order.created_at >= start_of_month
# # #             )
# # #         )
# # #         monthly_revenue = monthly_revenue_result.scalar() or Decimal("0.0")

# # #         return OrderSummary(
# # #             total_orders=total_orders,
# # #             pending_orders=pending.scalar() or 0,
# # #             completed_orders=completed.scalar() or 0,
# # #             cancelled_orders=cancelled.scalar() or 0,
# # #             total_revenue=total_revenue,
# # #             monthly_revenue=monthly_revenue,
# # #         )

# # #     # -----------------------------
# # #     # 🔹 PRIVATE HELPERS
# # #     # -----------------------------
# # #     async def _generate_order_number(self, db: AsyncSession, length: int = 10) -> str:
# # #         chars = string.ascii_uppercase + string.digits
# # #         while True:
# # #             number = "ORD-" + "".join(secrets.choice(chars) for _ in range(length))
# # #             result = await db.execute(
# # #                 select(Order).where(Order.order_number == number)
# # #             )
# # #             if not result.scalar_one_or_none():
# # #                 return number







# # from sqlalchemy.ext.asyncio import AsyncSession
# # from sqlalchemy import func, select
# # from typing import List, Optional, Dict, Any
# # from datetime import datetime, timedelta
# # from decimal import Decimal
# # import secrets
# # import string

# # from app.models.order import Order
# # from app.models.plan import HostingPlan
# # from app.models.users import UserProfile
# # from app.models.invoice import Invoice  # ✅ new import
# # from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary


# # class OrderService:
# #     # -----------------------------
# #     # 🔹 USER-SPECIFIC QUERIES
# #     # -----------------------------
# #     async def get_user_orders(
# #         self,
# #         db: AsyncSession,
# #         user_id: int,
# #         skip: int = 0,
# #         limit: int = 100,
# #         status: Optional[str] = None,
# #     ) -> List[Order]:
# #         query = select(Order).where(Order.user_id == user_id)
# #         if status and status != "all":
# #             query = query.where(Order.order_status == status)
# #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

# #         result = await db.execute(query)
# #         return result.scalars().all()

# #     async def get_user_order(
# #         self, db: AsyncSession, user_id: int, order_id: int
# #     ) -> Optional[Order]:
# #         result = await db.execute(
# #             select(Order).where(Order.id == order_id, Order.user_id == user_id)
# #         )
# #         return result.scalar_one_or_none()

# #     # -----------------------------
# #     # 🔹 ADMIN / GLOBAL QUERIES
# #     # -----------------------------
# #     async def get_all_orders(
# #         self,
# #         db: AsyncSession,
# #         skip: int = 0,
# #         limit: int = 100,
# #         status: Optional[str] = None,
# #     ) -> List[Order]:
# #         query = select(Order)
# #         if status and status != "all":
# #             query = query.where(Order.order_status == status)
# #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

# #         result = await db.execute(query)
# #         return result.scalars().all()

# #     async def get_orders_with_plan(
# #         self,
# #         db: AsyncSession,
# #         skip: int = 0,
# #         limit: int = 100,
# #         status: Optional[str] = None,
# #         payment_status: Optional[str] = None,
# #     ) -> List[Dict[str, Any]]:
# #         query = (
# #             select(Order, HostingPlan, UserProfile)
# #             .join(HostingPlan, Order.plan_id == HostingPlan.id)
# #             .join(UserProfile, Order.user_id == UserProfile.id)
# #         )

# #         if status and status != "all":
# #             query = query.where(Order.order_status == status)
# #         if payment_status and payment_status != "all":
# #             query = query.where(Order.payment_status == payment_status)

# #         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
# #         result = await db.execute(query)
# #         rows = result.all()

# #         return [
# #             {
# #                 "id": order.id,
# #                 "user_id": order.user_id,
# #                 "plan_id": order.plan_id,
# #                 "order_number": order.order_number,
# #                 "order_status": order.order_status,
# #                 "total_amount": order.total_amount,
# #                 "payment_status": order.payment_status,
# #                 "billing_cycle": order.billing_cycle,
# #                 "server_details": order.server_details,
# #                 "payment_method": order.payment_method,
# #                 "payment_reference": order.payment_reference,
# #                 "payment_date": order.payment_date,
# #                 "created_at": order.created_at,
# #                 "updated_at": order.updated_at,
# #                 "plan_name": plan.name,
# #                 "plan_type": plan.plan_type,
# #                 "user_email": user.email,
# #             }
# #             for order, plan, user in rows
# #         ]

# #     # -----------------------------
# #     # 🔹 CRUD OPERATIONS
# #     # -----------------------------
# #     async def get_order_by_id(self, db: AsyncSession, order_id: int) -> Optional[Order]:
# #         result = await db.execute(select(Order).where(Order.id == order_id))
# #         return result.scalar_one_or_none()

# #     async def create_order(
# #         self, db: AsyncSession, user_id: int, order_data: OrderCreate
# #     ) -> Dict[str, Any]:
# #         try:
# #             # ✅ 1. Get plan details
# #             result = await db.execute(
# #                 select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
# #             )
# #             plan = result.scalar_one_or_none()
# #             if not plan:
# #                 raise ValueError("Plan not found")

# #             # ✅ 2. Generate unique order number
# #             order_number = await self._generate_order_number(db)

# #             # ✅ 3. Create order
# #             new_order = Order(
# #                 user_id=user_id,
# #                 plan_id=order_data.plan_id,
# #                 order_number=order_number,
# #                 billing_cycle=order_data.billing_cycle,
# #                 total_amount=order_data.total_amount,
# #                 server_details=order_data.server_details,
# #                 order_status="pending",
# #                 payment_status="pending",
# #                 created_at=datetime.utcnow(),
# #                 updated_at=datetime.utcnow(),
# #             )

# #             db.add(new_order)
# #             await db.flush()  # So we can use new_order.id before commit

# #             # ✅ 4. Auto-generate Invoice
# #             invoice_number = await self._generate_invoice_number(db)

# #            # ✅ 4. Auto-generate Invoice

# #             new_invoice = Invoice(
# #                 user_id=user_id,
# #                 order_id=new_order.id,
# #                 invoice_number=invoice_number,
# #                 due_date=datetime.utcnow() + timedelta(days=7),
# #                 subtotal=order_data.total_amount,
# #                 tax_amount=0,
# #                 total_amount=order_data.total_amount,
# #                 balance_due=order_data.total_amount,
# #                 status="unpaid",
# #                 payment_status="pending",
                
# #                 items=  # 👈 FIXED: must be a list
# #                 {
# #                     "description": "Hosting Plan Purchase",
# #                     "quantity": 1,
# #                     "unit_price": float(order_data.total_amount),
# #                     "amount": float(order_data.total_amount)
# #                 },
# #                 created_at=datetime.utcnow(),
# #                 updated_at=datetime.utcnow(),
# #             )

# #             db.add(new_invoice)

# #             # ✅ 5. Commit both
# #             await db.commit()
# #             await db.refresh(new_order)
# #             await db.refresh(new_invoice)

# #             return {"order": new_order, "invoice": new_invoice}

# #         except Exception:
# #             await db.rollback()
# #             raise

# #     async def update_order(
# #         self, db: AsyncSession, order_id: int, order_update: OrderUpdate
# #     ) -> Optional[Order]:
# #         order = await self.get_order_by_id(db, order_id)
# #         if not order:
# #             return None

# #         update_data = order_update.dict(exclude_unset=True)
# #         for field, value in update_data.items():
# #             setattr(order, field, value)

# #         try:
# #             db.add(order)
# #             await db.commit()
# #             await db.refresh(order)
# #             return order
# #         except Exception:
# #             await db.rollback()
# #             raise

# #     # -----------------------------
# #     # 🔹 ORDER STATUS ACTIONS
# #     # -----------------------------
# #     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
# #         order = await self.get_order_by_id(db, order_id)
# #         if not order:
# #             return False

# #         order.order_status = "cancelled"
# #         try:
# #             db.add(order)
# #             await db.commit()
# #             return True
# #         except Exception:
# #             await db.rollback()
# #             raise

# #     async def cancel_user_order(
# #         self, db: AsyncSession, user_id: int, order_id: int
# #     ) -> bool:
# #         order = await self.get_user_order(db, user_id, order_id)
# #         if not order:
# #             return False

# #         order.order_status = "cancelled"
# #         try:
# #             db.add(order)
# #             await db.commit()
# #             return True
# #         except Exception:
# #             await db.rollback()
# #             raise

# #     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
# #         order = await self.get_order_by_id(db, order_id)
# #         if not order:
# #             return False

# #         order.order_status = "completed"
# #         order.payment_status = "paid"
# #         try:
# #             db.add(order)
# #             await db.commit()
# #             return True
# #         except Exception:
# #             await db.rollback()
# #             raise

# #     # -----------------------------
# #     # 🔹 ANALYTICS / STATS
# #     # -----------------------------
# #     async def get_total_orders(self, db: AsyncSession) -> int:
# #         result = await db.execute(select(func.count(Order.id)))
# #         return result.scalar() or 0

# #     async def get_recent_orders(self, db: AsyncSession, limit: int = 5) -> List[Order]:
# #         result = await db.execute(
# #             select(Order).order_by(Order.created_at.desc()).limit(limit)
# #         )
# #         return result.scalars().all()

# #     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
# #         total_orders = await self.get_total_orders(db)

# #         pending = await db.execute(
# #             select(func.count(Order.id)).where(Order.order_status == "pending")
# #         )
# #         completed = await db.execute(
# #             select(func.count(Order.id)).where(Order.order_status == "completed")
# #         )
# #         cancelled = await db.execute(
# #             select(func.count(Order.id)).where(Order.order_status == "cancelled")
# #         )

# #         total_revenue_result = await db.execute(
# #             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
# #         )
# #         total_revenue = total_revenue_result.scalar() or Decimal("0.0")

# #         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# #         monthly_revenue_result = await db.execute(
# #             select(func.sum(Order.total_amount)).where(
# #                 Order.payment_status == "paid", Order.created_at >= start_of_month
# #             )
# #         )
# #         monthly_revenue = monthly_revenue_result.scalar() or Decimal("0.0")

# #         return OrderSummary(
# #             total_orders=total_orders,
# #             pending_orders=pending.scalar() or 0,
# #             completed_orders=completed.scalar() or 0,
# #             cancelled_orders=cancelled.scalar() or 0,
# #             total_revenue=total_revenue,
# #             monthly_revenue=monthly_revenue,
# #         )

# #     # -----------------------------
# #     # 🔹 PRIVATE HELPERS
# #     # -----------------------------
# #     async def _generate_order_number(self, db: AsyncSession, length: int = 10) -> str:
# #         chars = string.ascii_uppercase + string.digits
# #         while True:
# #             number = "ORD-" + "".join(secrets.choice(chars) for _ in range(length))
# #             result = await db.execute(select(Order).where(Order.order_number == number))
# #             if not result.scalar_one_or_none():
# #                 return number

# #     async def _generate_invoice_number(self, db: AsyncSession, length: int = 6) -> str:
# #         chars = string.digits
# #         while True:
# #             number = "INV-" + "".join(secrets.choice(chars) for _ in range(length))
# #             result = await db.execute(
# #                 select(Invoice).where(Invoice.invoice_number == number)
# #             )
# #             if not result.scalar_one_or_none():
# #                 return number




# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import func, select
# from typing import List, Optional, Dict, Any
# from datetime import datetime, timedelta
# from decimal import Decimal
# import secrets
# import string

# from app.models.order import Order
# from app.models.plan import HostingPlan
# from app.models.users import UserProfile
# from app.models.invoice import Invoice
# from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary

# class OrderService:
#     # -----------------------------
#     # 🔹 USER-SPECIFIC QUERIES
#     # -----------------------------
#     async def get_user_orders(
#         self,
#         db: AsyncSession,
#         user_id: int,
#         skip: int = 0,
#         limit: int = 100,
#         status: Optional[str] = None,
#     ) -> List[Order]:
#         query = select(Order).where(Order.user_id == user_id)
#         if status and status != "all":
#             query = query.where(Order.order_status == status)
#         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

#         result = await db.execute(query)
#         return result.scalars().all()

#     async def get_user_order(
#         self, db: AsyncSession, user_id: int, order_id: int
#     ) -> Optional[Order]:
#         result = await db.execute(
#             select(Order).where(Order.id == order_id, Order.user_id == user_id)
#         )
#         return result.scalar_one_or_none()

#     # -----------------------------
#     # 🔹 ADMIN / GLOBAL QUERIES
#     # -----------------------------
#     async def get_all_orders(
#         self,
#         db: AsyncSession,
#         skip: int = 0,
#         limit: int = 100,
#         status: Optional[str] = None,
#     ) -> List[Order]:
#         query = select(Order)
#         if status and status != "all":
#             query = query.where(Order.order_status == status)
#         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

#         result = await db.execute(query)
#         return result.scalars().all()

#     async def get_orders_with_plan(
#         self,
#         db: AsyncSession,
#         skip: int = 0,
#         limit: int = 100,
#         status: Optional[str] = None,
#         payment_status: Optional[str] = None,
#     ) -> List[Dict[str, Any]]:
#         query = (
#             select(Order, HostingPlan, UserProfile)
#             .join(HostingPlan, Order.plan_id == HostingPlan.id)
#             .join(UserProfile, Order.user_id == UserProfile.id)
#         )

#         if status and status != "all":
#             query = query.where(Order.order_status == status)
#         if payment_status and payment_status != "all":
#             query = query.where(Order.payment_status == payment_status)

#         query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
#         result = await db.execute(query)
#         rows = result.all()

#         return [
#             {
#                 "id": order.id,
#                 "user_id": order.user_id,
#                 "plan_id": order.plan_id,
#                 "order_number": order.order_number,
#                 "order_status": order.order_status,
#                 "total_amount": order.total_amount,
#                 "payment_status": order.payment_status,
#                 "billing_cycle": order.billing_cycle,
#                 "server_details": order.server_details,
#                 "payment_method": order.payment_method,
#                 "payment_reference": order.payment_reference,
#                 "payment_date": order.payment_date,
#                 "created_at": order.created_at,
#                 "updated_at": order.updated_at,
#                 "plan_name": plan.name,
#                 "plan_type": plan.plan_type,
#                 "user_email": user.email,
#             }
#             for order, plan, user in rows
#         ]

#     # -----------------------------
#     # 🔹 CRUD OPERATIONS
#     # -----------------------------
#     async def get_order_by_id(self, db: AsyncSession, order_id: int) -> Optional[Order]:
#         result = await db.execute(select(Order).where(Order.id == order_id))
#         return result.scalar_one_or_none()

#     async def create_order(
#         self, db: AsyncSession, user_id: int, order_data: OrderCreate
#     ) -> Dict[str, Any]:
#         try:
#             # ✅ 1. Get plan details
#             result = await db.execute(
#                 select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
#             )
#             plan = result.scalar_one_or_none()
#             if not plan:
#                 raise ValueError("Plan not found")

#             # ✅ 2. Generate unique order number
#             order_number = await self._generate_order_number(db)

#             # ✅ 3. Create order
#             new_order = Order(
#                 user_id=user_id,
#                 plan_id=order_data.plan_id,
#                 order_number=order_number,
#                 billing_cycle=order_data.billing_cycle,
#                 total_amount=order_data.total_amount,
#                 server_details=order_data.server_details,
#                 order_status="pending",
#                 payment_status="pending",
#                 created_at=datetime.utcnow(),
#                 updated_at=datetime.utcnow(),
#             )

#             db.add(new_order)
#             await db.flush()  # So we can use new_order.id before commit

#             # ✅ 4. Auto-generate Invoice
#             invoice_number = await self._generate_invoice_number(db)

#             # ✅ 5. Create invoice with CORRECT items structure (as a list)
#             new_invoice = Invoice(
#                 user_id=user_id,
#                 order_id=new_order.id,
#                 invoice_number=invoice_number,
#                 invoice_date=datetime.utcnow(),
#                 due_date=datetime.utcnow() + timedelta(days=7),
#                 subtotal=order_data.total_amount,
#                 tax_amount=Decimal("0"),
#                 total_amount=order_data.total_amount,
#                 amount_paid=Decimal("0"),
#                 balance_due=order_data.total_amount,
#                 status="unpaid",
#                 payment_status="pending",
#                 # ✅ FIXED: items must be a list of dictionaries
#                 items=[
#                     {
#                         "description": f"{plan.name} - {order_data.billing_cycle}",
#                         "quantity": 1,
#                         "unit_price": float(order_data.total_amount),
#                         "amount": float(order_data.total_amount)
#                     }
#                 ],
#                 created_at=datetime.utcnow(),
#                 updated_at=datetime.utcnow(),
#             )

#             db.add(new_invoice)

#             # ✅ 6. Commit both
#             await db.commit()
#             await db.refresh(new_order)
#             await db.refresh(new_invoice)

#             return {"order": new_order, "invoice": new_invoice}

#         except Exception as e:
#             await db.rollback()
#             raise e

#     async def update_order(
#         self, db: AsyncSession, order_id: int, order_update: OrderUpdate
#     ) -> Optional[Order]:
#         order = await self.get_order_by_id(db, order_id)
#         if not order:
#             return None

#         update_data = order_update.dict(exclude_unset=True)
#         for field, value in update_data.items():
#             setattr(order, field, value)

#         try:
#             db.add(order)
#             await db.commit()
#             await db.refresh(order)
#             return order
#         except Exception:
#             await db.rollback()
#             raise

#     # -----------------------------
#     # 🔹 ORDER STATUS ACTIONS
#     # -----------------------------
#     async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
#         order = await self.get_order_by_id(db, order_id)
#         if not order:
#             return False

#         order.order_status = "cancelled"
#         try:
#             db.add(order)
#             await db.commit()
#             return True
#         except Exception:
#             await db.rollback()
#             raise

#     async def cancel_user_order(
#         self, db: AsyncSession, user_id: int, order_id: int
#     ) -> bool:
#         order = await self.get_user_order(db, user_id, order_id)
#         if not order:
#             return False

#         order.order_status = "cancelled"
#         try:
#             db.add(order)
#             await db.commit()
#             return True
#         except Exception:
#             await db.rollback()
#             raise

#     async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
#         order = await self.get_order_by_id(db, order_id)
#         if not order:
#             return False

#         order.order_status = "completed"
#         order.payment_status = "paid"
#         try:
#             db.add(order)
#             await db.commit()
#             return True
#         except Exception:
#             await db.rollback()
#             raise

#     # -----------------------------
#     # 🔹 ANALYTICS / STATS
#     # -----------------------------
#     async def get_total_orders(self, db: AsyncSession) -> int:
#         result = await db.execute(select(func.count(Order.id)))
#         return result.scalar() or 0

#     async def get_recent_orders(self, db: AsyncSession, limit: int = 5) -> List[Order]:
#         result = await db.execute(
#             select(Order).order_by(Order.created_at.desc()).limit(limit)
#         )
#         return result.scalars().all()

#     async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
#         total_orders = await self.get_total_orders(db)

#         pending = await db.execute(
#             select(func.count(Order.id)).where(Order.order_status == "pending")
#         )
#         completed = await db.execute(
#             select(func.count(Order.id)).where(Order.order_status == "completed")
#         )
#         cancelled = await db.execute(
#             select(func.count(Order.id)).where(Order.order_status == "cancelled")
#         )

#         total_revenue_result = await db.execute(
#             select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
#         )
#         total_revenue = total_revenue_result.scalar() or Decimal("0.0")

#         start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#         monthly_revenue_result = await db.execute(
#             select(func.sum(Order.total_amount)).where(
#                 Order.payment_status == "paid", Order.created_at >= start_of_month
#             )
#         )
#         monthly_revenue = monthly_revenue_result.scalar() or Decimal("0.0")

#         return OrderSummary(
#             total_orders=total_orders,
#             pending_orders=pending.scalar() or 0,
#             completed_orders=completed.scalar() or 0,
#             cancelled_orders=cancelled.scalar() or 0,
#             total_revenue=total_revenue,
#             monthly_revenue=monthly_revenue,
#         )

#     # -----------------------------
#     # 🔹 PRIVATE HELPERS
#     # -----------------------------
#     async def _generate_order_number(self, db: AsyncSession, length: int = 10) -> str:
#         chars = string.ascii_uppercase + string.digits
#         while True:
#             number = "ORD-" + "".join(secrets.choice(chars) for _ in range(length))
#             result = await db.execute(select(Order).where(Order.order_number == number))
#             if not result.scalar_one_or_none():
#                 return number

#     async def _generate_invoice_number(self, db: AsyncSession, length: int = 6) -> str:
#         chars = string.digits
#         while True:
#             number = "INV-" + "".join(secrets.choice(chars) for _ in range(length))
#             result = await db.execute(
#                 select(from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.models.order import Order


class OrderService:
    """Handle order creation and management"""

    async def create_order(
        self,
        db: AsyncSession,
        user_id: int,
        plan_id: int,
        billing_cycle: str,
        amount: Decimal,
        referral_code: Optional[str] = None
    ) -> Order:
        """Create a new order"""
        order_number = await self._generate_order_number(db)
        
        order = Order(
            user_id=user_id,
            plan_id=plan_id,
            order_number=order_number,
            billing_cycle=billing_cycle,
            total_amount=amount,
            status="pending",
            created_at=datetime.utcnow()
        )
        
        db.add(order)
        await db.commit()
        await db.refresh(order)
        return order

    async def get_order_by_razorpay_id(
        self,
        db: AsyncSession,
        razorpay_order_id: str
    ) -> Optional[Order]:
        """Get order by Razorpay order ID"""
        result = await db.execute(
            select(Order).where(Order.razorpay_order_id == razorpay_order_id)
        )
        return result.scalar_one_or_none()

    async def _generate_order_number(self, db: AsyncSession) -> str:
        """Generate unique order number"""
        year = datetime.utcnow().year
        prefix = f"ORD-{year}-"
        
        result = await db.execute(
            select(Order.order_number)
            .where(Order.order_number.like(f"{prefix}%"))
            .order_by(Order.order_number.desc())
            .limit(1)
        )
        last_order = result.scalar_one_or_none()
        
        next_num = int(last_order.split("-")[-1]) + 1 if last_order else 1
        return f"{prefix}{next_num:05d}l
import secrets
import string

from app.models.order import Order
from app.models.plan import HostingPlan
from app.models.users import UserProfile
from app.models.invoice import Invoice
from app.schemas.order import OrderCreate, OrderUpdate, OrderSummary, InvoiceResponse
from app.models.referrals import ReferralEarning
from app.services.referral_service import ReferralService




class OrderService:
    # -----------------------------
    # 🔹 USER-SPECIFIC QUERIES
    # -----------------------------
    async def get_user_orders(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> List[Order]:
        query = select(Order).where(Order.user_id == user_id)
        if status and status != "all":
            query = query.where(Order.order_status == status)
        query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_user_order(
        self, db: AsyncSession, user_id: int, order_id: int
    ) -> Optional[Order]:
        result = await db.execute(
            select(Order).where(Order.id == order_id, Order.user_id == user_id)
        )
        return result.scalar_one_or_none()

    # -----------------------------
    # 🔹 ADMIN / GLOBAL QUERIES
    # -----------------------------
    async def get_all_orders(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> List[Order]:
        query = select(Order)
        if status and status != "all":
            query = query.where(Order.order_status == status)
        query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_orders_with_plan(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        payment_status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query = (
            select(Order, HostingPlan, UserProfile)
            .join(HostingPlan, Order.plan_id == HostingPlan.id)
            .join(UserProfile, Order.user_id == UserProfile.id)
        )

        if status and status != "all":
            query = query.where(Order.order_status == status)
        if payment_status and payment_status != "all":
            query = query.where(Order.payment_status == payment_status)

        query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        rows = result.all()

        return [
            {
                "id": order.id,
                "user_id": order.user_id,
                "plan_id": order.plan_id,
                "order_number": order.order_number,
                "order_status": order.order_status,
                "total_amount": order.total_amount,
                "payment_status": order.payment_status,
                "billing_cycle": order.billing_cycle,
                "server_details": order.server_details,
                "payment_method": order.payment_method,
                "payment_reference": order.payment_reference,
                "payment_date": order.payment_date,
                "created_at": order.created_at,
                "updated_at": order.updated_at,
                "plan_name": plan.name,
                "plan_type": plan.plan_type,
                "user_email": user.email,
            }
            for order, plan, user in rows
        ]

    # -----------------------------
    # 🔹 CRUD OPERATIONS
    # -----------------------------
    async def get_order_by_id(self, db: AsyncSession, order_id: int) -> Optional[Order]:
        result = await db.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()

    # async def create_order(
    #     self, db: AsyncSession, user_id: int, order_data: OrderCreate
    # ) -> Dict[str, Any]:
    #     try:
    #         # ✅ 1. Get plan details
    #         result = await db.execute(
    #             select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
    #         )
    #         plan = result.scalar_one_or_none()
    #         if not plan:
    #             raise ValueError("Plan not found")

    #         # ✅ 2. Generate unique order number
    #         order_number = await self._generate_order_number(db)

    #         # ✅ 3. Create order
    #         new_order = Order(
    #             user_id=user_id,
    #             plan_id=order_data.plan_id,
    #             order_number=order_number,
    #             billing_cycle=order_data.billing_cycle,
    #             total_amount=order_data.total_amount,
    #             server_details=order_data.server_details,
    #             order_status="pending",
    #             payment_status="pending",
    #             created_at=datetime.utcnow(),
    #             updated_at=datetime.utcnow(),
    #         )

    #         db.add(new_order)
    #         await db.flush()  # So we can use new_order.id before commit

    #         # ✅ 4. Auto-generate Invoice
    #         invoice_number = await self._generate_invoice_number(db)

    #         # ✅ 5. Create invoice with CORRECT items structure (as a list)
    #         new_invoice = Invoice(
    #             user_id=user_id,
    #             order_id=new_order.id,
    #             invoice_number=invoice_number,
    #             invoice_date=datetime.utcnow(),
    #             due_date=datetime.utcnow() + timedelta(days=7),
    #             subtotal=order_data.total_amount,
    #             tax_amount=Decimal("0"),
    #             total_amount=order_data.total_amount,
    #             amount_paid=Decimal("0"),
    #             balance_due=order_data.total_amount,
    #             status="unpaid",
    #             payment_status="pending",
    #             # ✅ FIXED: items must be a list of dictionaries
    #             items=[
    #                 {
    #                     "description": f"{plan.name} - {order_data.billing_cycle}",
    #                     "quantity": 1,
    #                     "unit_price": float(order_data.total_amount),
    #                     "amount": float(order_data.total_amount)
    #                 }
    #             ],
    #             created_at=datetime.utcnow(),
    #             updated_at=datetime.utcnow(),
    #         )

    #         db.add(new_invoice)

    #         # ✅ 6. Commit both
    #         await db.commit()
    #         await db.refresh(new_order)
    #         await db.refresh(new_invoice)

    #         # ✅ 7. Return data in correct format for OrderWithInvoiceResponse
    #         return {
    #         "order": new_order,
    #         "invoice": new_invoice  # Return the Invoice object directly
    #         }
    #     except Exception as e:
    #         await db.rollback()
    #         raise e





    # async def create_order(
    #         self, db: AsyncSession, user_id: int, order_data
    #     ) -> Dict[str, Any]:
    #         try:
    #             # ✅ 1. Fetch plan details
    #             result = await db.execute(
    #                 select(HostingPlan).where(HostingPlan.id == order_data.plan_id)
    #             )
    #             plan = result.scalar_one_or_none()
    #             if not plan:
    #                 raise ValueeyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjI3NzcyMDIsInN1YiI6IjEifQ.mvZ8aE9gv7yAyLwS7n4-T4E09GqrPz8PLeJNLyAhoKIError("Plan not found")

    #             # ✅ 2. Generate unique order number
    #             order_number = await self._generate_order_number(db)

    #             # ✅ 3. Define Discount % by billing_cycle
    #             discount_map = {
    #                 "monthly": Decimal("5.00"),
    #                 "quarterly": Decimal("10.00"),
    #                 "semi-annually": Decimal("15.00"),
    #                 "annually": Decimal("20.00"),
    #                 "biennially": Decimal("25.00"),
    #                 "triennially": Decimal("35.00"),
    #             }

    #             discount_percent = discount_map.get(order_data.billing_cycle.lower(), Decimal("0.00"))

    #             # ✅ 4. Calculate discount, tax, and grand_total
    #             subtotal = Decimal(order_data.total_amount)
    #             discount_amount = (subtotal * discount_percent) / Decimal("100.00")

    #             # Apply discount
    #             discounted_total = subtotal - discount_amount

    #             # Add GST (18%)
    #             gst_amount = (discounted_total * Decimal("18.00")) / Decimal("100.00")

    #             # Deduct TDS (10%)
    #             tds_amount = (discounted_total * Decimal("10.00")) / Decimal("100.00")

    #             # Final grand total after taxes
    #             grand_total = discounted_total + gst_amount - tds_amount

    #             # ✅ 5. Create order entry
    #             new_order = Order(
    #                 user_id=user_id,
    #                 plan_id=order_data.plan_id,
    #                 order_number=order_number,
    #                 billing_cycle=order_data.billing_cycle,
    #                 total_amount=subtotal,
    #                 discount_amount=discount_amount,
    #                 tax_amount=gst_amount,
    #                 grand_total=grand_total,
    #                 server_details=order_data.server_details,
    #                 order_status="pending",
    #                 payment_status="pending",
    #                 currency="INR",
    #                 created_at=datetime.utcnow(),
    #                 updated_at=datetime.utcnow(),
    #             )

    #             db.add(new_order)
    #             await db.flush()

    #             # ✅ 6. Generate invoice
    #             invoice_number = await self._generate_invoice_number(db)

    #             new_invoice = Invoice(
    #                 user_id=user_id,
    #                 order_id=new_order.id,
    #                 invoice_number=invoice_number,
    #                 invoice_date=datetime.utcnow(),
    #                 due_date=datetime.utcnow() + timedelta(days=7),
    #                 subtotal=subtotal,
    #                 tax_amount=gst_amount,
    #                 total_amount=grand_total,
    #                 amount_paid=Decimal("0.00"),
    #                 balance_due=grand_total,
    #                 status="unpaid",
    #                 payment_status="pending",
    #                 currency="INR",
    #                 tax_rate=Decimal("18.00"),
    #                 late_fee=Decimal("0.00"),
    #                 days_overdue=0,
    #                 items=[
    #                     {
    #                         "description": f"{plan.name} - {order_data.billing_cycle.title()} Plan",
    #                         "quantity": 1,
    #                         "unit_price": float(subtotal),
    #                         "discount_percent": float(discount_percent),
    #                         "gst_percent": 18.0,
    #                         "tds_percent": 10.0,
    #                         "amount": float(grand_total)
    #                     }
    #                 ],
    #                 created_at=datetime.utcnow(),
    #                 updated_at=datetime.utcnow(),
    #             )

    #             db.add(new_invoice)

    #             # ✅ 7. Commit transaction
    #             await db.commit()
    #             await db.refresh(new_order)
    #             await db.refresh(new_invoice)

    #             # ✅ 8. Return result

    #             return {
    #                 "order": {
    #                     "id": new_order.id,
    #                     "user_id": new_order.user_id,
    #                     "plan_id": new_order.plan_id,
    #                     "order_number": new_order.order_number,
    #                     "order_status": new_order.order_status,
    #                     "payment_status": new_order.payment_status,
    #                     "billing_cycle": new_order.billing_cycle,
    #                     "total_amount": new_order.total_amount,
    #                     "server_details": new_order.server_details,
    #                     "created_at": new_order.created_at,
    #                     "updated_at": new_order.updated_at,
    #                 },
    #                 "invoice": {
    #                     "id": new_invoice.id,
    #                     "invoice_number": new_invoice.invoice_number,
    #                     "order_id": new_invoice.order_id,
    #                     "user_id": new_invoice.user_id,
    #                     "total_amount": new_invoice.total_amount,
    #                     "status": new_invoice.status,
    #                     "invoice_date": new_invoice.invoice_date,
    #                     "due_date": new_invoice.due_date,
    #                     "created_at": new_invoice.created_at,
    #                     "updated_at": new_invoice.updated_at,
    #                 },
    #             }

    #         except Exception as e:
    #             await db.rollback()
    #             raise ValueError(f"Error creating order: {e}")



    async def create_order(
            self, db: AsyncSession, user_id: int, order_data
        ) -> Dict[str, Any]:
            try:
                # ✅ 1️⃣ Fetch hosting plan
                result = await db.execute(select(HostingPlan).where(HostingPlan.id == order_data.plan_id))
                plan = result.scalar_one_or_none()
                if not plan:
                    raise ValueError("Hosting plan not found")

                # ✅ 2️⃣ Generate unique order number
                order_number = await self._generate_order_number(db)

                # ✅ 3️⃣ Billing cycle → discount %
                discount_map = {
                    "monthly": Decimal("5.00"),
                    "quarterly": Decimal("10.00"),
                    "semi-annually": Decimal("15.00"),
                    "annually": Decimal("20.00"),
                    "biennially": Decimal("25.00"),
                    "triennially": Decimal("35.00"),
                }
                discount_percent = discount_map.get(order_data.billing_cycle.lower(), Decimal("0.00"))

                # ✅ 4️⃣ Calculate totals
                subtotal = Decimal(order_data.total_amount)
                discount_amount = (subtotal * discount_percent) / Decimal("100.00")
                discounted_total = subtotal - discount_amount

                gst_amount = (discounted_total * Decimal("18.00")) / Decimal("100.00")
                tds_amount = (discounted_total * Decimal("10.00")) / Decimal("100.00")
                grand_total = discounted_total + gst_amount - tds_amount

                # ✅ 5️⃣ Create Order
                new_order = Order(
                    user_id=user_id,
                    plan_id=order_data.plan_id,
                    order_number=order_number,
                    billing_cycle=order_data.billing_cycle,
                    total_amount=subtotal,
                    discount_amount=discount_amount,
                    tax_amount=gst_amount,
                    grand_total=grand_total,
                    server_details=order_data.server_details,
                    order_status="pending",
                    payment_status="pending",
                    currency="INR",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )

                db.add(new_order)
                await db.flush()  # So we get new_order.id

                # ✅ 6️⃣ Create Invoice
                invoice_number = await self._generate_invoice_number(db)
                new_invoice = Invoice(
                    user_id=user_id,
                    order_id=new_order.id,
                    invoice_number=invoice_number,
                    invoice_date=datetime.utcnow(),
                    due_date=datetime.utcnow() + timedelta(days=7),
                    subtotal=subtotal,
                    tax_amount=gst_amount,
                    total_amount=grand_total,
                    amount_paid=Decimal("0.00"),
                    balance_due=grand_total,
                    status="unpaid",
                    payment_status="pending",
                    currency="INR",
                    tax_rate=Decimal("18.00"),
                    late_fee=Decimal("0.00"),
                    days_overdue=0,
                    items=[
                        {
                            "description": f"{plan.name} - {order_data.billing_cycle.title()} Plan",
                            "quantity": 1,
                            "unit_price": float(subtotal),
                            "discount_percent": float(discount_percent),
                            "gst_percent": 18.0,
                            "tds_percent": 10.0,
                            "amount": float(grand_total)
                        }
                    ],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )

                db.add(new_invoice)

                # ✅ 7️⃣ Commit both
                await db.commit()
                await db.refresh(new_order)
                await db.refresh(new_invoice)

                # ✅ 8️⃣ Auto Commission (optional)
                # If payment_status == "completed" → auto distribute commission
                if new_order.order_status == "completed":
                    referral_service = ReferralService()
                    await referral_service.record_commission_earnings(
                        db=db,
                        user_id=new_order.user_id,
                        plan_amount=new_order.grand_total,
                        plan_type="recurring" if order_data.billing_cycle.lower() == "monthly" else "longterm",
                    )

                # ✅ 9️⃣ Return combined response
                # return {
                #     "order": {
                #         "id": new_order.id,
                #         "order_number": new_order.order_number,
                #         "status": new_order.order_status,
                #         "billing_cycle": new_order.billing_cycle,
                #         "total": float(new_order.total_amount),
                #         "grand_total": float(new_order.grand_total),
                #         "created_at": str(new_order.created_at),
                #     },
                #     "invoice": {
                #         "id": new_invoice.id,
                #         "invoice_number": new_invoice.invoice_number,
                #         "total": float(new_invoice.total_amount),
                #         "status": new_invoice.status,
                #         "due_date": str(new_invoice.due_date),
                #     },
                # }
                return {
                    "order": {
                        "id": new_order.id,
                        "user_id": new_order.user_id,
                        "plan_id": new_order.plan_id,
                        "order_number": new_order.order_number,
                        "order_status": new_order.order_status,
                        "payment_status": new_order.payment_status,
                        "billing_cycle": new_order.billing_cycle,
                        "total_amount": float(new_order.total_amount),
                        "discount_amount": float(new_order.discount_amount),
                        "tax_amount": float(new_order.tax_amount),
                        "grand_total": float(new_order.grand_total),
                        "currency": new_order.currency,
                        "server_details": new_order.server_details,
                        "created_at": new_order.created_at,
                        "updated_at": new_order.updated_at,
                    },
                    "invoice": {
                        "id": new_invoice.id,
                        "invoice_number": new_invoice.invoice_number,
                        "order_id": new_invoice.order_id,
                        "user_id": new_invoice.user_id,
                        "total_amount": float(new_invoice.total_amount),
                        "subtotal": float(new_invoice.subtotal),
                        "tax_amount": float(new_invoice.tax_amount),
                        "invoice_date": new_invoice.invoice_date,
                        "due_date": new_invoice.due_date,
                        "created_at": new_invoice.created_at,
                        "updated_at": new_invoice.updated_at,
                        "status": new_invoice.status,
                        "payment_status": new_invoice.payment_status,
                        "currency": new_invoice.currency,
                    },
                }

            except Exception as e:
                await db.rollback()
                raise ValueError(f"❌ Error creating order: {str(e)}")

 


    async def update_order(
        self, db: AsyncSession, order_id: int, order_update: OrderUpdate
    ) -> Optional[Order]:
        order = await self.get_order_by_id(db, order_id)
        if not order:
            return None

        update_data = order_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)

        try:
            db.add(order)
            await db.commit()
            await db.refresh(order)
            return order
        except Exception:
            await db.rollback()
            raise

    # -----------------------------
    # 🔹 ORDER STATUS ACTIONS
    # -----------------------------
    async def cancel_order(self, db: AsyncSession, order_id: int) -> bool:
        order = await self.get_order_by_id(db, order_id)
        if not order:
            return False

        order.order_status = "cancelled"
        try:
            db.add(order)
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            raise

    async def cancel_user_order(
        self, db: AsyncSession, user_id: int, order_id: int
    ) -> bool:
        order = await self.get_user_order(db, user_id, order_id)
        if not order:
            return False

        order.order_status = "cancelled"
        try:
            db.add(order)
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            raise

    # async def complete_order(self, db: AsyncSession, order_id: int) -> bool:
    #     order = await self.get_order_by_id(db, order_id)
    #     if not order:
    #         return False

    #     order.order_status = "completed"
    #     order.payment_status = "paid"
    #     try:
    #         db.add(order)
    #         await db.commit()
    #         return True
    #     except Exception:
    #         await db.rollback()
    #         raise




    # async def complete_order(self, db: AsyncSession, order_id: int):
    #     """
    #     Mark order as completed and create referral earning if applicable
    #     """
    #     # 1️⃣ Find the order
    #     result = await db.execute(select(Order).filter(Order.id == order_id))
    #     order = result.scalars().first()
    #     if not order:
    #         return False

    #     # 2️⃣ Update order status
    #     order.order_status = "completed"
    #     order.completed_at = func.now()

    #     # 3️⃣ Referral earning logic
    #     result = await db.execute(select(UserProfile).filter(UserProfile.id == order.user_id))
    #     user = result.scalars().first()

    #     if user and user.referred_by:
    #         # Commission settings
    #         commission_rate = 10.0  # percent
    #         order_amount = float(order.grand_total or 0)
    #         commission_amount = order_amount * (commission_rate / 100)

    #         # Create referral earning record
    #         referral_earning = ReferralEarning(
    #             user_id=user.referred_by,           # The referrer who earns
    #             referred_user_id=user.id,           # The user who made the purchase
    #             order_id=order.id,
    #             level=1,                            # Level 1 commission
    #             commission_rate=commission_rate,
    #             order_amount=order_amount,
    #             commission_amount=commission_amount,
    #             status="pending"
    #         )
    #         db.add(referral_earning)

    #     # 4️⃣ Commit changes
    #     await db.commit()
    #     await db.refresh(order)

    #     return True


    async def complete_order(self, db: AsyncSession, order_id: int):
            """
            Mark order as completed and create multi-level referral earnings.
            """
            # 1️⃣ Fetch order
            result = await db.execute(select(Order).filter(Order.id == order_id))
            order = result.scalars().first()
            if not order:
                return False

            # 2️⃣ Update order
            order.order_status = "completed"
            order.completed_at = datetime.utcnow()
            db.add(order)

            # 3️⃣ Fetch buyer
            result = await db.execute(select(UserProfile).filter(UserProfile.id == order.user_id))
            buyer = result.scalars().first()
            if not buyer:
                await db.commit()
                return True

            # 4️⃣ Commission structure (percentages)
            commission_structure = {
                1: 10.0,
                2: 5.0,
                3: 2.0,
            }

            # 5️⃣ Detect referral direction and traverse up
            current_user = buyer
            current_level = 1
            order_amount = float(order.grand_total or 0)

            while current_user.referred_by and current_level <= len(commission_structure):
                # find the referrer (upline)
                result = await db.execute(select(UserProfile).filter(UserProfile.id == current_user.referred_by))
                referrer = result.scalars().first()
                if not referrer:
                    break

                commission_rate = commission_structure[current_level]
                commission_amount = round(order_amount * (commission_rate / 100), 2)

                # Create referral earning record
                earning = ReferralEarning(
                    # user_id=referrer.id,
                    # referred_user_id=buyer.id,  # buyer stays same for all levels
                    user_id=buyer.id,
                    referred_user_id=referrer.id,
                    order_id=order.id,
                    level=current_level,
                    commission_rate=commission_rate,
                    order_amount=order_amount,
                    commission_amount=commission_amount,
                    status="pending",
                    earned_at=datetime.utcnow(),
                )
                db.add(earning)

                # Move up the chain
                current_user = referrer
                current_level += 1

            await db.commit()
            await db.refresh(order)
            return True

        

    async def get_total_orders(self, db: AsyncSession) -> int:
        result = await db.execute(select(func.count(Order.id)))
        return result.scalar() or 0

    async def get_recent_orders(self, db: AsyncSession, limit: int = 5) -> List[Order]:
        result = await db.execute(
            select(Order).order_by(Order.created_at.desc()).limit(limit)
        )
        return result.scalars().all()

    async def get_order_stats(self, db: AsyncSession) -> OrderSummary:
        total_orders = await self.get_total_orders(db)

        pending = await db.execute(
            select(func.count(Order.id)).where(Order.order_status == "pending")
        )
        completed = await db.execute(
            select(func.count(Order.id)).where(Order.order_status == "completed")
        )
        cancelled = await db.execute(
            select(func.count(Order.id)).where(Order.order_status == "cancelled")
        )

        total_revenue_result = await db.execute(
            select(func.sum(Order.total_amount)).where(Order.payment_status == "paid")
        )
        total_revenue = total_revenue_result.scalar() or Decimal("0.0")

        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_revenue_result = await db.execute(
            select(func.sum(Order.total_amount)).where(
                Order.payment_status == "paid", Order.created_at >= start_of_month
            )
        )
        monthly_revenue = monthly_revenue_result.scalar() or Decimal("0.0")

        return OrderSummary(
            total_orders=total_orders,
            pending_orders=pending.scalar() or 0,
            completed_orders=completed.scalar() or 0,
            cancelled_orders=cancelled.scalar() or 0,
            total_revenue=total_revenue,
            monthly_revenue=monthly_revenue,
        )

    # -----------------------------
    # 🔹 PRIVATE HELPERS
    # -----------------------------
    async def _generate_order_number(self, db: AsyncSession, length: int = 10) -> str:
        chars = string.ascii_uppercase + string.digits
        while True:
            number = "ORD-" + "".join(secrets.choice(chars) for _ in range(length))
            result = await db.execute(select(Order).where(Order.order_number == number))
            if not result.scalar_one_or_none():
                return number

    async def _generate_invoice_number(self, db: AsyncSession, length: int = 6) -> str:
        chars = string.digits
        while True:
            number = "INV-" + "".join(secrets.choice(chars) for _ in range(length))
            result = await db.execute(
                select(Invoice).where(Invoice.invoice_number == number)
            )
            if not result.scalar_one_or_none():
                return number

   # ====================== Razorpay Integration Helpers ====================== #

    async def complete_order_by_gateway(
        self,
        db: AsyncSession,
        razorpay_order_id: str,
        payment_id: str,
        amount_paid: float = 0.0
    ) -> bool:
        """
        ✅ Mark order as 'completed' when Razorpay payment is captured.
        Automatically links the Razorpay payment_id and updates invoice.
        """

        try:
            # 🔹 Find order using gateway_order_id (linked when created via Razorpay)
            result = await db.execute(
                select(Order).where(Order.gateway_order_id == razorpay_order_id)
            )
            order = result.scalars().first()

            if not order:
                return False

            # ⚙️ Prevent double marking
            if order.payment_status == "paid" and order.order_status == "completed":
                return True  # Already completed

            # 🔹 Update order status
            order.payment_id = payment_id
            order.payment_status = "paid"
            order.order_status = "completed"
            order.payment_date = datetime.utcnow()
            order.updated_at = datetime.utcnow()

            # 🔹 Update linked invoice (if any)
            invoice_result = await db.execute(
                select(Invoice).where(Invoice.order_id == order.id)
            )
            invoice = invoice_result.scalars().first()
            if invoice:
                invoice.status = "paid"
                invoice.payment_status = "paid"
                invoice.amount_paid = Decimal(str(amount_paid))
                invoice.balance_due = Decimal("0.00")
                invoice.updated_at = datetime.utcnow()
                db.add(invoice)

            db.add(order)
            await db.commit()
            await db.refresh(order)

            return True

        except Exception as e:
            await db.rollback()
            print(f"❌ Error in complete_order_by_gateway: {str(e)}")
            raise
