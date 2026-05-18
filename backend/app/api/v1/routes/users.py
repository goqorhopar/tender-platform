"""
Tender Platform - User Routes
User management endpoints with CRUD operations and role-based access control.
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.models import User
from app.schemas.auth import UserResponse, UserUpdate, UserListResponse
from app.api.v1.routes.auth import get_current_active_user, get_current_superuser
from app.core.logging_config import get_logger, log_audit_event


router = APIRouter()
logger = get_logger(__name__)


# ============================================================================
# USER ENDPOINTS
# ============================================================================
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current authenticated user information.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_info(
    request: Request,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update current authenticated user information.
    """
    # Check if email is being changed and if it's already taken
    if user_in.email and user_in.email != current_user.email:
        existing_user = db.query(User).filter(User.email == user_in.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists",
            )
        current_user.email = user_in.email
    
    # Update other fields
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name
    if user_in.phone is not None:
        current_user.phone = user_in.phone
    if user_in.company_name is not None:
        current_user.company_name = user_in.company_name
    if user_in.inn is not None:
        current_user.inn = user_in.inn
    
    db.commit()
    db.refresh(current_user)
    
    log_audit_event(
        action="USER_UPDATED",
        user_id=str(current_user.id),
        resource_type="user",
        resource_id=str(current_user.id),
        details={"fields_updated": user_in.model_dump(exclude_unset=True).keys()},
        ip_address=request.client.host if request.client else None,
    )
    
    logger.info(f"User profile updated: {current_user.email}")
    
    return current_user


@router.delete("/me")
async def delete_current_user(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete current authenticated user account (soft delete).
    """
    # Soft delete
    from datetime import datetime
    current_user.is_deleted = True
    current_user.deleted_at = datetime.utcnow()
    db.commit()
    
    log_audit_event(
        action="USER_DELETED",
        user_id=str(current_user.id),
        resource_type="user",
        resource_id=str(current_user.id),
        ip_address=request.client.host if request.client else None,
    )
    
    logger.info(f"User account deleted: {current_user.email}")
    
    return {"message": "Account deleted successfully"}


# ============================================================================
# ADMIN USER MANAGEMENT (Superuser only)
# ============================================================================
@router.get("", response_model=UserListResponse)
async def list_users(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    List all users (superuser only).
    Supports filtering and pagination.
    """
    query = db.query(User).filter(User.is_deleted == False)
    
    # Apply filters
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (User.email.ilike(search_filter)) |
            (User.full_name.ilike(search_filter))
        )
    
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    users = query.offset(skip).limit(limit).all()
    
    logger.info(f"User list accessed by {current_user.email}, found {total} users")
    
    return UserListResponse.from_query(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    request: Request,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Get user by ID (superuser only).
    """
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    logger.info(f"User {user_id} accessed by {current_user.email}")
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    request: Request,
    user_id: UUID,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Update user by ID (superuser only).
    """
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if email is being changed and if it's already taken
    if user_in.email and user_in.email != user.email:
        existing_user = db.query(User).filter(User.email == user_in.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists",
            )
        user.email = user_in.email
    
    # Update other fields
    if user_in.full_name is not None:
        user.full_name = user_in.full_name
    if user_in.phone is not None:
        user.phone = user_in.phone
    if user_in.company_name is not None:
        user.company_name = user_in.company_name
    if user_in.inn is not None:
        user.inn = user_in.inn
    
    db.commit()
    db.refresh(user)
    
    log_audit_event(
        action="USER_UPDATED_BY_ADMIN",
        user_id=str(current_user.id),
        resource_type="user",
        resource_id=str(user.id),
        details={"fields_updated": user_in.model_dump(exclude_unset=True).keys()},
        ip_address=request.client.host if request.client else None,
    )
    
    logger.info(f"User {user_id} updated by admin {current_user.email}")
    
    return user


@router.delete("/{user_id}")
async def delete_user(
    request: Request,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Delete user by ID (superuser only, soft delete).
    """
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Prevent self-deletion
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )
    
    # Soft delete
    from datetime import datetime
    user.is_deleted = True
    user.deleted_at = datetime.utcnow()
    db.commit()
    
    log_audit_event(
        action="USER_DELETED_BY_ADMIN",
        user_id=str(current_user.id),
        resource_type="user",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else None,
    )
    
    logger.info(f"User {user_id} deleted by admin {current_user.email}")
    
    return {"message": "User deleted successfully"}


@router.post("/{user_id}/activate")
async def activate_user(
    request: Request,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Activate user account (superuser only).
    """
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user.is_active = True
    db.commit()
    
    log_audit_event(
        action="USER_ACTIVATED",
        user_id=str(current_user.id),
        resource_type="user",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else None,
    )
    
    logger.info(f"User {user_id} activated by admin {current_user.email}")
    
    return {"message": "User activated successfully"}


@router.post("/{user_id}/deactivate")
async def deactivate_user(
    request: Request,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Deactivate user account (superuser only).
    """
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Prevent deactivating self
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )
    
    user.is_active = False
    db.commit()
    
    log_audit_event(
        action="USER_DEACTIVATED",
        user_id=str(current_user.id),
        resource_type="user",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else None,
    )
    
    logger.info(f"User {user_id} deactivated by admin {current_user.email}")
    
    return {"message": "User deactivated successfully"}
