"""
RideX SOS / Emergency Service

Responsibilities:
    - Activate SOS
    - Track SOS status
    - Capture emergency location
    - Escalate emergency events
    - Acknowledge SOS
    - Cancel SOS
    - Resolve SOS
    - Generate emergency event payloads

IMPORTANT:
    This module does not directly call emergency services.
    Integrate the appropriate emergency provider through
    the notification/safety workflow.
"""

import uuid

from dataclasses import dataclass, field

from datetime import datetime, timezone

from enum import Enum

from typing import Optional


# ============================================================
# CONSTANTS
# ============================================================

MAX_LOCATION_HISTORY = 100

MAX_CONTACTS = 10


# ============================================================
# SOS STATUS
# ============================================================

class SOSStatus(str, Enum):

    ACTIVATED = "activated"

    ACKNOWLEDGED = "acknowledged"

    ESCALATED = "escalated"

    RESPONDING = "responding"

    CANCELLED = "cancelled"

    RESOLVED = "resolved"


# ============================================================
# SOS PRIORITY
# ============================================================

class SOSPriority(str, Enum):

    CRITICAL = "critical"

    HIGH = "high"


# ============================================================
# REPORTER TYPE
# ============================================================

class SOSReporterType(str, Enum):

    PASSENGER = "passenger"

    DRIVER = "driver"

    SYSTEM = "system"


# ============================================================
# LOCATION
# ============================================================

@dataclass
class SOSLocation:

    latitude: float

    longitude: float

    accuracy_meters: Optional[float] = None

    heading: Optional[float] = None

    speed_kmph: Optional[float] = None

    timestamp: datetime = field(
        default_factory=lambda:
        datetime.now(timezone.utc)
    )


# ============================================================
# SOS EVENT
# ============================================================

@dataclass
class SOSEvent:

    sos_id: str

    ride_id: str

    user_id: str

    reporter_type: str

    status: str

    priority: str

    reason: str

    initial_location: SOSLocation

    current_location: SOSLocation

    location_history: list[SOSLocation] = field(
        default_factory=list
    )

    driver_id: Optional[str] = None

    vehicle_number: Optional[str] = None

    emergency_contacts: list[str] = field(
        default_factory=list
    )

    notification_sent: bool = False

    admin_notified: bool = False

    escalation_count: int = 0

    created_at: datetime = field(
        default_factory=lambda:
        datetime.now(timezone.utc)
    )

    updated_at: datetime = field(
        default_factory=lambda:
        datetime.now(timezone.utc)
    )

    resolved_at: Optional[datetime] = None


# ============================================================
# SOS RESULT
# ============================================================

@dataclass
class SOSResult:

    success: bool

    sos: Optional[SOSEvent] = None

    error: Optional[str] = None


# ============================================================
# VALIDATION
# ============================================================

def validate_coordinates(
    latitude: float,
    longitude: float
) -> bool:

    try:

        latitude = float(latitude)

        longitude = float(longitude)

    except (
        TypeError,
        ValueError
    ):

        return False

    return (
        -90 <= latitude <= 90
        and
        -180 <= longitude <= 180
    )


def validate_reason(
    reason: str
) -> bool:

    if not reason:

        return False

    return (
        isinstance(
            reason,
            str
        )
        and
        len(reason.strip()) <= 500
    )


# ============================================================
# CREATE LOCATION
# ============================================================

def create_location(
    latitude: float,
    longitude: float,
    accuracy_meters: Optional[float] = None,
    heading: Optional[float] = None,
    speed_kmph: Optional[float] = None,
) -> SOSLocation:

    if not validate_coordinates(
        latitude,
        longitude
    ):

        raise ValueError(
            "Invalid GPS coordinates"
        )

    if (
        accuracy_meters is not None
        and
        accuracy_meters < 0
    ):

        raise ValueError(
            "Invalid GPS accuracy"
        )

    if (
        heading is not None
        and
        not (
            0 <= heading <= 360
        )
    ):

        raise ValueError(
            "Heading must be between 0 and 360"
        )

    if (
        speed_kmph is not None
        and
        speed_kmph < 0
    ):

        raise ValueError(
            "Speed cannot be negative"
        )

    return SOSLocation(

        latitude=float(latitude),

        longitude=float(longitude),

        accuracy_meters=accuracy_meters,

        heading=heading,

        speed_kmph=speed_kmph
    )


