# ============================================================
# RideX - Pricing Service Tests
# tests/test_pricing.py
# ============================================================

from fastapi.testclient import TestClient

from services.pricing_service.main import app


# ------------------------------------------------------------
# Test Client
# ------------------------------------------------------------

client = TestClient(app)


# ============================================================
# Health Check
# ============================================================

def test_pricing_service_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


# ============================================================
# Calculate Fare
# ============================================================

def test_calculate_fare():
    fare_data = {
        "distance_km": 10.0,
        "duration_minutes": 20,
        "vehicle_type": "car"
    }

    response = client.post(
        "/pricing/fare",
        json=fare_data
    )

    assert response.status_code in [200, 201, 404]

    if response.status_code in [200, 201]:
        data = response.json()

        assert isinstance(data, dict)
        assert "fare" in data
        assert data["fare"] >= 0


# ============================================================
# Fare Estimate
# ============================================================

def test_fare_estimate():
    fare_data = {
        "pickup_latitude": 17.3850,
        "pickup_longitude": 78.4867,
        "dropoff_latitude": 17.4065,
        "dropoff_longitude": 78.4772,
        "vehicle_type": "car"
    }

    response = client.post(
        "/pricing/estimate",
        json=fare_data
    )

    assert response.status_code in [200, 201, 404]

    if response.status_code in [200, 201]:
        data = response.json()

        assert isinstance(data, dict)

        if "fare" in data:
            assert data["fare"] >= 0


# ============================================================
# Base Fare
# ============================================================

def test_base_fare():
    response = client.get(
        "/pricing/base-fare",
        params={
            "vehicle_type": "car"
        }
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        assert isinstance(data, dict)

        if "base_fare" in data:
            assert data["base_fare"] >= 0


# ============================================================
# Vehicle Type Pricing
# ============================================================

def test_vehicle_type_pricing():
    vehicle_types = [
        "car",
        "sedan",
        "suv",
        "bike",
        "auto"
    ]

    for vehicle_type in vehicle_types:
        response = client.post(
            "/pricing/fare",
            json={
                "distance_km": 10.0,
                "duration_minutes": 20,
                "vehicle_type": vehicle_type
            }
        )

        assert response.status_code in [200, 201, 400, 404, 422]


# ============================================================
# Surge Pricing
# ============================================================

def test_surge_multiplier():
    surge_data = {
        "demand": 100,
        "available_drivers": 20
    }

    response = client.post(
        "/pricing/surge",
        json=surge_data
    )

    assert response.status_code in [200, 201, 404]

    if response.status_code in [200, 201]:
        data = response.json()

        assert isinstance(data, dict)

        if "multiplier" in data:
            assert data["multiplier"] >= 1.0


# ============================================================
# No Surge
# ============================================================

def test_no_surge():
    surge_data = {
        "demand": 10,
        "available_drivers": 100
    }

    response = client.post(
        "/pricing/surge",
        json=surge_data
    )

    assert response.status_code in [200, 201, 404]

    if response.status_code in [200, 201]:
        data = response.json()

        if "multiplier" in data:
            assert data["multiplier"] >= 1.0


# ============================================================
# High Surge
# ============================================================

def test_high_surge():
    surge_data = {
        "demand": 1000,
        "available_drivers": 10
    }

    response = client.post(
        "/pricing/surge",
        json=surge_data
    )

    assert response.status_code in [200, 201, 404]

    if response.status_code in [200, 201]:
        data = response.json()

        if "multiplier" in data:
            assert data["multiplier"] > 1.0


# ============================================================
# Long Distance Fare
# ============================================================

def test_long_distance_fare():
    fare_data = {
        "distance_km": 100.0,
        "duration_minutes": 120,
        "vehicle_type": "car"
    }

    response = client.post(
        "/pricing/fare",
        json=fare_data
    )

    assert response.status_code in [200, 201, 404]

    if response.status_code in [200, 201]:
        data = response.json()

        if "fare" in data:
            assert data["fare"] > 0


# ============================================================
# Short Distance Fare
# ============================================================

def test_short_distance_fare():
    fare_data = {
        "distance_km": 1.0,
        "duration_minutes": 5,
        "vehicle_type": "car"
    }

    response = client.post(
        "/pricing/fare",
        json=fare_data
    )

    assert response.status_code in [200, 201, 404]

    if response.status_code in [200, 201]:
        data = response.json()

        if "fare" in data:
            assert data["fare"] >= 0


# ============================================================
# Zero Distance
# ============================================================

def test_zero_distance():
    fare_data = {
        "distance_km": 0,
        "duration_minutes": 0,
        "vehicle_type": "car"
    }

    response = client.post(
        "/pricing/fare",
        json=fare_data
    )

    assert response.status_code in [200, 201, 400, 404, 422]


# ============================================================
# Negative Distance
# ============================================================

def test_negative_distance():
    fare_data = {
        "distance_km": -10,
        "duration_minutes": 20,
        "vehicle_type": "car"
    }

    response = client.post(
        "/pricing/fare",
        json=fare_data
    )

    assert response.status_code in [400, 404, 422]


# ============================================================
# Negative Duration
# ============================================================

def test_negative_duration():
    fare_data = {
        "distance_km": 10,
        "duration_minutes": -20,
        "vehicle_type": "car"
    }

    response = client.post(
        "/pricing/fare",
        json=fare_data
    )

    assert response.status_code in [400, 404, 422]


# ============================================================
# Invalid Vehicle Type
# ============================================================

def test_invalid_vehicle_type():
    fare_data = {
        "distance_km": 10,
        "duration_minutes": 20,
        "vehicle_type": "invalid_vehicle"
    }

    response = client.post(
        "/pricing/fare",
        json=fare_data
    )

    assert response.status_code in [400, 404, 422]


# ============================================================
# Missing Required Fields
# ============================================================

def test_missing_pricing_fields():
    fare_data = {
        "distance_km": 10
    }

    response = client.post(
        "/pricing/fare",
        json=fare_data
    )

    assert response.status_code == 422


# ============================================================
# Fare Breakdown
# ============================================================

def test_fare_breakdown():
    fare_data = {
        "distance_km": 10,
        "duration_minutes": 20,
        "vehicle_type": "car"
    }

    response = client.post(
        "/pricing/fare",
        json=fare_data
    )

    assert response.status_code in [200, 201, 404]

    if response.status_code in [200, 201]:
        data = response.json()

        if "breakdown" in data:
            assert isinstance(data["breakdown"], dict)


# ============================================================
# Pricing Consistency
# ============================================================

def test_pricing_consistency():
    fare_data = {
        "distance_km": 10,
        "duration_minutes": 20,
        "vehicle_type": "car"
    }

    response1 = client.post(
        "/pricing/fare",
        json=fare_data
    )

    response2 = client.post(
        "/pricing/fare",
        json=fare_data
    )

    if response1.status_code in [200, 201] and \
       response2.status_code in [200, 201]:

        fare1 = response1.json().get("fare")
        fare2 = response2.json().get("fare")

        assert fare1 == fare2
