"""
RideX Microservice - Main Application

This file is used by every RideX backend service:

    user-service
    driver-service
    ride-service
    matching-service
    pricing-service
    payment-service
    notification-service
    rating-safety-service
"""

import os
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# SERVICE CONFIGURATION
# ============================================================

SERVICE_NAME = os.getenv(
    "SERVICE_NAME",
    "ridex-service"
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
        "8001"
    )
)


# ============================================================
# APPLICATION START TIME
# ============================================================

START_TIME = time.time()


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title=SERVICE_NAME,
    description=f"{SERVICE_NAME} for RideX",
    version=SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
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
# ROOT
# ============================================================

@app.get("/")
async def root():

    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "environment": ENVIRONMENT,
        "status": "running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():

    uptime = (
        time.time() - START_TIME
    )

    return {
        "service": SERVICE_NAME,
        "status": "healthy",
        "version": SERVICE_VERSION,
        "environment": ENVIRONMENT,
        "uptime_seconds": round(
            uptime,
            2
        )
    }


# ============================================================
# READINESS CHECK
# ============================================================

@app.get("/ready")
async def readiness():

    return {
        "service": SERVICE_NAME,
        "status": "ready"
    }


# ============================================================
# LIVENESS CHECK
# ============================================================

@app.get("/live")
async def liveness():

    return {
        "service": SERVICE_NAME,
        "status": "alive"
    }


# ============================================================
# SERVICE INFO
# ============================================================

@app.get("/info")
async def info():

    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "environment": ENVIRONMENT,
        "host": HOST,
        "port": PORT
    }


# ============================================================
# START APPLICATION
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