# ============================================================
# ACTIVATE SOS
# ============================================================

def activate_sos(
    ride_id: str,
    user_id: str,
    reporter_type: str,
    latitude: float,
    longitude: float,
    reason: str = "Emergency SOS activated",
    driver_id: Optional[str] = None,
    vehicle_number: Optional[str] = None,
    emergency_contacts: Optional[list[str]] = None,
) -> SOSResult:
    """
    Activate an SOS event.
    """

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    if not ride_id:

        return SOSResult(
            success=False,
            error="ride_id is required"
        )

    if not user_id:

        return SOSResult(
            success=False,
            error="user_id is required"
        )

    # --------------------------------------------------------
    # Reporter validation
    # --------------------------------------------------------

    valid_reporters = {
        item.value
        for item in SOSReporterType
    }

    if reporter_type not in valid_reporters:

        return SOSResult(
            success=False,
            error="Invalid reporter_type"
        )

    # --------------------------------------------------------
    # Reason validation
    # --------------------------------------------------------

    if not validate_reason(
        reason
    ):

        return SOSResult(
            success=False,
            error="Invalid SOS reason"
        )

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    try:

        location = create_location(
            latitude,
            longitude
        )

    except ValueError as error:

        return SOSResult(
            success=False,
            error=str(error)
        )

    # --------------------------------------------------------
    # Emergency contacts
    # --------------------------------------------------------

    contacts = (
        emergency_contacts
        or []
    )

    if len(contacts) > MAX_CONTACTS:

        return SOSResult(
            success=False,
            error=(
                "Maximum emergency contacts "
                "exceeded"
            )
        )

    # --------------------------------------------------------
    # Create SOS
    # --------------------------------------------------------

    now = datetime.now(
        timezone.utc
    )

    sos_id = (
        "SOS-"
        +
        uuid.uuid4()
        .hex[:16]
        .upper()
    )

    sos = SOSEvent(

        sos_id=sos_id,

        ride_id=ride_id,

        user_id=user_id,

        reporter_type=reporter_type,

        status=SOSStatus.ACTIVATED.value,

        priority=SOSPriority.CRITICAL.value,

        reason=reason.strip(),

        initial_location=location,

        current_location=location,

        location_history=[
            location
        ],

        driver_id=driver_id,

        vehicle_number=vehicle_number,

        emergency_contacts=contacts,

        created_at=now,

        updated_at=now
    )

    return SOSResult(
        success=True,
        sos=sos
    )


# ============================================================
# UPDATE LOCATION
# ============================================================

def update_sos_location(
    sos: SOSEvent,
    latitude: float,
    longitude: float,
    accuracy_meters: Optional[float] = None,
    heading: Optional[float] = None,
    speed_kmph: Optional[float] = None,
) -> SOSResult:
    """
    Update current emergency location.
    """

    if sos.status in {

        SOSStatus.CANCELLED.value,

        SOSStatus.RESOLVED.value

    }:

        return SOSResult(

            success=False,

            sos=sos,

            error=(
                "Cannot update location "
                "for closed SOS"
            )
        )

    try:

        location = create_location(

            latitude,

            longitude,

            accuracy_meters,

            heading,

            speed_kmph
        )

    except ValueError as error:

        return SOSResult(

            success=False,

            sos=sos,

            error=str(error)
        )

    sos.current_location = location

    sos.location_history.append(
        location
    )

    # Prevent unlimited memory growth
    if (
        len(sos.location_history)
        >
        MAX_LOCATION_HISTORY
    ):

        sos.location_history = (
            sos.location_history[
                -MAX_LOCATION_HISTORY:
            ]
        )

    sos.updated_at = (
        datetime.now(
            timezone.utc
        )
    )

    return SOSResult(
        success=True,
        sos=sos
    )


# ============================================================
# ACKNOWLEDGE SOS
# ============================================================

