"""
RideX Microservice API Schemas

Pydantic models used for:

    - Request validation
    - Response serialization
    - API contracts
    - Data validation
"""

from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


# ============================================================
# BASE SCHEMA
# ============================================================

class RideXBaseSchema(BaseModel):
    """
    Base schema shared by RideX API models.
    """

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# HEALTH RESPONSE
# ============================================================

class HealthResponse(RideXBaseSchema):

    service: str

    status: str

    version: str

    environment: str

    uptime_seconds: float | None = None


# ============================================================
# GENERIC API RESPONSE
# ============================================================

class APIResponse(RideXBaseSchema):

    success: bool = True

    message: str

    data: Any | None = None


# ============================================================
# ERROR RESPONSE
# ============================================================

class ErrorResponse(RideXBaseSchema):

    success: bool = False

    error: str

    message: str | None = None

    details: Any | None = None


# ============================================================
# ID RESPONSE
# ============================================================

class IDResponse(RideXBaseSchema):

    id: int


# ============================================================
# PAGINATION
# ============================================================

class Pagination(RideXBaseSchema):

    page: int = Field(
        default=1,
        ge=1
    )

    page_size: int = Field(
        default=20,
        ge=1,
        le=100
    )

    total: int = Field(
        default=0,
        ge=0
    )

    total_pages: int = Field(
        default=0,
        ge=0
    )


# ============================================================
# PAGINATED RESPONSE
# ============================================================

class PaginatedResponse(RideXBaseSchema):

    success: bool = True

    data: list[Any] = []

    pagination: Pagination


# ============================================================
# USER
# ============================================================

class UserCreate(RideXBaseSchema):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    email: str

    phone: str

    password: str = Field(
        min_length=8,
        max_length=128
    )


class UserUpdate(RideXBaseSchema):

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    email: str | None = None

    phone: str | None = None


class UserResponse(RideXBaseSchema):

    id: int

    name: str

    email: str

    phone: str

    is_active: bool

    created_at: datetime

    updated_at: datetime


# ============================================================
# LOGIN
# ============================================================

class LoginRequest(RideXBaseSchema):

    email: str

    password: str


class LoginResponse(RideXBaseSchema):

    access_token: str

    token_type: str = "bearer"

    expires_in: int | None = None

    user_id: int | None = None


# ============================================================
# DRIVER
# ============================================================

class DriverCreate(RideXBaseSchema):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    phone: str

    email: str | None = None

    license_number: str

    vehicle_id: int | None = None


class DriverUpdate(RideXBaseSchema):

    name: str | None = None

    phone: str | None = None

    email: str | None = None

    license_number: str | None = None


class DriverResponse(RideXBaseSchema):

    id: int

    name: str

    phone: str

    email: str | None = None

    license_number: str

    is_active: bool

    created_at: datetime

    updated_at: datetime


# ============================================================
# DRIVER STATUS
# ============================================================

class DriverStatusUpdate(RideXBaseSchema):

    online: bool

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180
    )


class DriverStatusResponse(RideXBaseSchema):

    driver_id: int

    online: bool

    latitude: float | None = None

    longitude: float | None = None

    updated_at: datetime | None = None


# ============================================================
# LOCATION
# ============================================================

class Location(RideXBaseSchema):

    latitude: float = Field(
        ge=-90,
        le=90
    )

    longitude: float = Field(
        ge=-180,
        le=180
    )

    address: str | None = None


# ============================================================
# RIDE CREATE
# ============================================================

class RideCreate(RideXBaseSchema):

    passenger_id: int

    pickup: Location

    destination: Location

    vehicle_type: str = Field(
        default="standard",
        max_length=50
    )


# ============================================================
# RIDE UPDATE
# ============================================================

class RideUpdate(RideXBaseSchema):

    status: str | None = None

    driver_id: int | None = None


# ============================================================
# RIDE RESPONSE
# ============================================================

