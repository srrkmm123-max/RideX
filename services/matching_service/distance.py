"""
RideX Matching Service - Distance Utilities

Responsibilities:
    - Validate GPS coordinates
    - Calculate Haversine distance
    - Calculate approximate bounding box
    - Calculate distances for multiple locations

Units:
    - Distance: kilometers
    - Latitude/Longitude: decimal degrees
"""

from math import (
    atan2,
    cos,
    degrees,
    radians,
    sin,
    sqrt,
)


# ============================================================
# CONSTANTS
# ============================================================

EARTH_RADIUS_KM = 6371.0088


# ============================================================
# COORDINATE VALIDATION
# ============================================================

def validate_latitude(
    latitude: float
) -> None:
    """
    Validate latitude.

    Valid range:
        -90 to +90
    """

    if not isinstance(
        latitude,
        (int, float)
    ):

        raise TypeError(
            "Latitude must be a number"
        )

    if not -90 <= latitude <= 90:

        raise ValueError(
            "Latitude must be between -90 and 90"
        )


def validate_longitude(
    longitude: float
) -> None:
    """
    Validate longitude.

    Valid range:
        -180 to +180
    """

    if not isinstance(
        longitude,
        (int, float)
    ):

        raise TypeError(
            "Longitude must be a number"
        )

    if not -180 <= longitude <= 180:

        raise ValueError(
            "Longitude must be between -180 and 180"
        )


