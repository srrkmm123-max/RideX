"""
RideX Notification Service - Push Notifications

Responsibilities:
    - Create push notification messages
    - Validate device tokens
    - Send push notifications
    - Support Android/iOS
    - Handle provider responses
    - Provide a mock provider for development

Production providers can include:
    - Firebase Cloud Messaging (FCM)
    - Apple Push Notification service (APNs)

IMPORTANT:
    Never store private keys, API secrets, or credentials
    directly in this source file.
"""

import os
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


# ============================================================
# CONFIGURATION
# ============================================================

PUSH_PROVIDER = os.getenv(
    "PUSH_PROVIDER",
    "mock"
)

APP_NAME = os.getenv(
    "APP_NAME",
    "RideX"
)


# ============================================================
# PUSH STATUS
# ============================================================

class PushStatus:
    """
    Push notification delivery states.
    """

    CREATED = "created"

    SENT = "sent"

    FAILED = "failed"

    INVALID_TOKEN = "invalid_token"

    NOT_REGISTERED = "not_registered"


# ============================================================
# PUSH MESSAGE
# ============================================================

@dataclass
class PushMessage:
    """
    Push notification message.

    The device token identifies the destination device.
    """

    notification_id: str

    device_token: str

    title: str

    body: str

    data: dict[str, Any] = field(
        default_factory=dict
    )

    platform: str = "android"

    priority: str = "high"

    created_at: datetime = field(
        default_factory=lambda:
        datetime.now(timezone.utc)
    )


# ============================================================
# PUSH RESPONSE
# ============================================================

@dataclass
class PushResponse:
    """
    Standardized push provider response.
    """

    success: bool

    status: str

    notification_id: str

    provider: str

    message_id: Optional[str] = None

    error: Optional[str] = None

    raw_response: Optional[dict] = None


# ============================================================
# PUSH PROVIDER INTERFACE
# ============================================================

class PushProvider(ABC):
    """
    Abstract push notification provider.
    """

    @abstractmethod
    def send(
        self,
        message: PushMessage
    ) -> PushResponse:
        """
        Send push notification.
        """

        raise NotImplementedError


# ============================================================
# TOKEN VALIDATION
# ============================================================

def validate_device_token(
    device_token: str
) -> bool:
    """
    Basic device-token validation.

    Provider-specific token validation should happen
    at the provider/API level.
    """

    if not device_token:

        return False

    if not isinstance(
        device_token,
        str
    ):

        return False

    token = device_token.strip()

    if len(token) < 10:

        return False

    return True


# ============================================================
# MESSAGE CREATION
# ============================================================

def create_push_message(
    device_token: str,
    title: str,
    body: str,
    data: Optional[dict] = None,
    platform: str = "android",
    priority: str = "high",
) -> PushMessage:
    """
    Create a validated push notification.
    """

    if not validate_device_token(
        device_token
    ):

        raise ValueError(
            "Invalid device token"
        )

    if not title:

        raise ValueError(
            "Notification title is required"
        )

    if not body:

        raise ValueError(
            "Notification body is required"
        )

    platform = platform.lower()

    if platform not in {
        "android",
        "ios",
    }:

        raise ValueError(
            "Platform must be android or ios"
        )

    priority = priority.lower()

    if priority not in {
        "normal",
        "high",
    }:

        raise ValueError(
            "Priority must be normal or high"
        )

    return PushMessage(

        notification_id=(
            "NOTIF-"
            +
            uuid.uuid4()
            .hex[:16]
            .upper()
        ),

        device_token=device_token.strip(),

        title=title.strip(),

        body=body.strip(),

        data=data or {},

        platform=platform,

        priority=priority,
    )


# ============================================================
# MOCK PUSH PROVIDER
# ============================================================

class MockPushProvider(
    PushProvider
):
    """
    Development/testing provider.

    Does not send a real notification.
    """

    def send(
        self,
        message: PushMessage
    ) -> PushResponse:

        print(
            "\n[MOCK PUSH]"
        )

        print(
            f"Title: {message.title}"
        )

        print(
            f"Body: {message.body}"
        )

        print(
            f"Platform: {message.platform}"
        )

        print(
            f"Data: {message.data}"
        )

        provider_message_id = (
            "MOCK-"
            +
            uuid.uuid4()
            .hex[:12]
            .upper()
        )

        return PushResponse(

            success=True,

            status=PushStatus.SENT,

            notification_id=(
                message.notification_id
            ),

            provider="mock",

            message_id=(
                provider_message_id
            ),

            raw_response={
                "provider": "mock",
                "message_id":
                    provider_message_id,
            }
        )


