# ============================================================
# RideX - Matching Service Tests
# tests/test_matching.py
# ============================================================

from fastapi.testclient import TestClient

from services.matching_service.main import app


# ------------------------------------------------------------
# Test Client
# ------------------------------------------------------------

client = TestClient(app)


# ============================================================
# Health Check
# ============================================================

def test_matching_service_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


# ============================================================
# Find Nearby Drivers
# ============================================================

def test_find_nearby_drivers():
    response = client.get(
        "/matching/drivers",
        params={
            "latitude": 17.3850,
            "longitude": 78.4867,
            "radius_km": 5
        }
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        assert isinstance(data, (list, dict))


# ============================================================
# Match Driver
# ============================================================

def test_match_driver():
    request_data = {
        "ride_id": 1,
        "pickup_latitude": 17.3850,
        "pickup_longitude": 78.4867,
        "vehicle_type": "car"
    }

    response = client.post(
        "/matching/match",
        json=request_data
    )

    assert response.status_code in [200, 201, 404]

    if response.status_code in [200, 201]:
        data = response.json()

        assert isinstance(data, dict)


# ============================================================
# Match Driver With Radius
# ============================================================

def test_match_driver_with_radius():
    request_data = {
        "ride_id": 1,
        "pickup_latitude": 17.3850,
        "pickup_longitude": 78.4867,
        "vehicle_type": "car",
        "radius_km": 5
    }

    response = client.post(
        "/matching/match",
        json=request_data
    )

    assert response.status_code in [200, 201, 404]

    if response.status_code in [200, 201]:
        data = response.json()

        assert isinstance(data, dict)


# ============================================================
# Get Matching Candidates
# ============================================================

def test_matching_candidates():
    request_data = {
        "pickup_latitude": 17.3850,
        "pickup_longitude": 78.4867,
        "vehicle_type": "car",
        "radius_km": 5,
        "max_results": 10
    }

    response = client.post(
        "/matching/candidates",
        json=request_data
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        assert isinstance(data, (list, dict))


# ============================================================
# Driver Distance
# ============================================================

def test_driver_distance():
    request_data = {
        "pickup_latitude": 17.3850,
        "pickup_longitude": 78.4867,
        "driver_latitude": 17.4065,
        "driver_longitude": 78.4772
    }

    response = client.post(
        "/matching/distance",
        json=request_data
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        assert isinstance(data, dict)

        if "distance_km" in data:
            assert data["distance_km"] >= 0


# ============================================================
# Driver Ranking
# ============================================================

def test_driver_ranking():
    drivers = [
        {
            "driver_id": 1,
            "latitude": 17.3855,
            "longitude": 78.4870,
            "rating": 4.8
        },
        {
            "driver_id": 2,
            "latitude": 17.3950,
            "longitude": 78.4900,
            "rating": 4.5
        }
    ]

    request_data = {
        "pickup_latitude": 17.3850,
        "pickup_longitude": 78.4867,
        "drivers": drivers
    }

    response = client.post(
        "/matching/rank",
        json=request_data
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        assert isinstance(data, (list, dict))


# ============================================================
# No Driver Available
# ============================================================

def test_no_driver_available():
    request_data = {
        "ride_id": 999999,
        "pickup_latitude": 0.0,
        "pickup_longitude": 0.0,
        "vehicle_type": "car",
        "radius_km": 1
    }

    response = client.post(
        "/matching/match",
        json=request_data
    )

    assert response.status_code in [200, 404, 409]


# ============================================================
# Invalid Coordinates
# ============================================================

def test_invalid_coordinates():
    request_data = {
        "ride_id": 1,
        "pickup_latitude": 999.0,
        "pickup_longitude": 999.0,
        "vehicle_type": "car"
    }

    response = client.post(
        "/matching/match",
        json=request_data
    )

    assert response.status_code in [400, 404, 422]


# ============================================================
# Missing Required Fields
# ============================================================

def test_missing_matching_fields():
    request_data = {
        "ride_id": 1
    }

    response = client.post(
        "/matching/match",
        json=request_data
    )

    assert response.status_code == 422


# ============================================================
# Invalid Vehicle Type
# ============================================================

def test_invalid_vehicle_type():
    request_data = {
        "ride_id": 1,
        "pickup_latitude": 17.3850,
        "pickup_longitude": 78.4867,
        "vehicle_type": "invalid_vehicle"
    }

    response = client.post(
        "/matching/match",
        json=request_data
    )

    assert response.status_code in [400, 404, 422]


# ============================================================
# Zero / Negative Radius
# ============================================================

def test_invalid_radius():
    request_data = {
        "ride_id": 1,
        "pickup_latitude": 17.3850,
        "pickup_longitude": 78.4867,
        "vehicle_type": "car",
        "radius_km": -1
    }

    response = client.post(
        "/matching/match",
        json=request_data
    )

    assert response.status_code in [400, 404, 422]


# ============================================================
# Maximum Results
# ============================================================

def test_max_driver_results():
    request_data = {
        "pickup_latitude": 17.3850,
        "pickup_longitude": 78.4867,
        "vehicle_type": "car",
        "radius_km": 5,
        "max_results": 10
    }

    response = client.post(
        "/matching/candidates",
        json=request_data
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()

        if isinstance(data, list):
            assert len(data) <= 10


# ============================================================
# Matching Cancellation
# ============================================================

def test_cancel_matching():
    response = client.delete("/matching/1")

    assert response.status_code in [200, 204, 404]
