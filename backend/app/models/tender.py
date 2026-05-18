"""Tender model for procurement opportunities."""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.database import Base


class TenderStatus(enum.Enum):
    """Tender status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class TenderType(enum.Enum):
    """Tender type enumeration."""
    GOVERNMENT = "government"  # 44-ФЗ
    COMMERCIAL = "commercial"  # 223-ФЗ
    PRIVATE = "private"


class Tender(Base):
    """Tender model representing procurement opportunities."""
    
    __tablename__ = "tenders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_number = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # Type and status
    tender_type = Column(SQLEnum(TenderType), default=TenderType.COMMERCIAL)
    status = Column(SQLEnum(TenderStatus), default=TenderStatus.DRAFT)
    
    # Pricing
    initial_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    currency = Column(String(3), default="RUB")
    
    # Dates
    publication_date = Column(DateTime(timezone=True), nullable=True)
    submission_deadline = Column(DateTime(timezone=True), nullable=True)
    opening_date = Column(DateTime(timezone=True), nullable=True)
    
    # Customer info
    customer_name = Column(String(255), nullable=True)
    customer_inn = Column(String(12), nullable=True)
    customer_kpp = Column(String(9), nullable=True)
    
    # Documents
    documentation_url = Column(String(500), nullable=True)
    technical_specification = Column(Text, nullable=True)
    
    # AI Analysis
    ai_analysis = Column(JSON, nullable=True)
    risk_score = Column(Float, nullable=True)  # 0-100
    profitability_score = Column(Float, nullable=True)  # 0-100
    
    # Metadata
    source_url = Column(String(500), nullable=True)
    region = Column(String(100), nullable=True)
    okpd2_codes = Column(JSON, nullable=True)  # Classification codes
    keywords = Column(JSON, nullable=True)
    
    is_favorite = Column(Boolean, default=False)
    is_analyzed = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self) -> str:
        return f"<Tender {self.tender_number}: {self.title}>"