def acknowledge_sos(
    sos: SOSEvent,
    acknowledged_by: str
) -> SOSResult:

    if not acknowledged_by:

        return SOSResult(

            success=False,

            sos=sos,

            error=(
                "acknowledged_by is required"
            )
        )

    if sos.status not in {

        SOSStatus.ACTIVATED.value,

        SOSStatus.ESCALATED.value

    }:

        return SOSResult(

            success=False,

            sos=sos,

            error=(
                f"Cannot acknowledge SOS "
                f"in status {sos.status}"
            )
        )

    sos.status = (
        SOSStatus.ACKNOWLEDGED.value
    )

    sos.updated_at = (
        datetime.now(
            timezone.utc
        )
    )

    return SOSResult(
        success=True,
        sos=sos
    )


# ============================================================
# ESCALATE SOS
# ============================================================

def escalate_sos(
    sos: SOSEvent
) -> SOSResult:

    if sos.status in {

        SOSStatus.CANCELLED.value,

        SOSStatus.RESOLVED.value

    }:

        return SOSResult(

            success=False,

            sos=sos,

            error=(
                "Cannot escalate closed SOS"
            )
        )

    sos.status = (
        SOSStatus.ESCALATED.value
    )

    sos.escalation_count += 1

    sos.updated_at = (
        datetime.now(
            timezone.utc
        )
    )

    return SOSResult(
        success=True,
        sos=sos
    )


# ============================================================
# START RESPONSE
# ============================================================

def start_response(
    sos: SOSEvent
) -> SOSResult:

    if sos.status not in {

        SOSStatus.ACKNOWLEDGED.value,

        SOSStatus.ESCALATED.value

    }:

        return SOSResult(

            success=False,

            sos=sos,

            error=(
                "SOS must be acknowledged "
                "or escalated before responding"
            )
        )

    sos.status = (
        SOSStatus.RESPONDING.value
    )

    sos.updated_at = (
        datetime.now(
            timezone.utc
        )
    )

    return SOSResult(
        success=True,
        sos=sos
    )


# ============================================================
# CANCEL SOS
# ============================================================

def cancel_sos(
    sos: SOSEvent,
    user_id: str
) -> SOSResult:
    """
    Cancel an SOS.

    In production, cancellation may require
    additional verification.
    """

    if not user_id:

        return SOSResult(

            success=False,

            sos=sos,

            error="user_id is required"
        )

    if sos.user_id != user_id:

        return SOSResult(

            success=False,

            sos=sos,

            error="Unauthorized SOS cancellation"
        )

    if sos.status in {

        SOSStatus.CANCELLED.value,

        SOSStatus.RESOLVED.value

    }:

        return SOSResult(

            success=False,

            sos=sos,

            error="SOS is already closed"
        )

    sos.status = (
        SOSStatus.CANCELLED.value
    )

    sos.updated_at = (
        datetime.now(
            timezone.utc
        )
    )

    return SOSResult(
        success=True,
        sos=sos
    )


# ============================================================
# RESOLVE SOS
# ============================================================

def resolve_sos(
    sos: SOSEvent,
    resolved_by: str
) -> SOSResult:

    if not resolved_by:

        return SOSResult(

            success=False,

            sos=sos,

            error="resolved_by is required"
        )

    if sos.status == (
        SOSStatus.CANCELLED.value
    ):

        return SOSResult(

            success=False,

            sos=sos,

            error="Cancelled SOS cannot be resolved"
        )

    now = datetime.now(
        timezone.utc
    )

    sos.status = (
        SOSStatus.RESOLVED.value
    )

    sos.updated_at = now

    sos.resolved_at = now

    return SOSResult(
        success=True,
        sos=sos
    )


# ============================================================
# MARK NOTIFICATION SENT
# ============================================================

def mark_notification_sent(
    sos: SOSEvent
) -> SOSResult:

    sos.notification_sent = True

    sos.updated_at = (
        datetime.now(
            timezone.utc
        )
    )

    return SOSResult(
        success=True,
        sos=sos
    )


# ============================================================
# MARK ADMIN NOTIFIED
# ============================================================

