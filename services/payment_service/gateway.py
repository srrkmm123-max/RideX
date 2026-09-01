"""
RideX Payment Service - Payment Gateway

Responsibilities:
    - Provide a common interface for payment providers
    - Create payment orders
    - Verify payment responses
    - Process refunds
    - Normalize provider responses

IMPORTANT:
    This is a provider abstraction layer.

    Do NOT store:
        - Card numbers
        - CVV
        - UPI PIN
        - Net-banking passwords

    Provider API keys must come from environment variables
    or a secret-management system.
"""

import hashlib
import hmac
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional
from uuid import uuid4


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_CURRENCY = "INR"

PAYMENT_GATEWAY = os.getenv(
    "PAYMENT_GATEWAY",
    "mock"
)

GATEWAY_TIMEOUT = int(
    os.getenv(
        "PAYMENT_GATEWAY_TIMEOUT",
        "30"
    )
)


# ============================================================
# GATEWAY RESPONSE
# ============================================================

@dataclass
class GatewayResponse:
    """
    Standardized payment gateway response.
    """

    success: bool

    status: str

    gateway: str

    order_id: Optional[str] = None

    payment_id: Optional[str] = None

    refund_id: Optional[str] = None

    amount: Optional[Decimal] = None

    currency: str = DEFAULT_CURRENCY

    message: Optional[str] = None

    raw_response: Optional[dict] = None


# ============================================================
# PAYMENT GATEWAY INTERFACE
# ============================================================

class PaymentGateway(ABC):
    """
    Abstract interface for all payment providers.
    """

    @abstractmethod
    def create_order(
        self,
        amount: Decimal,
        currency: str,
        receipt: str,
        metadata: Optional[dict] = None,
    ) -> GatewayResponse:
        """
        Create payment order.
        """
        raise NotImplementedError

    @abstractmethod
    def verify_payment(
        self,
        order_id: str,
        payment_id: str,
        signature: Optional[str] = None,
    ) -> GatewayResponse:
        """
        Verify payment.
        """
        raise NotImplementedError

    @abstractmethod
    def refund(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
    ) -> GatewayResponse:
        """
        Refund payment.
        """
        raise NotImplementedError

    @abstractmethod
    def get_payment(
        self,
        payment_id: str,
    ) -> GatewayResponse:
        """
        Get payment status.
        """
        raise NotImplementedError


# ============================================================
# MOCK GATEWAY
# ============================================================

class MockPaymentGateway(
    PaymentGateway
):
    """
    Development/testing payment gateway.

    This does NOT move real money.
    """

    def create_order(
        self,
        amount: Decimal,
        currency: str,
        receipt: str,
        metadata: Optional[dict] = None,
    ) -> GatewayResponse:

        amount = Decimal(
            str(amount)
        ).quantize(
            Decimal("0.01")
        )

        order_id = (
            "MOCK_ORDER_"
            +
            uuid4().hex[:12].upper()
        )

        return GatewayResponse(

            success=True,

            status="created",

            gateway="mock",

            order_id=order_id,

            amount=amount,

            currency=currency.upper(),

            message="Mock order created",

            raw_response={
                "order_id": order_id,
                "receipt": receipt,
                "amount": str(amount),
                "currency": currency,
                "metadata": metadata or {},
            }
        )

    def verify_payment(
        self,
        order_id: str,
        payment_id: str,
        signature: Optional[str] = None,
    ) -> GatewayResponse:

        if not order_id:

            return GatewayResponse(

                success=False,

                status="failed",

                gateway="mock",

                message="Missing order_id"
            )

        if not payment_id:

            return GatewayResponse(

                success=False,

                status="failed",

                gateway="mock",

                message="Missing payment_id"
            )

        return GatewayResponse(

            success=True,

            status="success",

            gateway="mock",

            order_id=order_id,

            payment_id=payment_id,

            message="Mock payment verified",

            raw_response={
                "order_id": order_id,
                "payment_id": payment_id,
            }
        )

    def refund(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
    ) -> GatewayResponse:

        if not payment_id:

            return GatewayResponse(

                success=False,

                status="failed",

                gateway="mock",

                message="Missing payment_id"
            )

        refund_id = (
            "MOCK_REFUND_"
            +
            uuid4().hex[:12].upper()
        )

        refund_amount = None

        if amount is not None:

            refund_amount = Decimal(
                str(amount)
            ).quantize(
                Decimal("0.01")
            )

        return GatewayResponse(

            success=True,

            status="refunded",

            gateway="mock",

            payment_id=payment_id,

            refund_id=refund_id,

            amount=refund_amount,

            message="Mock refund successful",

            raw_response={
                "refund_id": refund_id,
                "payment_id": payment_id,
                "amount": (
                    str(refund_amount)
                    if refund_amount is not None
                    else None
                ),
            }
        )

    def get_payment(
        self,
        payment_id: str,
    ) -> GatewayResponse:

        if not payment_id:

            return GatewayResponse(

                success=False,

                status="failed",

                gateway="mock",

                message="Missing payment_id"
            )

        return GatewayResponse(

            success=True,

            status="success",

            gateway="mock",

            payment_id=payment_id,

            message="Mock payment found"
        )


# ============================================================
# GENERIC HMAC SIGNATURE VERIFIER
# ============================================================

