"""
RideX Microservice Routes

Common REST API routes for a RideX microservice.

Actual business logic should remain in service.py.
Database models should remain in models.py.
Request/response schemas should remain in schemas.py.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from schemas import (
    APIResponse,
    DeleteResponse,
    HealthResponse,
    IDResponse,
    PaginatedResponse,
    PaginationRequest,
    StatusResponse,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter()


# ============================================================
# SERVICE INFORMATION
# ============================================================

SERVICE_NAME = "ridex-service"
SERVICE_VERSION = "1.0.0"


# ============================================================
# ROOT / SERVICE STATUS
# ============================================================

@router.get(
    "/",
    response_model=APIResponse[StatusResponse]
)
async def service_root():
    """
    Basic service information.
    """

    return APIResponse(
        message=f"{SERVICE_NAME} is running",
        data=StatusResponse(
            status="running",
            message=f"{SERVICE_NAME} version {SERVICE_VERSION}"
        )
    )


# ============================================================
# HEALTH
# ============================================================

@router.get(
    "/health",
    response_model=HealthResponse
)
async def health_check():
    """
    Health check used by API Gateway,
    Docker and Kubernetes.
    """

    return HealthResponse(
        service=SERVICE_NAME,
        status="healthy",
        version=SERVICE_VERSION,
        environment="development"
    )


# ============================================================
# READINESS
# ============================================================

@router.get(
    "/ready",
    response_model=StatusResponse
)
async def readiness_check():
    """
    Indicates whether the service is ready
    to receive traffic.
    """

    return StatusResponse(
        status="ready",
        message="Service is ready"
    )


# ============================================================
# LIVENESS
# ============================================================

@router.get(
    "/live",
    response_model=StatusResponse
)
async def liveness_check():
    """
    Kubernetes liveness check.
    """

    return StatusResponse(
        status="alive",
        message="Service is alive"
    )


# ============================================================
# SERVICE INFO
# ============================================================

@router.get(
    "/info",
    response_model=APIResponse[dict]
)
async def service_info():
    """
    Return service metadata.
    """

    return APIResponse(
        message="Service information",
        data={
            "service": SERVICE_NAME,
            "version": SERVICE_VERSION,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat()
        }
    )


# ============================================================
# EXAMPLE GET RESOURCE
# ============================================================

@router.get(
    "/resources/{resource_id}",
    response_model=APIResponse[dict]
)
async def get_resource(
    resource_id: int
):
    """
    Example GET resource endpoint.

    Replace this with actual service-specific
    implementation.
    """

    if resource_id <= 0:

        raise HTTPException(
            status_code=400,
            detail="Invalid resource ID"
        )

    return APIResponse(
        message="Resource retrieved",
        data={
            "id": resource_id,
            "service": SERVICE_NAME
        }
    )


# ============================================================
# EXAMPLE CREATE RESOURCE
# ============================================================

@router.post(
    "/resources",
    response_model=APIResponse[IDResponse]
)
async def create_resource():
    """
    Example CREATE endpoint.

    Actual implementation should call service.py.
    """

    # Replace this with database/service logic.
    new_id = 1

    return APIResponse(
        message="Resource created",
        data=IDResponse(
            id=new_id
        )
    )


# ============================================================
# EXAMPLE UPDATE RESOURCE
# ============================================================

@router.put(
    "/resources/{resource_id}",
    response_model=APIResponse[IDResponse]
)
async def update_resource(
    resource_id: int
):
    """
    Example UPDATE endpoint.
    """

    if resource_id <= 0:

        raise HTTPException(
            status_code=400,
            detail="Invalid resource ID"
        )

    return APIResponse(
        message="Resource updated",
        data=IDResponse(
            id=resource_id
        )
    )


# ============================================================
# EXAMPLE DELETE RESOURCE
# ============================================================

@router.delete(
    "/resources/{resource_id}",
    response_model=DeleteResponse
)
async def delete_resource(
    resource_id: int
):
    """
    Example DELETE endpoint.
    """

    if resource_id <= 0:

        raise HTTPException(
            status_code=400,
            detail="Invalid resource ID"
        )

    return DeleteResponse(
        id=resource_id
    )


# ============================================================
# EXAMPLE PAGINATION
# ============================================================

@router.get(
    "/resources",
    response_model=PaginatedResponse
)
async def list_resources(
    page: int = Query(
        default=1,
        ge=1
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100
    )
):
    """
    Example paginated resource endpoint.
    """

    pagination = PaginationRequest(
        page=page,
        page_size=page_size
    )

    # Replace with database query.
    resources = []

    return PaginatedResponse(
        data=resources,
        pagination={
            "page": pagination.page,
            "page_size": pagination.page_size,
            "total": 0,
            "total_pages": 0
        }
    )
