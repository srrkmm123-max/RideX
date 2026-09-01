"""
RideX Rating Service

Responsibilities:
    - Validate ratings
    - Create ratings
    - Calculate average ratings
    - Calculate rating summaries
    - Validate reviews
    - Support passenger -> driver ratings
    - Support driver -> passenger ratings

Database persistence should be handled by service.py
or repository/database layer.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from statistics import mean
from typing import Optional


# ============================================================
# CONSTANTS
# ============================================================

MIN_RATING = 1
MAX_RATING = 5

MAX_REVIEW_LENGTH = 500

ALLOWED_RATING_TYPES = {
    "passenger_to_driver",
    "driver_to_passenger",
}


# ============================================================
# RATING STATUS
# ============================================================

class RatingStatus:

    CREATED = "created"

    UPDATED = "updated"

    DELETED = "deleted"

    INVALID = "invalid"


# ============================================================
# RATING DATA MODEL
# ============================================================

@dataclass
class Rating:

    rating_id: str

    ride_id: str

    from_user_id: str

    to_user_id: str

    rating_type: str

    stars: int

    review: Optional[str] = None

    tags: list[str] = field(
        default_factory=list
    )

    created_at: datetime = field(
        default_factory=lambda:
        datetime.now(timezone.utc)
    )


# ============================================================
# RATING RESULT
# ============================================================

@dataclass
class RatingResult:

    success: bool

    status: str

    rating: Optional[Rating] = None

    error: Optional[str] = None


# ============================================================
# VALIDATION
# ============================================================

def validate_stars(
    stars: int
) -> bool:
    """
    Validate star rating.

    Valid values:

        1
        2
        3
        4
        5
    """

    if not isinstance(
        stars,
        int
    ):

        return False

    return (
        MIN_RATING
        <=
        stars
        <=
        MAX_RATING
    )


def validate_rating_type(
    rating_type: str
) -> bool:
    """
    Validate rating direction.
    """

    return (
        rating_type
        in ALLOWED_RATING_TYPES
    )


def validate_review(
    review: Optional[str]
) -> bool:
    """
    Validate optional review text.
    """

    if review is None:

        return True

    if not isinstance(
        review,
        str
    ):

        return False

    review = review.strip()

    if len(review) > MAX_REVIEW_LENGTH:

        return False

    return True


def validate_tags(
    tags: Optional[list[str]]
) -> bool:
    """
    Validate rating tags.
    """

    if tags is None:

        return True

    if not isinstance(
        tags,
        list
    ):

        return False

    if len(tags) > 10:

        return False

    for tag in tags:

        if not isinstance(
            tag,
            str
        ):

            return False

        if len(tag.strip()) > 50:

            return False

    return True


# ============================================================
# CREATE RATING
# ============================================================

def create_rating(
    ride_id: str,
    from_user_id: str,
    to_user_id: str,
    rating_type: str,
    stars: int,
    review: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> RatingResult:
    """
    Create a validated rating.
    """

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    if not ride_id:

        return RatingResult(

            success=False,

            status=RatingStatus.INVALID,

            error="ride_id is required"
        )

    if not from_user_id:

        return RatingResult(

            success=False,

            status=RatingStatus.INVALID,

            error="from_user_id is required"
        )

    if not to_user_id:

        return RatingResult(

            success=False,

            status=RatingStatus.INVALID,

            error="to_user_id is required"
        )

    # --------------------------------------------------------
    # Prevent self-rating
    # --------------------------------------------------------

    if from_user_id == to_user_id:

        return RatingResult(

            success=False,

            status=RatingStatus.INVALID,

            error=(
                "A user cannot rate themselves"
            )
        )

    # --------------------------------------------------------
    # Validate rating type
    # --------------------------------------------------------

    if not validate_rating_type(
        rating_type
    ):

        return RatingResult(

            success=False,

            status=RatingStatus.INVALID,

            error=(
                "Invalid rating_type"
            )
        )

    # --------------------------------------------------------
    # Validate stars
    # --------------------------------------------------------

    if not validate_stars(
        stars
    ):

        return RatingResult(

            success=False,

            status=RatingStatus.INVALID,

            error=(
                "Rating must be between "
                "1 and 5 stars"
            )
        )

    # --------------------------------------------------------
    # Validate review
    # --------------------------------------------------------

    if not validate_review(
        review
    ):

        return RatingResult(

            success=False,

            status=RatingStatus.INVALID,

            error=(
                "Invalid review"
            )
        )

    # --------------------------------------------------------
    # Validate tags
    # --------------------------------------------------------

    if not validate_tags(
        tags
    ):

        return RatingResult(

            success=False,

            status=RatingStatus.INVALID,

            error=(
                "Invalid rating tags"
            )
        )

    # --------------------------------------------------------
    # Clean values
    # --------------------------------------------------------

    if review:

        review = review.strip()

    cleaned_tags = []

    if tags:

        cleaned_tags = [
            tag.strip()
            for tag in tags
            if tag.strip()
        ]

    # --------------------------------------------------------
    # Create object
    # --------------------------------------------------------

    rating = Rating(

        rating_id=(
            "RATE-"
            +
            uuid.uuid4()
            .hex[:16]
            .upper()
        ),

        ride_id=ride_id,

        from_user_id=from_user_id,

        to_user_id=to_user_id,

        rating_type=rating_type,

        stars=stars,

        review=review,

        tags=cleaned_tags
    )

    return RatingResult(

        success=True,

        status=RatingStatus.CREATED,

        rating=rating
    )


# ============================================================
# AVERAGE RATING
# ============================================================

def calculate_average_rating(
    ratings: list[Rating]
) -> float:
    """
    Calculate average star rating.
    """

    if not ratings:

        return 0.0

    stars = [
        rating.stars
        for rating in ratings
        if validate_stars(
            rating.stars
        )
    ]

    if not stars:

        return 0.0

    return round(
        mean(stars),
        2
    )


# ============================================================
# RATING COUNT
# ============================================================

def count_ratings(
    ratings: list[Rating]
) -> int:
    """
    Return total number of valid ratings.
    """

    return len([
        rating
        for rating in ratings
        if validate_stars(
            rating.stars
        )
    ])


# ============================================================
# RATING DISTRIBUTION
# ============================================================

def rating_distribution(
    ratings: list[Rating]
) -> dict:
    """
    Calculate number of 1, 2, 3, 4 and 5 star ratings.
    """

    distribution = {

        "1": 0,

        "2": 0,

        "3": 0,

        "4": 0,

        "5": 0,
    }

    for rating in ratings:

        if validate_stars(
            rating.stars
        ):

            distribution[
                str(rating.stars)
            ] += 1

    return distribution


# ============================================================
# RATING SUMMARY
# ============================================================

def rating_summary(
    ratings: list[Rating]
) -> dict:
    """
    Generate complete rating summary.
    """

    total = count_ratings(
        ratings
    )

    average = calculate_average_rating(
        ratings
    )

    distribution = rating_distribution(
        ratings
    )

    return {

        "total_ratings": total,

        "average_rating": average,

        "distribution": distribution,

        "five_star_percentage":
            percentage(
                distribution["5"],
                total
            ),

        "four_star_percentage":
            percentage(
                distribution["4"],
                total
            ),

        "three_star_percentage":
            percentage(
                distribution["3"],
                total
            ),

        "two_star_percentage":
            percentage(
                distribution["2"],
                total
            ),

        "one_star_percentage":
            percentage(
                distribution["1"],
                total
            ),
    }


# ============================================================
# PERCENTAGE
# ============================================================

def percentage(
    value: int,
    total: int
) -> float:
    """
    Calculate percentage safely.
    """

    if total <= 0:

        return 0.0

    return round(
        (value / total) * 100,
        2
    )


# ============================================================
# DRIVER RATING
# ============================================================

def calculate_driver_rating(
    ratings: list[Rating]
) -> dict:
    """
    Calculate passenger -> driver rating summary.
    """

    driver_ratings = [
        rating
        for rating in ratings
        if rating.rating_type
        ==
        "passenger_to_driver"
    ]

    return rating_summary(
        driver_ratings
    )


# ============================================================
# PASSENGER RATING
# ============================================================

def calculate_passenger_rating(
    ratings: list[Rating]
) -> dict:
    """
    Calculate driver -> passenger rating summary.
    """

    passenger_ratings = [
        rating
        for rating in ratings
        if rating.rating_type
        ==
        "driver_to_passenger"
    ]

    return rating_summary(
        passenger_ratings
    )


# ============================================================
# RATING TAGS
# ============================================================

DEFAULT_DRIVER_TAGS = [

    "Clean Vehicle",

    "Safe Driving",

    "Professional",

    "Friendly",

    "On Time",

    "Good Navigation",

]


DEFAULT_PASSENGER_TAGS = [

    "Polite",

    "Ready On Time",

    "Respectful",

    "Clear Pickup",

    "Good Communication",

]


def get_default_tags(
    rating_type: str
) -> list[str]:
    """
    Return predefined feedback tags.
    """

    if (
        rating_type
        ==
        "passenger_to_driver"
    ):

        return DEFAULT_DRIVER_TAGS.copy()

    if (
        rating_type
        ==
        "driver_to_passenger"
    ):

        return DEFAULT_PASSENGER_TAGS.copy()

    return []


# ============================================================
# LOW RATING DETECTION
# ============================================================

def is_low_rating(
    stars: int
) -> bool:
    """
    Determine whether rating requires attention.
    """

    return (
        validate_stars(stars)
        and
        stars <= 2
    )


# ============================================================
# RATING FLAGS
# ============================================================

def generate_rating_flags(
    rating: Rating
) -> list[str]:
    """
    Generate internal review flags.

    These flags can be used by the safety/admin service.
    """

    flags = []

    if rating.stars <= 2:

        flags.append(
            "LOW_RATING"
        )

    if (
        rating.review
        and
        len(rating.review) >= 400
    ):

        flags.append(
            "LONG_REVIEW"
        )

    if (
        rating.tags
        and
        "Safe Driving"
        not in rating.tags
        and
        rating.rating_type
        ==
        "passenger_to_driver"
        and
        rating.stars <= 3
    ):

        flags.append(
            "DRIVING_CONCERN"
        )

    return flags


# ============================================================
# UPDATE RATING
# ============================================================

def update_rating(
    rating: Rating,
    stars: Optional[int] = None,
    review: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> RatingResult:
    """
    Update an existing rating.
    """

    if stars is not None:

        if not validate_stars(
            stars
        ):

            return RatingResult(

                success=False,

                status=RatingStatus.INVALID,

                error=(
                    "Rating must be "
                    "between 1 and 5"
                )
            )

        rating.stars = stars

    if review is not None:

        if not validate_review(
            review
        ):

            return RatingResult(

                success=False,

                status=RatingStatus.INVALID,

                error="Invalid review"
            )

        rating.review = review.strip()

    if tags is not None:

        if not validate_tags(
            tags
        ):

            return RatingResult(

                success=False,

                status=RatingStatus.INVALID,

                error="Invalid tags"
            )

        rating.tags = [
            tag.strip()
            for tag in tags
            if tag.strip()
        ]

    return RatingResult(

        success=True,

        status=RatingStatus.UPDATED,

        rating=rating
    )


# ============================================================
# RATING ELIGIBILITY
# ============================================================

def can_rate_ride(
    ride_status: str,
    from_user_id: str,
    to_user_id: str
) -> tuple[bool, str]:
    """
    Determine whether a ride can be rated.
    """

    if ride_status.lower() != "completed":

        return (
            False,
            "Ride must be completed"
        )

    if not from_user_id:

        return (
            False,
            "Rating user is required"
        )

    if not to_user_id:

        return (
            False,
            "Target user is required"
        )

    if from_user_id == to_user_id:

        return (
            False,
            "User cannot rate themselves"
        )

    return (
        True,
        "Rating allowed"
    )


# ============================================================
# RATING QUALITY
# ============================================================

def rating_quality(
    average_rating: float,
    total_ratings: int
) -> str:
    """
    Classify rating quality.

    This is an internal classification and should
    not by itself be used to suspend a driver.
    """

    if total_ratings == 0:

        return "new"

    if average_rating >= 4.5:

        return "excellent"

    if average_rating >= 4.0:

        return "good"

    if average_rating >= 3.0:

        return "average"

    return "needs_attention"


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    ratings = []

    # --------------------------------------------------------
    # Passenger rates driver
    # --------------------------------------------------------

    result = create_rating(

        ride_id="RIDE-1001",

        from_user_id="PASSENGER-001",

        to_user_id="DRIVER-001",

        rating_type=(
            "passenger_to_driver"
        ),

        stars=5,

        review=(
            "Excellent driver. "
            "Very safe and professional."
        ),

        tags=[
            "Safe Driving",
            "Professional",
            "Clean Vehicle"
        ]
    )

    if result.success:

        ratings.append(
            result.rating
        )

        print(
            "Rating created:"
        )

        print(
            result.rating
        )

    # --------------------------------------------------------
    # Another rating
    # --------------------------------------------------------

    result = create_rating(

        ride_id="RIDE-1002",

        from_user_id="PASSENGER-002",

        to_user_id="DRIVER-001",

        rating_type=(
            "passenger_to_driver"
        ),

        stars=4,

        review="Good ride.",

        tags=[
            "On Time"
        ]
    )

    if result.success:

        ratings.append(
            result.rating
        )

    # --------------------------------------------------------
    # Rating summary
    # --------------------------------------------------------

    print(
        "\nRating Summary:"
    )

    print(
        calculate_driver_rating(
            ratings
        )
    )

    # --------------------------------------------------------
    # Rating flags
    # --------------------------------------------------------

    for rating in ratings:

        print(
            "\nRating Flags:"
        )

        print(
            generate_rating_flags(
                rating
            )
        )
