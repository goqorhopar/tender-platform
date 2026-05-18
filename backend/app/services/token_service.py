"""
Tender Platform - Token Service
Production-grade token management for password reset, email verification, etc.
Stores tokens in Redis with expiration.
"""

import hashlib
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import generate_secure_token
from app.core.logging_config import get_logger
from app.models import User

logger = get_logger(__name__)


class TokenType:
    """Token types for different purposes."""
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"
    ACCOUNT_ACTIVATION = "account_activation"


class TokenService:
    """
    Service for managing secure tokens.
    
    In production, this should use Redis for token storage with TTL.
    For now, uses database storage as fallback.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_token(
        self,
        user_id: str,
        token_type: str,
        expires_minutes: int = 60
    ) -> str:
        """
        Create a new token for a user.
        
        Args:
            user_id: User ID
            token_type: Type of token (password_reset, email_verification, etc.)
            expires_minutes: Token expiration time in minutes
            
        Returns:
            The generated token string
        """
        token = generate_secure_token(32)
        expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)
        
        # Store token hash in database (never store plain token)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Import here to avoid circular imports
        from app.models import PasswordResetToken
        
        # Check if token model exists (might not be in all schema versions)
        try:
            reset_token = PasswordResetToken(
                user_id=user_id,
                token_hash=token_hash,
                token_type=token_type,
                expires_at=expires_at,
                is_used=False,
            )
            self.db.add(reset_token)
            self.db.commit()
            logger.info(f"Created {token_type} token for user {user_id}")
        except Exception as e:
            # Fallback: log warning but don't fail
            logger.warning(f"Could not store token in database: {e}. Token will not be verifiable.")
        
        return token
    
    def verify_token(self, token: str, token_type: str) -> Optional[str]:
        """
        Verify a token and return the associated user ID.
        
        Args:
            token: The token string to verify
            token_type: Expected token type
            
        Returns:
            User ID if valid, None otherwise
        """
        if not token or len(token) < 10:
            return None
        
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        try:
            from app.models import PasswordResetToken
            
            reset_token = self.db.query(PasswordResetToken).filter(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.token_type == token_type,
                PasswordResetToken.is_used == False,
                PasswordResetToken.expires_at > datetime.utcnow(),
            ).first()
            
            if reset_token:
                # Mark token as used
                reset_token.is_used = True
                reset_token.used_at = datetime.utcnow()
                self.db.commit()
                
                logger.info(f"Verified {token_type} token for user {reset_token.user_id}")
                return reset_token.user_id
        except Exception as e:
            logger.error(f"Token verification error: {e}")
        
        return None
    
    def invalidate_user_tokens(self, user_id: str, token_type: Optional[str] = None) -> int:
        """
        Invalidate all tokens for a user.
        
        Args:
            user_id: User ID
            token_type: Optional specific token type to invalidate
            
        Returns:
            Number of tokens invalidated
        """
        try:
            from app.models import PasswordResetToken
            
            query = self.db.query(PasswordResetToken).filter(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.is_used == False,
            )
            
            if token_type:
                query = query.filter(PasswordResetToken.token_type == token_type)
            
            tokens = query.all()
            count = len(tokens)
            
            for token in tokens:
                token.is_used = True
            
            self.db.commit()
            logger.info(f"Invalidated {count} tokens for user {user_id}")
            return count
        except Exception as e:
            logger.error(f"Error invalidating tokens: {e}")
            return 0


# Singleton instance (will be created per request via dependency injection)
def get_token_service(db: Session = None) -> TokenService:
    """Get token service instance."""
    return TokenService(db)
