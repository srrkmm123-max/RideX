"""
RideX Payment Service

Responsibilities:
    - Start the Payment Service
    - Register payment routes
    - Health/readiness/liveness checks
    - Configure CORS
    - Manage application lifecycle

Payment processing logic belongs in:
    payment_engine.py
    service.py
    provider integrations
"""

import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.database import check_database
from .routes import router


# ============================================================
# CONFIGURATION
# ============================================================

SERVICE_NAME = os.getenv(
    "SERVICE_NAME",
    "payment-service"
)

SERVICE_VERSION = os.getenv(
    "SERVICE_VERSION",
    "1.0.0"
)

ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    "development"
)

HOST = os.getenv(
    "HOST",
    "0.0.0.0"
)

PORT = int(
    os.getenv(
        "PORT",
        "8006"
    )
)

START_TIME = time.time()


# ============================================================
# APPLICATION LIFECYCLE
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.
    """

    print(
        f"Starting {SERVICE_NAME} "
        f"v{SERVICE_VERSION}"
    )

    print(
        f"Environment: {ENVIRONMENT}"
    )

    # --------------------------------------------------------
    # DATABASE CHECK
    # --------------------------------------------------------

    try:

        database_ok = check_database()

        if database_ok:

            print(
                "Database connection: OK"
            )

        else:

            print(
                "WARNING: Database connection failed"
            )

    except Exception as error:

        print(
            f"WARNING: Database check failed: "
            f"{error}"
        )

    print(
        f"{SERVICE_NAME} started "
        f"on port {PORT}"
    )

    yield

    # --------------------------------------------------------
    # SHUTDOWN
    # --------------------------------------------------------

    print(
        f"Stopping {SERVICE_NAME}"
    )


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(

    title="RideX Payment Service",

    description=(
        "RideX microservice responsible for "
        "payment creation, payment status, "
        "refunds and transaction management."
    ),

    version=SERVICE_VERSION,

    lifespan=lifespan
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

    allow_headers=["*"]
)


# ============================================================
# PAYMENT ROUTES
# ============================================================

app.include_router(

    router,

    prefix="/api/v1/payments",

    tags=["Payments"]
)


# ============================================================
# ROOT
# ============================================================

@app.get(
    "/",
    tags=["System"]
)
async def root():

    return {

        "service": SERVICE_NAME,

        "version": SERVICE_VERSION,

        "status": "running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get(
    "/health",
    tags=["System"]
)
async def health():

    try:

        database_ok = check_database()

    except Exception:

        database_ok = False

    uptime = (
        time.time()
        -
        START_TIME
    )

    return {

        "service": SERVICE_NAME,

        "status": (
            "healthy"
            if database_ok
            else "degraded"
        ),

        "version": SERVICE_VERSION,

        "environment": ENVIRONMENT,

        "database": (
            "healthy"
            if database_ok
            else "unhealthy"
        ),

        "uptime_seconds": round(
            uptime,
            2
        )
    }


# ============================================================
# READINESS CHECK
# ============================================================

@app.get(
    "/ready",
    tags=["System"]
)
async def ready():

    try:

        database_ok = check_database()

    except Exception:

        database_ok = False

    if not database_ok:

        return {

            "service": SERVICE_NAME,

            "status": "not_ready"
        }

    return {

        "service": SERVICE_NAME,

        "status": "ready"
    }


# ============================================================
# LIVENESS CHECK
# ============================================================

@app.get(
    "/live",
    tags=["System"]
)
async def live():

    return {

        "service": SERVICE_NAME,

        "status": "alive"
    }


# ============================================================
# VERSION
# ============================================================

@app.get(
    "/version",
    tags=["System"]
)
async def version():

    return {

        "service": SERVICE_NAME,

        "version": SERVICE_VERSION,

        "environment": ENVIRONMENT
    }


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        "main:app",

        host=HOST,

        port=PORT,

        reload=(
            ENVIRONMENT
            ==
            "development"
        )
    )
