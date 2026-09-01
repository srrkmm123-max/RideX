

"""
RideX Pricing Service - Fare Engine

Responsibilities:
    - Calculate base fare
    - Calculate distance charge
    - Calculate time charge
    - Apply surge pricing
    - Apply discounts
    - Calculate taxes
    - Calculate final fare
    - Provide fare breakdown

This module contains pricing logic only.
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_CURRENCY = "INR"

MINIMUM_FARE = Decimal("40.00")

DEFAULT_TAX_RATE = Decimal("0.05")

MAX_SURGE_MULTIPLIER = Decimal("3.00")


# ============================================================
# VEHICLE PRICING
# ============================================================

@dataclass(frozen=True)
class VehiclePricing:
    """
    Pricing configuration for a vehicle category.
    """

    vehicle_type: str

    base_fare: Decimal

    per_km: Decimal

    per_minute: Decimal

    minimum_fare: Decimal

    booking_fee: Decimal


# ============================================================
# FARE RESULT
# ============================================================

@dataclass
class FareResult:
    """
    Complete fare calculation result.
    """

    vehicle_type: str

    currency: str

    distance_km: Decimal

    duration_minutes: Decimal

    base_fare: Decimal

    distance_charge: Decimal

    time_charge: Decimal

    booking_fee: Decimal

    subtotal: Decimal

    surge_multiplier: Decimal

    surge_charge: Decimal

    discount: Decimal

    taxable_amount: Decimal

    tax: Decimal

    final_fare: Decimal


# ============================================================
# DEFAULT VEHICLE PRICES
# ============================================================

DEFAULT_VEHICLE_PRICING = {

    "standard": VehiclePricing(
        vehicle_type="standard",
        base_fare=Decimal("40.00"),
        per_km=Decimal("14.00"),
        per_minute=Decimal("2.00"),
        minimum_fare=Decimal("50.00"),
        booking_fee=Decimal("10.00")
    ),

    "premium": VehiclePricing(
        vehicle_type="premium",
        base_fare=Decimal("80.00"),
        per_km=Decimal("22.00"),
        per_minute=Decimal("3.50"),
        minimum_fare=Decimal("100.00"),
        booking_fee=Decimal("20.00")
    ),

    "xl": VehiclePricing(
        vehicle_type="xl",
        base_fare=Decimal("70.00"),
        per_km=Decimal("20.00"),
        per_minute=Decimal("3.00"),
        minimum_fare=Decimal("90.00"),
        booking_fee=Decimal("15.00")
    )
}


# ============================================================
# FARE ENGINE
# ============================================================

class FareEngine:
    """
    RideX fare calculation engine.
    """

    def __init__(
        self,
        vehicle_pricing: Optional[
            dict[str, VehiclePricing]
        ] = None,
        tax_rate: Decimal = DEFAULT_TAX_RATE
    ):

        self.vehicle_pricing = (
            vehicle_pricing
            or DEFAULT_VEHICLE_PRICING
        )

        self.tax_rate = (
            Decimal(tax_rate)
        )

        if self.tax_rate < 0:

            raise ValueError(
                "Tax rate cannot be negative"
            )

    # ========================================================
    # DECIMAL CONVERSION
    # ========================================================

    @staticmethod
    def money(
        value
    ) -> Decimal:
        """
        Convert value to currency-safe Decimal.
        """

        return Decimal(
            str(value)
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

    # ========================================================
    # VEHICLE CONFIGURATION
    # ========================================================

    def get_vehicle_pricing(
        self,
        vehicle_type: str
    ) -> VehiclePricing:
        """
        Return pricing configuration.
        """

        vehicle_type = (
            vehicle_type.lower()
            .strip()
        )

        pricing = (
            self.vehicle_pricing.get(
                vehicle_type
            )
        )

        if pricing is None:

            raise ValueError(
                f"Unsupported vehicle type: "
                f"{vehicle_type}"
            )

        return pricing

    # ========================================================
    # VALIDATE INPUT
    # ========================================================

    @staticmethod
    def validate_trip(
        distance_km,
        duration_minutes
    ) -> None:

        if Decimal(
            str(distance_km)
        ) < 0:

            raise ValueError(
                "Distance cannot be negative"
            )

        if Decimal(
            str(duration_minutes)
        ) < 0:

            raise ValueError(
                "Duration cannot be negative"
            )

    # ========================================================
    # BASE FARE
    # ========================================================

    def calculate_base_fare(
        self,
        pricing: VehiclePricing
    ) -> Decimal:

        return self.money(
            pricing.base_fare
        )

    # ========================================================
    # DISTANCE CHARGE
    # ========================================================

    def calculate_distance_charge(
        self,
        distance_km,
        pricing: VehiclePricing
    ) -> Decimal:

        distance = Decimal(
            str(distance_km)
        )

        charge = (
            distance
            * pricing.per_km
        )

        return self.money(
            charge
        )

    # ========================================================
    # TIME CHARGE
    # ========================================================

    def calculate_time_charge(
        self,
        duration_minutes,
        pricing: VehiclePricing
    ) -> Decimal:

        duration = Decimal(
            str(duration_minutes)
        )

        charge = (
            duration
            * pricing.per_minute
        )

        return self.money(
            charge
        )

    # ========================================================
    # SUBTOTAL
    # ========================================================

    def calculate_subtotal(
        self,
        base_fare: Decimal,
        distance_charge: Decimal,
        time_charge: Decimal,
        booking_fee: Decimal,
        minimum_fare: Decimal
    ) -> Decimal:
        """
        Calculate subtotal before surge,
        discounts and tax.
        """

        calculated = (
            base_fare
            +
            distance_charge
            +
            time_charge
            +
            booking_fee
        )

        # Enforce minimum fare.
        calculated = max(
            calculated,
            minimum_fare
        )

        return self.money(
            calculated
        )

    # ========================================================
    # SURGE CHARGE
    # ========================================================

    def calculate_surge(
        self,
        subtotal: Decimal,
        surge_multiplier: Decimal
    ) -> tuple[
        Decimal,
        Decimal
    ]:
        """
        Calculate surge charge.

        Example:

            subtotal = ₹200
            multiplier = 1.5

            surge fare = ₹300
            surge charge = ₹100
        """

        multiplier = Decimal(
            str(surge_multiplier)
        )

        if multiplier < 1:

            raise ValueError(
                "Surge multiplier must be >= 1"
            )

        if multiplier > MAX_SURGE_MULTIPLIER:

            raise ValueError(
                f"Surge multiplier cannot exceed "
                f"{MAX_SURGE_MULTIPLIER}"
            )

        surged_total = (
            subtotal
            * multiplier
        )

        surge_charge = (
            surged_total
            - subtotal
        )

        return (
            self.money(surged_total),
            self.money(surge_charge)
        )

    # ========================================================
    # DISCOUNT
    # ========================================================

    def apply_discount(
        self,
        amount: Decimal,
        discount: Decimal
    ) -> Decimal:

        discount = Decimal(
            str(discount)
        )

        if discount < 0:

            raise ValueError(
                "Discount cannot be negative"
            )

        discount = min(
            discount,
            amount
        )

        return self.money(
            amount - discount
        )

    # ========================================================
    # TAX
    # ========================================================

    def calculate_tax(
        self,
        taxable_amount: Decimal
    ) -> Decimal:

        tax = (
            taxable_amount
            * self.tax_rate
        )

        return self.money(
            tax
        )

    # ========================================================
    # FINAL FARE
    # ========================================================

    def calculate_fare(
        self,
        distance_km,
        duration_minutes,
        vehicle_type: str = "standard",
        surge_multiplier=Decimal("1.0"),
        discount=Decimal("0.00"),
        currency: str = DEFAULT_CURRENCY
    ) -> FareResult:
        """
        Calculate complete ride fare.
        """

        self.validate_trip(
            distance_km,
            duration_minutes
        )

        pricing = (
            self.get_vehicle_pricing(
                vehicle_type
            )
        )

        distance = Decimal(
            str(distance_km)
        )

        duration = Decimal(
            str(duration_minutes)
        )

        # ----------------------------------------------------
        # Components
        # ----------------------------------------------------

        base_fare = (
            self.calculate_base_fare(
                pricing
            )
        )

        distance_charge = (
            self.calculate_distance_charge(
                distance,
                pricing
            )
        )

        time_charge = (
            self.calculate_time_charge(
                duration,
                pricing
            )
        )

        booking_fee = self.money(
            pricing.booking_fee
        )

        # ----------------------------------------------------
        # Subtotal
        # ----------------------------------------------------

        subtotal = (
            self.calculate_subtotal(
                base_fare,
                distance_charge,
                time_charge,
                booking_fee,
                pricing.minimum_fare
            )
        )

        # ----------------------------------------------------
        # Surge
        # ----------------------------------------------------

        surged_total, surge_charge = (
            self.calculate_surge(
                subtotal,
                Decimal(
                    str(surge_multiplier)
                )
            )
        )

        # ----------------------------------------------------
        # Discount
        # ----------------------------------------------------

        discount_amount = min(
            Decimal(str(discount)),
            surged_total
        )

        discount_amount = self.money(
            discount_amount
        )

        taxable_amount = (
            surged_total
            -
            discount_amount
        )

        taxable_amount = max(
            taxable_amount,
            Decimal("0.00")
        )

        taxable_amount = self.money(
            taxable_amount
        )

        # ----------------------------------------------------
        # Tax
        # ----------------------------------------------------

        tax = self.calculate_tax(
            taxable_amount
        )

        # ----------------------------------------------------
        # Final fare
        # ----------------------------------------------------

        final_fare = self.money(
            taxable_amount
            +
            tax
        )

        return FareResult(

            vehicle_type=(
                vehicle_type.lower()
            ),

            currency=currency,

            distance_km=self.money(
                distance
            ),

            duration_minutes=self.money(
                duration
            ),

            base_fare=base_fare,

            distance_charge=distance_charge,

            time_charge=time_charge,

            booking_fee=booking_fee,

            subtotal=subtotal,

            surge_multiplier=(
                Decimal(
                    str(surge_multiplier)
                )
            ),

            surge_charge=surge_charge,

            discount=discount_amount,

            taxable_amount=taxable_amount,

            tax=tax,

            final_fare=final_fare
        )

    # ========================================================
    # FARE ESTIMATE
    # ========================================================

    def estimate_fare(
        self,
        distance_km,
        duration_minutes,
        vehicle_type="standard",
        surge_multiplier=Decimal("1.0")
    ) -> FareResult:
        """
        Generate fare estimate without discount.
        """

        return self.calculate_fare(
            distance_km=distance_km,
            duration_minutes=duration_minutes,
            vehicle_type=vehicle_type,
            surge_multiplier=surge_multiplier,
            discount=Decimal("0.00")
        )


# ============================================================
# SIMPLE FUNCTION API
# ============================================================

def calculate_fare(
    distance_km,
    duration_minutes,
    vehicle_type="standard",
    surge_multiplier=1.0,
    discount=0.0
) -> FareResult:
    """
    Convenience function for service.py.
    """

    engine = FareEngine()

    return engine.calculate_fare(
        distance_km=distance_km,
        duration_minutes=duration_minutes,
        vehicle_type=vehicle_type,
        surge_multiplier=surge_multiplier,
        discount=discount
    )


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    engine = FareEngine()

    # Example:
    # 12 km ride
    # 30 minutes
    # Standard vehicle
    # 1.2x surge

    result = engine.calculate_fare(

        distance_km=12,

        duration_minutes=30,

        vehicle_type="standard",

        surge_multiplier=Decimal("1.2"),

        discount=Decimal("20")
    )

    print(
        "\nRideX Fare Estimate"
    )

    print(
        "----------------------------"
    )

    print(
        f"Vehicle: "
        f"{result.vehicle_type}"
    )

    print(
        f"Distance: "
        f"{result.distance_km} km"
    )

    print(
        f"Duration: "
        f"{result.duration_minutes} min"
    )

    print(
        f"Base Fare: "
        f"₹{result.base_fare}"
    )

    print(
        f"Distance Charge: "
        f"₹{result.distance_charge}"
    )

    print(
        f"Time Charge: "
        f"₹{result.time_charge}"
    )

    print(
        f"Booking Fee: "
        f"₹{result.booking_fee}"
    )

    print(
        f"Subtotal: "
        f"₹{result.subtotal}"
    )

    print(
        f"Surge: "
        f"{result.surge_multiplier}x"
    )

    print(
        f"Surge Charge: "
        f"₹{result.surge_charge}"
    )

    print(
        f"Discount: "
        f"-₹{result.discount}"
    )

    print(
        f"Tax: "
        f"₹{result.tax}"
    )

    print(
        "----------------------------"
    )

    print(
        f"FINAL FARE: "
        f"₹{result.final_fare}"
    )
