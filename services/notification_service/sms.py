"""
RideX Notification Service - SMS

Responsibilities:
    - Create SMS messages
    - Validate phone numbers
    - Send SMS through a provider
    - Provide mock provider for development
    - Provide ride-related SMS helpers

IMPORTANT:
    Do not store OTPs, provider secrets, or other sensitive
    credentials in this source file.
"""

import os
import re
import uuid

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


# ============================================================
# CONFIGURATION
# ============================================================

SMS_PROVIDER = os.getenv(
    "SMS_PROVIDER",
    "mock"
)

DEFAULT_COUNTRY_CODE = os.getenv(
    "DEFAULT_COUNTRY_CODE",
    "+91"
)

APP_NAME = os.getenv(
    "APP_NAME",
    "RideX"
)


# ============================================================
# SMS STATUS
# ============================================================

class SMSStatus:

    CREATED = "created"

    SENT = "sent"

    FAILED = "failed"

    INVALID_NUMBER = "invalid_number"

    PROVIDER_ERROR = "provider_error"


# ============================================================
# SMS MESSAGE
# ============================================================

@dataclass
class SMSMessage:
    """
    Represents an SMS message.
    """

    message_id: str

    phone_number: str

    message: str

    created_at: datetime = field(
        default_factory=lambda:
        datetime.now(timezone.utc)
    )


# ============================================================
# SMS RESPONSE
# ============================================================

@dataclass
class SMSResponse:
    """
    Standard response returned by SMS providers.
    """

    success: bool

    status: str

    message_id: str

    provider: str

    provider_message_id: Optional[str] = None

    error: Optional[str] = None

    raw_response: Optional[dict] = None


# ============================================================
# PHONE NUMBER VALIDATION
# ============================================================

def normalize_phone_number(
    phone_number: str,
    default_country_code: str = DEFAULT_COUNTRY_CODE
) -> str:
    """
    Normalize a phone number.

    Examples:

        9876543210
        +919876543210
        919876543210

    Result:

        +919876543210
    """

    if not phone_number:

        raise ValueError(
            "Phone number is required"
        )

    phone_number = str(
        phone_number
    ).strip()

    # Remove spaces, hyphens and brackets.
    cleaned = re.sub(
        r"[()\s\-]",
        "",
        phone_number
    )

    # Already international format.
    if cleaned.startswith("+"):

        normalized = cleaned

    # India-style 10 digit number.
    elif (
        default_country_code == "+91"
        and len(cleaned) == 10
        and cleaned.isdigit()
    ):

        normalized = (
            default_country_code
            +
            cleaned
        )

    # Country code without '+'.
    elif (
        cleaned.isdigit()
        and cleaned.startswith("91")
        and len(cleaned) == 12
    ):

        normalized = "+" + cleaned

    else:

        raise ValueError(
            "Invalid phone number format"
        )

    # Basic E.164-style validation.
    if not re.match(
        r"^\+[1-9]\d{7,14}$",
        normalized
    ):

        raise ValueError(
            "Invalid international phone number"
        )

    return normalized


# ============================================================
# SMS MESSAGE CREATOR
# ============================================================

def create_sms(
    phone_number: str,
    message: str
) -> SMSMessage:
    """
    Create a validated SMS message.
    """

    normalized_number = (
        normalize_phone_number(
            phone_number
        )
    )

    if not message:

        raise ValueError(
            "SMS message is required"
        )

    message = str(
        message
    ).strip()

    if not message:

        raise ValueError(
            "SMS message cannot be empty"
        )

    return SMSMessage(

        message_id=(
            "SMS-"
            +
            uuid.uuid4()
            .hex[:16]
            .upper()
        ),

        phone_number=normalized_number,

        message=message
    )


# ============================================================
# SMS PROVIDER INTERFACE
# ============================================================

class SMSProvider(ABC):
    """
    Abstract SMS provider.
    """

    @abstractmethod
    def send(
        self,
        sms: SMSMessage
    ) -> SMSResponse:

        raise NotImplementedError


# ============================================================
# MOCK SMS PROVIDER
# ============================================================