def mark_admin_notified(
    sos: SOSEvent
) -> SOSResult:

    sos.admin_notified = True

    sos.updated_at = (
        datetime.now(
            timezone.utc
        )
    )

    return SOSResult(
        success=True,
        sos=sos
    )


# ============================================================
# SOS EVENT PAYLOAD
# ============================================================

def build_sos_event(
    sos: SOSEvent
) -> dict:
    """
    Build an event that can be published to a queue/event bus.
    """

    location = sos.current_location

    return {

        "event_type": "SOS_ACTIVATED",

        "event_id": sos.sos_id,

        "sos_id": sos.sos_id,

        "ride_id": sos.ride_id,

        "user_id": sos.user_id,

        "driver_id": sos.driver_id,

        "reporter_type": sos.reporter_type,

        "priority": sos.priority,

        "status": sos.status,

        "reason": sos.reason,

        "vehicle_number":
            sos.vehicle_number,

        "location": {

            "latitude":
                location.latitude,

            "longitude":
                location.longitude,

            "accuracy_meters":
                location.accuracy_meters,

            "heading":
                location.heading,

            "speed_kmph":
                location.speed_kmph,

            "timestamp":
                location.timestamp.isoformat()
        },

        "created_at":
            sos.created_at.isoformat()
    }


# ============================================================
# SOS STATUS
# ============================================================

def get_sos_status(
    sos: SOSEvent
) -> dict:

    location = sos.current_location

    return {

        "sos_id": sos.sos_id,

        "ride_id": sos.ride_id,

        "status": sos.status,

        "priority": sos.priority,

        "escalation_count":
            sos.escalation_count,

        "notification_sent":
            sos.notification_sent,

        "admin_notified":
            sos.admin_notified,

        "location": {

            "latitude":
                location.latitude,

            "longitude":
                location.longitude
        },

        "created_at":
            sos.created_at.isoformat(),

        "updated_at":
            sos.updated_at.isoformat()
    }


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # ACTIVATE SOS
    # --------------------------------------------------------

    result = activate_sos(

        ride_id="RIDE-1001",

        user_id="PASSENGER-001",

        reporter_type=(
            SOSReporterType.PASSENGER.value
        ),

        latitude=17.3850,

        longitude=78.4867,

        reason=(
            "Passenger activated SOS "
            "because of an emergency."
        ),

        driver_id="DRIVER-001",

        vehicle_number="TS09AB1234",

        emergency_contacts=[
            "+91XXXXXXXXXX"
        ]
    )

    if not result.success:

        print(
            "SOS activation failed:",
            result.error
        )

        raise SystemExit(1)

    sos = result.sos

    print(
        "\nSOS ACTIVATED"
    )

    print(
        get_sos_status(sos)
    )

    # --------------------------------------------------------
    # EVENT
    # --------------------------------------------------------

    print(
        "\nSOS EVENT:"
    )

    print(
        build_sos_event(sos)
    )

    # --------------------------------------------------------
    # UPDATE LOCATION
    # --------------------------------------------------------

    result = update_sos_location(

        sos,

        latitude=17.3900,

        longitude=78.4900,

        accuracy_meters=10,

        heading=90,

        speed_kmph=25
    )

    print(
        "\nLOCATION UPDATED:"
    )

    print(
        get_sos_status(sos)
    )

    # --------------------------------------------------------
    # ACKNOWLEDGE
    # --------------------------------------------------------

    result = acknowledge_sos(

        sos,

        acknowledged_by="ADMIN-001"
    )

    print(
        "\nSOS ACKNOWLEDGED:"
    )

    print(
        get_sos_status(sos)
    )

    # --------------------------------------------------------
    # START RESPONSE
    # --------------------------------------------------------

    result = start_response(
        sos
    )

    print(
        "\nRESPONSE STARTED:"
    )

    print(
        get_sos_status(sos)
    )

    # --------------------------------------------------------
    # RESOLVE
    # --------------------------------------------------------

    result = resolve_sos(

        sos,

        resolved_by="ADMIN-001"
    )

    print(
        "\nSOS RESOLVED:"
    )

    print(
        get_sos_status(sos)
    )
