from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.core.database import get_db
# from app.core.utils import get_password_hash,verify_token
from app.utils.security_utils import  verify_password

from app.core.security import (
    verify_password, create_access_token,
    get_current_user, verify_token
)
from app.services.user_service import UserService
from app.schemas.users import User, UserCreate, LoginRequest, Token, PasswordChange,SubscriptionInfo, SubscriptionActivate

router = APIRouter()
security = HTTPBearer()








# @router.post("/register", response_model=Token)
# async def register(
#     user_data: UserCreate,
#     db: AsyncSession = Depends(get_db),
#     user_service: UserService = Depends()
# ):
#     """
#     Register a new user
#     """
#     # Check if user already exists
#     existing_user = await user_service.get_user_by_email(db, user_data.email)
#     if existing_user:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="User with this email already exists"
#         )
    
#     # Validate referral code if provided
#     if user_data.referral_code:
#         referral_user = await user_service.get_user_by_referral_code(db, user_data.referral_code)
#         if not referral_user:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Invalid referral code"
#             )
    
#     try:
#         # Create new user
#         user = await user_service.create_user(db, user_data)
        
#         # Generate access token
#         access_token = create_access_token(
#             subject=str(user.id),
#             expires_delta=timedelta(minutes=30)
#         )
        
#         return {
#             "access_token": access_token,
#             "token_type": "bearer",
#             "user": user
#         }
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error creating user: {str(e)}"
#         )
    

@router.post("/register", response_model=Token)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends()
):
    """
    Register a new user
    """
    try:
        # Check if user already exists
        existing_user = await user_service.get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Validate referral code if provided
        if user_data.referral_code:
            referral_user = await user_service.get_user_by_referral_code(db, user_data.referral_code)
            if not referral_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid referral code"
                )
        
        # Create new user
        user = await user_service.create_user(db, user_data)
        
        # Generate access token
        access_token = create_access_token(
            subject=str(user.id),
            expires_delta=timedelta(minutes=30)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the actual error for debugging
        print(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends()
):
    """
    Login user and return access token
    """
    # Add await here since authenticate_user is an async method
    user = await user_service.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if user.account_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended or inactive"
        )
    
    # Generate access token
    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=30)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """
    Refresh access token
    """
    access_token = create_access_token(
        subject=str(current_user.id),
        expires_delta=timedelta(minutes=30)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": current_user
    }

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends()
):
    """
    Change user password
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    # success = user_service.update_password(
    #     db, current_user.id, password_data.new_password
    # )

    success = await user_service.update_password(
        db, current_user.id, password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )
    
    return {"message": "Password updated successfully"}



@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    """
    return current_user


@router.post("/logout")
async def logout():
    """
    Logout user (client should remove token)
    """
    return {"message": "Successfully logged out"}





# ================================ Subscription Endpoints ================================


# # 🔹 1. Check subscription status (for user dashboard)
# @router.get("/status", response_model=SubscriptionInfo)
# async def get_subscription_status(
#     db: AsyncSession = Depends(get_db),
#     current_user=Depends(get_current_user)
# ):
#     user = await UserService.get_user_by_id(db, current_user.id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user


# # 🔹 2. Activate subscription (after successful payment)
# @router.post("/activate")
# async def activate_subscription(
#     subscription: SubscriptionActivate,
#     db: AsyncSession = Depends(get_db)
# ):
#     result = await UserService.activate_subscription(
#         db=db,
#         user_id=subscription.user_id,
#         plan_name=subscription.plan_name,
#         amount=subscription.amount
#     )
#     return {"success": True, **result}





@router.get("/status")
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends()
):
    user = await user_service.get_user_by_id(db, current_user.id)
    return {
        "subscription_status": user.subscription_status,
        "subscription_start": user.subscription_start,
        "subscription_end": user.subscription_end,
    }
# 🔹 2. Activate subscription (after successful payment)


@router.post("/activate")
async def activate_subscription(
    subscription: SubscriptionActivate,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends()
):
    result = await user_service.activate_subscription(
        db=db,
        user_id=subscription.user_id,
        plan_name=subscription.plan_name,
        amount=subscription.amount
    )
    return {"success": True, **result}








# from fastapi import APIRouter, Depends, HTTPException, status
# from app.core.security import HTTPBearer
# from sqlalchemy.orm import Session
# from sqlalchemy.ext.asyncio import AsyncSession
# from datetime import timedelta

# from app.core.database import get_db
# # from app.core.utils import get_password_hash,verify_token
# from app.utils.security_utils import get_password_hash, verify_password

# from app.core.security import (
#     verify_password, create_access_token,
#     get_current_user, verify_token
# )
# from app.services.user_service import UserService 
# from app.schemas.users import User, UserCreate, LoginRequest, Token, PasswordChange,SubscriptionActivate, SubscriptionInfo

# router = APIRouter()
# security = HTTPBearer()


