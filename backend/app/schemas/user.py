"""Pydantic schemas for User."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema."""
    
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "user"


class UserCreate(UserBase):
    """Schema for creating a user."""
    
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """Schema for user in database."""
    
    id: UUID
    hashed_password: str
    is_active: bool = True
    is_email_verified: bool = False
    is_superuser: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """Schema for user response (without sensitive data)."""
    
    id: UUID
    is_active: bool = True
    is_email_verified: bool = False
    role: str = "user"
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token payload schema."""
    
    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None
