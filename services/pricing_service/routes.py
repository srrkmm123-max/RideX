from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .fare_engine import calculate_fare
from .pricing_rules import (
    get_vehicle_pricing,
    get_peak_multiplier,
    calculate_waiting_fee,
)
from .surge import calculate_surge_multiplier

router = APIRouter()


class FareRequest(BaseModel):
    distance_km: float
    duration_minutes: float
    vehicle_type: str = "standard"
    surge_multiplier: float = 1.0
    discount: float = 0.0


class SurgeRequest(BaseModel):
    demand: int
    available_drivers: int


class PeakRequest(BaseModel):
    hour: int
    minute: int = 0
    day: str


class WaitingRequest(BaseModel):
    vehicle_type: str = "standard"
    waiting_minutes: int = 0


@router.get("/status")
async def status():
    return {
        "service": "pricing-service",
        "status": "running"
    }


@router.post("/fare")
async def fare(request: FareRequest):
    try:
        result = calculate_fare(
            distance_km=request.distance_km,
            duration_minutes=request.duration_minutes,
            vehicle_type=request.vehicle_type,
            surge_multiplier=request.surge_multiplier,
            discount=request.discount,
        )

        return {
            "success": True,
            "result": getattr(result, "__dict__", result),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@router.post("/surge")
async def surge(request: SurgeRequest):
    try:
        multiplier = calculate_surge_multiplier(
            demand=request.demand,
            available_drivers=request.available_drivers,
        )

        return {
            "success": True,
            "surge_multiplier": multiplier,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@router.post("/peak-multiplier")
async def peak_multiplier(request: PeakRequest):
    try:
        multiplier = get_peak_multiplier(
            request.hour,
            request.minute,
            request.day,
        )

        return {
            "success": True,
            "peak_multiplier": multiplier,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@router.post("/waiting-fee")
async def waiting_fee(request: WaitingRequest):
    try:
        fee = calculate_waiting_fee(
            request.vehicle_type,
            request.waiting_minutes,
        )

        return {
            "success": True,
            "waiting_fee": fee,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@router.get("/vehicle/{vehicle_type}")
async def vehicle_pricing(vehicle_type: str):
    try:
        result = get_vehicle_pricing(vehicle_type)

        return {
            "success": True,
            "pricing": getattr(result, "__dict__", result),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )
