"""
Tender Platform - Database Models
Production-grade SQLAlchemy models with proper relationships, indexes, and audit fields.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Float, ForeignKey, Index,
    Integer, String, Text, UniqueConstraint, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from app.db.database import Base


# ============================================================================
# ENUMS
# ============================================================================
class UserRole(str, PyEnum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    VIEWER = "viewer"


class TenderStatus(str, PyEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class TenderType(str, PyEnum):
    GOVERNMENT = "government"
    COMMERCIAL = "commercial"
    INTERNATIONAL = "international"


class DocumentType(str, PyEnum):
    TECHNICAL_SPEC = "technical_spec"
    COMMERCIAL_PROPOSAL = "commercial_proposal"
    CONTRACT = "contract"
    ADDENDUM = "addendum"
    OTHER = "other"


# ============================================================================
# MIXINS
# ============================================================================
class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        index=True
    )


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class UUIDPrimaryKeyMixin:
    """Mixin for UUID primary key."""
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )


# ============================================================================
# MODELS
# ============================================================================
class User(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """User model with authentication and role management."""
    
    __tablename__ = "users"
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Profile
    full_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    company_name = Column(String(255), nullable=True)
    inn = Column(String(12), nullable=True)  # Russian tax ID
    
    # Role
    role = Column(
        Enum(UserRole),
        default=UserRole.USER,
        nullable=False
    )
    
    # Preferences
    preferences = Column(JSONB, default=dict)
    
    # Last login
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    tenders_created = relationship("Tender", back_populates="creator", foreign_keys="Tender.created_by")
    tenders_assigned = relationship("Tender", back_populates="assigned_to")
    favorite_tenders = relationship("FavoriteTender", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_users_email_active", "email", "is_active"),
        Index("idx_users_role", "role"),
        UniqueConstraint("email", name="uq_users_email"),
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


class Tender(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Tender model representing a procurement opportunity."""
    
    __tablename__ = "tenders"
    
    # Basic Info
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    tender_number = Column(String(100), unique=True, nullable=False, index=True)
    
    # Classification
    type = Column(Enum(TenderType), default=TenderType.COMMERCIAL, nullable=False)
    status = Column(Enum(TenderStatus), default=TenderStatus.DRAFT, nullable=False, index=True)
    category = Column(String(100), nullable=True, index=True)
    okpd2_codes = Column(JSONB, default=list)  # Russian product classification
    
    # Pricing
    initial_price = Column(Float, nullable=False)
    currency = Column(String(3), default="RUB", nullable=False)
    
    # Dates
    publication_date = Column(DateTime(timezone=True), nullable=True)
    submission_deadline = Column(DateTime(timezone=True), nullable=True)
    review_date = Column(DateTime(timezone=True), nullable=True)
    
    # Customer Info
    customer_name = Column(String(500), nullable=True)
    customer_inn = Column(String(12), nullable=True, index=True)
    customer_region = Column(String(100), nullable=True, index=True)
    
    # Documents
    documents_url = Column(String(1000), nullable=True)
    technical_spec_url = Column(String(1000), nullable=True)
    
    # AI Analysis
    ai_summary = Column(Text, nullable=True)
    ai_risk_score = Column(Float, nullable=True)  # 0-100
    ai_recommendations = Column(JSONB, default=list)
    
    # Relationships
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    creator = relationship("User", foreign_keys=[creator_id], back_populates="tenders_created")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="tenders_assigned")
    documents = relationship("TenderDocument", back_populates="tender", cascade="all, delete-orphan")
    comments = relationship("TenderComment", back_populates="tender", cascade="all, delete-orphan")
    favorites = relationship("FavoriteTender", back_populates="tender", cascade="all, delete-orphan")
    
    # Full-text search vector (PostgreSQL)
    search_vector = Column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index("idx_tenders_status_deadline", "status", "submission_deadline"),
        Index("idx_tenders_price", "initial_price"),
        Index("idx_tenders_customer_inn", "customer_inn"),
        Index("idx_tenders_search", "search_vector", postgresql_using="gin"),
    )
    
    def __repr__(self) -> str:
        return f"<Tender(id={self.id}, number={self.tender_number}, status={self.status})>"


class TenderDocument(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Documents associated with a tender."""
    
    __tablename__ = "tender_documents"
    
    tender_id = Column(UUID(as_uuid=True), ForeignKey("tenders.id"), nullable=False)
    
    # Document Info
    name = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(Enum(DocumentType), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    
    # Storage
    storage_path = Column(String(1000), nullable=False)
    s3_key = Column(String(500), nullable=True)
    
    # Metadata
    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    checksum = Column(String(64), nullable=True)  # SHA-256 hash
    
    # Relationships
    tender = relationship("Tender", back_populates="documents")
    uploader = relationship("User")
    
    __table_args__ = (
        Index("idx_tender_documents_tender_id", "tender_id"),
        Index("idx_tender_documents_file_type", "file_type"),
    )
    
    def __repr__(self) -> str:
        return f"<TenderDocument(id={self.id}, name={self.name})>"


class TenderComment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Comments on tenders for team collaboration."""
    
    __tablename__ = "tender_comments"
    
    tender_id = Column(UUID(as_uuid=True), ForeignKey("tenders.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("tender_comments.id"), nullable=True)
    
    content = Column(Text, nullable=False)
    is_edited = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    tender = relationship("Tender", back_populates="comments")
    user = relationship("User")
    replies = relationship("TenderComment", remote_side=[parent_id])
    
    __table_args__ = (
        Index("idx_tender_comments_tender_id", "tender_id"),
        Index("idx_tender_comments_user_id", "user_id"),
    )
    
    def __repr__(self) -> str:
        return f"<TenderComment(id={self.id}, tender_id={self.tender_id})>"


class FavoriteTender(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """User's favorite tenders."""
    
    __tablename__ = "favorite_tenders"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tender_id = Column(UUID(as_uuid=True), ForeignKey("tenders.id"), nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="favorite_tenders")
    tender = relationship("Tender", back_populates="favorites")
    
    __table_args__ = (
        UniqueConstraint("user_id", "tender_id", name="uq_favorite_tenders_user_tender"),
        Index("idx_favorite_tenders_user_id", "user_id"),
    )
    
    def __repr__(self) -> str:
        return f"<FavoriteTender(user_id={self.user_id}, tender_id={self.tender_id})>"


class AuditLog(UUIDPrimaryKeyMixin, Base):
    """Audit log for tracking important actions."""
    
    __tablename__ = "audit_logs"
    
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    __table_args__ = (
        Index("idx_audit_logs_timestamp_action", "timestamp", "action"),
        Index("idx_audit_logs_resource", "resource_type", "resource_id"),
    )
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action})>"
