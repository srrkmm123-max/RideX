"""
RideX API Gateway

Entry point for:
    Passenger App
    Driver App
    Admin Dashboard

Routes requests to:
    User Service
    Driver Service
    Ride Service
    Matching Service
    Pricing Service
    Payment Service
    Notification Service
    Rating & Safety Service
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import time


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="RideX API Gateway",
    description="API Gateway for RideX ride-hailing platform",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# SERVICE CONFIGURATION
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
# APPLICATION START TIME
# ============================================================

START_TIME = time.time()


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
async def root():

    return {
        "service": "RideX API Gateway",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():

    return {
        "service": "api-gateway",
        "status": "healthy",
        "uptime_seconds": round(
            time.time() - START_TIME,
            2
        )
    }


# ============================================================
# SERVICE HEALTH
# ============================================================

@app.get("/health/services")
async def service_health():

    results = {}

    async with httpx.AsyncClient(
        timeout=3.0
    ) as client:

        for service, url in SERVICES.items():

            try:

                response = await client.get(
                    f"{url}/health"
                )

                results[service] = {
                    "status": "healthy",
                    "http_status": response.status_code,
                    "url": url
                }

            except Exception as error:

                results[service] = {
                    "status": "unavailable",
                    "url": url,
                    "error": str(error)
                }

    return {
        "gateway": "healthy",
        "services": results
    }


# ============================================================
# GENERIC SERVICE FORWARDER
# ============================================================

async def forward_request(
    service_name: str,
    request: Request,
    path: str
):

    if service_name not in SERVICES:

        return JSONResponse(
            status_code=404,
            content={
                "error": "Unknown service",
                "service": service_name
            }
        )

    service_url = SERVICES[service_name]

    target_url = (
        f"{service_url}/{path}"
    )

    # --------------------------------------------------------
    # Request body
    # --------------------------------------------------------

    body = await request.body()

    # --------------------------------------------------------
    # Forward headers
    # --------------------------------------------------------

    headers = {}

    ignored_headers = {
        "host",
        "content-length",
        "connection"
    }

    for key, value in request.headers.items():

        if key.lower() not in ignored_headers:
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

        response_headers = {}

        for key, value in response.headers.items():

            if key.lower() not in {
                "content-length",
                "transfer-encoding",
                "connection"
            }:
                response_headers[key] = value

        return JSONResponse(
            status_code=response.status_code,
            content=(
                response.json()
                if response.content
                else {}
            ),
            headers=response_headers
        )

    except httpx.ConnectError:

        return JSONResponse(
            status_code=503,
            content={
                "error": "Service unavailable",
                "service": service_name,
                "target": target_url
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
                "service": service_name,
                "message": str(error)
            }
        )


# ============================================================
# USER SERVICE
# ============================================================

@app.api_route(
    "/api/v1/users/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def user_service(
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

@app.api_route(
    "/api/v1/drivers/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def driver_service(
    request: Request,
    path: str
):

    return await forward_request(
        "driver",
        request,
        f"api/v1/drivers/{path}"
    )


# ============================================================
# RIDE SERVICE
# ============================================================

@app.api_route(
    "/api/v1/rides/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def ride_service(
    request: Request,
    path: str
):

    return await forward_request(
        "ride",
        request,
        f"api/v1/rides/{path}"
    )


# ============================================================
# MATCHING SERVICE
# ============================================================

@app.api_route(
    "/api/v1/matching/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def matching_service(
    request: Request,
    path: str
):

    return await forward_request(
        "matching",
        request,
        f"api/v1/matching/{path}"
    )


# ============================================================
# PRICING SERVICE
# ============================================================

@app.api_route(
    "/api/v1/pricing/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def pricing_service(
    request: Request,
    path: str
):

    return await forward_request(
        "pricing",
        request,
        f"api/v1/pricing/{path}"
    )


# ============================================================
# PAYMENT SERVICE
# ============================================================

@app.api_route(
    "/api/v1/payments/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def payment_service(
    request: Request,
    path: str
):

    return await forward_request(
        "payment",
        request,
        f"api/v1/payments/{path}"
    )


# ============================================================
# NOTIFICATION SERVICE
# ============================================================

@app.api_route(
    "/api/v1/notifications/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def notification_service(
    request: Request,
    path: str
):

    return await forward_request(
        "notification",
        request,
        f"api/v1/notifications/{path}"
    )


# ============================================================
# RATING & SAFETY SERVICE
# ============================================================

@app.api_route(
    "/api/v1/ratings/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def rating_service(
    request: Request,
    path: str
):

    return await forward_request(
        "rating",
        request,
        f"api/v1/ratings/{path}"
    )


# ============================================================
# ADMIN ROUTES
# ============================================================

@app.api_route(
    "/api/v1/admin/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
)
async def admin_service(
    request: Request,
    path: str
):

    # Admin APIs are distributed to
    # appropriate backend services.

    if path.startswith("users"):
        service = "user"

    elif path.startswith("drivers"):
        service = "driver"

    elif path.startswith("rides"):
        service = "ride"

    elif path.startswith("payments"):
        service = "payment"

    elif path.startswith("reports"):
        service = "ride"

    else:
        return JSONResponse(
            status_code=404,
            content={
                "error": "Unknown admin endpoint",
                "path": path
            }
        )

    return await forward_request(
        service,
        request,
        f"api/v1/admin/{path}"
    )


# ============================================================
# LOGIN
# ============================================================

@app.post("/api/v1/auth/login")
async def login(request: Request):

    return await forward_request(
        "user",
        request,
        "api/v1/auth/login"
    )


# ============================================================
# REGISTER PASSENGER
# ============================================================

@app.post("/api/v1/auth/register")
async def register(request: Request):

    return await forward_request(
        "user",
        request,
        "api/v1/auth/register"
    )


# ============================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):

    print(
        f"Gateway exception: {exc}"
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal gateway error"
        }
    )


# ============================================================
# LOCAL DEVELOPMENT
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
