"""
Tests for Authentication API

This module tests the authentication endpoints (signup, login).
"""

import os
# Set required environment variables for testing
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only-do-not-use-in-production"
os.environ["ENCRYPTION_KEY"] = "test-encryption-key-32-bytes-long!!"

from fastapi.testclient import TestClient
import pytest
from backend.app.main import app
from backend.app.api.v1.endpoints.auth import fake_users_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_users_db():
    """Clear the fake user DB before each test."""
    fake_users_db.clear()
    yield


def test_signup_success():
    """Test successful user signup."""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "password": "StrongPassword123!",
            "full_name": "Test User"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data  # Password should not be returned


def test_signup_duplicate_email():
    """Test signup with existing email."""
    # Create first user
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "password": "StrongPassword123!"
        }
    )
    
    # Try to create same user again
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "password": "AnotherPassword123!"
        }
    )
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_success():
    """Test successful login."""
    # Create user
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "password": "StrongPassword123!"
        }
    )
    
    # Login
    response = client.post(
        "/api/v1/auth/login/access-token",
        data={
            "username": "test@example.com",
            "password": "StrongPassword123!"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials():
    """Test login with wrong password."""
    # Create user
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "password": "StrongPassword123!"
        }
    )
    
    # Login with wrong password
    response = client.post(
        "/api/v1/auth/login/access-token",
        data={
            "username": "test@example.com",
            "password": "WrongPassword123!"
        }
    )
    
    assert response.status_code == 400
    assert "Incorrect email or password" in response.json()["detail"]


def test_protected_route():
    """Test accessing protected route with valid token."""
    # Create user and login
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "password": "StrongPassword123!"
        }
    )
    
    login_res = client.post(
        "/api/v1/auth/login/access-token",
        data={
            "username": "test@example.com",
            "password": "StrongPassword123!"
        }
    )
    token = login_res.json()["access_token"]
    
    # Access protected route
    response = client.post(
        "/api/v1/auth/login/test-token",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
