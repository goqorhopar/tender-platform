"""Pydantic schemas for Tender."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class TenderStatusEnum(str, Enum):
    """Tender status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class TenderTypeEnum(str, Enum):
    """Tender type enumeration."""
    GOVERNMENT = "government"
    COMMERCIAL = "commercial"
    PRIVATE = "private"


class TenderBase(BaseModel):
    """Base tender schema."""
    
    tender_number: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    initial_price: float = Field(..., gt=0)
    currency: str = "RUB"
    tender_type: TenderTypeEnum = TenderTypeEnum.COMMERCIAL
    customer_name: Optional[str] = None
    customer_inn: Optional[str] = None


class TenderCreate(TenderBase):
    """Schema for creating a tender."""
    
    submission_deadline: Optional[datetime] = None
    region: Optional[str] = None
    source_url: Optional[str] = None


class TenderUpdate(BaseModel):
    """Schema for updating a tender."""
    
    title: Optional[str] = None
    description: Optional[str] = None
    current_price: Optional[float] = None
    status: Optional[TenderStatusEnum] = None
    is_favorite: Optional[bool] = None
    technical_specification: Optional[str] = None


class TenderInDB(TenderBase):
    """Schema for tender in database."""
    
    id: UUID
    status: TenderStatusEnum = TenderStatusEnum.DRAFT
    current_price: Optional[float] = None
    publication_date: Optional[datetime] = None
    submission_deadline: Optional[datetime] = None
    opening_date: Optional[datetime] = None
    customer_kpp: Optional[str] = None
    documentation_url: Optional[str] = None
    technical_specification: Optional[str] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    risk_score: Optional[float] = None
    profitability_score: Optional[float] = None
    source_url: Optional[str] = None
    region: Optional[str] = None
    okpd2_codes: Optional[List[Any]] = None
    keywords: Optional[List[str]] = None
    is_favorite: bool = False
    is_analyzed: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TenderResponse(TenderBase):
    """Schema for tender response."""
    
    id: UUID
    status: TenderStatusEnum
    current_price: Optional[float] = None
    publication_date: Optional[datetime] = None
    submission_deadline: Optional[datetime] = None
    customer_name: Optional[str] = None
    region: Optional[str] = None
    is_favorite: bool = False
    risk_score: Optional[float] = None
    profitability_score: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TenderSearch(BaseModel):
    """Schema for tender search parameters."""
    
    query: Optional[str] = None
    status: Optional[TenderStatusEnum] = None
    tender_type: Optional[TenderTypeEnum] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    region: Optional[str] = None
    is_favorite: Optional[bool] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class TenderListResponse(BaseModel):
    """Schema for paginated tender list response."""
    
    items: List[TenderResponse]
    total: int
    page: int
    page_size: int
    pages: int
