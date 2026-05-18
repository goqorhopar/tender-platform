"""Pydantic schemas for Supplier."""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class SupplierBase(BaseModel):
    """Base supplier schema."""
    
    name: str = Field(..., min_length=1, max_length=255)
    inn: str = Field(..., min_length=10, max_length=12)
    kpp: Optional[str] = Field(None, min_length=9, max_length=9)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class SupplierCreate(SupplierBase):
    """Schema for creating a supplier."""
    
    legal_address: Optional[str] = None
    actual_address: Optional[str] = None
    website: Optional[str] = None
    specialization: Optional[List[str]] = None


class SupplierUpdate(BaseModel):
    """Schema for updating a supplier."""
    
    name: Optional[str] = None
    kpp: Optional[str] = None
    legal_address: Optional[str] = None
    actual_address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    is_blacklisted: Optional[bool] = None
    notes: Optional[str] = None


class SupplierInDB(SupplierBase):
    """Schema for supplier in database."""
    
    id: UUID
    ogrn: Optional[str] = None
    legal_address: Optional[str] = None
    actual_address: Optional[str] = None
    website: Optional[str] = None
    okved_codes: Optional[List[Any]] = None
    specialization: Optional[List[str]] = None
    authorized_capital: Optional[float] = None
    employee_count: Optional[int] = None
    reliability_score: Optional[float] = None
    credit_rating: Optional[str] = None
    is_blacklisted: bool = False
    is_verified: bool = False
    notes: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SupplierResponse(SupplierBase):
    """Schema for supplier response."""
    
    id: UUID
    ogrn: Optional[str] = None
    legal_address: Optional[str] = None
    website: Optional[str] = None
    reliability_score: Optional[float] = None
    is_blacklisted: bool = False
    is_verified: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


class SupplierSearch(BaseModel):
    """Schema for supplier search parameters."""
    
    query: Optional[str] = None
    inn: Optional[str] = None
    is_blacklisted: Optional[bool] = None
    is_verified: Optional[bool] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class SupplierListResponse(BaseModel):
    """Schema for paginated supplier list response."""
    
    items: List[SupplierResponse]
    total: int
    page: int
    page_size: int
    pages: int