class SignatureVerifier:
    """
    Utility for verifying provider webhook/payment signatures.

    The actual signature format depends on the provider.
    """

    @staticmethod
    def verify_hmac_sha256(
        payload: bytes,
        received_signature: str,
        secret: str,
    ) -> bool:
        """
        Verify HMAC-SHA256 signature.
        """

        if not received_signature:
            return False

        if not secret:
            return False

        expected_signature = (
            hmac.new(
                secret.encode("utf-8"),
                payload,
                hashlib.sha256
            )
            .hexdigest()
        )

        return hmac.compare_digest(
            expected_signature,
            received_signature
        )


# ============================================================
# RAZORPAY PLACEHOLDER
# ============================================================

class RazorpayGateway(
    PaymentGateway
):
    """
    Razorpay gateway adapter.

    Install the official Razorpay Python SDK separately
    before implementing real provider calls.

    This class intentionally does not contain live API calls.
    """

    def __init__(
        self,
        key_id: Optional[str] = None,
        key_secret: Optional[str] = None,
    ):

        self.key_id = (
            key_id
            or os.getenv(
                "RAZORPAY_KEY_ID"
            )
        )

        self.key_secret = (
            key_secret
            or os.getenv(
                "RAZORPAY_KEY_SECRET"
            )
        )

        if not self.key_id:

            raise ValueError(
                "RAZORPAY_KEY_ID is not configured"
            )

        if not self.key_secret:

            raise ValueError(
                "RAZORPAY_KEY_SECRET is not configured"
            )

    def create_order(
        self,
        amount: Decimal,
        currency: str,
        receipt: str,
        metadata: Optional[dict] = None,
    ) -> GatewayResponse:

        raise NotImplementedError(
            "Implement using the official "
            "Razorpay SDK/API"
        )

    def verify_payment(
        self,
        order_id: str,
        payment_id: str,
        signature: Optional[str] = None,
    ) -> GatewayResponse:

        raise NotImplementedError(
            "Implement using the official "
            "Razorpay SDK/API"
        )

    def refund(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
    ) -> GatewayResponse:

        raise NotImplementedError(
            "Implement using the official "
            "Razorpay SDK/API"
        )

    def get_payment(
        self,
        payment_id: str,
    ) -> GatewayResponse:

        raise NotImplementedError(
            "Implement using the official "
            "Razorpay SDK/API"
        )


# ============================================================
# STRIPE PLACEHOLDER
# ============================================================

class StripeGateway(
    PaymentGateway
):
    """
    Stripe gateway adapter.

    Real Stripe API calls should be implemented
    using the official Stripe SDK.
    """

    def __init__(
        self,
        secret_key: Optional[str] = None,
    ):

        self.secret_key = (
            secret_key
            or os.getenv(
                "STRIPE_SECRET_KEY"
            )
        )

        if not self.secret_key:

            raise ValueError(
                "STRIPE_SECRET_KEY is not configured"
            )

    def create_order(
        self,
        amount: Decimal,
        currency: str,
        receipt: str,
        metadata: Optional[dict] = None,
    ) -> GatewayResponse:

        raise NotImplementedError(
            "Implement using the official "
            "Stripe SDK/API"
        )

    def verify_payment(
        self,
        order_id: str,
        payment_id: str,
        signature: Optional[str] = None,
    ) -> GatewayResponse:

        raise NotImplementedError(
            "Implement using the official "
            "Stripe SDK/API"
        )

    def refund(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
    ) -> GatewayResponse:

        raise NotImplementedError(
            "Implement using the official "
            "Stripe SDK/API"
        )

    def get_payment(
        self,
        payment_id: str,
    ) -> GatewayResponse:

        raise NotImplementedError(
            "Implement using the official "
            "Stripe SDK/API"
        )


# ============================================================
# GATEWAY FACTORY
# ============================================================

def get_payment_gateway(
    gateway_name: Optional[str] = None,
) -> PaymentGateway:
    """
    Return configured payment gateway.
    """

    gateway_name = (
        gateway_name
        or PAYMENT_GATEWAY
    ).lower()

    if gateway_name == "mock":

        return MockPaymentGateway()

    if gateway_name == "razorpay":

        return RazorpayGateway()

    if gateway_name == "stripe":

        return StripeGateway()

    raise ValueError(
        f"Unsupported payment gateway: "
        f"{gateway_name}"
    )


# ============================================================
# SIMPLE API
# ============================================================

def create_payment_order(
    amount,
    currency="INR",
    receipt="",
    metadata=None,
    gateway_name=None,
) -> GatewayResponse:
    """
    Convenience function.
    """

    gateway = get_payment_gateway(
        gateway_name
    )

    return gateway.create_order(

        amount=Decimal(
            str(amount)
        ),

        currency=currency,

        receipt=receipt,

        metadata=metadata
    )


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    gateway = get_payment_gateway(
        "mock"
    )

    # --------------------------------------------------------
    # Create order
    # --------------------------------------------------------

    order = gateway.create_order(

        amount=Decimal("450.00"),

        currency="INR",

        receipt="RIDE-1001",

        metadata={
            "ride_id": "RIDE-1001",
            "passenger_id": "USER-501",
        }
    )

    print(
        "\nCreate Order"
    )

    print(
        order
    )

    # --------------------------------------------------------
    # Verify payment
    # --------------------------------------------------------

    verification = (
        gateway.verify_payment(

            order_id=order.order_id,

            payment_id="MOCK_PAYMENT_123"
        )
    )

    print(
        "\nPayment Verification"
    )

    print(
        verification
    )

    # --------------------------------------------------------
    # Refund
    # --------------------------------------------------------

    refund = gateway.refund(

        payment_id="MOCK_PAYMENT_123",

        amount=Decimal("100.00")
    )

    print(
        "\nRefund"
    )

    print(
        refund
    )
