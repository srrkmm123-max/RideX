"""
RideX API Gateway Configuration

Centralizes:
    - Application settings
    - Microservice URLs
    - CORS configuration
    - HTTP timeout
    - Environment configuration
"""

import os
from dataclasses import dataclass
from typing import List


# ============================================================
# HELPER
# ============================================================

def get_env(
    name: str,
    default: str
) -> str:
    """
    Read an environment variable.
    Return default if it is not defined.
    """

    return os.getenv(name, default)


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

@dataclass(frozen=True)
class AppConfig:

    # Application
    APP_NAME: str = get_env(
        "APP_NAME",
        "RideX API Gateway"
    )

    APP_VERSION: str = get_env(
        "APP_VERSION",
        "1.0.0"
    )

    ENVIRONMENT: str = get_env(
        "ENVIRONMENT",
        "development"
    )

    DEBUG: bool = get_env(
        "DEBUG",
        "true"
    ).lower() == "true"

    HOST: str = get_env(
        "HOST",
        "0.0.0.0"
    )

    PORT: int = int(
        get_env(
            "PORT",
            "8000"
        )
    )

    # --------------------------------------------------------
    # HTTP
    # --------------------------------------------------------

    REQUEST_TIMEOUT: float = float(
        get_env(
            "REQUEST_TIMEOUT",
            "30"
        )
    )

    CONNECT_TIMEOUT: float = float(
        get_env(
            "CONNECT_TIMEOUT",
            "5"
        )
    )

    # --------------------------------------------------------
    # CORS
    # --------------------------------------------------------

    CORS_ORIGINS: str = get_env(
        "CORS_ORIGINS",
        "http://localhost:3000,"
        "http://localhost:3001,"
        "http://localhost:3002"
    )

    # --------------------------------------------------------
    # Security
    # --------------------------------------------------------

    JWT_SECRET: str = get_env(
        "JWT_SECRET",
        "CHANGE_THIS_SECRET_IN_PRODUCTION"
    )

    JWT_ALGORITHM: str = get_env(
        "JWT_ALGORITHM",
        "HS256"
    )

    # --------------------------------------------------------
    # API
    # --------------------------------------------------------

    API_PREFIX: str = get_env(
        "API_PREFIX",
        "/api/v1"
    )


# ============================================================
# MICROSERVICE CONFIGURATION
# ============================================================

@dataclass(frozen=True)
class ServiceConfig:

    # User Service
    USER_SERVICE_URL: str = get_env(
        "USER_SERVICE_URL",
        "http://localhost:8001"
    )

    # Driver Service
    DRIVER_SERVICE_URL: str = get_env(
        "DRIVER_SERVICE_URL",
        "http://localhost:8002"
    )

    # Ride Service
    RIDE_SERVICE_URL: str = get_env(
        "RIDE_SERVICE_URL",
        "http://localhost:8003"
    )

    # Matching Service
    MATCHING_SERVICE_URL: str = get_env(
        "MATCHING_SERVICE_URL",
        "http://localhost:8004"
    )

    # Pricing Service
    PRICING_SERVICE_URL: str = get_env(
        "PRICING_SERVICE_URL",
        "http://localhost:8005"
    )

    # Payment Service
    PAYMENT_SERVICE_URL: str = get_env(
        "PAYMENT_SERVICE_URL",
        "http://localhost:8006"
    )

    # Notification Service
    NOTIFICATION_SERVICE_URL: str = get_env(
        "NOTIFICATION_SERVICE_URL",
        "http://localhost:8007"
    )

    # Rating & Safety Service
    RATING_SERVICE_URL: str = get_env(
        "RATING_SERVICE_URL",
        "http://localhost:8008"
    )


# ============================================================
# CREATE CONFIG INSTANCES
# ============================================================

app_config = AppConfig()

service_config = ServiceConfig()


# ============================================================
# SERVICE MAP
# ============================================================

SERVICES = {

    "user": service_config.USER_SERVICE_URL,

    "driver": service_config.DRIVER_SERVICE_URL,

    "ride": service_config.RIDE_SERVICE_URL,

    "matching": service_config.MATCHING_SERVICE_URL,

    "pricing": service_config.PRICING_SERVICE_URL,

    "payment": service_config.PAYMENT_SERVICE_URL,

    "notification":
        service_config.NOTIFICATION_SERVICE_URL,

    "rating":
        service_config.RATING_SERVICE_URL
}


# ============================================================
# CORS ORIGINS
# ============================================================

def get_cors_origins() -> List[str]:
    """
    Convert comma-separated CORS origins
    into a Python list.
    """

    return [
        origin.strip()
        for origin
        in app_config.CORS_ORIGINS.split(",")
        if origin.strip()
    ]


CORS_ORIGINS = get_cors_origins()


# ============================================================
# CONFIGURATION DISPLAY
# ============================================================

def get_public_config() -> dict:
    """
    Return non-sensitive configuration.

    Never expose JWT_SECRET.
    """

    return {

        "app_name":
            app_config.APP_NAME,

        "version":
            app_config.APP_VERSION,

        "environment":
            app_config.ENVIRONMENT,

        "debug":
            app_config.DEBUG,

        "host":
            app_config.HOST,

        "port":
            app_config.PORT,

        "api_prefix":
            app_config.API_PREFIX,

        "request_timeout":
            app_config.REQUEST_TIMEOUT,

        "services":
            SERVICES
    }
