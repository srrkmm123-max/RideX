"""
RideX Matching Engine

Responsibilities:
    - Find nearby available drivers
    - Calculate distance
    - Filter drivers
    - Score drivers
    - Rank drivers
    - Select the best driver

This module contains matching logic only.
It does NOT contain FastAPI routes or database code.
"""

from dataclasses import dataclass
from math import atan2, cos, radians, sin, sqrt
from typing import Optional


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_MAX_DISTANCE_KM = 10.0

EARTH_RADIUS_KM = 6371.0


# ============================================================
# DRIVER DATA
# ============================================================

@dataclass
class DriverCandidate:
    """
    Driver information used by the matching engine.
    """

    driver_id: int

    latitude: float

    longitude: float

    vehicle_type: str = "standard"

    is_online: bool = True

    is_available: bool = True

    rating: float = 5.0

    total_rides: int = 0

    acceptance_rate: float = 1.0

    cancellation_rate: float = 0.0


# ============================================================
# MATCH RESULT
# ============================================================

@dataclass
class MatchResult:
    """
    Result returned by the matching engine.
    """

    driver_id: int

    distance_km: float

    score: float

    rating: float

    acceptance_rate: float


# ============================================================
# MATCHING ENGINE
# ============================================================

class MatchingEngine:
    """
    RideX driver matching engine.
    """

    def __init__(
        self,
        max_distance_km: float = DEFAULT_MAX_DISTANCE_KM
    ):

        self.max_distance_km = (
            max_distance_km
        )

    # ========================================================
    # VALIDATE COORDINATES
    # ========================================================

    @staticmethod
    def validate_coordinates(
        latitude: float,
        longitude: float
    ) -> None:

        if not -90 <= latitude <= 90:

            raise ValueError(
                "Latitude must be between -90 and 90"
            )

        if not -180 <= longitude <= 180:

            raise ValueError(
                "Longitude must be between -180 and 180"
            )

    # ========================================================
    # DISTANCE CALCULATION
    # ========================================================

    @staticmethod
    def calculate_distance(
        latitude1: float,
        longitude1: float,
        latitude2: float,
        longitude2: float
    ) -> float:
        """
        Calculate distance between two GPS coordinates
        using the Haversine formula.

        Returns:
            Distance in kilometers.
        """

        MatchingEngine.validate_coordinates(
            latitude1,
            longitude1
        )

        MatchingEngine.validate_coordinates(
            latitude2,
            longitude2
        )

        lat1 = radians(latitude1)

        lat2 = radians(latitude2)

        delta_lat = radians(
            latitude2 - latitude1
        )

        delta_lon = radians(
            longitude2 - longitude1
        )

        a = (
            sin(delta_lat / 2) ** 2
            +
            cos(lat1)
            *
            cos(lat2)
            *
            sin(delta_lon / 2) ** 2
        )

        c = 2 * atan2(
            sqrt(a),
            sqrt(1 - a)
        )

        return (
            EARTH_RADIUS_KM * c
        )

    # ========================================================
    # VEHICLE FILTER
    # ========================================================

    @staticmethod
    def vehicle_matches(
        driver: DriverCandidate,
        requested_vehicle_type: str
    ) -> bool:
        """
        Check whether driver's vehicle matches
        passenger's requested vehicle.
        """

        return (
            driver.vehicle_type.lower()
            ==
            requested_vehicle_type.lower()
        )

    # ========================================================
    # DRIVER ELIGIBILITY
    # ========================================================

    def is_eligible(
        self,
        driver: DriverCandidate,
        pickup_latitude: float,
        pickup_longitude: float,
        requested_vehicle_type: str
    ) -> bool:
        """
        Determine whether a driver can be considered.
        """

        if not driver.is_online:

            return False

        if not driver.is_available:

            return False

        if not self.vehicle_matches(
            driver,
            requested_vehicle_type
        ):

            return False

        distance = self.calculate_distance(
            pickup_latitude,
            pickup_longitude,
            driver.latitude,
            driver.longitude
        )

        if distance > self.max_distance_km:

            return False

        return True

    # ========================================================
    # DRIVER SCORE
    # ========================================================

    def calculate_score(
        self,
        driver: DriverCandidate,
        distance_km: float
    ) -> float:
        """
        Calculate driver matching score.

        Higher score = better candidate.

        Current scoring:

            50% proximity
            25% driver rating
            15% acceptance rate
            10% cancellation performance
        """

        # ----------------------------------------------------
        # DISTANCE SCORE
        # ----------------------------------------------------

        if self.max_distance_km <= 0:

            distance_score = 0

        else:

            distance_score = max(
                0,
                1 -
                (
                    distance_km
                    /
                    self.max_distance_km
                )
            )

        # ----------------------------------------------------
        # RATING SCORE
        # ----------------------------------------------------

        rating_score = min(
            max(
                driver.rating / 5.0,
                0
            ),
            1
        )

        # ----------------------------------------------------
        # ACCEPTANCE SCORE
        # ----------------------------------------------------

        acceptance_score = min(
            max(
                driver.acceptance_rate,
                0
            ),
            1
        )

        # ----------------------------------------------------
        # CANCELLATION SCORE
        # ----------------------------------------------------

        cancellation_score = max(
            0,
            1 -
            driver.cancellation_rate
        )

        # ----------------------------------------------------
        # WEIGHTED SCORE
        # ----------------------------------------------------

        score = (
            distance_score * 0.50
            +
            rating_score * 0.25
            +
            acceptance_score * 0.15
            +
            cancellation_score * 0.10
        )

        return round(
            score,
            4
        )

    # ========================================================
    # RANK DRIVERS
    # ========================================================

    def rank_drivers(
        self,
        pickup_latitude: float,
        pickup_longitude: float,
        drivers: list[DriverCandidate],
        requested_vehicle_type: str = "standard"
    ) -> list[MatchResult]:
        """
        Filter, score and rank available drivers.
        """

        results: list[
            MatchResult
        ] = []

        for driver in drivers:

            if not self.is_eligible(
                driver,
                pickup_latitude,
                pickup_longitude,
                requested_vehicle_type
            ):

                continue

            distance = self.calculate_distance(
                pickup_latitude,
                pickup_longitude,
                driver.latitude,
                driver.longitude
            )

            score = self.calculate_score(
                driver,
                distance
            )

            results.append(
                MatchResult(
                    driver_id=driver.driver_id,
                    distance_km=round(
                        distance,
                        3
                    ),
                    score=score,
                    rating=driver.rating,
                    acceptance_rate=driver.acceptance_rate
                )
            )

        # Highest score first
        results.sort(
            key=lambda result: (
                result.score,
                -result.distance_km
            ),
            reverse=True
        )

        return results

    # ========================================================
    # BEST DRIVER
    # ========================================================

    def find_best_driver(
        self,
        pickup_latitude: float,
        pickup_longitude: float,
        drivers: list[DriverCandidate],
        requested_vehicle_type: str = "standard"
    ) -> Optional[MatchResult]:
        """
        Select the highest-ranked eligible driver.
        """

        ranked_drivers = self.rank_drivers(
            pickup_latitude,
            pickup_longitude,
            drivers,
            requested_vehicle_type
        )

        if not ranked_drivers:

            return None

        return ranked_drivers[0]

    # ========================================================
    # TOP N DRIVERS
    # ========================================================

    def find_top_drivers(
        self,
        pickup_latitude: float,
        pickup_longitude: float,
        drivers: list[DriverCandidate],
        requested_vehicle_type: str = "standard",
        limit: int = 5
    ) -> list[MatchResult]:
        """
        Return the top N matching drivers.
        """

        if limit <= 0:

            return []

        ranked_drivers = self.rank_drivers(
            pickup_latitude,
            pickup_longitude,
            drivers,
            requested_vehicle_type
        )

        return ranked_drivers[:limit]


