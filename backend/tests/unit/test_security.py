"""
Unit tests for security module.
"""

import pytest
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_refresh_token,
    sanitize_input,
    secure_filename,
)


class TestPasswordHashing:
    """Test password hashing functions."""

    def test_hash_password(self):
        """Test that password is hashed correctly."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_correct_password(self):
        """Test verifying correct password."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_incorrect_password(self):
        """Test verifying incorrect password."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False

    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "TestPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Test JWT token creation and verification."""

    def test_create_access_token(self):
        """Test creating access token."""
        user_id = "test-user-id"
        token = create_access_token(subject=user_id)
        
        assert token is not None
        assert len(token) > 0

    def test_create_refresh_token(self):
        """Test creating refresh token."""
        user_id = "test-user-id"
        token = create_refresh_token(subject=user_id)
        
        assert token is not None
        assert len(token) > 0

    def test_verify_valid_access_token(self):
        """Test verifying valid access token."""
        user_id = "test-user-id"
        token = create_access_token(subject=user_id)
        
        payload = verify_access_token(token)
        
        assert payload is not None
        assert payload.get("sub") == user_id
        assert payload.get("type") == "access"

    def test_verify_valid_refresh_token(self):
        """Test verifying valid refresh token."""
        user_id = "test-user-id"
        token = create_refresh_token(subject=user_id)
        
        payload = verify_refresh_token(token)
        
        assert payload is not None
        assert payload.get("sub") == user_id
        assert payload.get("type") == "refresh"

    def test_verify_invalid_token(self):
        """Test verifying invalid token."""
        invalid_token = "invalid.token.here"
        
        assert verify_access_token(invalid_token) is None
        assert verify_refresh_token(invalid_token) is None

    def test_access_token_not_valid_as_refresh(self):
        """Test that access token is not valid as refresh token."""
        user_id = "test-user-id"
        access_token = create_access_token(subject=user_id)
        
        payload = verify_refresh_token(access_token)
        assert payload is None

    def test_refresh_token_not_valid_as_access(self):
        """Test that refresh token is not valid as access token."""
        user_id = "test-user-id"
        refresh_token = create_refresh_token(subject=user_id)
        
        payload = verify_access_token(refresh_token)
        assert payload is None


class TestInputSanitization:
    """Test input sanitization functions."""

    def test_sanitize_normal_input(self):
        """Test sanitizing normal input."""
        input_str = "Normal text input"
        result = sanitize_input(input_str)
        
        assert result == input_str

    def test_sanitize_null_bytes(self):
        """Test removing null bytes."""
        input_str = "Text\x00with\x00nulls"
        result = sanitize_input(input_str)
        
        assert "\x00" not in result
        assert result == "Textwithnulls"

    def test_sanitize_control_characters(self):
        """Test removing control characters."""
        input_str = "Text\x0b\x0cwith\x0econtrol"
        result = sanitize_input(input_str)
        
        assert result == "Textwithcontrol"

    def test_sanitize_long_input(self):
        """Test truncating long input."""
        input_str = "A" * 15000
        result = sanitize_input(input_str)
        
        assert len(result) <= 10000

    def test_sanitize_non_string_input(self):
        """Test handling non-string input."""
        result = sanitize_input(123)
        assert result == 123


class TestSecureFilename:
    """Test secure filename generation."""

    def test_secure_normal_filename(self):
        """Test securing normal filename."""
        filename = "document.pdf"
        result = secure_filename(filename)
        
        assert result == "document.pdf"

    def test_secure_filename_with_spaces(self):
        """Test securing filename with spaces."""
        filename = "my document.pdf"
        result = secure_filename(filename)
        
        assert " " not in result or result == "my document.pdf"

    def test_secure_filename_with_special_chars(self):
        """Test securing filename with special characters."""
        filename = "../evil<script>.pdf"
        result = secure_filename(filename)
        
        assert "/" not in result
        assert "\\" not in result
        assert "<" not in result
        assert ">" not in result

    def test_secure_filename_path_traversal(self):
        """Test preventing path traversal."""
        filename = "../../../etc/passwd"
        result = secure_filename(filename)
        
        assert "/" not in result
        assert ".." not in result

    def test_secure_filename_unicode(self):
        """Test handling unicode filenames."""
        filename = "документ.pdf"
        result = secure_filename(filename)
        
        assert result is not None
        assert len(result) > 0
