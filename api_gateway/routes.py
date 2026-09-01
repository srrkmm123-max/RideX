"""
RideX API Gateway Routes

Routes:
    /api/v1/auth
    /api/v1/users
    /api/v1/drivers
    /api/v1/rides
    /api/v1/matching
    /api/v1/pricing
    /api/v1/payments
    /api/v1/notifications
    /api/v1/ratings
    /api/v1/admin
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import httpx
import os


# ============================================================
# ROUTER
# ============================================================

router = APIRouter()


# ============================================================
# SERVICE URLS
# ============================================================

SERVICES = {
    "user": os.getenv(
        "USER_SERVICE_URL",
        "http://localhost:8001"
    ),

    "driver": os.getenv(
        "DRIVER_SERVICE_URL",
        "http://localhost:8002"
    ),

    "ride": os.getenv(
        "RIDE_SERVICE_URL",
        "http://localhost:8003"
    ),

    "matching": os.getenv(
        "MATCHING_SERVICE_URL",
        "http://localhost:8004"
    ),

    "pricing": os.getenv(
        "PRICING_SERVICE_URL",
        "http://localhost:8005"
    ),

    "payment": os.getenv(
        "PAYMENT_SERVICE_URL",
        "http://localhost:8006"
    ),

    "notification": os.getenv(
        "NOTIFICATION_SERVICE_URL",
        "http://localhost:8007"
    ),

    "rating": os.getenv(
        "RATING_SERVICE_URL",
        "http://localhost:8008"
    )
}


# ============================================================
# FORWARD REQUEST
# ============================================================

async def forward_request(
    service_name: str,
    request: Request,
    service_path: str
):

    service_url = SERVICES.get(service_name)

    if not service_url:

        return JSONResponse(
            status_code=404,
            content={
                "error": "Service not configured",
                "service": service_name
            }
        )

    target_url = (
        f"{service_url}/{service_path}"
    )

    # --------------------------------------------------------
    # Read request body
    # --------------------------------------------------------

    body = await request.body()

    # --------------------------------------------------------
    # Copy request headers
    # --------------------------------------------------------

    headers = {}

    for key, value in request.headers.items():

        if key.lower() not in {
            "host",
            "content-length",
            "connection"
        }:

            headers[key] = value

    # --------------------------------------------------------
    # Forward request
    # --------------------------------------------------------

    try:

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.request(
                method=request.method,
                url=target_url,
                params=dict(request.query_params),
                content=body,
                headers=headers
            )

        # ----------------------------------------------------
        # Response headers
        # ----------------------------------------------------

        response_headers = {}

        for key, value in response.headers.items():

            if key.lower() not in {
                "content-length",
                "transfer-encoding",
                "connection"
            }:

                response_headers[key] = value

        # ----------------------------------------------------
        # Response body
        # ----------------------------------------------------

        try:
            content = response.json()

        except Exception:
            content = {
                "data": response.text
            }

        return JSONResponse(
            status_code=response.status_code,
            content=content,
            headers=response_headers
        )

    except httpx.ConnectError:

        return JSONResponse(
            status_code=503,
            content={
                "error": "Service unavailable",
                "service": service_name
            }
        )

    except httpx.TimeoutException:

        return JSONResponse(
            status_code=504,
            content={
                "error": "Service timeout",
                "service": service_name
            }
        )

    except Exception as error:

        return JSONResponse(
            status_code=500,
            content={
                "error": "Gateway error",
                "message": str(error)
            }
        )


# ============================================================
# AUTH
# ============================================================

@router.post("/api/v1/auth/login")
async def login(request: Request):

    return await forward_request(
        "user",
        request,
        "api/v1/auth/login"
    )


@router.post("/api/v1/auth/register")
async def register(request: Request):

    return await forward_request(
        "user",
        request,
        "api/v1/auth/register"
    )


@router.post("/api/v1/auth/refresh")
async def refresh_token(request: Request):

    return await forward_request(
        "user",
        request,
        "api/v1/auth/refresh"
    )


# ============================================================
# USER SERVICE
# ============================================================

@router.api_route(
    "/api/v1/users/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def users(
    request: Request,
    path: str
):

    return await forward_request(
        "user",
        request,
        f"api/v1/users/{path}"
    )


# ============================================================
# DRIVER SERVICE
# ============================================================

@router.api_route(
    "/api/v1/drivers/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def drivers(
    request: Request,
    path: str
):

    return await forward_request(
        "driver",
        request,
        f"api/v1/drivers/{path}"
    )


# ============================================================
# DRIVER ONLINE/OFFLINE
# ============================================================

@router.post(
    "/api/v1/drivers/{driver_id}/online"
)
async def driver_online(
    driver_id: int,
    request: Request
):

    return await forward_request(
        "driver",
        request,
        f"api/v1/drivers/{driver_id}/online"
    )


@router.post(
    "/api/v1/drivers/{driver_id}/offline"
)
async def driver_offline(
    driver_id: int,
    request: Request
):

    return await forward_request(
        "driver",
        request,
        f"api/v1/drivers/{driver_id}/offline"
    )


# ============================================================
# RIDE SERVICE
# ============================================================

@router.api_route(
    "/api/v1/rides/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def rides(
    request: Request,
    path: str
):

    return await forward_request(
        "ride",
        request,
        f"api/v1/rides/{path}"
    )


# ============================================================
# CREATE RIDE
# ============================================================

@router.post("/api/v1/rides")
async def create_ride(
    request: Request
):

    return await forward_request(
        "ride",
        request,
        "api/v1/rides"
    )


# ============================================================
# RIDE STATUS
# ============================================================

@router.get(
    "/api/v1/rides/{ride_id}/status"
)
async def ride_status(
    ride_id: int,
    request: Request
):

    return await forward_request(
        "ride",
        request,
        f"api/v1/rides/{ride_id}/status"
    )


# ============================================================
# CANCEL RIDE
# ============================================================

@router.post(
    "/api/v1/rides/{ride_id}/cancel"
)
async def cancel_ride(
    ride_id: int,
    request: Request
):

    return await forward_request(
        "ride",
        request,
        f"api/v1/rides/{ride_id}/cancel"
    )


# ============================================================
# MATCHING SERVICE
# ============================================================

@router.api_route(
    "/api/v1/matching/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def matching(
    request: Request,
    path: str
):

    return await forward_request(
        "matching",
        request,
        f"api/v1/matching/{path}"
    )


# ============================================================
# FIND DRIVER
# ============================================================

@router.post(
    "/api/v1/matching/find-driver"
)
async def find_driver(
    request: Request
):

    return await forward_request(
        "matching",
        request,
        "api/v1/matching/find-driver"
    )


# ============================================================
# PRICING SERVICE
# ============================================================

@router.api_route(
    "/api/v1/pricing/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def pricing(
    request: Request,
    path: str
):

    return await forward_request(
        "pricing",
        request,
        f"api/v1/pricing/{path}"
    )


# ============================================================
# FARE ESTIMATE
# ============================================================

@router.post(
    "/api/v1/pricing/fare-estimate"
)
async def fare_estimate(
    request: Request
):

    return await forward_request(
        "pricing",
        request,
        "api/v1/pricing/fare-estimate"
    )


# ============================================================
# PAYMENT SERVICE
# ============================================================

@router.api_route(
    "/api/v1/payments/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def payments(
    request: Request,
    path: str
):

    return await forward_request(
        "payment",
        request,
        f"api/v1/payments/{path}"
    )


# ============================================================
# CREATE PAYMENT
# ============================================================

@router.post(
    "/api/v1/payments"
)
async def create_payment(
    request: Request
):

    return await forward_request(
        "payment",
        request,
        "api/v1/payments"
    )


# ============================================================
# PAYMENT STATUS
# ============================================================

@router.get(
    "/api/v1/payments/{payment_id}/status"
)
async def payment_status(
    payment_id: int,
    request: Request
):

    return await forward_request(
        "payment",
        request,
        f"api/v1/payments/{payment_id}/status"
    )


# ============================================================
# NOTIFICATION SERVICE
# ============================================================

@router.api_route(
    "/api/v1/notifications/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def notifications(
    request: Request,
    path: str
):

    return await forward_request(
        "notification",
        request,
        f"api/v1/notifications/{path}"
    )


# ============================================================
# RATING SERVICE
# ============================================================

@router.api_route(
    "/api/v1/ratings/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def ratings(
    request: Request,
    path: str
):

    return await forward_request(
        "rating",
        request,
        f"api/v1/ratings/{path}"
    )


# ============================================================
# SUBMIT RATING
# ============================================================

@router.post(
    "/api/v1/ratings"
)
async def submit_rating(
    request: Request
):

    return await forward_request(
        "rating",
        request,
        "api/v1/ratings"
    )


# ============================================================
# ADMIN USERS
# ============================================================

@router.api_route(
    "/api/v1/admin/users/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def admin_users(
    request: Request,
    path: str
):

    return await forward_request(
        "user",
        request,
        f"api/v1/admin/users/{path}"
    )


# ============================================================
# ADMIN DRIVERS
# ============================================================

@router.api_route(
    "/api/v1/admin/drivers/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def admin_drivers(
    request: Request,
    path: str
):

    return await forward_request(
        "driver",
        request,
        f"api/v1/admin/drivers/{path}"
    )


# ============================================================
# ADMIN RIDES
# ============================================================

@router.api_route(
    "/api/v1/admin/rides/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def admin_rides(
    request: Request,
    path: str
):

    return await forward_request(
        "ride",
        request,
        f"api/v1/admin/rides/{path}"
    )


# ============================================================
# ADMIN PAYMENTS
# ============================================================

@router.api_route(
    "/api/v1/admin/payments/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def admin_payments(
    request: Request,
    path: str
):

    return await forward_request(
        "payment",
        request,
        f"api/v1/admin/payments/{path}"
    )


# ============================================================
# ADMIN REPORTS
# ============================================================

@router.api_route(
    "/api/v1/admin/reports/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def admin_reports(
    request: Request,
    path: str
):

    return await forward_request(
        "ride",
        request,
        f"api/v1/admin/reports/{path}"
    )


# ============================================================
# SIMPLE REPORT ENDPOINT
# ============================================================

@router.get(
    "/api/v1/admin/reports"
)
async def reports(
    request: Request
):

    return await forward_request(
        "ride",
        request,
        "api/v1/admin/reports"
    )
