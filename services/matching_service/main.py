"""
RideX Matching Service

Responsibilities:
    - Find nearby available drivers
    - Match drivers with ride requests
    - Check service/database health
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
    "matching-service"
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
        "8004"
    )
)

START_TIME = time.time()


# ============================================================
# STARTUP / SHUTDOWN
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

    if check_database():

        print(
            "Database connection: OK"
        )

    else:

        print(
            "WARNING: Database connection failed"
        )

    print(
        f"{SERVICE_NAME} started"
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
    title="RideX Matching Service",

    description=(
        "Matches passenger ride requests "
        "with nearby available drivers."
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
# ROUTES
# ============================================================

app.include_router(
    router,
    prefix="/api/v1/matching",
    tags=["Matching"]
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

    database_status = check_database()

    uptime = (
        time.time() - START_TIME
    )

    return {
        "service": SERVICE_NAME,

        "status": (
            "healthy"
            if database_status
            else "degraded"
        ),

        "version": SERVICE_VERSION,

        "environment": ENVIRONMENT,

        "database": (
            "healthy"
            if database_status
            else "unhealthy"
        ),

        "uptime_seconds": round(
            uptime,
            2
        )
    }


# ============================================================
# READINESS
# ============================================================

@app.get(
    "/ready",
    tags=["System"]
)
async def ready():

    database_status = check_database()

    if not database_status:

        return {
            "service": SERVICE_NAME,
            "status": "not_ready"
        }

    return {
        "service": SERVICE_NAME,
        "status": "ready"
    }


# ============================================================
# LIVENESS
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
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",

        host=HOST,

        port=PORT,

        reload=(
            ENVIRONMENT == "development"
        )
    )
