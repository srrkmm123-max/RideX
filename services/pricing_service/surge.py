"""
RideX Pricing Service - Surge Pricing Engine

Responsibilities:
    - Calculate demand/supply ratio
    - Determine surge multiplier
    - Apply configurable surge limits
    - Provide surge information
    - Support manual/admin surge overrides

This module contains pricing logic only.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_MIN_MULTIPLIER = Decimal("1.00")

DEFAULT_MAX_MULTIPLIER = Decimal("3.00")

DEFAULT_TARGET_RATIO = Decimal("2.00")

DEFAULT_SMOOTHING_FACTOR = Decimal("0.50")


# ============================================================
# SURGE RESULT
# ============================================================

@dataclass
class SurgeResult:
    """
    Result of surge calculation.
    """

    multiplier: Decimal

    demand: int

    available_drivers: int

    demand_supply_ratio: Decimal

    reason: str

    is_surge_active: bool


# ============================================================
# SURGE CONFIGURATION
# ============================================================

@dataclass
class SurgeConfig:
    """
    Configuration for dynamic pricing.
    """

    min_multiplier: Decimal = DEFAULT_MIN_MULTIPLIER

    max_multiplier: Decimal = DEFAULT_MAX_MULTIPLIER

    target_ratio: Decimal = DEFAULT_TARGET_RATIO

    smoothing_factor: Decimal = DEFAULT_SMOOTHING_FACTOR


# ============================================================
# SURGE ENGINE
# ============================================================

class SurgeEngine:
    """
    RideX dynamic surge pricing engine.

    The basic principle is:

        Demand ↑
        Drivers ↓
        Ratio ↑
        Surge ↑

    Example:

        10 ride requests
        5 available drivers

        Demand/Supply = 2.0
    """

    def __init__(
        self,
        config: Optional[SurgeConfig] = None
    ):

        self.config = (
            config
            or SurgeConfig()
        )

        self._validate_config()

    # ========================================================
    # VALIDATE CONFIGURATION
    # ========================================================

    def _validate_config(self) -> None:

        if (
            self.config.min_multiplier
            < Decimal("1.0")
        ):

            raise ValueError(
                "Minimum multiplier cannot be below 1.0"
            )

        if (
            self.config.max_multiplier
            <
            self.config.min_multiplier
        ):

            raise ValueError(
                "Maximum multiplier must be >= minimum multiplier"
            )

        if self.config.target_ratio <= 0:

            raise ValueError(
                "Target ratio must be greater than zero"
            )

        if not (
            Decimal("0")
            <=
            self.config.smoothing_factor
            <=
            Decimal("1")
        ):

            raise ValueError(
                "Smoothing factor must be between 0 and 1"
            )

    # ========================================================
    # DEMAND / SUPPLY RATIO
    # ========================================================

    @staticmethod
    def calculate_ratio(
        demand: int,
        available_drivers: int
    ) -> Decimal:
        """
        Calculate demand-to-driver ratio.
        """

        if demand < 0:

            raise ValueError(
                "Demand cannot be negative"
            )

        if available_drivers < 0:

            raise ValueError(
                "Available drivers cannot be negative"
            )

        # No drivers available.
        if available_drivers == 0:

            if demand > 0:

                return Decimal("999.99")

            return Decimal("0.00")

        ratio = (
            Decimal(demand)
            /
            Decimal(available_drivers)
        )

        return ratio.quantize(
            Decimal("0.01")
        )

    # ========================================================
    # CALCULATE RAW MULTIPLIER
    # ========================================================

    def calculate_raw_multiplier(
        self,
        demand: int,
        available_drivers: int
    ) -> Decimal:
        """
        Calculate multiplier from demand/supply.

        Formula:

            multiplier =
                demand/supply
                /
                target_ratio

        Then add 1.0 to represent the normal fare.

        Example:

            ratio = 2
            target = 2

            multiplier = 2.0

        Low demand results in 1.0.
        """

        ratio = self.calculate_ratio(
            demand,
            available_drivers
        )

        if ratio <= self.config.target_ratio:

            return Decimal("1.00")

        excess_ratio = (
            ratio
            /
            self.config.target_ratio
        )

        multiplier = (
            Decimal("1.00")
            +
            (
                excess_ratio
                -
                Decimal("1.00")
            )
        )

        return multiplier

    # ========================================================
    # SMOOTH MULTIPLIER
    # ========================================================

    def smooth_multiplier(
        self,
        multiplier: Decimal,
        previous_multiplier: Optional[
            Decimal
        ] = None
    ) -> Decimal:
        """
        Smooth sudden changes in surge pricing.

        Formula:

            new =
                previous * smoothing
                +
                current * (1 - smoothing)
        """

        if previous_multiplier is None:

            return multiplier

        smoothing = (
            self.config.smoothing_factor
        )

        result = (
            previous_multiplier
            * smoothing
            +
            multiplier
            * (
                Decimal("1")
                -
                smoothing
            )
        )

        return result

    # ========================================================
    # APPLY LIMITS
    # ========================================================

    def clamp_multiplier(
        self,
        multiplier: Decimal
    ) -> Decimal:
        """
        Keep surge multiplier within configured limits.
        """

        multiplier = max(
            multiplier,
            self.config.min_multiplier
        )

        multiplier = min(
            multiplier,
            self.config.max_multiplier
        )

        return multiplier.quantize(
            Decimal("0.01")
        )

    # ========================================================
    # CALCULATE SURGE
    # ========================================================

    def calculate_surge(
        self,
        demand: int,
        available_drivers: int,
        previous_multiplier: Optional[
            Decimal
        ] = None
    ) -> SurgeResult:
        """
        Calculate current surge multiplier.
        """

        ratio = self.calculate_ratio(
            demand,
            available_drivers
        )

        raw_multiplier = (
            self.calculate_raw_multiplier(
                demand,
                available_drivers
            )
        )

        smoothed_multiplier = (
            self.smooth_multiplier(
                raw_multiplier,
                previous_multiplier
            )
        )

        multiplier = (
            self.clamp_multiplier(
                smoothed_multiplier
            )
        )

        # ----------------------------------------------------
        # Reason
        # ----------------------------------------------------

        if available_drivers == 0 and demand > 0:

            reason = (
                "No available drivers"
            )

        elif multiplier > Decimal("1.00"):

            reason = (
                "High demand relative to "
                "available drivers"
            )

        else:

            reason = (
                "Normal demand/supply"
            )

        return SurgeResult(

            multiplier=multiplier,

            demand=demand,

            available_drivers=available_drivers,

            demand_supply_ratio=ratio,

            reason=reason,

            is_surge_active=(
                multiplier > Decimal("1.00")
            )
        )

    # ========================================================
    # MANUAL SURGE
    # ========================================================

    def manual_surge(
        self,
        multiplier: Decimal
    ) -> Decimal:
        """
        Apply an administrator-controlled surge multiplier.

        Example:

            Admin sets 1.5x surge.
        """

        multiplier = Decimal(
            str(multiplier)
        )

        if multiplier < Decimal("1.00"):

            raise ValueError(
                "Surge multiplier cannot be below 1.0"
            )

        return self.clamp_multiplier(
            multiplier
        )

    # ========================================================
    # AREA SURGE
    # ========================================================

    def calculate_area_surge(
        self,
        demand: int,
        available_drivers: int,
        area_name: str,
        previous_multiplier: Optional[
            Decimal
        ] = None
    ) -> dict:
        """
        Return surge information for a geographic area.
        """

        result = self.calculate_surge(
            demand=demand,
            available_drivers=available_drivers,
            previous_multiplier=previous_multiplier
        )

        return {
            "area": area_name,

            "multiplier": (
                result.multiplier
            ),

            "demand": result.demand,

            "available_drivers": (
                result.available_drivers
            ),

            "demand_supply_ratio": (
                result.demand_supply_ratio
            ),

            "surge_active": (
                result.is_surge_active
            ),

            "reason": result.reason
        }


# ============================================================
# SIMPLE FUNCTION API
# ============================================================

def calculate_surge_multiplier(
    demand: int,
    available_drivers: int
) -> Decimal:
    """
    Convenience function for service.py.
    """

    engine = SurgeEngine()

    result = engine.calculate_surge(
        demand=demand,
        available_drivers=available_drivers
    )

    return result.multiplier


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    engine = SurgeEngine()

    examples = [
        (5, 10),
        (10, 10),
        (10, 5),
        (20, 5),
        (30, 5),
        (50, 2),
        (20, 0)
    ]

    print(
        "\nRideX Surge Pricing"
    )

    print(
        "=============================="
    )

    for demand, drivers in examples:

        result = engine.calculate_surge(
            demand=demand,
            available_drivers=drivers
        )

        print(
            f"Demand: {demand:>3} | "
            f"Drivers: {drivers:>3} | "
            f"Ratio: "
            f"{result.demand_supply_ratio:>6} | "
            f"Surge: "
            f"{result.multiplier}x | "
            f"{result.reason}"
        )
