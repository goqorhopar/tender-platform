"""
Unit tests for Pydantic schemas.
"""

import pytest
from pydantic import ValidationError
from app.schemas.auth import (
    UserCreate,
    UserResponse,
    PasswordChangeRequest,
    PasswordResetRequest,
    TokenResponse,
)
from datetime import datetime
import uuid


class TestUserCreateSchema:
    """Test UserCreate schema validation."""

    def test_valid_user_create(self):
        """Test creating user with valid data."""
        user_data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User",
        }
        user = UserCreate(**user_data)
        
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"

    def test_invalid_email(self):
        """Test that invalid email raises error."""
        user_data = {
            "email": "invalid-email",
            "password": "SecurePass123!",
        }
        
        with pytest.raises(ValidationError):
            UserCreate(**user_data)

    def test_weak_password_too_short(self):
        """Test that too short password raises error."""
        user_data = {
            "email": "test@example.com",
            "password": "short",
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "8 characters" in str(exc_info.value).lower()

    def test_password_requires_uppercase(self):
        """Test that password without uppercase raises error."""
        user_data = {
            "email": "test@example.com",
            "password": "alllowercase123!",
        }
        
        with pytest.raises(ValidationError):
            UserCreate(**user_data)

    def test_password_requires_lowercase(self):
        """Test that password without lowercase raises error."""
        user_data = {
            "email": "test@example.com",
            "password": "ALLUPPERCASE123!",
        }
        
        with pytest.raises(ValidationError):
            UserCreate(**user_data)

    def test_password_requires_digit(self):
        """Test that password without digit raises error."""
        user_data = {
            "email": "test@example.com",
            "password": "NoDigitsHere!",
        }
        
        with pytest.raises(ValidationError):
            UserCreate(**user_data)

    def test_optional_fields(self):
        """Test that optional fields are truly optional."""
        user_data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
        }
        user = UserCreate(**user_data)
        
        assert user.full_name is None
        assert user.phone is None
        assert user.company_name is None
        assert user.inn is None

    def test_valid_inn_10_digits(self):
        """Test valid 10-digit INN."""
        user_data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "inn": "1234567890",
        }
        user = UserCreate(**user_data)
        assert user.inn == "1234567890"

    def test_valid_inn_12_digits(self):
        """Test valid 12-digit INN."""
        user_data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "inn": "123456789012",
        }
        user = UserCreate(**user_data)
        assert user.inn == "123456789012"

    def test_invalid_inn(self):
        """Test invalid INN format."""
        user_data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "inn": "12345",  # Too short
        }
        
        with pytest.raises(ValidationError):
            UserCreate(**user_data)


class TestPasswordChangeRequestSchema:
    """Test PasswordChangeRequest schema validation."""

    def test_valid_password_change(self):
        """Test valid password change request."""
        data = {
            "current_password": "OldPass123!",
            "new_password": "NewSecurePass456!",
        }
        request = PasswordChangeRequest(**data)
        
        assert request.current_password == "OldPass123!"
        assert request.new_password == "NewSecurePass456!"

    def test_new_password_too_short(self):
        """Test that new password too short raises error."""
        data = {
            "current_password": "OldPass123!",
            "new_password": "short",
        }
        
        with pytest.raises(ValidationError):
            PasswordChangeRequest(**data)

    def test_new_password_requirements(self):
        """Test new password strength requirements."""
        data = {
            "current_password": "OldPass123!",
            "new_password": "weakpass",
        }
        
        with pytest.raises(ValidationError):
            PasswordChangeRequest(**data)


class TestTokenResponseSchema:
    """Test TokenResponse schema validation."""

    def test_valid_token_response(self):
        """Test valid token response."""
        data = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "expires_in": 1800,
        }
        response = TokenResponse(**data)
        
        assert response.token_type == "bearer"
        assert response.expires_in == 1800

    def test_default_token_type(self):
        """Test default token type is bearer."""
        data = {
            "access_token": "token123",
            "refresh_token": "refresh123",
            "expires_in": 1800,
        }
        response = TokenResponse(**data)
        
        assert response.token_type == "bearer"


class TestUserResponseSchema:
    """Test UserResponse schema validation."""

    def test_valid_user_response(self):
        """Test valid user response."""
        data = {
            "id": str(uuid.uuid4()),
            "email": "test@example.com",
            "is_active": True,
            "is_verified": False,
            "role": "user",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        response = UserResponse(**data)
        
        assert response.email == "test@example.com"
        assert response.is_active is True
        assert response.role == "user"
