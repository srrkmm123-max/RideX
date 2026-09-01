"""
RideX Matching Service - Driver Search

Responsibilities:
    - Search for nearby drivers
    - Filter online/available drivers
    - Filter by vehicle type
    - Calculate distance
    - Expand search radius when necessary

This module does NOT:
    - Handle FastAPI routes
    - Perform driver assignment
    - Calculate final ride fare

Those responsibilities belong to routes.py,
service.py, and matching_engine.py.
"""

from dataclasses import dataclass
from math import atan2, cos, radians, sin, sqrt
from typing import Optional


# ============================================================
# CONFIGURATION
# ============================================================

EARTH_RADIUS_KM = 6371.0

DEFAULT_SEARCH_RADIUS_KM = 5.0

MAX_SEARCH_RADIUS_KM = 20.0

SEARCH_RADIUS_INCREMENT_KM = 5.0


# ============================================================
# DRIVER LOCATION
# ============================================================

@dataclass
class DriverLocation:
    """
    Driver's current GPS/location information.
    """

    driver_id: int

    latitude: float

    longitude: float

    vehicle_type: str = "standard"

    is_online: bool = True

    is_available: bool = True

    rating: float = 5.0


# ============================================================
# SEARCH RESULT
# ============================================================

@dataclass
class DriverSearchResult:
    """
    Driver returned from nearby-driver search.
    """

    driver_id: int

    latitude: float

    longitude: float

    vehicle_type: str

    distance_km: float

    rating: float


# ============================================================
# DRIVER SEARCH CLASS
# ============================================================

class DriverSearch:
    """
    Finds nearby eligible drivers.
    """

    def __init__(
        self,
        default_radius_km: float = DEFAULT_SEARCH_RADIUS_KM,
        max_radius_km: float = MAX_SEARCH_RADIUS_KM
    ):

        if default_radius_km <= 0:

            raise ValueError(
                "Default radius must be greater than zero"
            )

        if max_radius_km <= 0:

            raise ValueError(
                "Maximum radius must be greater than zero"
            )

        if default_radius_km > max_radius_km:

            raise ValueError(
                "Default radius cannot exceed maximum radius"
            )

        self.default_radius_km = (
            default_radius_km
        )

        self.max_radius_km = (
            max_radius_km
        )

    # ========================================================
    # VALIDATE GPS
    # ========================================================

    @staticmethod
    def validate_coordinates(
        latitude: float,
        longitude: float
    ) -> None:
        """
        Validate latitude and longitude.
        """

        if not -90 <= latitude <= 90:

            raise ValueError(
                "Latitude must be between -90 and 90"
            )

        if not -180 <= longitude <= 180:

            raise ValueError(
                "Longitude must be between -180 and 180"
            )

    # ========================================================
    # DISTANCE
    # ========================================================

    @staticmethod
    def calculate_distance(
        latitude1: float,
        longitude1: float,
        latitude2: float,
        longitude2: float
    ) -> float:
        """
        Calculate straight-line distance using
        the Haversine formula.

        Returns:
            Distance in kilometers.
        """

        DriverSearch.validate_coordinates(
            latitude1,
            longitude1
        )

        DriverSearch.validate_coordinates(
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
            * cos(lat2)
            * sin(delta_lon / 2) ** 2
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
        driver: DriverLocation,
        vehicle_type: Optional[str]
    ) -> bool:
        """
        Check requested vehicle type.
        """

        if not vehicle_type:

            return True

        return (
            driver.vehicle_type.lower()
            ==
            vehicle_type.lower()
        )

    # ========================================================
    # DRIVER ELIGIBILITY
    # ========================================================

    @staticmethod
    def is_eligible(
        driver: DriverLocation
    ) -> bool:
        """
        Check whether driver can receive a ride.
        """

        return (
            driver.is_online
            and
            driver.is_available
        )

    # ========================================================
    # SEARCH
    # ========================================================

    def search(
        self,
        pickup_latitude: float,
        pickup_longitude: float,
        drivers: list[DriverLocation],
        radius_km: Optional[float] = None,
        vehicle_type: Optional[str] = None,
        limit: int = 20
    ) -> list[DriverSearchResult]:
        """
        Find nearby available drivers.

        Parameters:
            pickup_latitude:
                Passenger pickup latitude.

            pickup_longitude:
                Passenger pickup longitude.

            drivers:
                Candidate driver locations.

            radius_km:
                Search radius.

            vehicle_type:
                Requested vehicle type.

            limit:
                Maximum number of drivers returned.
        """

        self.validate_coordinates(
            pickup_latitude,
            pickup_longitude
        )

        if radius_km is None:

            radius_km = (
                self.default_radius_km
            )

        if radius_km <= 0:

            raise ValueError(
                "Search radius must be greater than zero"
            )

        if radius_km > self.max_radius_km:

            radius_km = (
                self.max_radius_km
            )

        if limit <= 0:

            return []

        results = []

        for driver in drivers:

            # ------------------------------------------------
            # Online / availability
            # ------------------------------------------------

            if not self.is_eligible(
                driver
            ):

                continue

            # ------------------------------------------------
            # Vehicle type
            # ------------------------------------------------

            if not self.vehicle_matches(
                driver,
                vehicle_type
            ):

                continue

            # ------------------------------------------------
            # Distance
            # ------------------------------------------------

            distance = self.calculate_distance(
                pickup_latitude,
                pickup_longitude,
                driver.latitude,
                driver.longitude
            )

            if distance > radius_km:

                continue

            # ------------------------------------------------
            # Add result
            # ------------------------------------------------

            results.append(
                DriverSearchResult(
                    driver_id=driver.driver_id,
                    latitude=driver.latitude,
                    longitude=driver.longitude,
                    vehicle_type=driver.vehicle_type,
                    distance_km=round(
                        distance,
                        3
                    ),
                    rating=driver.rating
                )
            )

        # Closest driver first
        results.sort(
            key=lambda driver:
                driver.distance_km
        )

        return results[:limit]

    # ========================================================
    # EXPANDING SEARCH
    # ========================================================

    def search_with_expansion(
        self,
        pickup_latitude: float,
        pickup_longitude: float,
        drivers: list[DriverLocation],
        vehicle_type: Optional[str] = None,
        initial_radius_km: Optional[float] = None,
        limit: int = 20
    ) -> list[DriverSearchResult]:
        """
        Search nearby drivers and gradually increase
        the radius when no drivers are found.

        Example:

            5 km
             ↓
            10 km
             ↓
            15 km
             ↓
            20 km
        """

        if initial_radius_km is None:

            radius = (
                self.default_radius_km
            )

        else:

            radius = initial_radius_km

        while radius <= self.max_radius_km:

            results = self.search(
                pickup_latitude=pickup_latitude,
                pickup_longitude=pickup_longitude,
                drivers=drivers,
                radius_km=radius,
                vehicle_type=vehicle_type,
                limit=limit
            )

            if results:

                return results

            radius += (
                SEARCH_RADIUS_INCREMENT_KM
            )

        return []

    # ========================================================
    # COUNT NEARBY DRIVERS
    # ========================================================

    def count_nearby_drivers(
        self,
        pickup_latitude: float,
        pickup_longitude: float,
        drivers: list[DriverLocation],
        radius_km: Optional[float] = None,
        vehicle_type: Optional[str] = None
    ) -> int:
        """
        Return number of nearby eligible drivers.
        """

        results = self.search(
            pickup_latitude,
            pickup_longitude,
            drivers,
            radius_km,
            vehicle_type,
            limit=len(drivers)
        )

        return len(results)