class MockSMSProvider(
    SMSProvider
):
    """
    Development/testing provider.

    Does not send a real SMS.
    """

    def send(
        self,
        sms: SMSMessage
    ) -> SMSResponse:

        provider_message_id = (
            "MOCK-SMS-"
            +
            uuid.uuid4()
            .hex[:12]
            .upper()
        )

        print(
            "\n=============================="
        )

        print(
            "[MOCK SMS]"
        )

        print(
            f"To: {sms.phone_number}"
        )

        print(
            f"Message: {sms.message}"
        )

        print(
            f"Provider ID: "
            f"{provider_message_id}"
        )

        print(
            "==============================\n"
        )

        return SMSResponse(

            success=True,

            status=SMSStatus.SENT,

            message_id=sms.message_id,

            provider="mock",

            provider_message_id=(
                provider_message_id
            ),

            raw_response={
                "provider": "mock",
                "message_id":
                    provider_message_id
            }
        )


# ============================================================
# TWILIO PROVIDER
# ============================================================

class TwilioSMSProvider(
    SMSProvider
):
    """
    Twilio SMS adapter.

    Credentials must be supplied through environment
    variables or secure secret management.

    Required:

        TWILIO_ACCOUNT_SID
        TWILIO_AUTH_TOKEN
        TWILIO_FROM_NUMBER
    """

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None,
    ):

        self.account_sid = (
            account_sid
            or os.getenv(
                "TWILIO_ACCOUNT_SID"
            )
        )

        self.auth_token = (
            auth_token
            or os.getenv(
                "TWILIO_AUTH_TOKEN"
            )
        )

        self.from_number = (
            from_number
            or os.getenv(
                "TWILIO_FROM_NUMBER"
            )
        )

        if not self.account_sid:

            raise ValueError(
                "TWILIO_ACCOUNT_SID "
                "is not configured"
            )

        if not self.auth_token:

            raise ValueError(
                "TWILIO_AUTH_TOKEN "
                "is not configured"
            )

        if not self.from_number:

            raise ValueError(
                "TWILIO_FROM_NUMBER "
                "is not configured"
            )

    def send(
        self,
        sms: SMSMessage
    ) -> SMSResponse:

        # ----------------------------------------------------
        # Production implementation
        # ----------------------------------------------------
        #
        # Install and use the official Twilio SDK.
        #
        # Example flow:
        #
        #   Twilio credentials
        #          ↓
        #   Twilio SDK
        #          ↓
        #   messages.create()
        #          ↓
        #   Provider response
        #
        # Keep provider-specific code here.
        #

        raise NotImplementedError(
            "Implement using the official "
            "Twilio SDK"
        )


# ============================================================
# GENERIC SMS PROVIDER PLACEHOLDER
# ============================================================