# ============================================================
# SIMPLE FUNCTION API
# ============================================================

def find_best_driver(
    pickup_latitude: float,
    pickup_longitude: float,
    drivers: list[DriverCandidate],
    requested_vehicle_type: str = "standard",
    max_distance_km: float = DEFAULT_MAX_DISTANCE_KM
) -> Optional[MatchResult]:
    """
    Convenience function for other modules.
    """

    engine = MatchingEngine(
        max_distance_km=max_distance_km
    )

    return engine.find_best_driver(
        pickup_latitude,
        pickup_longitude,
        drivers,
        requested_vehicle_type
    )


# ============================================================
# TEST / DEMO
# ============================================================

if __name__ == "__main__":

    drivers = [

        DriverCandidate(
            driver_id=101,
            latitude=17.3850,
            longitude=78.4867,
            vehicle_type="standard",
            rating=4.8,
            acceptance_rate=0.95,
            cancellation_rate=0.03
        ),

        DriverCandidate(
            driver_id=102,
            latitude=17.4000,
            longitude=78.4900,
            vehicle_type="standard",
            rating=4.6,
            acceptance_rate=0.90,
            cancellation_rate=0.05
        ),

        DriverCandidate(
            driver_id=103,
            latitude=17.3500,
            longitude=78.4500,
            vehicle_type="standard",
            rating=4.9,
            acceptance_rate=0.98,
            cancellation_rate=0.02
        ),

        DriverCandidate(
            driver_id=104,
            latitude=17.3900,
            longitude=78.4800,
            vehicle_type="premium",
            rating=4.9,
            acceptance_rate=0.97,
            cancellation_rate=0.01
        )
    ]

    pickup_latitude = 17.3850

    pickup_longitude = 78.4867

    engine = MatchingEngine(
        max_distance_km=10
    )

    best_driver = engine.find_best_driver(
        pickup_latitude,
        pickup_longitude,
        drivers,
        requested_vehicle_type="standard"
    )

    print(
        "Best Driver:"
    )

    print(
        best_driver
    )

    print(
        "\nTop Drivers:"
    )

    top_drivers = engine.find_top_drivers(
        pickup_latitude,
        pickup_longitude,
        drivers,
        requested_vehicle_type="standard",
        limit=5
    )

    for driver in top_drivers:

        print(driver)
