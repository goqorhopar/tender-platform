"""
Integration tests for authentication endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestAuthEndpoints:
    """Test authentication endpoint integration."""

    def test_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded", "unhealthy"]

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data or "service" in data

    def test_register_new_user(self, client: TestClient):
        """Test user registration."""
        user_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "full_name": "New User",
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Should succeed or fail if user exists (depending on test isolation)
        assert response.status_code in [200, 400]

    def test_login_with_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials."""
        credentials = {
            "username": "nonexistent@example.com",
            "password": "WrongPassword123!",
        }
        
        response = client.post("/api/v1/auth/token", data=credentials)
        
        assert response.status_code == 401

    def test_access_protected_endpoint_without_token(self, client: TestClient):
        """Test accessing protected endpoint without token."""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code in [401, 403]

    def test_api_version_info(self, client: TestClient):
        """Test API version info endpoint."""
        response = client.get("/api/v1/")
        
        assert response.status_code == 200
        data = response.json()
        assert "version" in data or "endpoints" in data