class IndiaSMSProvider(
    SMSProvider
):
    """
    Adapter placeholder for an India-focused SMS provider.

    You can connect this later to the provider selected
    for your RideX deployment.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
    ):

        self.api_key = (
            api_key
            or os.getenv(
                "SMS_API_KEY"
            )
        )

        if not self.api_key:

            raise ValueError(
                "SMS_API_KEY is not configured"
            )

    def send(
        self,
        sms: SMSMessage
    ) -> SMSResponse:

        raise NotImplementedError(
            "Implement using the selected "
            "SMS provider's official API"
        )


# ============================================================
# PROVIDER FACTORY
# ============================================================

def get_sms_provider(
    provider_name: Optional[str] = None
) -> SMSProvider:
    """
    Return configured SMS provider.
    """

    provider_name = (
        provider_name
        or SMS_PROVIDER
    ).lower()

    if provider_name == "mock":

        return MockSMSProvider()

    if provider_name == "twilio":

        return TwilioSMSProvider()

    if provider_name in {
        "india",
        "india_sms"
    }:

        return IndiaSMSProvider()

    raise ValueError(
        f"Unsupported SMS provider: "
        f"{provider_name}"
    )


# ============================================================
# SMS SERVICE
# ============================================================

class SMSService:
    """
    High-level SMS service.
    """

    def __init__(
        self,
        provider: Optional[
            SMSProvider
        ] = None
    ):

        self.provider = (
            provider
            or get_sms_provider()
        )

    # ========================================================
    # SEND SMS
    # ========================================================

    def send(
        self,
        phone_number: str,
        message: str
    ) -> SMSResponse:
        """
        Send generic SMS.
        """

        sms = create_sms(

            phone_number=phone_number,

            message=message
        )

        return self.provider.send(
            sms
        )

    # ========================================================
    # RIDE BOOKED
    # ========================================================

    def ride_booked(
        self,
        phone_number: str,
        ride_id: str
    ) -> SMSResponse:
        """
        Notify passenger that ride is booked.
        """

        message = (
            f"{APP_NAME}: Your ride "
            f"{ride_id} has been booked."
        )

        return self.send(
            phone_number,
            message
        )

    # ========================================================
    # DRIVER ASSIGNED
    # ========================================================

    def driver_assigned(
        self,
        phone_number: str,
        driver_name: str,
        vehicle_number: str
    ) -> SMSResponse:
        """
        Notify passenger that driver is assigned.
        """

        message = (
            f"{APP_NAME}: Driver "
            f"{driver_name} is assigned. "
            f"Vehicle: {vehicle_number}."
        )

        return self.send(
            phone_number,
            message
        )

    # ========================================================
    # DRIVER ARRIVING
    # ========================================================

    def driver_arriving(
        self,
        phone_number: str,
        driver_name: str,
        eta_minutes: int
    ) -> SMSResponse:
        """
        Notify passenger that driver is arriving.
        """

        message = (
            f"{APP_NAME}: {driver_name} "
            f"is arriving. "
            f"ETA {eta_minutes} minutes."
        )

        return self.send(
            phone_number,
            message
        )

    # ========================================================
    # DRIVER ARRIVED
    # ========================================================

    def driver_arrived(
        self,
        phone_number: str,
        vehicle_number: str
    ) -> SMSResponse:
        """
        Notify passenger that driver has arrived.
        """

        message = (
            f"{APP_NAME}: Your driver "
            f"has arrived. "
            f"Vehicle: {vehicle_number}."
        )

        return self.send(
            phone_number,
            message
        )

    # ========================================================
    # RIDE STARTED
    # ========================================================

    def ride_started(
        self,
        phone_number: str,
        ride_id: str
    ) -> SMSResponse:

        message = (
            f"{APP_NAME}: Ride "
            f"{ride_id} has started."
        )

        return self.send(
            phone_number,
            message
        )

    # ========================================================
    # RIDE COMPLETED
    # ========================================================

    def ride_completed(
        self,
        phone_number: str,
        fare: str
    ) -> SMSResponse:
        """
        Notify passenger of completed ride.
        """

        message = (
            f"{APP_NAME}: Ride completed. "
            f"Final fare: ₹{fare}."
        )

        return self.send(
            phone_number,
            message
        )

    # ========================================================
    # PAYMENT SUCCESS
    # ========================================================

    def payment_success(
        self,
        phone_number: str,
        amount: str
    ) -> SMSResponse:

        message = (
            f"{APP_NAME}: Payment of "
            f"₹{amount} was successful."
        )

        return self.send(
            phone_number,
            message
        )

    # ========================================================
    # PAYMENT FAILED
    # ========================================================

    def payment_failed(
        self,
        phone_number: str
    ) -> SMSResponse:

        message = (
            f"{APP_NAME}: Payment failed. "
            f"Please try again."
        )

        return self.send(
            phone_number,
            message
        )

    # ========================================================
    # RIDE CANCELLED
    # ========================================================

    def ride_cancelled(
        self,
        phone_number: str,
        ride_id: str
    ) -> SMSResponse:

        message = (
            f"{APP_NAME}: Ride "
            f"{ride_id} has been cancelled."
        )

        return self.send(
            phone_number,
            message
        )


# ============================================================
# SIMPLE FUNCTION
# ============================================================

def send_sms(
    phone_number: str,
    message: str
) -> SMSResponse:
    """
    Convenience function for service.py.
    """

    service = SMSService()

    return service.send(
        phone_number,
        message
    )


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    # Development mode.
    service = SMSService(
        provider=MockSMSProvider()
    )

    # --------------------------------------------------------
    # Generic SMS
    # --------------------------------------------------------

    result = service.send(

        phone_number="9876543210",

        message=(
            "Your RideX driver is "
            "on the way."
        )
    )

    print(
        "\nSMS Response:"
    )

    print(
        result
    )

    # --------------------------------------------------------
    # Ride booked
    # --------------------------------------------------------

    result = service.ride_booked(

        phone_number="9876543210",

        ride_id="RIDE-1001"
    )

    print(
        "\nRide Booked:"
    )

    print(
        result
    )

    # --------------------------------------------------------
    # Driver arriving
    # --------------------------------------------------------

    result = service.driver_arriving(

        phone_number="9876543210",

        driver_name="Raj",

        eta_minutes=5
    )

    print(
        "\nDriver Arriving:"
    )

    print(
        result
    )