# ============================================================
# FIREBASE CLOUD MESSAGING PROVIDER
# ============================================================

class FCMProvider(
    PushProvider
):
    """
    Firebase Cloud Messaging provider.

    This class provides the integration boundary.

    Configure Firebase credentials using secure
    environment/secret-management mechanisms.

    Do not place service-account JSON or private
    credentials in this source file.
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
    ):

        self.project_id = (
            project_id
            or os.getenv(
                "FCM_PROJECT_ID"
            )
        )

        if not self.project_id:

            raise ValueError(
                "FCM_PROJECT_ID is not configured"
            )

    def send(
        self,
        message: PushMessage
    ) -> PushResponse:

        # ----------------------------------------------------
        # Production implementation
        # ----------------------------------------------------
        #
        # Use the official Firebase Admin SDK here.
        #
        # Example flow:
        #
        #   Firebase credentials
        #          ↓
        #   Firebase Admin SDK
        #          ↓
        #   FCM send()
        #          ↓
        #   FCM response
        #
        # The actual SDK initialization should be kept
        # outside the notification business logic.
        #

        raise NotImplementedError(
            "Implement FCM using the official "
            "Firebase Admin SDK"
        )


# ============================================================
# APNs PROVIDER
# ============================================================

class APNsProvider(
    PushProvider
):
    """
    Apple Push Notification service provider.

    Use Apple's official APNs authentication mechanism
    and keep credentials in secure secret storage.
    """

    def __init__(
        self,
        team_id: Optional[str] = None,
        key_id: Optional[str] = None,
    ):

        self.team_id = (
            team_id
            or os.getenv(
                "APNS_TEAM_ID"
            )
        )

        self.key_id = (
            key_id
            or os.getenv(
                "APNS_KEY_ID"
            )
        )

        if not self.team_id:

            raise ValueError(
                "APNS_TEAM_ID is not configured"
            )

        if not self.key_id:

            raise ValueError(
                "APNS_KEY_ID is not configured"
            )

    def send(
        self,
        message: PushMessage
    ) -> PushResponse:

        raise NotImplementedError(
            "Implement APNs using Apple's "
            "official APNs interface"
        )


# ============================================================
# PROVIDER FACTORY
# ============================================================

def get_push_provider(
    provider_name: Optional[str] = None
) -> PushProvider:
    """
    Return configured push provider.
    """

    provider_name = (
        provider_name
        or PUSH_PROVIDER
    ).lower()

    if provider_name == "mock":

        return MockPushProvider()

    if provider_name == "fcm":

        return FCMProvider()

    if provider_name == "apns":

        return APNsProvider()

    raise ValueError(
        f"Unsupported push provider: "
        f"{provider_name}"
    )


# ============================================================
# PUSH SERVICE
# ============================================================

class PushNotificationService:
    """
    High-level push notification service.
    """

    def __init__(
        self,
        provider: Optional[
            PushProvider
        ] = None,
    ):

        self.provider = (
            provider
            or get_push_provider()
        )

    # ========================================================
    # SEND
    # ========================================================

    def send(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[dict] = None,
        platform: str = "android",
        priority: str = "high",
    ) -> PushResponse:
        """
        Create and send push notification.
        """

        message = create_push_message(

            device_token=device_token,

            title=title,

            body=body,

            data=data,

            platform=platform,

            priority=priority,
        )

        return self.provider.send(
            message
        )

    # ========================================================
    # RIDE ACCEPTED
    # ========================================================

    def ride_accepted(
        self,
        device_token: str,
        driver_name: str,
        vehicle_number: str,
        eta_minutes: int,
    ) -> PushResponse:
        """
        Notify passenger that driver accepted ride.
        """

        return self.send(

            device_token=device_token,

            title="Driver Accepted Ride",

            body=(
                f"{driver_name} accepted your ride. "
                f"ETA: {eta_minutes} minutes."
            ),

            data={
                "event": "ride_accepted",
                "driver_name": driver_name,
                "vehicle_number":
                    vehicle_number,
                "eta_minutes":
                    eta_minutes,
            },

            platform="android",

            priority="high",
        )

    # ========================================================
    # DRIVER ARRIVING
    # ========================================================

    def driver_arriving(
        self,
        device_token: str,
        driver_name: str,
        eta_minutes: int,
    ) -> PushResponse:
        """
        Notify passenger that driver is arriving.
        """

        return self.send(

            device_token=device_token,

            title="Driver Arriving",

            body=(
                f"{driver_name} is arriving. "
                f"ETA: {eta_minutes} minutes."
            ),

            data={
                "event": "driver_arriving",
                "driver_name": driver_name,
                "eta_minutes":
                    eta_minutes,
            },

            priority="high",
        )

    # ========================================================
    # DRIVER ARRIVED
    # ========================================================

    def driver_arrived(
        self,
        device_token: str,
        vehicle_number: str,
    ) -> PushResponse:
        """
        Notify passenger that driver arrived.
        """

        return self.send(

            device_token=device_token,

            title="Driver Has Arrived",

            body=(
                f"Your driver is waiting. "
                f"Vehicle: {vehicle_number}"
            ),

            data={
                "event": "driver_arrived",
                "vehicle_number":
                    vehicle_number,
            },

            priority="high",
        )

    # ========================================================
    # RIDE STARTED
    # ========================================================

    def ride_started(
        self,
        device_token: str,
        ride_id: str,
    ) -> PushResponse:
        """
        Notify passenger that ride started.
        """

        return self.send(

            device_token=device_token,

            title="Ride Started",

            body=(
                "Your RideX trip has started."
            ),

            data={
                "event": "ride_started",
                "ride_id": ride_id,
            },

            priority="high",
        )

    # ========================================================
    # RIDE COMPLETED
    # ========================================================

    def ride_completed(
        self,
        device_token: str,
        ride_id: str,
        fare: str,
    ) -> PushResponse:
        """
        Notify passenger that ride completed.
        """

        return self.send(

            device_token=device_token,

            title="Ride Completed",

            body=(
                f"Your RideX trip is complete. "
                f"Fare: ₹{fare}"
            ),

            data={
                "event": "ride_completed",
                "ride_id": ride_id,
                "fare": fare,
            },

            priority="normal",
        )

    # ========================================================
    # PAYMENT SUCCESS
    # ========================================================

    def payment_success(
        self,
        device_token: str,
        payment_id: str,
        amount: str,
    ) -> PushResponse:
        """
        Notify passenger of successful payment.
        """

        return self.send(

            device_token=device_token,

            title="Payment Successful",

            body=(
                f"Payment of ₹{amount} "
                f"was successful."
            ),

            data={
                "event": "payment_success",
                "payment_id": payment_id,
                "amount": amount,
            },

            priority="normal",
        )


# ============================================================
# SIMPLE FUNCTION
# ============================================================

def send_push_notification(
    device_token: str,
    title: str,
    body: str,
    data: Optional[dict] = None,
    platform: str = "android",
) -> PushResponse:
    """
    Convenience function for service.py.
    """

    service = (
        PushNotificationService()
    )

    return service.send(

        device_token=device_token,

        title=title,

        body=body,

        data=data,

        platform=platform,
    )


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    # Development uses mock provider.
    service = PushNotificationService(
        provider=MockPushProvider()
    )

    # --------------------------------------------------------
    # Generic notification
    # --------------------------------------------------------

    result = service.send(

        device_token=(
            "sample-device-token-12345"
        ),

        title="RideX",

        body=(
            "Your driver is on the way."
        ),

        data={
            "ride_id": "RIDE-1001",
            "screen": "track-driver",
        },

        platform="android",
    )

    print(
        "\nPush Response:"
    )

    print(
        result
    )

    # --------------------------------------------------------
    # Ride accepted notification
    # --------------------------------------------------------

    result = service.ride_accepted(

        device_token=(
            "sample-device-token-12345"
        ),

        driver_name="Raj",

        vehicle_number="TS09AB1234",

        eta_minutes=5,
    )

    print(
        "\nRide Accepted:"
    )

    print(
        result
    )