def validate_coordinates(
    latitude: float,
    longitude: float
) -> None:
    """
    Validate latitude and longitude.
    """

    validate_latitude(
        latitude
    )

    validate_longitude(
        longitude
    )


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def haversine_distance(
    latitude1: float,
    longitude1: float,
    latitude2: float,
    longitude2: float
) -> float:
    """
    Calculate the great-circle distance between
    two GPS coordinates.

    Returns:
        Distance in kilometers.

    Example:

        distance = haversine_distance(
            17.3850,
            78.4867,
            17.3900,
            78.4900
        )
    """

    validate_coordinates(
        latitude1,
        longitude1
    )

    validate_coordinates(
        latitude2,
        longitude2
    )

    lat1 = radians(
        latitude1
    )

    lat2 = radians(
        latitude2
    )

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

    # Protect against floating-point errors.
    a = min(
        1.0,
        max(
            0.0,
            a
        )
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return (
        EARTH_RADIUS_KM * c
    )


# ============================================================
# DISTANCE IN METERS
# ============================================================

def distance_meters(
    latitude1: float,
    longitude1: float,
    latitude2: float,
    longitude2: float
) -> float:
    """
    Calculate distance in meters.
    """

    return (
        haversine_distance(
            latitude1,
            longitude1,
            latitude2,
            longitude2
        )
        * 1000
    )


# ============================================================
# DISTANCE IN MILES
# ============================================================

def distance_miles(
    latitude1: float,
    longitude1: float,
    latitude2: float,
    longitude2: float
) -> float:
    """
    Calculate distance in miles.
    """

    distance_km = haversine_distance(
        latitude1,
        longitude1,
        latitude2,
        longitude2
    )

    return (
        distance_km
        * 0.621371
    )


# ============================================================
# WITHIN RADIUS
# ============================================================

def is_within_radius(
    latitude1: float,
    longitude1: float,
    latitude2: float,
    longitude2: float,
    radius_km: float
) -> bool:
    """
    Determine whether point 2 is within
    radius_km of point 1.
    """

    if radius_km < 0:

        raise ValueError(
            "Radius cannot be negative"
        )

    distance = haversine_distance(
        latitude1,
        longitude1,
        latitude2,
        longitude2
    )

    return distance <= radius_km


# ============================================================
# APPROXIMATE BOUNDING BOX
# ============================================================

def bounding_box(
    latitude: float,
    longitude: float,
    radius_km: float
) -> dict[str, float]:
    """
    Calculate an approximate geographic bounding box.

    Useful as a first-stage database filter before
    performing the exact Haversine calculation.

    Returns:

        min_latitude
        max_latitude
        min_longitude
        max_longitude
    """

    validate_coordinates(
        latitude,
        longitude
    )

    if radius_km <= 0:

        raise ValueError(
            "Radius must be greater than zero"
        )

    # Approximate degrees per kilometer.
    latitude_delta = (
        radius_km / 111.32
    )

    # Prevent division by zero near the poles.
    cos_latitude = cos(
        radians(latitude)
    )

    if abs(cos_latitude) < 0.000001:

        longitude_delta = 180.0

    else:

        longitude_delta = (
            radius_km
            /
            (
                111.32
                * abs(cos_latitude)
            )
        )

    min_latitude = max(
        -90.0,
        latitude - latitude_delta
    )

    max_latitude = min(
        90.0,
        latitude + latitude_delta
    )

    min_longitude = max(
        -180.0,
        longitude - longitude_delta
    )

    max_longitude = min(
        180.0,
        longitude + longitude_delta
    )

    return {
        "min_latitude": min_latitude,
        "max_latitude": max_latitude,
        "min_longitude": min_longitude,
        "max_longitude": max_longitude
    }


# ============================================================
# BEARING
# ============================================================

def calculate_bearing(
    latitude1: float,
    longitude1: float,
    latitude2: float,
    longitude2: float
) -> float:
    """
    Calculate initial bearing from point 1 to point 2.

    Returns:
        Bearing in degrees from North.
        Range: 0-360
    """

    validate_coordinates(
        latitude1,
        longitude1
    )

    validate_coordinates(
        latitude2,
        longitude2
    )

    lat1 = radians(
        latitude1
    )

    lat2 = radians(
        latitude2
    )

    delta_lon = radians(
        longitude2 - longitude1
    )

    x = (
        sin(delta_lon)
        * cos(lat2)
    )

    y = (
        cos(lat1)
        * sin(lat2)
        -
        sin(lat1)
        * cos(lat2)
        * cos(delta_lon)
    )

    bearing = degrees(
        atan2(x, y)
    )

    return (
        bearing + 360
    ) % 360


# ============================================================
# CARDINAL DIRECTION
# ============================================================

def bearing_to_direction(
    bearing: float
) -> str:
    """
    Convert bearing into a simple compass direction.
    """

    bearing = bearing % 360

    directions = [
        "N",
        "NE",
        "E",
        "SE",
        "S",
        "SW",
        "W",
        "NW"
    ]

    index = int(
        (bearing + 22.5)
        / 45
    ) % 8

    return directions[index]


# ============================================================
# DESTINATION POINT
# ============================================================

def destination_point(
    latitude: float,
    longitude: float,
    distance_km: float,
    bearing: float
) -> tuple[float, float]:
    """
    Calculate a destination GPS coordinate from:

        starting point
        distance
        bearing

    Returns:
        (latitude, longitude)
    """

    validate_coordinates(
        latitude,
        longitude
    )

    if distance_km < 0:

        raise ValueError(
            "Distance cannot be negative"
        )

    bearing_rad = radians(
        bearing
    )

    angular_distance = (
        distance_km
        /
        EARTH_RADIUS_KM
    )

    lat1 = radians(
        latitude
    )

    lon1 = radians(
        longitude
    )

    lat2 = (
        __import__("math").asin(
            sin(lat1)
            * cos(angular_distance)
            +
            cos(lat1)
            * sin(angular_distance)
            * cos(bearing_rad)
        )
    )

    lon2 = (
        lon1
        +
        atan2(
            sin(bearing_rad)
            * sin(angular_distance)
            * cos(lat1),
            cos(angular_distance)
            -
            sin(lat1)
            * sin(lat2)
        )
    )

    return (
        degrees(lat2),
        (
            degrees(lon2) + 540
        ) % 360 - 180
    )


# ============================================================
# ROUTE DISTANCE
# ============================================================

def route_distance(
    points: list[tuple[float, float]]
) -> float:
    """
    Calculate total straight-line distance through
    a sequence of GPS points.

    Example:

        points = [
            (17.3850, 78.4867),
            (17.3900, 78.4900),
            (17.4000, 78.5000)
        ]
    """

    if len(points) < 2:

        return 0.0

    total_distance = 0.0

    for index in range(
        len(points) - 1
    ):

        lat1, lon1 = points[index]

        lat2, lon2 = points[index + 1]

        total_distance += (
            haversine_distance(
                lat1,
                lon1,
                lat2,
                lon2
            )
        )

    return total_distance


# ============================================================
# FORMAT DISTANCE
# ============================================================

def format_distance(
    distance_km: float
) -> str:
    """
    Format distance for passenger/driver UI.
    """

    if distance_km < 0:

        raise ValueError(
            "Distance cannot be negative"
        )

    if distance_km < 1:

        return f"{round(distance_km * 1000)} m"

    return f"{distance_km:.2f} km"


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    # Hyderabad example
    pickup = (
        17.3850,
        78.4867
    )

    driver = (
        17.3900,
        78.4900
    )

    # --------------------------------------------------------
    # Distance
    # --------------------------------------------------------

    distance = haversine_distance(
        pickup[0],
        pickup[1],
        driver[0],
        driver[1]
    )

    print(
        "Distance:",
        format_distance(distance)
    )

    # --------------------------------------------------------
    # Meters
    # --------------------------------------------------------

    print(
        "Meters:",
        round(
            distance_meters(
                pickup[0],
                pickup[1],
                driver[0],
                driver[1]
            )
        )
    )

    # --------------------------------------------------------
    # Bearing
    # --------------------------------------------------------

    bearing = calculate_bearing(
        pickup[0],
        pickup[1],
        driver[0],
        driver[1]
    )

    print(
        "Bearing:",
        round(
            bearing,
            2
        ),
        "degrees"
    )

    print(
        "Direction:",
        bearing_to_direction(
            bearing
        )
    )

    # --------------------------------------------------------
    # Radius
    # --------------------------------------------------------

    print(
        "Within 5 km:",
        is_within_radius(
            pickup[0],
            pickup[1],
            driver[0],
            driver[1],
            5
        )
    )

    # --------------------------------------------------------
    # Bounding box
    # --------------------------------------------------------

    print(
        "Bounding box:"
    )

    print(
        bounding_box(
            pickup[0],
            pickup[1],
            5
        )
    )