class RideResponse(RideXBaseSchema):

    id: int

    passenger_id: int

    driver_id: int | None = None

    pickup: Location

    destination: Location

    vehicle_type: str

    status: str

    estimated_fare: float | None = None

    final_fare: float | None = None

    created_at: datetime

    updated_at: datetime


# ============================================================
# FARE ESTIMATE
# ============================================================

class FareEstimateRequest(RideXBaseSchema):

    pickup: Location

    destination: Location

    vehicle_type: str = "standard"


class FareEstimateResponse(RideXBaseSchema):

    estimated_fare: float

    currency: str = "INR"

    distance_km: float

    estimated_duration_minutes: int


# ============================================================
# MATCHING
# ============================================================

class MatchingRequest(RideXBaseSchema):

    ride_id: int

    pickup: Location

    vehicle_type: str = "standard"

    max_distance_km: float = Field(
        default=5.0,
        gt=0,
        le=50
    )


class MatchingResponse(RideXBaseSchema):

    ride_id: int

    driver_id: int | None = None

    distance_km: float | None = None

    matched: bool


# ============================================================
# PAYMENT
# ============================================================

class PaymentCreate(RideXBaseSchema):

    ride_id: int

    passenger_id: int

    amount: float = Field(
        gt=0
    )

    currency: str = "INR"

    payment_method: str


class PaymentResponse(RideXBaseSchema):

    id: int

    ride_id: int

    passenger_id: int

    amount: float

    currency: str

    payment_method: str

    status: str

    transaction_id: str | None = None

    created_at: datetime


# ============================================================
# NOTIFICATION
# ============================================================

class NotificationCreate(RideXBaseSchema):

    user_id: int

    title: str = Field(
        min_length=1,
        max_length=200
    )

    message: str = Field(
        min_length=1,
        max_length=2000
    )

    notification_type: str = "push"


class NotificationResponse(RideXBaseSchema):

    id: int

    user_id: int

    title: str

    message: str

    notification_type: str

    status: str

    created_at: datetime


# ============================================================
# RATING
# ============================================================

class RatingCreate(RideXBaseSchema):

    ride_id: int

    passenger_id: int

    driver_id: int

    rating: int = Field(
        ge=1,
        le=5
    )

    comment: str | None = Field(
        default=None,
        max_length=1000
    )


class RatingResponse(RideXBaseSchema):

    id: int

    ride_id: int

    passenger_id: int

    driver_id: int

    rating: int

    comment: str | None = None

    created_at: datetime


# ============================================================
# SAFETY INCIDENT
# ============================================================

class SafetyIncidentCreate(RideXBaseSchema):

    ride_id: int

    user_id: int

    incident_type: str

    description: str = Field(
        min_length=1,
        max_length=5000
    )

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180
    )


class SafetyIncidentResponse(RideXBaseSchema):

    id: int

    ride_id: int

    user_id: int

    incident_type: str

    description: str

    status: str

    created_at: datetime


# ============================================================
# EXPORTS
# ============================================================

__all__ = [

    # Base
    "RideXBaseSchema",

    # Generic
    "APIResponse",
    "ErrorResponse",
    "IDResponse",

    # Health
    "HealthResponse",

    # Pagination
    "Pagination",
    "PaginatedResponse",

    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",

    # Authentication
    "LoginRequest",
    "LoginResponse",

    # Driver
    "DriverCreate",
    "DriverUpdate",
    "DriverResponse",

    # Driver Status
    "DriverStatusUpdate",
    "DriverStatusResponse",

    # Location
    "Location",

    # Ride
    "RideCreate",
    "RideUpdate",
    "RideResponse",

    # Pricing
    "FareEstimateRequest",
    "FareEstimateResponse",

    # Matching
    "MatchingRequest",
    "MatchingResponse",

    # Payment
    "PaymentCreate",
    "PaymentResponse",

    # Notification
    "NotificationCreate",
    "NotificationResponse",

    # Rating
    "RatingCreate",
    "RatingResponse",

    # Safety
    "SafetyIncidentCreate",
    "SafetyIncidentResponse"
]
