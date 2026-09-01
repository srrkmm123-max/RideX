"""
RideX Microservice
Pydantic API Schemas

Used for:
    - Request validation
    - Response validation
    - API serialization
    - Error responses
"""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# BASE SCHEMA
# ============================================================

class BaseSchema(BaseModel):
    """
    Base Pydantic schema for all RideX services.
    """

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# GENERIC RESPONSE
# ============================================================

T = TypeVar("T")


class APIResponse(BaseSchema, Generic[T]):
    """
    Standard successful API response.
    """

    success: bool = True

    message: str = "Request successful"

    data: T | None = None


# ============================================================
# ERROR RESPONSE
# ============================================================

class ErrorResponse(BaseSchema):
    """
    Standard API error response.
    """

    success: bool = False

    error: str

    message: str | None = None

    details: Any | None = None


# ============================================================
# HEALTH
# ============================================================

class HealthResponse(BaseSchema):

    service: str

    status: str

    version: str

    environment: str

    uptime_seconds: float | None = None


# ============================================================
# READINESS
# ============================================================

class ReadinessResponse(BaseSchema):

    service: str

    status: str


# ============================================================
# PAGINATION REQUEST
# ============================================================

class PaginationRequest(BaseSchema):

    page: int = Field(
        default=1,
        ge=1
    )

    page_size: int = Field(
        default=20,
        ge=1,
        le=100
    )


# ============================================================
# PAGINATION RESPONSE
# ============================================================

class PaginationResponse(BaseSchema):

    page: int

    page_size: int

    total: int

    total_pages: int


# ============================================================
# PAGINATED API RESPONSE
# ============================================================

class PaginatedResponse(BaseSchema):

    success: bool = True

    data: list[Any] = Field(
        default_factory=list
    )

    pagination: PaginationResponse


# ============================================================
# LOCATION
# ============================================================

class LocationSchema(BaseSchema):

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
# COMMON ID RESPONSE
# ============================================================

class IDResponse(BaseSchema):

    id: int


# ============================================================
# COMMON STATUS
# ============================================================

class StatusResponse(BaseSchema):

    status: str

    message: str | None = None


# ============================================================
# CREATED RESPONSE
# ============================================================

class CreatedResponse(BaseSchema):

    id: int

    created_at: datetime


# ============================================================
# UPDATED RESPONSE
# ============================================================

class UpdatedResponse(BaseSchema):

    id: int

    updated_at: datetime


# ============================================================
# DELETE RESPONSE
# ============================================================

class DeleteResponse(BaseSchema):

    success: bool = True

    message: str = "Resource deleted successfully"

    id: int


# ============================================================
# SERVICE ERROR
# ============================================================

class ServiceError(BaseSchema):

    service: str

    error_code: str

    message: str

    timestamp: datetime


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "BaseSchema",
    "APIResponse",
    "ErrorResponse",
    "HealthResponse",
    "ReadinessResponse",
    "PaginationRequest",
    "PaginationResponse",
    "PaginatedResponse",
    "LocationSchema",
    "IDResponse",
    "StatusResponse",
    "CreatedResponse",
    "UpdatedResponse",
    "DeleteResponse",
    "ServiceError"
]
