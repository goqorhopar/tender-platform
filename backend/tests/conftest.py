"""
Pytest configuration and fixtures for Tender Platform tests.
"""

import os
import pytest
from typing import Generator, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_db
from app.core.config import settings


# Override settings for testing - use SQLite for unit tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    from sqlalchemy.dialects import sqlite
    
    # Use synchronous engine for tests with SQLite
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create tables manually without PostgreSQL-specific types
    from app.models import User  # Import models to register them with Base
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


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
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


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
