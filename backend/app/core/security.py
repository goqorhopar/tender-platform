"""
Tender Platform - Security Module
Production-grade authentication, authorization, and security utilities.
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
from jose import jwt, JWTError
import bcrypt
from pydantic import ValidationError

from app.core.config import settings


# ============================================================================
# PASSWORD HASHING
# ============================================================================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """Hash a password securely using bcrypt."""
    # bcrypt has a 72-byte limit, truncate if needed
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)  # OWASP recommendation
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


# ============================================================================
# JWT TOKEN MANAGEMENT
# ============================================================================
def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: The subject (usually user ID or email)
        expires_delta: Optional custom expiration time
        additional_claims: Optional additional JWT claims
    
    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "sub": str(subject),
        "type": "access"
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        subject: The subject (usually user ID)
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT refresh token
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "sub": str(subject),
        "type": "refresh"
    }
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: The JWT token to decode
    
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except (JWTError, ValidationError):
        return None


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify an access token.
    
    Args:
        token: The access token to verify
    
    Returns:
        Decoded token payload or None if invalid
    """
    payload = decode_token(token)
    if payload and payload.get("type") == "access":
        return payload
    return None


def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a refresh token.
    
    Args:
        token: The refresh token to verify
    
    Returns:
        Decoded token payload or None if invalid
    """
    payload = decode_token(token)
    if payload and payload.get("type") == "refresh":
        return payload
    return None


# ============================================================================
# RATE LIMITING
# ============================================================================
class RateLimiter:
    """
    In-memory rate limiter for API endpoints.
    For production, use Redis-based rate limiting.
    """
    
    def __init__(self):
        self._requests: Dict[str, list] = {}
    
    def is_allowed(self, identifier: str, max_requests: int, window_seconds: int) -> bool:
        """
        Check if a request is allowed based on rate limits.
        
        Args:
            identifier: Unique identifier (e.g., IP address, user ID)
            max_requests: Maximum requests allowed in the window
            window_seconds: Time window in seconds
        
        Returns:
            True if request is allowed, False if rate limited
        """
        now = datetime.utcnow().timestamp()
        window_start = now - window_seconds
        
        if identifier not in self._requests:
            self._requests[identifier] = []
        
        # Remove old requests outside the window
        self._requests[identifier] = [
            ts for ts in self._requests[identifier]
            if ts > window_start
        ]
        
        # Check if under limit
        if len(self._requests[identifier]) < max_requests:
            self._requests[identifier].append(now)
            return True
        
        return False
    
    def get_remaining(self, identifier: str, max_requests: int, window_seconds: int) -> int:
        """Get remaining requests allowed in the current window."""
        now = datetime.utcnow().timestamp()
        window_start = now - window_seconds
        
        if identifier not in self._requests:
            return max_requests
        
        current_requests = [
            ts for ts in self._requests[identifier]
            if ts > window_start
        ]
        
        return max(0, max_requests - len(current_requests))


# Global rate limiter instance
rate_limiter = RateLimiter()


# ============================================================================
# SECURITY HEADERS
# ============================================================================
def get_security_headers() -> Dict[str, str]:
    """
    Get recommended security headers for responses.
    
    Returns:
        Dictionary of security headers
    """
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "Cache-Control": "no-store, no-cache, must-revalidate",
        "Pragma": "no-cache",
    }


# ============================================================================
# INPUT SANITIZATION
# ============================================================================
import re


def sanitize_input(value: str) -> str:
    """
    Sanitize user input to prevent XSS and injection attacks.
    
    Args:
        value: Raw user input
    
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return value
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Remove control characters except newlines and tabs
    value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
    
    # Limit length
    max_length = 10000
    if len(value) > max_length:
        value = value[:max_length]
    
    return value


def sanitize_html(value: str) -> str:
    """
    Sanitize HTML content to prevent XSS.
    Simple implementation - for production, use bleach library.
    
    Args:
        value: HTML string
    
    Returns:
        Sanitized HTML
    """
    # Remove script tags
    value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove event handlers
    value = re.sub(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', '', value, flags=re.IGNORECASE)
    value = re.sub(r'\s+on\w+\s*=\s*[^\s>]+', '', value, flags=re.IGNORECASE)
    
    # Remove javascript: protocol
    value = re.sub(r'javascript:', '', value, flags=re.IGNORECASE)
    
    return value


# ============================================================================
# FILE SECURITY
# ============================================================================
def generate_file_hash(file_content: bytes) -> str:
    """Generate SHA-256 hash of file content."""
    return hashlib.sha256(file_content).hexdigest()


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """
    Validate file extension against allowed list.
    
    Args:
        filename: Original filename
        allowed_extensions: List of allowed extensions (with dots)
    
    Returns:
        True if extension is allowed
    """
    if not filename or '.' not in filename:
        return False
    
    ext = '.' + filename.rsplit('.', 1)[1].lower()
    return ext in allowed_extensions


def secure_filename(filename: str) -> str:
    """
    Generate a secure filename by removing dangerous characters.
    
    Args:
        filename: Original filename
    
    Returns:
        Secure filename
    """
    import unicodedata
    
    # Convert to ASCII
    filename = unicodedata.normalize('NFKD', filename)
    filename = filename.encode('ascii', 'ignore').decode('ascii')
    
    # Remove dangerous characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    
    # Remove path separators
    filename = filename.replace('/', '').replace('\\', '')
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = f"{name[:250-len(ext)]}.{ext}" if ext else filename[:255]
    
    return filename or "unnamed_file"
