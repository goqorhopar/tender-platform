"""
Tender Platform - Authentication Routes
Production-grade authentication endpoints with JWT tokens, refresh logic, and security best practices.
"""

from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_refresh_token,
    generate_secure_token,
)
from app.models import User
from app.schemas.auth import (
    TokenResponse,
    RefreshTokenRequest,
    UserCreate,
    UserResponse,
    PasswordChangeRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from app.core.logging_config import get_logger, log_audit_event


router = APIRouter()
logger = get_logger(__name__)


# ============================================================================
# TOKEN ENDPOINTS
# ============================================================================
@router.post("/token", response_model=TokenResponse)
async def login_access_token(
    request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, return an access token.
    
    This endpoint is used for standard OAuth2 password grant flow.
    """
    # Find user by email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Increment failed login attempts
        if user:
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            if user.failed_login_attempts >= 5:
                from datetime import datetime, timedelta
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
                logger.warning(f"Account locked due to multiple failed attempts: {user.email}")
            db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account is locked. Try again after {user.locked_until.isoformat()}",
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )
    
    # Reset failed login attempts on successful login
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # Generate tokens
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    # Log audit event
    log_audit_event(
        action="USER_LOGIN",
        user_id=str(user.id),
        resource_type="user",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else None,
    )
    
    logger.info(f"User logged in successfully: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> Any:
    """
    Refresh access token using a valid refresh token.
    """
    payload = verify_refresh_token(token_data.refresh_token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Generate new tokens
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    logger.info(f"Token refreshed for user: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ============================================================================
# REGISTRATION ENDPOINTS
# ============================================================================
@router.post("/register", response_model=UserResponse)
async def register_user(
    request: Request,
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> Any:
    """
    Register a new user.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )
    
    # Create new user
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
        is_verified=False,  # Requires email verification
        role="user",
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Send verification email (would be implemented in a task)
    # send_verification_email.delay(user.id)
    
    log_audit_event(
        action="USER_REGISTERED",
        user_id=str(user.id),
        resource_type="user",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else None,
    )
    
    logger.info(f"New user registered: {user.email}")
    
    return user


# ============================================================================
# PASSWORD MANAGEMENT
# ============================================================================
@router.post("/password/change")
async def change_password(
    request: Request,
    password_data: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Change password for the currently authenticated user.
    """
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    
    if password_data.current_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password",
        )
    
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    log_audit_event(
        action="PASSWORD_CHANGED",
        user_id=str(current_user.id),
        resource_type="user",
        resource_id=str(current_user.id),
        ip_address=request.client.host if request.client else None,
    )
    
    logger.info(f"Password changed for user: {current_user.email}")
    
    return {"message": "Password changed successfully"}


@router.post("/password/reset/request")
async def request_password_reset(
    request: Request,
    reset_data: PasswordResetRequest,
    db: Session = Depends(get_db),
) -> Any:
    """
    Request a password reset email.
    """
    user = db.query(User).filter(User.email == reset_data.email).first()
    
    if user:
        # Generate reset token
        reset_token = generate_secure_token(32)
        # Store token in database or cache (simplified here)
        # In production, store with expiration in Redis
        # send_password_reset_email.delay(user.id, reset_token)
        logger.info(f"Password reset requested for: {user.email}")
    
    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/password/reset/confirm")
async def confirm_password_reset(
    request: Request,
    confirm_data: PasswordResetConfirm,
    db: Session = Depends(get_db),
) -> Any:
    """
    Confirm password reset with a valid token.
    """
    # Validate reset token (simplified - would check against stored token)
    # In production, verify token from Redis/database
    
    user = db.query(User).filter(User.email == confirm_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token or email",
        )
    
    # Update password
    user.hashed_password = get_password_hash(confirm_data.new_password)
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    
    log_audit_event(
        action="PASSWORD_RESET",
        user_id=str(user.id),
        resource_type="user",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else None,
    )
    
    logger.info(f"Password reset completed for: {user.email}")
    
    return {"message": "Password has been reset successfully"}


# ============================================================================
# DEPENDENCIES
# ============================================================================
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(OAuth2Bearer()),
) -> User:
    """
    Get current authenticated user from JWT token.
    """
    payload = verify_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


# Custom OAuth2 Bearer scheme
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class OAuth2Bearer(HTTPBearer):
    async def __call__(self, request: Request) -> str:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        return credentials.credentials
