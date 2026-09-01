"""
RideX Pricing Service - Pricing Rules

Contains configurable business rules for ride pricing.

This module does NOT:
    - Handle FastAPI
    - Access the database
    - Handle HTTP requests
    - Calculate GPS distance

The fare_engine.py uses these rules to calculate fares.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


# ============================================================
# VEHICLE PRICING RULE
# ============================================================

@dataclass(frozen=True)
class VehiclePricingRule:
    """
    Pricing rules for a vehicle category.
    """

    vehicle_type: str

    base_fare: Decimal

    per_km: Decimal

    per_minute: Decimal

    minimum_fare: Decimal

    booking_fee: Decimal

    cancellation_fee: Decimal

    waiting_per_minute: Decimal

    free_waiting_minutes: int


# ============================================================
# PEAK PERIOD RULE
# ============================================================

@dataclass(frozen=True)
class PeakPeriodRule:
    """
    Defines a time period when pricing may increase.
    """

    name: str

    start_hour: int

    start_minute: int

    end_hour: int

    end_minute: int

    multiplier: Decimal

    days: tuple[str, ...] = (
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
    )


# ============================================================
# DISCOUNT RULE
# ============================================================

@dataclass(frozen=True)
class DiscountRule:
    """
    Defines a promotional discount.
    """

    code: str

    discount_type: str

    value: Decimal

    max_discount: Optional[Decimal] = None

    minimum_fare: Decimal = Decimal("0.00")

    active: bool = True


# ============================================================
# DEFAULT VEHICLE RULES
# ============================================================

VEHICLE_PRICING_RULES = {

    "standard": VehiclePricingRule(

        vehicle_type="standard",

        base_fare=Decimal("40.00"),

        per_km=Decimal("14.00"),

        per_minute=Decimal("2.00"),

        minimum_fare=Decimal("50.00"),

        booking_fee=Decimal("10.00"),

        cancellation_fee=Decimal("50.00"),

        waiting_per_minute=Decimal("2.00"),

        free_waiting_minutes=3,
    ),

    "premium": VehiclePricingRule(

        vehicle_type="premium",

        base_fare=Decimal("80.00"),

        per_km=Decimal("22.00"),

        per_minute=Decimal("3.50"),

        minimum_fare=Decimal("100.00"),

        booking_fee=Decimal("20.00"),

        cancellation_fee=Decimal("100.00"),

        waiting_per_minute=Decimal("3.50"),

        free_waiting_minutes=5,
    ),

    "xl": VehiclePricingRule(

        vehicle_type="xl",

        base_fare=Decimal("70.00"),

        per_km=Decimal("20.00"),

        per_minute=Decimal("3.00"),

        minimum_fare=Decimal("90.00"),

        booking_fee=Decimal("15.00"),

        cancellation_fee=Decimal("75.00"),

        waiting_per_minute=Decimal("3.00"),

        free_waiting_minutes=5,
    ),
}


# ============================================================
# DEFAULT PEAK PERIODS
# ============================================================

PEAK_PERIOD_RULES = [

    PeakPeriodRule(

        name="morning_peak",

        start_hour=7,

        start_minute=0,

        end_hour=10,

        end_minute=0,

        multiplier=Decimal("1.20"),

        days=(
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
        ),
    ),

    PeakPeriodRule(

        name="evening_peak",

        start_hour=17,

        start_minute=0,

        end_hour=21,

        end_minute=0,

        multiplier=Decimal("1.25"),

        days=(
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
        ),
    ),
]


# ============================================================
# DEFAULT DISCOUNT RULES
# ============================================================

DISCOUNT_RULES = {

    "WELCOME50": DiscountRule(

        code="WELCOME50",

        discount_type="fixed",

        value=Decimal("50.00"),

        max_discount=Decimal("50.00"),

        minimum_fare=Decimal("100.00"),

        active=True,
    ),

    "RIDE10": DiscountRule(

        code="RIDE10",

        discount_type="percentage",

        value=Decimal("10.00"),

        max_discount=Decimal("100.00"),

        minimum_fare=Decimal("200.00"),

        active=True,
    ),
}


# ============================================================
# PRICING RULES CLASS
# ============================================================

class PricingRules:
    """
    Provides access to RideX pricing business rules.
    """

    def __init__(
        self,
        vehicle_rules=None,
        peak_rules=None,
        discount_rules=None,
    ):

        self.vehicle_rules = (
            vehicle_rules
            or VEHICLE_PRICING_RULES
        )

        self.peak_rules = (
            peak_rules
            or PEAK_PERIOD_RULES
        )

        self.discount_rules = (
            discount_rules
            or DISCOUNT_RULES
        )

    # ========================================================
    # VEHICLE
    # ========================================================

    def get_vehicle_rule(
        self,
        vehicle_type: str
    ) -> VehiclePricingRule:
        """
        Get pricing configuration for a vehicle.
        """

        vehicle_type = (
            vehicle_type
            .strip()
            .lower()
        )

        rule = self.vehicle_rules.get(
            vehicle_type
        )

        if rule is None:

            raise ValueError(
                f"Unknown vehicle type: "
                f"{vehicle_type}"
            )

        return rule

    # ========================================================
    # VEHICLE TYPES
    # ========================================================

    def get_vehicle_types(self) -> list[str]:
        """
        Return supported vehicle categories.
        """

        return list(
            self.vehicle_rules.keys()
        )

    # ========================================================
    # PEAK PERIOD
    # ========================================================

    def get_peak_rule(
        self,
        hour: int,
        minute: int,
        day: str
    ) -> Optional[PeakPeriodRule]:
        """
        Find active peak-period rule.

        day example:
            monday
            tuesday
        """

        if not 0 <= hour <= 23:

            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= minute <= 59:

            raise ValueError(
                "Minute must be between 0 and 59"
            )

        day = day.lower()

        current_minutes = (
            hour * 60
            + minute
        )

        for rule in self.peak_rules:

            if day not in rule.days:

                continue

            start_minutes = (
                rule.start_hour * 60
                + rule.start_minute
            )

            end_minutes = (
                rule.end_hour * 60
                + rule.end_minute
            )

            if (
                start_minutes
                <= current_minutes
                <
                end_minutes
            ):

                return rule

        return None

    # ========================================================
    # PEAK MULTIPLIER
    # ========================================================

    def get_peak_multiplier(
        self,
        hour: int,
        minute: int,
        day: str
    ) -> Decimal:
        """
        Return peak-period multiplier.

        Returns 1.00 when there is no peak period.
        """

        rule = self.get_peak_rule(
            hour,
            minute,
            day
        )

        if rule is None:

            return Decimal("1.00")

        return rule.multiplier

    # ========================================================
    # DISCOUNT
    # ========================================================

    def get_discount_rule(
        self,
        code: str
    ) -> DiscountRule:
        """
        Get discount rule by coupon code.
        """

        code = (
            code
            .strip()
            .upper()
        )

        rule = self.discount_rules.get(
            code
        )

        if rule is None:

            raise ValueError(
                f"Invalid discount code: {code}"
            )

        if not rule.active:

            raise ValueError(
                f"Discount code {code} is inactive"
            )

        return rule

    # ========================================================
    # CALCULATE DISCOUNT
    # ========================================================

    def calculate_discount(
        self,
        code: str,
        fare: Decimal
    ) -> Decimal:
        """
        Calculate discount amount.

        Supports:
            fixed
            percentage
        """

        fare = Decimal(
            str(fare)
        )

        if fare < 0:

            raise ValueError(
                "Fare cannot be negative"
            )

        rule = self.get_discount_rule(
            code
        )

        if fare < rule.minimum_fare:

            return Decimal("0.00")

        if rule.discount_type == "fixed":

            discount = rule.value

        elif rule.discount_type == "percentage":

            discount = (
                fare
                *
                rule.value
                /
                Decimal("100")
            )

        else:

            raise ValueError(
                f"Unsupported discount type: "
                f"{rule.discount_type}"
            )

        # Maximum discount
        if rule.max_discount is not None:

            discount = min(
                discount,
                rule.max_discount
            )

        # Discount cannot exceed fare
        discount = min(
            discount,
            fare
        )

        return discount.quantize(
            Decimal("0.01")
        )

    # ========================================================
    # WAITING FEE
    # ========================================================

    def calculate_waiting_fee(
        self,
        vehicle_type: str,
        waiting_minutes: int
    ) -> Decimal:
        """
        Calculate passenger waiting charge.
        """

        if waiting_minutes < 0:

            raise ValueError(
                "Waiting time cannot be negative"
            )

        rule = self.get_vehicle_rule(
            vehicle_type
        )

        chargeable_minutes = max(
            0,
            waiting_minutes
            -
            rule.free_waiting_minutes
        )

        fee = (
            Decimal(chargeable_minutes)
            *
            rule.waiting_per_minute
        )

        return fee.quantize(
            Decimal("0.01")
        )

    # ========================================================
    # CANCELLATION FEE
    # ========================================================

    def get_cancellation_fee(
        self,
        vehicle_type: str
    ) -> Decimal:
        """
        Return cancellation fee.
        """

        rule = self.get_vehicle_rule(
            vehicle_type
        )

        return rule.cancellation_fee

    # ========================================================
    # PRICING SUMMARY
    # ========================================================

    def get_pricing_summary(
        self,
        vehicle_type: str
    ) -> dict:

        rule = self.get_vehicle_rule(
            vehicle_type
        )

        return {

            "vehicle_type":
                rule.vehicle_type,

            "base_fare":
                rule.base_fare,

            "per_km":
                rule.per_km,

            "per_minute":
                rule.per_minute,

            "minimum_fare":
                rule.minimum_fare,

            "booking_fee":
                rule.booking_fee,

            "cancellation_fee":
                rule.cancellation_fee,

            "waiting_per_minute":
                rule.waiting_per_minute,

            "free_waiting_minutes":
                rule.free_waiting_minutes,
        }


# ============================================================
# SIMPLE FUNCTIONS
# ============================================================

def get_vehicle_pricing(
    vehicle_type: str
) -> VehiclePricingRule:
    """
    Convenience function.
    """

    rules = PricingRules()

    return rules.get_vehicle_rule(
        vehicle_type
    )


def get_peak_multiplier(
    hour: int,
    minute: int,
    day: str
) -> Decimal:
    """
    Convenience function.
    """

    rules = PricingRules()

    return rules.get_peak_multiplier(
        hour,
        minute,
        day
    )


def calculate_waiting_fee(
    vehicle_type: str,
    waiting_minutes: int
) -> Decimal:
    """
    Convenience function.
    """

    rules = PricingRules()

    return rules.calculate_waiting_fee(
        vehicle_type,
        waiting_minutes
    )


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    rules = PricingRules()

    print(
        "\nRideX Pricing Rules"
    )

    print(
        "=============================="
    )

    # --------------------------------------------------------
    # Vehicle pricing
    # --------------------------------------------------------

    for vehicle in rules.get_vehicle_types():

        summary = (
            rules.get_pricing_summary(
                vehicle
            )
        )

        print(
            f"\nVehicle: {vehicle}"
        )

        print(
            f"Base Fare: "
            f"₹{summary['base_fare']}"
        )

        print(
            f"Per KM: "
            f"₹{summary['per_km']}"
        )

        print(
            f"Per Minute: "
            f"₹{summary['per_minute']}"
        )

        print(
            f"Minimum Fare: "
            f"₹{summary['minimum_fare']}"
        )

    # --------------------------------------------------------
    # Peak pricing
    # --------------------------------------------------------

    peak = rules.get_peak_rule(
        hour=18,
        minute=30,
        day="monday"
    )

    if peak:

        print(
            "\nPeak Period:"
        )

        print(
            peak.name
        )

        print(
            f"Multiplier: "
            f"{peak.multiplier}x"
        )

    # --------------------------------------------------------
    # Waiting fee
    # --------------------------------------------------------

    waiting_fee = (
        rules.calculate_waiting_fee(
            vehicle_type="standard",
            waiting_minutes=10
        )
    )

    print(
        f"\nWaiting fee for 10 minutes: "
        f"₹{waiting_fee}"
    )

    # --------------------------------------------------------
    # Discount
    # --------------------------------------------------------

    discount = (
        rules.calculate_discount(
            code="RIDE10",
            fare=Decimal("500.00")
        )
    )

    print(
        f"RIDE10 discount on ₹500: "
        f"₹{discount}"
    )