# @router.post("/register", response_model=Token)
# async def register(
#     user_data: UserCreate,
#     db: AsyncSession = Depends(get_db),
#     user_service: UserService = Depends()
# ):
#     """
#     Register a new user
#     """
#     try:
#         # Check if user already exists
#         existing_user = await user_service.get_user_by_email(db, user_data.email)
#         if existing_user:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="User with this email already exists"
#             )
        
#         # Validate referral code if provided
#         if user_data.referral_code:
#             referral_user = await user_service.get_user_by_referral_code(db, user_data.referral_code)
#             if not referral_user:
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail="Invalid referral code"
#                 )
        
#         # Create new user
#         user = await user_service.create_user(db, user_data)
        
#         # Generate access token
#         access_token = create_access_token(
#             subject=str(user.id),
#             expires_delta=timedelta(minutes=30)
#         )
        
#         return {
#             "access_token": access_token,
#             "token_type": "bearer",
#             "user": user
#         }
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         # Log the actual error for debugging
#         print(f"Registration error: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="An error occurred during registration"
#         )


# # @router.post("/login", response_model=Token)
# # async def login(
# #     login_data: LoginRequest,
# #     db: AsyncSession = Depends(get_db),
# #     user_service: UserService = Depends()
# # ):
# #     user = await user_service.authenticate_user(db, login_data.email, login_data.password)
# #     if not user:
# #         raise HTTPException(
# #             status_code=status.HTTP_401_UNAUTHORIZED,
# #             detail="Incorrect email or password"
# #         )

# #     # For customers, check if account is active
# #     if user.role == "customer" and user.account_status != "active":
# #         raise HTTPException(
# #             status_code=status.HTTP_403_FORBIDDEN,
# #             detail="Account inactive — please subscribe to activate your account"
# #         )

# #     # For admin, account must be active (already enforced during registration)
# #     if user.role == "admin" and user.account_status != "active":
# #         raise HTTPException(
# #             status_code=status.HTTP_403_FORBIDDEN,
# #             detail="Admin account is inactive - please contact system administrator"
# #         )

# #     token = create_access_token(str(user.id), timedelta(minutes=30))
# #     return {"access_token": token, "token_type": "bearer", "user": user}





# @router.post("/login", response_model=Token)
# async def login(
#     login_data: LoginRequest,
#     db: AsyncSession = Depends(get_db),
#     user_service: UserService = Depends()
# ):
#     try:
#         print(f"🔄 Login attempt for: {login_data.email}")  # Debug
        
#         # Authenticate user
#         user = await user_service.authenticate_user(db, login_data.email, login_data.password)
        
#         if not user:
#             print("❌ Authentication failed")  # Debug
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Incorrect email or password"
#             )

#         print(f"✅ User authenticated: {user.email}, Role: {user.role}, Status: {user.account_status}")  # Debug

#         # Check account status based on role
#         if user.role == "customer":
#             if user.account_status != "active":
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="Account inactive — please subscribe to activate your account"
#                 )
        
#         elif user.role == "admin":
#             if user.account_status != "active":
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="Admin account is inactive - please contact system administrator"
#                 )

#         # Create access token
#         token = create_access_token(str(user.id), timedelta(minutes=30))
        
#         print("✅ Login successful")  # Debug
        
#         return {
#             "access_token": token, 
#             "token_type": "bearer", 
#             "user": user
#         }
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"❌ Login error: {str(e)}")  # Debug
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal server error during login"
#         )





# @router.post("/refresh", response_model=Token)
# async def refresh_token(
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Refresh access token
#     """
#     access_token = create_access_token(
#         subject=str(current_user.id),
#         expires_delta=timedelta(minutes=30)
#     )
    
#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "user": current_user
#     }

# @router.post("/change-password")
# async def change_password(
#     password_data: PasswordChange,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
#     user_service: UserService = Depends()
# ):
#     """
#     Change user password
#     """
#     # Verify current password
#     if not verify_password(password_data.current_password, current_user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Current password is incorrect"
#         )
#     # Update to new password

#     success = await user_service.update_password(
#         db, current_user.id, password_data.new_password
#     )
    
#     if not success:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to update password"
#         )
    
#     return {"message": "Password updated successfully"}



# @router.get("/me", response_model=User)
# async def get_current_user_info(
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Get current user information
#     """
#     return current_user



# # ================================ Subscription Endpoints ================================


# # 🔹 1. Check subscription status (for user dashboard)
# @router.get("/status", response_model=SubscriptionInfo)
# async def get_subscription_status(
#     db: AsyncSession = Depends(get_db),
#     current_user=Depends(get_current_user)
# ):
#     user = await UserService.get_user_by_id(db, current_user.id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user


# # 🔹 2. Activate subscription (after successful payment)
# @router.post("/activate")
# async def activate_subscription(
#     subscription: SubscriptionActivate,
#     db: AsyncSession = Depends(get_db)
# ):
#     result = await UserService.activate_subscription(
#         db=db,
#         user_id=subscription.user_id,
#         plan_name=subscription.plan_name,
#         amount=subscription.amount
#     )
#     return {"success": True, **result}





# @router.post("/logout")
# async def logout():
#     """
#     Logout user (client should remove token)
#     """
#     return {"message": "Successfully logged out"}

























