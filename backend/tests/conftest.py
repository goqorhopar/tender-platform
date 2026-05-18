"""
Pytest configuration and fixtures for Tender Platform tests.
All tests use SQLite for fast, isolated execution without external dependencies.
"""

import os
import pytest
from typing import Generator, Any
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# ============================================================================
# CRITICAL: Set environment variables BEFORE ANY app imports
# This must happen at the very top of this file
# ============================================================================

# Always use SQLite for tests - fast and isolated
TEST_DATABASE_URL = "sqlite:///:memory:"
TEST_ASYNC_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Set environment variables immediately
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["ASYNC_DATABASE_URL"] = TEST_ASYNC_DATABASE_URL
os.environ["PROMETHEUS_ENABLED"] = "false"
os.environ["CELERY_BROKER_URL"] = "memory://"
os.environ["REDIS_HOST"] = "localhost"
os.environ["DEBUG"] = "true"

# Now we can safely import app modules
from fastapi.testclient import TestClient
from app.db.database import Base, get_db
from app.core.config import settings


def create_test_app():
    """Create a fresh FastAPI app instance for testing with SQLite."""
    # Import here after env vars are set
    from app.main import create_application
    
    app = create_application()
    
    # Override exception handlers for testing
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors(), "body": exc.body}
        )
    
    return app


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine using SQLite."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    # Create tables
    from app.models import User, Tender, TenderDocument, TenderComment, FavoriteTender, AuditLog
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """Create a new database session for each test."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Create test client with overridden database dependency."""
    # Create fresh app for each test
    test_app = create_test_app()
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    test_app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(test_app) as test_client:
        yield test_client
    
    test_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session) -> dict:
    """Create test user data."""
    return {
        "email": "test@example.com",
        "password": "Test1234!",
        "full_name": "Test User",
    }


@pytest.fixture(scope="function")
def authenticated_client(client, test_user, db_session) -> Generator[TestClient, None, None]:
    """Create authenticated test client."""
    from app.core.security import get_password_hash
    from app.models import User
    import uuid
    
    # Create test user in database
    user = User(
        id=uuid.uuid4(),
        email=test_user["email"],
        hashed_password=get_password_hash(test_user["password"]),
        is_active=True,
        is_verified=True,
        role="user",
    )
    db_session.add(user)
    db_session.commit()
    
    # Login to get token
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": test_user["email"],
            "password": test_user["password"],
        },
    )
    
    if response.status_code == 200:
        tokens = response.json()
        client.headers.update({
            "Authorization": f"Bearer {tokens['access_token']}",
        })
    
    yield client
    
    # Cleanup
    db_session.delete(user)
    db_session.commit()
