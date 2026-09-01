"""
RideX Notification Service - Email

Responsibilities:
    - Create email messages
    - Validate email addresses
    - Send email through a provider
    - Provide mock provider for development
    - Provide SMTP provider for production
    - Provide RideX-specific email templates

IMPORTANT:
    Never hard-code SMTP passwords, API keys,
    or other secrets in this file.
"""

import os
import re
import uuid
import smtplib

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Optional


# ============================================================
# CONFIGURATION
# ============================================================

EMAIL_PROVIDER = os.getenv(
    "EMAIL_PROVIDER",
    "mock"
)

APP_NAME = os.getenv(
    "APP_NAME",
    "RideX"
)

DEFAULT_FROM_EMAIL = os.getenv(
    "FROM_EMAIL",
    "no-reply@ridex.example"
)

SMTP_HOST = os.getenv(
    "SMTP_HOST",
    ""
)

SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        "587"
    )
)

SMTP_USERNAME = os.getenv(
    "SMTP_USERNAME",
    ""
)

SMTP_PASSWORD = os.getenv(
    "SMTP_PASSWORD",
    ""
)

SMTP_USE_TLS = os.getenv(
    "SMTP_USE_TLS",
    "true"
).lower() == "true"


# ============================================================
# EMAIL STATUS
# ============================================================

class EmailStatus:

    CREATED = "created"

    SENT = "sent"

    FAILED = "failed"

    INVALID_EMAIL = "invalid_email"

    PROVIDER_ERROR = "provider_error"


# ============================================================
# EMAIL MESSAGE
# ============================================================

@dataclass
class Email:

    message_id: str

    to_email: str

    subject: str

    body: str

    from_email: str = DEFAULT_FROM_EMAIL

    html: bool = False

    created_at: datetime = field(
        default_factory=lambda:
        datetime.now(timezone.utc)
    )


# ============================================================
# EMAIL RESPONSE
# ============================================================

@dataclass
class EmailResponse:

    success: bool

    status: str

    message_id: str

    provider: str

    provider_message_id: Optional[str] = None

    error: Optional[str] = None

    raw_response: Optional[dict] = None


# ============================================================
# EMAIL VALIDATION
# ============================================================

def validate_email(
    email: str
) -> bool:
    """
    Basic email address validation.
    """

    if not email:

        return False

    email = str(
        email
    ).strip()

    pattern = (
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )

    return bool(
        re.match(
            pattern,
            email
        )
    )


# ============================================================
# EMAIL CREATOR
# ============================================================

def create_email(
    to_email: str,
    subject: str,
    body: str,
    from_email: str = DEFAULT_FROM_EMAIL,
    html: bool = False,
) -> Email:
    """
    Create a validated email.
    """

    if not validate_email(
        to_email
    ):

        raise ValueError(
            "Invalid recipient email address"
        )

    if not validate_email(
        from_email
    ):

        raise ValueError(
            "Invalid sender email address"
        )

    if not subject:

        raise ValueError(
            "Email subject is required"
        )

    if not body:

        raise ValueError(
            "Email body is required"
        )

    return Email(

        message_id=(
            "EMAIL-"
            +
            uuid.uuid4()
            .hex[:16]
            .upper()
        ),

        to_email=to_email.strip(),

        subject=subject.strip(),

        body=body,

        from_email=from_email.strip(),

        html=html
    )


# ============================================================
# EMAIL PROVIDER INTERFACE
# ============================================================

class EmailProvider(ABC):
    """
    Abstract email provider.
    """

    @abstractmethod
    def send(
        self,
        email: Email
    ) -> EmailResponse:

        raise NotImplementedError


# ============================================================
# MOCK EMAIL PROVIDER
# ============================================================

