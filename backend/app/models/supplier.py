"""Supplier model for vendor information."""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database import Base


class Supplier(Base):
    """Supplier model representing vendors and contractors."""
    
    __tablename__ = "suppliers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic info
    name = Column(String(255), nullable=False, index=True)
    inn = Column(String(12), unique=True, nullable=False, index=True)
    kpp = Column(String(9), nullable=True)
    ogrn = Column(String(13), nullable=True)
    
    # Contact info
    legal_address = Column(Text, nullable=True)
    actual_address = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Classification
    okved_codes = Column(JSON, nullable=True)  # Primary activity codes
    specialization = Column(JSON, nullable=True)  # Business areas
    
    # Financial info
    authorized_capital = Column(Float, nullable=True)
    employee_count = Column(Integer, nullable=True)
    
    # Ratings and scores
    reliability_score = Column(Float, nullable=True)  # 0-100
    credit_rating = Column(String(10), nullable=True)
    
    # Tracking
    is_blacklisted = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    # Additional data from APIs
    additional_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self) -> str:
        return f"<Supplier {self.name} (INN: {self.inn})>"
