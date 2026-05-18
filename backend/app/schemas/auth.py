"""
Tender Platform - Authentication Schemas
Pydantic models for authentication request/response validation.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


# ============================================================================
# TOKEN SCHEMAS
# ============================================================================
class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


# ============================================================================
# USER SCHEMAS
# ============================================================================
class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    inn: Optional[str] = None
    
    @field_validator("inn")
    @classmethod
    def validate_inn(cls, v: Optional[str]) -> Optional[str]:
        """Validate Russian INN (tax ID)."""
        if v is None:
            return v
        # INN should be 10 or 12 digits
        if not re.match(r"^\d{10}$|^\d{12}$", v):
            raise ValueError("INN must be 10 or 12 digits")
        return v
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if v is None:
            return v
        # Remove all non-digit characters except +
        cleaned = re.sub(r"[^\d+]", "", v)
        if len(cleaned) < 10 or len(cleaned) > 15:
            raise ValueError("Invalid phone number format")
        return cleaned


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(UserBase):
    """User update schema."""
    pass


class UserResponse(UserBase):
    """User response schema."""
    id: str
    is_active: bool
    is_verified: bool
    role: str
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    """User schema for database operations."""
    hashed_password: str


# ============================================================================
# PASSWORD MANAGEMENT SCHEMAS
# ============================================================================
class PasswordChangeRequest(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class PasswordResetRequest(BaseModel):
    """Password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""
    email: EmailStr
    reset_token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


# ============================================================================
# LOGIN/REGISTER RESPONSE SCHEMAS
# ============================================================================
class LoginResponse(BaseModel):
    """Login response."""
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    """Registration response."""
    user: UserResponse
    message: str = "Registration successful. Please check your email to verify your account."


# ============================================================================
# PAGINATION SCHEMAS
# ============================================================================
class UserListResponse(BaseModel):
    """Paginated user list response."""
    items: List[UserResponse]
    total: int
    page: int
    page_size: int
    pages: int
    
    @classmethod
    def from_query(cls, items: List[UserResponse], total: int, page: int, page_size: int):
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size,
        )