class MockEmailProvider(
    EmailProvider
):
    """
    Development/testing provider.

    Does not send a real email.
    """

    def send(
        self,
        email: Email
    ) -> EmailResponse:

        provider_message_id = (
            "MOCK-EMAIL-"
            +
            uuid.uuid4()
            .hex[:12]
            .upper()
        )

        print(
            "\n=============================="
        )

        print(
            "[MOCK EMAIL]"
        )

        print(
            f"From: {email.from_email}"
        )

        print(
            f"To: {email.to_email}"
        )

        print(
            f"Subject: {email.subject}"
        )

        print(
            f"Body:\n{email.body}"
        )

        print(
            f"Provider ID: "
            f"{provider_message_id}"
        )

        print(
            "==============================\n"
        )

        return EmailResponse(

            success=True,

            status=EmailStatus.SENT,

            message_id=email.message_id,

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
# SMTP PROVIDER
# ============================================================

class SMTPEmailProvider(
    EmailProvider
):
    """
    SMTP email provider.

    Configuration:

        SMTP_HOST
        SMTP_PORT
        SMTP_USERNAME
        SMTP_PASSWORD
        SMTP_USE_TLS
    """

    def __init__(
        self,
        host: str = SMTP_HOST,
        port: int = SMTP_PORT,
        username: str = SMTP_USERNAME,
        password: str = SMTP_PASSWORD,
        use_tls: bool = SMTP_USE_TLS,
    ):

        self.host = host

        self.port = port

        self.username = username

        self.password = password

        self.use_tls = use_tls

        if not self.host:

            raise ValueError(
                "SMTP_HOST is not configured"
            )

    def send(
        self,
        email: Email
    ) -> EmailResponse:

        try:

            message = EmailMessage()

            message["From"] = (
                email.from_email
            )

            message["To"] = (
                email.to_email
            )

            message["Subject"] = (
                email.subject
            )

            if email.html:

                message.set_content(
                    "This email contains "
                    "HTML content."
                )

                message.add_alternative(
                    email.body,
                    subtype="html"
                )

            else:

                message.set_content(
                    email.body
                )

            # ------------------------------------------------
            # SMTP CONNECTION
            # ------------------------------------------------

            with smtplib.SMTP(
                self.host,
                self.port,
                timeout=30
            ) as smtp:

                smtp.ehlo()

                if self.use_tls:

                    smtp.starttls()

                    smtp.ehlo()

                if (
                    self.username
                    and
                    self.password
                ):

                    smtp.login(
                        self.username,
                        self.password
                    )

                smtp.send_message(
                    message
                )

            return EmailResponse(

                success=True,

                status=EmailStatus.SENT,

                message_id=email.message_id,

                provider="smtp",

                provider_message_id=(
                    email.message_id
                )
            )

        except Exception as error:

            return EmailResponse(

                success=False,

                status=EmailStatus.FAILED,

                message_id=email.message_id,

                provider="smtp",

                error=str(error)
            )


# ============================================================
# PROVIDER FACTORY
# ============================================================

def get_email_provider(
    provider_name: Optional[str] = None
) -> EmailProvider:
    """
    Return configured email provider.
    """

    provider_name = (
        provider_name
        or EMAIL_PROVIDER
    ).lower()

    if provider_name == "mock":

        return MockEmailProvider()

    if provider_name == "smtp":

        return SMTPEmailProvider()

    raise ValueError(
        f"Unsupported email provider: "
        f"{provider_name}"
    )


# ============================================================
# EMAIL SERVICE
# ============================================================

class EmailService:
    """
    High-level RideX email service.
    """

    def __init__(
        self,
        provider: Optional[
            EmailProvider
        ] = None
    ):

        self.provider = (
            provider
            or get_email_provider()
        )

    # ========================================================
    # SEND EMAIL
    # ========================================================

    def send(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = False,
        from_email: str = DEFAULT_FROM_EMAIL,
    ) -> EmailResponse:

        email = create_email(

            to_email=to_email,

            subject=subject,

            body=body,

            from_email=from_email,

            html=html
        )

        return self.provider.send(
            email
        )

    # ========================================================
    # RIDE BOOKED
    # ========================================================

    def ride_booked(
        self,
        to_email: str,
        ride_id: str,
        pickup: str,
        destination: str,
        estimated_fare: str,
    ) -> EmailResponse:

        subject = (
            f"{APP_NAME} - "
            f"Ride Booked"
        )

        body = (
            f"Hello,\n\n"
            f"Your RideX ride has been booked.\n\n"
            f"Ride ID: {ride_id}\n"
            f"Pickup: {pickup}\n"
            f"Destination: {destination}\n"
            f"Estimated Fare: ₹{estimated_fare}\n\n"
            f"Thank you for using {APP_NAME}."
        )

        return self.send(
            to_email,
            subject,
            body
        )

    # ========================================================
    # DRIVER ASSIGNED
    # ========================================================

    def driver_assigned(
        self,
        to_email: str,
        driver_name: str,
        vehicle_number: str,
        eta_minutes: int,
    ) -> EmailResponse:

        subject = (
            f"{APP_NAME} - "
            f"Driver Assigned"
        )

        body = (
            f"Hello,\n\n"
            f"Your RideX driver has been assigned.\n\n"
            f"Driver: {driver_name}\n"
            f"Vehicle: {vehicle_number}\n"
            f"ETA: {eta_minutes} minutes\n\n"
            f"Please be ready at your pickup location."
        )

        return self.send(
            to_email,
            subject,
            body
        )

    # ========================================================
    # DRIVER ARRIVING
    # ========================================================

    def driver_arriving(
        self,
        to_email: str,
        driver_name: str,
        eta_minutes: int,
    ) -> EmailResponse:

        subject = (
            f"{APP_NAME} - "
            f"Driver Arriving"
        )

        body = (
            f"Hello,\n\n"
            f"{driver_name} is arriving.\n\n"
            f"Estimated arrival: "
            f"{eta_minutes} minutes.\n\n"
            f"Thank you for using {APP_NAME}."
        )

        return self.send(
            to_email,
            subject,
            body
        )

    # ========================================================
    # RIDE COMPLETED
    # ========================================================

    def ride_completed(
        self,
        to_email: str,
        ride_id: str,
        fare: str,
    ) -> EmailResponse:

        subject = (
            f"{APP_NAME} - "
            f"Ride Completed"
        )

        body = (
            f"Hello,\n\n"
            f"Your RideX trip is complete.\n\n"
            f"Ride ID: {ride_id}\n"
            f"Final Fare: ₹{fare}\n\n"
            f"Thank you for riding with {APP_NAME}."
        )

        return self.send(
            to_email,
            subject,
            body
        )

    # ========================================================
    # PAYMENT SUCCESS
    # ========================================================

    def payment_success(
        self,
        to_email: str,
        payment_id: str,
        amount: str,
    ) -> EmailResponse:

        subject = (
            f"{APP_NAME} - "
            f"Payment Successful"
        )

        body = (
            f"Hello,\n\n"
            f"Your payment was successful.\n\n"
            f"Payment ID: {payment_id}\n"
            f"Amount: ₹{amount}\n\n"
            f"Thank you for using {APP_NAME}."
        )

        return self.send(
            to_email,
            subject,
            body
        )

    # ========================================================
    # PAYMENT FAILED
    # ========================================================

    def payment_failed(
        self,
        to_email: str,
        payment_id: str,
    ) -> EmailResponse:

        subject = (
            f"{APP_NAME} - "
            f"Payment Failed"
        )

        body = (
            f"Hello,\n\n"
            f"We could not complete your payment.\n\n"
            f"Payment ID: {payment_id}\n\n"
            f"Please try again."
        )

        return self.send(
            to_email,
            subject,
            body
        )

    # ========================================================
    # RIDE CANCELLED
    # ========================================================

    def ride_cancelled(
        self,
        to_email: str,
        ride_id: str,
        reason: str = "",
    ) -> EmailResponse:

        subject = (
            f"{APP_NAME} - "
            f"Ride Cancelled"
        )

        body = (
            f"Hello,\n\n"
            f"Your RideX ride has been cancelled.\n\n"
            f"Ride ID: {ride_id}\n"
        )

        if reason:

            body += (
                f"Reason: {reason}\n"
            )

        body += (
            f"\nThank you for using {APP_NAME}."
        )

        return self.send(
            to_email,
            subject,
            body
        )


# ============================================================
# SIMPLE FUNCTION
# ============================================================

def send_email(
    to_email: str,
    subject: str,
    body: str,
) -> EmailResponse:
    """
    Convenience function for service.py.
    """

    service = EmailService()

    return service.send(
        to_email,
        subject,
        body
    )


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    # Development mode.
    service = EmailService(
        provider=MockEmailProvider()
    )

    # --------------------------------------------------------
    # Generic email
    # --------------------------------------------------------

    result = service.send(

        to_email="passenger@example.com",

        subject="RideX Test Email",

        body=(
            "This is a test email "
            "from RideX."
        )
    )

    print(
        "\nEmail Response:"
    )

    print(
        result
    )

    # --------------------------------------------------------
    # Ride booked
    # --------------------------------------------------------

    result = service.ride_booked(

        to_email="passenger@example.com",

        ride_id="RIDE-1001",

        pickup="Hyderabad Airport",

        destination="HITEC City",

        estimated_fare="450"
    )

    print(
        "\nRide Booked Email:"
    )

    print(
        result
    )

    # --------------------------------------------------------
    # Payment successful
    # --------------------------------------------------------

    result = service.payment_success(

        to_email="passenger@example.com",

        payment_id="PAY-1001",

        amount="450"
    )

    print(
        "\nPayment Email:"
    )

    print(
        result
    )
