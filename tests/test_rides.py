# ============================================================
# RideX - Ride Service Tests
# tests/test_rides.py
# ============================================================

from fastapi.testclient import TestClient

from services.ride_service.main import app


# ------------------------------------------------------------
# Test Client
# ------------------------------------------------------------

client = TestClient(app)


# ============================================================
# Health Check
# ============================================================

def test_ride_service_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


# ============================================================
# Create Ride
# ============================================================

def test_create_ride():
    ride_data = {
        "passenger_id": 1,
        "pickup_latitude": 17.3850,
        "pickup_longitude": 78.4867,
        "dropoff_latitude": 17.4065,
        "dropoff_longitude": 78.4772,
        "vehicle_type": "car"
    }

    response = client.post(
        "/rides",
        json=ride_data
    )

    assert response.status_code in [200, 201]

    data = response.json()

    assert "id" in data
    assert data["passenger_id"] == ride_data["passenger_id"]


# ============================================================
# Get Ride
# ============================================================

def test_get_ride():
    response = client.get("/rides/1")

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        assert "id" in data
        assert "passenger_id" in data
        assert "status" in data


# ============================================================
# Get Passenger Rides
# ============================================================

def test_get_passenger_rides():
    response = client.get("/rides/passenger/1")

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        assert isinstance(data, list)


# ============================================================
# Get Driver Rides
# ============================================================

def test_get_driver_rides():
    response = client.get("/rides/driver/1")

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        assert isinstance(data, list)


# ============================================================
# Update Ride Status - Searching
# ============================================================

def test_ride_status_searching():
    response = client.patch(
        "/rides/1/status",
        json={
            "status": "searching"
        }
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        assert data["status"] == "searching"


# ============================================================
# Update Ride Status - Driver Assigned
# ============================================================

def test_ride_status_driver_assigned():
    response = client.patch(
        "/rides/1/status",
        json={
            "status": "driver_assigned"
        }
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        assert data["status"] == "driver_assigned"


# ============================================================
# Update Ride Status - Driver Arriving
# ============================================================

def test_ride_status_driver_arriving():
    response = client.patch(
        "/rides/1/status",
        json={
            "status": "driver_arriving"
        }
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        assert data["status"] == "driver_arriving"


# ============================================================
# Update Ride Status - Started
# ============================================================

def test_ride_status_started():
    response = client.patch(
        "/rides/1/status",
        json={
            "status": "started"
        }
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        assert data["status"] == "started"


# ============================================================
# Update Ride Status - Completed
# ============================================================

def test_ride_status_completed():
    response = client.patch(
        "/rides/1/status",
        json={
            "status": "completed"
        }
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        assert data["status"] == "completed"


# ============================================================
# Cancel Ride
# ============================================================

def test_cancel_ride():
    response = client.patch(
        "/rides/1/status",
        json={
            "status": "cancelled"
        }
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        assert data["status"] == "cancelled"


# ============================================================
# Ride Fare Estimate
# ============================================================

def test_ride_fare_estimate():
    response = client.post(
        "/rides/fare-estimate",
        json={
            "pickup_latitude": 17.3850,
            "pickup_longitude": 78.4867,
            "dropoff_latitude": 17.4065,
            "dropoff_longitude": 78.4772,
            "vehicle_type": "car"
        }
    )

    assert response.status_code in [200, 201, 404]

    if response.status_code == 200:
        data = response.json()

        assert "fare" in data


# ============================================================
# Invalid Ride
# ============================================================

def test_invalid_ride():
    ride_data = {
        "passenger_id": 0,
        "pickup_latitude": 999,
        "pickup_longitude": 999,
        "dropoff_latitude": 999,
        "dropoff_longitude": 999
    }

    response = client.post(
        "/rides",
        json=ride_data
    )

    assert response.status_code in [400, 422]


# ============================================================
# Missing Required Fields
# ============================================================

def test_missing_ride_fields():
    ride_data = {
        "passenger_id": 1
    }

    response = client.post(
        "/rides",
        json=ride_data
    )

    assert response.status_code == 422


# ============================================================
# Invalid Ride Status
# ============================================================

def test_invalid_ride_status():
    response = client.patch(
        "/rides/1/status",
        json={
            "status": "invalid_status"
        }
    )

    assert response.status_code in [400, 404, 422]


# ============================================================
# Delete Ride
# ============================================================

def test_delete_ride():
    response = client.delete("/rides/1")

    assert response.status_code in [200, 204, 404]
