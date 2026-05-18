"""Comprehensive authentication tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration."""
    user_data = {
        "email": "test@example.com",
        "password": "securepassword123",
        "full_name": "Test User",
        "role": "user",
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test registering with duplicate email fails."""
    user_data = {
        "email": "duplicate@example.com",
        "password": "securepassword123",
        "full_name": "Test User",
    }
    
    # First registration
    response1 = await client.post("/api/v1/auth/register", json=user_data)
    assert response1.status_code == 201
    
    # Second registration with same email
    response2 = await client.post("/api/v1/auth/register", json=user_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    """Test registration with weak password fails."""
    user_data = {
        "email": "weak@example.com",
        "password": "123",
        "full_name": "Test User",
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful login."""
    user_data = {
        "email": "login@example.com",
        "password": "securepassword123",
        "full_name": "Login Test",
    }
    
    await client.post("/api/v1/auth/register", json=user_data)
    
    login_data = {
        "username": "login@example.com",
        "password": "securepassword123",
    }
    
    response = await client.post("/api/v1/auth/login", data=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Test login with wrong password fails."""
    user_data = {
        "email": "wrongpass@example.com",
        "password": "correctpassword123",
        "full_name": "Test User",
    }
    
    await client.post("/api/v1/auth/register", json=user_data)
    
    login_data = {
        "username": "wrongpass@example.com",
        "password": "wrongpassword",
    }
    
    response = await client.post("/api/v1/auth/login", data=login_data)
    
    assert response.status_code == 401
    assert "Incorrect" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent user fails."""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "anypassword",
    }
    
    response = await client.post("/api/v1/auth/login", data=login_data)
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient):
    """Test getting current authenticated user."""
    user_data = {
        "email": "current@example.com",
        "password": "securepassword123",
        "full_name": "Current User",
    }
    
    await client.post("/api/v1/auth/register", json=user_data)
    
    login_data = {
        "username": "current@example.com",
        "password": "securepassword123",
    }
    
    login_response = await client.post("/api/v1/auth/login", data=login_data)
    access_token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    """Test getting current user without token fails."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient):
    """Test getting current user with invalid token fails."""
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    """Test token refresh."""
    user_data = {
        "email": "refresh@example.com",
        "password": "securepassword123",
    }
    
    await client.post("/api/v1/auth/register", json=user_data)
    
    login_data = {
        "username": "refresh@example.com",
        "password": "securepassword123",
    }
    
    login_response = await client.post("/api/v1/auth/login", data=login_data)
    refresh_token = login_response.json()["refresh_token"]
    
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["access_token"] != login_response.json()["access_token"]


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    """Test refresh with invalid token fails."""
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid_token"})
    assert response.status_code == 401
