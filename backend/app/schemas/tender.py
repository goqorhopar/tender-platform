"""
Tender Platform - Tender Schemas
Pydantic models for tender request/response validation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from enum import Enum


class TenderStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class TenderType(str, Enum):
    GOVERNMENT = "government"
    COMMERCIAL = "commercial"
    INTERNATIONAL = "international"


# ============================================================================
# TENDER SCHEMAS
# ============================================================================
class TenderBase(BaseModel):
    """Base tender schema."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    tender_number: str = Field(..., min_length=1, max_length=100)
    type: TenderType = TenderType.COMMERCIAL
    status: TenderStatus = TenderStatus.DRAFT
    category: Optional[str] = None
    initial_price: float = Field(..., gt=0)
    currency: str = Field(default="RUB", min_length=3, max_length=3)
    customer_name: Optional[str] = None
    customer_inn: Optional[str] = None
    customer_region: Optional[str] = None
    
    @field_validator("customer_inn")
    @classmethod
    def validate_inn(cls, v: Optional[str]) -> Optional[str]:
        """Validate Russian INN (tax ID)."""
        if v is None:
            return v
        import re
        if not re.match(r"^\d{10}$|^\d{12}$", v):
            raise ValueError("INN must be 10 or 12 digits")
        return v
    
    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency code."""
        if not v.isupper() or len(v) != 3:
            raise ValueError("Currency must be a 3-letter ISO code")
        return v


class TenderCreate(TenderBase):
    """Tender creation schema."""
    submission_deadline: Optional[datetime] = None
    publication_date: Optional[datetime] = None
    okpd2_codes: Optional[List[str]] = []
    documents_url: Optional[str] = None
    technical_spec_url: Optional[str] = None


class TenderUpdate(BaseModel):
    """Tender update schema - all fields optional."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    tender_number: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[TenderType] = None
    status: Optional[TenderStatus] = None
    category: Optional[str] = None
    initial_price: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    customer_name: Optional[str] = None
    customer_inn: Optional[str] = None
    customer_region: Optional[str] = None
    submission_deadline: Optional[datetime] = None
    publication_date: Optional[datetime] = None
    okpd2_codes: Optional[List[str]] = None
    documents_url: Optional[str] = None
    technical_spec_url: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_risk_score: Optional[float] = Field(None, ge=0, le=100)
    ai_recommendations: Optional[List[Dict[str, Any]]] = None


class TenderResponse(TenderBase):
    """Tender response schema."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    publication_date: Optional[datetime] = None
    submission_deadline: Optional[datetime] = None
    review_date: Optional[datetime] = None
    creator_id: UUID
    assigned_to_id: Optional[UUID] = None
    ai_summary: Optional[str] = None
    ai_risk_score: Optional[float] = None
    ai_recommendations: List[Dict[str, Any]] = []
    
    class Config:
        from_attributes = True


class TenderListItem(BaseModel):
    """Tender list item schema (lightweight)."""
    id: UUID
    title: str
    tender_number: str
    status: TenderStatus
    initial_price: float
    currency: str
    submission_deadline: Optional[datetime] = None
    publication_date: Optional[datetime] = None


class TenderListResponse(BaseModel):
    """Paginated tender list response."""
    items: List[TenderListItem]
    total: int
    page: int
    page_size: int
    pages: int
    
    @classmethod
    def from_query(cls, items: List[TenderListItem], total: int, page: int, page_size: int):
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size if page_size > 0 else 0,
        )


class TenderSearchRequest(BaseModel):
    """Tender search request schema."""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)
    status_filter: Optional[TenderStatus] = None
    type_filter: Optional[TenderType] = None
    search: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    customer_inn: Optional[str] = None
    region: Optional[str] = None
    
    @field_validator("max_price")
    @classmethod
    def validate_price_range(cls, v: Optional[float], info) -> Optional[float]:
        """Validate price range."""
        if v is not None and 'min_price' in info.data and info.data['min_price'] is not None:
            if v < info.data['min_price']:
                raise ValueError("max_price must be greater than or equal to min_price")
        return v


# ============================================================================
# DOCUMENT SCHEMAS
# ============================================================================
class DocumentType(str, Enum):
    TECHNICAL_SPEC = "technical_spec"
    COMMERCIAL_PROPOSAL = "commercial_proposal"
    CONTRACT = "contract"
    ADDENDUM = "addendum"
    OTHER = "other"


class TenderDocumentCreate(BaseModel):
    """Tender document creation schema."""
    name: str = Field(..., min_length=1, max_length=255)
    original_filename: str = Field(..., min_length=1, max_length=255)
    file_type: DocumentType
    mime_type: str = Field(..., min_length=1, max_length=100)
    file_size: int = Field(..., gt=0)
    storage_path: str = Field(..., min_length=1, max_length=1000)


class TenderDocumentResponse(BaseModel):
    """Tender document response schema."""
    id: UUID
    tender_id: UUID
    name: str
    original_filename: str
    file_type: DocumentType
    mime_type: str
    file_size: int
    storage_path: str
    uploaded_by_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# COMMENT SCHEMAS
# ============================================================================
class TenderCommentCreate(BaseModel):
    """Tender comment creation schema."""
    content: str = Field(..., min_length=1, max_length=10000)
    parent_id: Optional[UUID] = None


class TenderCommentResponse(BaseModel):
    """Tender comment response schema."""
    id: UUID
    tender_id: UUID
    user_id: UUID
    content: str
    is_edited: bool
    created_at: datetime
    updated_at: datetime
    parent_id: Optional[UUID] = None
    
    class Config:
        from_attributes = True