# ============================================================
# SIMPLE FUNCTION API
# ============================================================

def find_nearby_drivers(
    pickup_latitude: float,
    pickup_longitude: float,
    drivers: list[DriverLocation],
    radius_km: float = DEFAULT_SEARCH_RADIUS_KM,
    vehicle_type: Optional[str] = None,
    limit: int = 20
) -> list[DriverSearchResult]:
    """
    Convenience function for service.py.
    """

    search_engine = DriverSearch(
        default_radius_km=radius_km
    )

    return search_engine.search(
        pickup_latitude=pickup_latitude,
        pickup_longitude=pickup_longitude,
        drivers=drivers,
        radius_km=radius_km,
        vehicle_type=vehicle_type,
        limit=limit
    )


# ============================================================
# TEST / DEMO
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # Example drivers
    # --------------------------------------------------------

    drivers = [

        DriverLocation(
            driver_id=101,
            latitude=17.3850,
            longitude=78.4867,
            vehicle_type="standard",
            is_online=True,
            is_available=True,
            rating=4.8
        ),

        DriverLocation(
            driver_id=102,
            latitude=17.3900,
            longitude=78.4900,
            vehicle_type="standard",
            is_online=True,
            is_available=True,
            rating=4.7
        ),

        DriverLocation(
            driver_id=103,
            latitude=17.4200,
            longitude=78.5200,
            vehicle_type="premium",
            is_online=True,
            is_available=True,
            rating=4.9
        ),

        DriverLocation(
            driver_id=104,
            latitude=17.3500,
            longitude=78.4500,
            vehicle_type="standard",
            is_online=False,
            is_available=False,
            rating=4.6
        )
    ]

    # --------------------------------------------------------
    # Pickup location
    # --------------------------------------------------------

    pickup_latitude = 17.3850

    pickup_longitude = 78.4867

    # --------------------------------------------------------
    # Create search engine
    # --------------------------------------------------------

    search = DriverSearch(
        default_radius_km=5,
        max_radius_km=20
    )

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    results = search.search(
        pickup_latitude=pickup_latitude,
        pickup_longitude=pickup_longitude,
        drivers=drivers,
        radius_km=5,
        vehicle_type="standard",
        limit=10
    )

    # --------------------------------------------------------
    # Display results
    # --------------------------------------------------------

    print(
        "\nNearby Drivers:"
    )

    for result in results:

        print(
            f"Driver {result.driver_id} | "
            f"Distance: {result.distance_km} km | "
            f"Rating: {result.rating}"
        )

    # --------------------------------------------------------
    # Count
    # --------------------------------------------------------

    count = search.count_nearby_drivers(
        pickup_latitude,
        pickup_longitude,
        drivers,
        radius_km=5,
        vehicle_type="standard"
    )

    print(
        f"\nAvailable drivers: {count}"
    )
