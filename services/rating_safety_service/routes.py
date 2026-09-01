from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .rating import create_rating
from .safety import create_safety_incident, create_emergency_incident
from .sos import activate_sos

router = APIRouter()


class RatingRequest(BaseModel):
    ride_id: str
    from_user_id: str
    to_user_id: str
    rating_type: str
    stars: int
    review: str | None = None
    tags: list[str] | None = None


class SafetyRequest(BaseModel):
    ride_id: str
    reporter_id: str
    reporter_type: str
    incident_type: str
    description: str
    severity: str | None = None
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    target_user_id: str | None = None
    vehicle_number: str | None = None
    evidence: list[dict] | None = None
    emergency: bool = False


class EmergencyRequest(BaseModel):
    ride_id: str
    reporter_id: str
    reporter_type: str
    latitude: float | None = None
    longitude: float | None = None
    description: str = "Emergency SOS activated"
    vehicle_number: str | None = None


class SOSRequest(BaseModel):
    ride_id: str
    user_id: str
    reporter_type: str
    latitude: float
    longitude: float
    reason: str = "Emergency SOS activated"
    driver_id: str | None = None
    vehicle_number: str | None = None
    emergency_contacts: list[str] | None = None


@router.get("/status")
async def status():
    return {
        "service": "rating-safety-service",
        "status": "running"
    }


@router.post("/ratings")
async def rating(request: RatingRequest):
    try:
        result = create_rating(**request.model_dump())

        return {
            "success": True,
            "result": getattr(result, "__dict__", result),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@router.post("/safety/incidents")
async def safety_incident(request: SafetyRequest):
    try:
        result = create_safety_incident(**request.model_dump())

        return {
            "success": True,
            "result": getattr(result, "__dict__", result),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@router.post("/safety/emergency")
async def emergency(request: EmergencyRequest):
    try:
        result = create_emergency_incident(**request.model_dump())

        return {
            "success": True,
            "result": getattr(result, "__dict__", result),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@router.post("/sos")
async def sos(request: SOSRequest):
    try:
        result = activate_sos(**request.model_dump())

        return {
            "success": True,
            "result": getattr(result, "__dict__", result),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )
