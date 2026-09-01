# ============================================================
# RideX - Driver Service Tests
# tests/test_drivers.py
# ============================================================

from fastapi.testclient import TestClient

from services.driver_service.main import app


# ------------------------------------------------------------
# Test Client
# ------------------------------------------------------------

client = TestClient(app)


# ============================================================
# Health Check
# ============================================================

def test_driver_service_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


# ============================================================
# Create Driver
# ============================================================

def test_create_driver():
    driver_data = {
        "name": "Test Driver",
        "email": "driver@example.com",
        "phone": "+919999999999",
        "license_number": "DL123456789",
        "vehicle_type": "car",
        "vehicle_number": "TS09AB1234"
    }

    response = client.post(
        "/drivers",
        json=driver_data
    )

    assert response.status_code in [200, 201]

    data = response.json()

    assert "id" in data
    assert data["name"] == driver_data["name"]
    assert data["email"] == driver_data["email"]
    assert data["phone"] == driver_data["phone"]


# ============================================================
# Get Driver
# ============================================================

def test_get_driver():
    response = client.get("/drivers/1")

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        assert "id" in data
        assert "name" in data
        assert "phone" in data


# ============================================================
# Update Driver
# ============================================================

def test_update_driver():
    driver_data = {
        "name": "Updated Driver",
        "vehicle_type": "sedan",
        "vehicle_number": "TS09XY5678"
    }

    response = client.put(
        "/drivers/1",
        json=driver_data
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        assert data["name"] == driver_data["name"]
        assert data["vehicle_type"] == driver_data["vehicle_type"]


# ============================================================
# Driver Online
# ============================================================

def test_driver_goes_online():
    response = client.patch(
        "/drivers/1/status",
        json={
            "status": "online"
        }
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        assert data["status"] == "online"


# ============================================================
# Driver Offline
# ============================================================

def test_driver_goes_offline():
    response = client.patch(
        "/drivers/1/status",
        json={
            "status": "offline"
        }
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        assert data["status"] == "offline"


# ============================================================
# Update Driver Location
# ============================================================

def test_update_driver_location():
    location_data = {
        "latitude": 17.3850,
        "longitude": 78.4867
    }

    response = client.patch(
        "/drivers/1/location",
        json=location_data
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        assert "latitude" in data
        assert "longitude" in data


# ============================================================
# Get Available Drivers
# ============================================================

def test_get_available_drivers():
    response = client.get("/drivers/available")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


# ============================================================
# Delete Driver
# ============================================================

def test_delete_driver():
    response = client.delete("/drivers/1")

    assert response.status_code in [200, 204, 404]


# ============================================================
# Invalid Driver
# ============================================================

def test_invalid_driver():
    driver_data = {
        "name": "",
        "email": "invalid-email",
        "phone": "",
        "license_number": ""
    }

    response = client.post(
        "/drivers",
        json=driver_data
    )

    assert response.status_code in [400, 422]


# ============================================================
# Missing Required Fields
# ============================================================

def test_missing_driver_fields():
    driver_data = {
        "name": "Test Driver"
    }

    response = client.post(
        "/drivers",
        json=driver_data
    )

    assert response.status_code == 422


# ============================================================
# Invalid Driver Status
# ============================================================

def test_invalid_driver_status():
    response = client.patch(
        "/drivers/1/status",
        json={
            "status": "invalid_status"
        }
    )

    assert response.status_code in [400, 404, 422]
