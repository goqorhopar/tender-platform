"""
Tender Platform - Database Module
Production-grade database configuration with connection pooling, async support, and session management.
"""

import os
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

from app.core.config import settings
from app.core.logging_config import get_logger


# ============================================================================
# SYNC DATABASE ENGINE
# ============================================================================
sync_engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    echo=settings.DB_ECHO,
    future=True,
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    future=True,
)


# ============================================================================
# ASYNC DATABASE ENGINE
# ============================================================================
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    echo=settings.DB_ECHO,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    future=True,
)


# ============================================================================
# BASE MODEL
# ============================================================================
Base = declarative_base()


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================
def get_db() -> Generator[Session, None, None]:
    """
    Get database session (sync).
    Use as FastAPI dependency.
    """
    db = SyncSessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session (async).
    Use as FastAPI dependency for async endpoints.
    """
    db = AsyncSessionLocal()
    try:
        yield db
    except Exception:
        await db.rollback()
        raise
    finally:
        await db.close()


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================
def init_db() -> None:
    """
    Initialize database using Alembic migrations.
    Falls back to create_all() only for development if no migrations exist.
    """
    from app.models import User, Tender, TenderDocument  # noqa: F401
    import subprocess
    import sys
    
    logger = get_logger(__name__)
    
    try:
        # Run Alembic migrations
        logger.info("Running Alembic migrations...")
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            logger.info("Database migrations completed successfully")
        else:
            logger.warning(f"Migration output: {result.stdout}")
            logger.error(f"Migration errors: {result.stderr}")
            # Fall back to create_all for development
            Base.metadata.create_all(bind=sync_engine)
            logger.info("Fallback: Created tables directly")
    except Exception as e:
        logger.warning(f"Alembic migration failed: {e}. Falling back to create_all()")
        Base.metadata.create_all(bind=sync_engine)


async def init_db_async() -> None:
    """
    Initialize database tables (async).
    Should be called on application startup for async apps.
    """
    from app.models import User, Tender, TenderDocument  # noqa: F401
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db_connections() -> None:
    """
    Close all database connections.
    Should be called on application shutdown.
    """
    await async_engine.dispose()
    sync_engine.dispose()


# ============================================================================
# CONTEXT MANAGERS
# ============================================================================
class DatabaseSession:
    """Context manager for database sessions."""
    
    def __init__(self, async_mode: bool = False):
        self.async_mode = async_mode
        self.db: Session | AsyncSession | None = None
    
    def __enter__(self) -> Session:
        self.db = SyncSessionLocal()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db.rollback()
        self.db.close()
        return False
    
    async def __aenter__(self) -> AsyncSession:
        self.db = AsyncSessionLocal()
        return self.db
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.db.rollback()
        await self.db.close()
        return False
