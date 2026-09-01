"""
RideX Payment Service - Payment Domain

Responsibilities:
    - Payment data model
    - Payment status management
    - Payment validation
    - Payment state transitions
    - Payment summaries

This module does NOT:
    - Call Razorpay/Stripe/etc.
    - Handle FastAPI routes
    - Store card numbers or CVV
    - Process raw payment credentials
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import uuid4


# ============================================================
# PAYMENT STATUS
# ============================================================

class PaymentStatus(str, Enum):
    """
    Payment lifecycle states.
    """

    CREATED = "created"

    PENDING = "pending"

    PROCESSING = "processing"

    SUCCESS = "success"

    FAILED = "failed"

    CANCELLED = "cancelled"

    REFUNDED = "refunded"

    PARTIALLY_REFUNDED = "partially_refunded"


# ============================================================
# PAYMENT METHOD
# ============================================================

class PaymentMethod(str, Enum):
    """
    Supported payment methods.

    These are identifiers only.
    Actual payment credentials must be handled
    by the payment provider.
    """

    UPI = "upi"

    CARD = "card"

    WALLET = "wallet"

    NET_BANKING = "net_banking"

    CASH = "cash"


# ============================================================
# PAYMENT CURRENCY
# ============================================================

DEFAULT_CURRENCY = "INR"


# ============================================================
# PAYMENT
# ============================================================

@dataclass
class Payment:
    """
    RideX payment object.

    Sensitive payment information such as:
        - card number
        - CVV
        - PIN
        - UPI PIN

    must NEVER be stored here.
    """

    payment_id: str

    ride_id: str

    passenger_id: str

    amount: Decimal

    currency: str = DEFAULT_CURRENCY

    payment_method: PaymentMethod = (
        PaymentMethod.UPI
    )

    status: PaymentStatus = (
        PaymentStatus.CREATED
    )

    provider: Optional[str] = None

    provider_payment_id: Optional[str] = None

    failure_reason: Optional[str] = None

    refund_amount: Decimal = (
        Decimal("0.00")
    )

    created_at: datetime = field(
        default_factory=lambda:
            datetime.now(timezone.utc)
    )

    updated_at: datetime = field(
        default_factory=lambda:
            datetime.now(timezone.utc)
    )

    metadata: dict = field(
        default_factory=dict
    )


# ============================================================
# PAYMENT MANAGER
# ============================================================

class PaymentManager:
    """
    Manages payment creation and state transitions.
    """

    # --------------------------------------------------------
    # VALID STATUS TRANSITIONS
    # --------------------------------------------------------

    VALID_TRANSITIONS = {

        PaymentStatus.CREATED: {
            PaymentStatus.PENDING,
            PaymentStatus.CANCELLED,
        },

        PaymentStatus.PENDING: {
            PaymentStatus.PROCESSING,
            PaymentStatus.SUCCESS,
            PaymentStatus.FAILED,
            PaymentStatus.CANCELLED,
        },

        PaymentStatus.PROCESSING: {
            PaymentStatus.SUCCESS,
            PaymentStatus.FAILED,
        },

        PaymentStatus.SUCCESS: {
            PaymentStatus.REFUNDED,
            PaymentStatus.PARTIALLY_REFUNDED,
        },

        PaymentStatus.FAILED: {
            PaymentStatus.PENDING,
        },

        PaymentStatus.CANCELLED: set(),

        PaymentStatus.REFUNDED: set(),

        PaymentStatus.PARTIALLY_REFUNDED: {
            PaymentStatus.REFUNDED,
        },
    }

    # ========================================================
    # CREATE PAYMENT
    # ========================================================

    def create_payment(
        self,
        ride_id: str,
        passenger_id: str,
        amount,
        payment_method: PaymentMethod,
        currency: str = DEFAULT_CURRENCY,
        provider: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Payment:
        """
        Create a new payment.
        """

        if not ride_id:

            raise ValueError(
                "ride_id is required"
            )

        if not passenger_id:

            raise ValueError(
                "passenger_id is required"
            )

        amount = self._validate_amount(
            amount
        )

        if not isinstance(
            payment_method,
            PaymentMethod
        ):

            payment_method = (
                PaymentMethod(
                    payment_method
                )
            )

        payment = Payment(

            payment_id=self.generate_payment_id(),

            ride_id=ride_id,

            passenger_id=passenger_id,

            amount=amount,

            currency=currency.upper(),

            payment_method=payment_method,

            status=PaymentStatus.CREATED,

            provider=provider,

            metadata=metadata or {},
        )

        return payment

    # ========================================================
    # GENERATE PAYMENT ID
    # ========================================================

    @staticmethod
    def generate_payment_id() -> str:
        """
        Generate unique payment ID.
        """

        return (
            "PAY-"
            +
            uuid4().hex[:16].upper()
        )

    # ========================================================
    # VALIDATE AMOUNT
    # ========================================================

    @staticmethod
    def _validate_amount(
        amount
    ) -> Decimal:
        """
        Validate and normalize monetary amount.
        """

        amount = Decimal(
            str(amount)
        )

        if amount <= 0:

            raise ValueError(
                "Payment amount must be greater than zero"
            )

        return amount.quantize(
            Decimal("0.01")
        )

    # ========================================================
    # CHANGE STATUS
    # ========================================================

    def transition_status(
        self,
        payment: Payment,
        new_status: PaymentStatus,
        reason: Optional[str] = None,
    ) -> Payment:
        """
        Safely transition payment state.
        """

        if not isinstance(
            new_status,
            PaymentStatus
        ):

            new_status = PaymentStatus(
                new_status
            )

        current_status = (
            payment.status
        )

        allowed_statuses = (
            self.VALID_TRANSITIONS.get(
                current_status,
                set()
            )
        )

        if new_status not in allowed_statuses:

            raise ValueError(
                f"Invalid payment transition: "
                f"{current_status.value} -> "
                f"{new_status.value}"
            )

        payment.status = new_status

        payment.updated_at = (
            datetime.now(timezone.utc)
        )

        if (
            new_status
            ==
            PaymentStatus.FAILED
        ):

            payment.failure_reason = (
                reason
                or
                "Payment failed"
            )

        return payment

    # ========================================================
    # MARK PENDING
    # ========================================================

    def mark_pending(
        self,
        payment: Payment
    ) -> Payment:

        return self.transition_status(
            payment,
            PaymentStatus.PENDING
        )

    # ========================================================
    # MARK PROCESSING
    # ========================================================

    def mark_processing(
        self,
        payment: Payment
    ) -> Payment:

        return self.transition_status(
            payment,
            PaymentStatus.PROCESSING
        )

    # ========================================================
    # MARK SUCCESS
    # ========================================================

    def mark_success(
        self,
        payment: Payment,
        provider_payment_id: Optional[str] = None,
    ) -> Payment:

        payment = self.transition_status(
            payment,
            PaymentStatus.SUCCESS
        )

        if provider_payment_id:

            payment.provider_payment_id = (
                provider_payment_id
            )

        return payment

    # ========================================================
    # MARK FAILED
    # ========================================================

    def mark_failed(
        self,
        payment: Payment,
        reason: str
    ) -> Payment:

        return self.transition_status(
            payment,
            PaymentStatus.FAILED,
            reason=reason
        )

    # ========================================================
    # CANCEL PAYMENT
    # ========================================================

    def cancel_payment(
        self,
        payment: Payment
    ) -> Payment:

        return self.transition_status(
            payment,
            PaymentStatus.CANCELLED
        )

    # ========================================================
    # REFUND
    # ========================================================

    def refund_payment(
        self,
        payment: Payment,
        refund_amount=None
    ) -> Payment:
        """
        Refund all or part of a successful payment.
        """

        if payment.status not in {
            PaymentStatus.SUCCESS,
            PaymentStatus.PARTIALLY_REFUNDED,
        }:

            raise ValueError(
                "Only successful payments can be refunded"
            )

        if refund_amount is None:

            refund_amount = (
                payment.amount
                -
                payment.refund_amount
            )

        refund_amount = Decimal(
            str(refund_amount)
        ).quantize(
            Decimal("0.01")
        )

        if refund_amount <= 0:

            raise ValueError(
                "Refund amount must be greater than zero"
            )

        remaining_amount = (
            payment.amount
            -
            payment.refund_amount
        )

        if refund_amount > remaining_amount:

            raise ValueError(
                "Refund amount exceeds remaining payment amount"
            )

        payment.refund_amount += (
            refund_amount
        )

        payment.refund_amount = (
            payment.refund_amount.quantize(
                Decimal("0.01")
            )
        )

        if (
            payment.refund_amount
            ==
            payment.amount
        ):

            payment.status = (
                PaymentStatus.REFUNDED
            )

        else:

            payment.status = (
                PaymentStatus.PARTIALLY_REFUNDED
            )

        payment.updated_at = (
            datetime.now(timezone.utc)
        )

        return payment

    # ========================================================
    # PAYMENT COMPLETED?
    # ========================================================

    @staticmethod
    def is_successful(
        payment: Payment
    ) -> bool:

        return (
            payment.status
            ==
            PaymentStatus.SUCCESS
        )

    # ========================================================
    # PAYMENT FINAL?
    # ========================================================

    @staticmethod
    def is_final(
        payment: Payment
    ) -> bool:

        return payment.status in {

            PaymentStatus.SUCCESS,

            PaymentStatus.CANCELLED,

            PaymentStatus.REFUNDED,
        }

    # ========================================================
    # REMAINING REFUND
    # ========================================================

    @staticmethod
    def remaining_refundable_amount(
        payment: Payment
    ) -> Decimal:

        remaining = (
            payment.amount
            -
            payment.refund_amount
        )

        return max(
            remaining,
            Decimal("0.00")
        ).quantize(
            Decimal("0.01")
        )

    # ========================================================
    # PAYMENT SUMMARY
    # ========================================================

    @staticmethod
    def summary(
        payment: Payment
    ) -> dict:
        """
        Return safe payment information.

        Does not expose sensitive credentials.
        """

        return {

            "payment_id":
                payment.payment_id,

            "ride_id":
                payment.ride_id,

            "passenger_id":
                payment.passenger_id,

            "amount":
                str(payment.amount),

            "currency":
                payment.currency,

            "payment_method":
                payment.payment_method.value,

            "status":
                payment.status.value,

            "provider":
                payment.provider,

            "provider_payment_id":
                payment.provider_payment_id,

            "refund_amount":
                str(payment.refund_amount),

            "remaining_refundable":
                str(
                    PaymentManager
                    .remaining_refundable_amount(
                        payment
                    )
                ),

            "failure_reason":
                payment.failure_reason,

            "created_at":
                payment.created_at.isoformat(),

            "updated_at":
                payment.updated_at.isoformat(),
        }


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    manager = PaymentManager()

    # --------------------------------------------------------
    # Create payment
    # --------------------------------------------------------

    payment = manager.create_payment(

        ride_id="RIDE-1001",

        passenger_id="USER-501",

        amount=450.00,

        payment_method=PaymentMethod.UPI,

        provider="example-provider",
    )

    print(
        "\nPayment Created"
    )

    print(
        manager.summary(payment)
    )

    # --------------------------------------------------------
    # Payment lifecycle
    # --------------------------------------------------------

    manager.mark_pending(
        payment
    )

    print(
        "\nStatus:",
        payment.status.value
    )

    manager.mark_processing(
        payment
    )

    print(
        "Status:",
        payment.status.value
    )

    # --------------------------------------------------------
    # Successful payment
    # --------------------------------------------------------

    manager.mark_success(

        payment,

        provider_payment_id=(
            "PROVIDER-TXN-12345"
        )
    )

    print(
        "Status:",
        payment.status.value
    )

    # --------------------------------------------------------
    # Partial refund
    # --------------------------------------------------------

    manager.refund_payment(
        payment,
        refund_amount=100
    )

    print(
        "\nAfter ₹100 refund:"
    )

    print(
        manager.summary(payment)
    )

    # --------------------------------------------------------
    # Full remaining refund
    # --------------------------------------------------------

    manager.refund_payment(
        payment
    )

    print(
        "\nAfter full refund:"
    )

    print(
        manager.summary(payment)
    )
