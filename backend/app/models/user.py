"""User model for authentication and authorization."""

from sqlalchemy import Column, String, Boolean, DateTime, UUID, Text
from sqlalchemy.sql import func
import uuid

from app.database import Base


class User(Base):
    """User model for the application."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="user")  # user, admin, moderator
    
    is_active = Column(Boolean, default=True)
    is_email_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"
