# ============================================================
# RideX - User Service Tests
# tests/test_users.py
# ============================================================

import pytest
from fastapi.testclient import TestClient

from services.user_service.main import app


# ------------------------------------------------------------
# Test Client
# ------------------------------------------------------------

client = TestClient(app)


# ============================================================
# Health Check
# ============================================================

def test_user_service_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


# ============================================================
# Create User
# ============================================================

def test_create_user():
    user_data = {
        "name": "Rangaraju",
        "email": "rangaraju@example.com",
        "phone": "+919999999999"
    }

    response = client.post(
        "/users",
        json=user_data
    )

    assert response.status_code in [200, 201]

    data = response.json()

    assert "id" in data
    assert data["name"] == user_data["name"]
    assert data["email"] == user_data["email"]
    assert data["phone"] == user_data["phone"]


# ============================================================
# Get User
# ============================================================

def test_get_user():
    response = client.get("/users/1")

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        assert "id" in data
        assert "name" in data
        assert "email" in data


# ============================================================
# Update User
# ============================================================

def test_update_user():
    user_data = {
        "name": "Rangaraju Updated",
        "phone": "+918888888888"
    }

    response = client.put(
        "/users/1",
        json=user_data
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        assert data["name"] == user_data["name"]
        assert data["phone"] == user_data["phone"]


# ============================================================
# Delete User
# ============================================================

def test_delete_user():
    response = client.delete("/users/1")

    assert response.status_code in [200, 204, 404]


# ============================================================
# Invalid User
# ============================================================

def test_invalid_user():
    user_data = {
        "name": "",
        "email": "invalid-email",
        "phone": ""
    }

    response = client.post(
        "/users",
        json=user_data
    )

    assert response.status_code in [400, 422]


# ============================================================
# Missing Required Fields
# ============================================================

def test_missing_user_fields():
    user_data = {
        "name": "Test User"
    }

    response = client.post(
        "/users",
        json=user_data
    )

    assert response.status_code == 422
