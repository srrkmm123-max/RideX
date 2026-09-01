from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .driver_search import DriverLocation, find_nearby_drivers
from .matching_engine import DriverCandidate, find_best_driver

router = APIRouter()


class DriverLocationRequest(BaseModel):
    driver_id: int
    latitude: float
    longitude: float
    vehicle_type: str = "standard"
    rating: float = 5.0
    acceptance_rate: float = 1.0
    cancellation_rate: float = 0.0


class NearbyDriversRequest(BaseModel):
    pickup_latitude: float
    pickup_longitude: float
    drivers: list[DriverLocationRequest] = Field(default_factory=list)
    radius_km: float = 5.0
    vehicle_type: str | None = None
    limit: int = 20


class MatchDriverRequest(BaseModel):
    pickup_latitude: float
    pickup_longitude: float
    drivers: list[DriverLocationRequest] = Field(default_factory=list)
    requested_vehicle_type: str = "standard"
    max_distance_km: float = 10.0


@router.get("/status")
async def status():
    return {
        "service": "matching-service",
        "status": "running"
    }


@router.post("/nearby-drivers")
async def nearby_drivers(request: NearbyDriversRequest):
    try:
        drivers = [
            DriverLocation(
                driver_id=d.driver_id,
                latitude=d.latitude,
                longitude=d.longitude,
                vehicle_type=d.vehicle_type,
            )
            for d in request.drivers
        ]

        result = find_nearby_drivers(
            pickup_latitude=request.pickup_latitude,
            pickup_longitude=request.pickup_longitude,
            drivers=drivers,
            radius_km=request.radius_km,
            vehicle_type=request.vehicle_type,
            limit=request.limit,
        )

        return {
            "success": True,
            "count": len(result),
            "drivers": [
                getattr(item, "__dict__", item)
                for item in result
            ],
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@router.post("/best-driver")
async def best_driver(request: MatchDriverRequest):
    try:
        drivers = [
            DriverCandidate(
                driver_id=d.driver_id,
                latitude=d.latitude,
                longitude=d.longitude,
                vehicle_type=d.vehicle_type,
                rating=d.rating,
                acceptance_rate=d.acceptance_rate,
                cancellation_rate=d.cancellation_rate,
            )
            for d in request.drivers
        ]

        result = find_best_driver(
            pickup_latitude=request.pickup_latitude,
            pickup_longitude=request.pickup_longitude,
            drivers=drivers,
            requested_vehicle_type=request.requested_vehicle_type,
            max_distance_km=request.max_distance_km,
        )

        return {
            "success": result is not None,
            "match": getattr(result, "__dict__", result)
            if result else None,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )
