"""
RideX Safety Service

Responsibilities:
    - Create safety incidents
    - Handle SOS/emergency events
    - Validate safety reports
    - Classify incident severity
    - Track incident status
    - Manage evidence metadata
    - Generate escalation flags
    - Support passenger and driver safety reports

IMPORTANT:
    This module contains business logic only.
    Database persistence should be handled by service.py
    or the repository/database layer.
"""

import uuid

from dataclasses import dataclass, field

from datetime import datetime, timezone

from enum import Enum

from typing import Optional


# ============================================================
# CONSTANTS
# ============================================================

MAX_DESCRIPTION_LENGTH = 2000

MAX_LOCATION_LENGTH = 300

MAX_EVIDENCE_ITEMS = 20


# ============================================================
# INCIDENT TYPES
# ============================================================

class IncidentType(str, Enum):

    ACCIDENT = "accident"

    HARASSMENT = "harassment"

    UNSAFE_DRIVING = "unsafe_driving"

    ASSAULT = "assault"

    THEFT = "theft"

    LOST_ITEM = "lost_item"

    VEHICLE_PROBLEM = "vehicle_problem"

    DRIVER_BEHAVIOR = "driver_behavior"

    PASSENGER_BEHAVIOR = "passenger_behavior"

    ROUTE_DEVIATION = "route_deviation"

    PAYMENT_FRAUD = "payment_fraud"

    OTHER = "other"


# ============================================================
# SEVERITY
# ============================================================

class Severity(str, Enum):

    LOW = "low"

    MEDIUM = "medium"

    HIGH = "high"

    CRITICAL = "critical"


# ============================================================
# INCIDENT STATUS
# ============================================================

class IncidentStatus(str, Enum):

    OPEN = "open"

    ACKNOWLEDGED = "acknowledged"

    INVESTIGATING = "investigating"

    ESCALATED = "escalated"

    RESOLVED = "resolved"

    CLOSED = "closed"


# ============================================================
# REPORTER TYPE
# ============================================================

class ReporterType(str, Enum):

    PASSENGER = "passenger"

    DRIVER = "driver"

    ADMIN = "admin"

    SYSTEM = "system"


# ============================================================
# SAFETY INCIDENT
# ============================================================

@dataclass
class SafetyIncident:

    incident_id: str

    ride_id: str

    reporter_id: str

    reporter_type: str

    incident_type: str

    severity: str

    description: str

    location: Optional[str] = None

    latitude: Optional[float] = None

    longitude: Optional[float] = None

    target_user_id: Optional[str] = None

    vehicle_number: Optional[str] = None

    evidence: list[dict] = field(
        default_factory=list
    )

    emergency: bool = False

    status: str = IncidentStatus.OPEN.value

    created_at: datetime = field(
        default_factory=lambda:
        datetime.now(timezone.utc)
    )

    updated_at: datetime = field(
        default_factory=lambda:
        datetime.now(timezone.utc)
    )


# ============================================================
# SAFETY RESULT
# ============================================================

@dataclass
class SafetyResult:

    success: bool

    incident: Optional[SafetyIncident] = None

    error: Optional[str] = None


# ============================================================
# VALIDATION
# ============================================================

def validate_incident_type(
    incident_type: str
) -> bool:

    return incident_type in {
        item.value
        for item in IncidentType
    }


def validate_severity(
    severity: str
) -> bool:

    return severity in {
        item.value
        for item in Severity
    }


def validate_reporter_type(
    reporter_type: str
) -> bool:

    return reporter_type in {
        item.value
        for item in ReporterType
    }


def validate_description(
    description: str
) -> bool:

    if not description:

        return False

    if not isinstance(
        description,
        str
    ):

        return False

    description = description.strip()

    if not description:

        return False

    if len(description) > MAX_DESCRIPTION_LENGTH:

        return False

    return True


# ============================================================
# LOCATION VALIDATION
# ============================================================

def validate_coordinates(
    latitude: Optional[float],
    longitude: Optional[float]
) -> bool:

    if latitude is None and longitude is None:

        return True

    if latitude is None or longitude is None:

        return False

    try:

        latitude = float(latitude)

        longitude = float(longitude)

    except (
        TypeError,
        ValueError
    ):

        return False

    if not (
        -90
        <=
        latitude
        <=
        90
    ):

        return False

    if not (
        -180
        <=
        longitude
        <=
        180
    ):

        return False

    return True


# ============================================================
# EVIDENCE VALIDATION
# ============================================================

def validate_evidence(
    evidence: Optional[list[dict]]
) -> bool:

    if evidence is None:

        return True

    if not isinstance(
        evidence,
        list
    ):

        return False

    if len(evidence) > MAX_EVIDENCE_ITEMS:

        return False

    for item in evidence:

        if not isinstance(
            item,
            dict
        ):

            return False

    return True


# ============================================================
# SEVERITY CLASSIFICATION
# ============================================================

def classify_severity(
    incident_type: str,
    emergency: bool = False
) -> str:
    """
    Automatically determine an initial severity.

    This is only an initial classification.
    Human/admin review may change it.
    """

    if emergency:

        return Severity.CRITICAL.value

    critical_types = {

        IncidentType.ASSAULT.value,

        IncidentType.ACCIDENT.value,
    }

    high_types = {

        IncidentType.HARASSMENT.value,

        IncidentType.UNSAFE_DRIVING.value,

        IncidentType.ROUTE_DEVIATION.value,
    }

    medium_types = {

        IncidentType.THEFT.value,

        IncidentType.VEHICLE_PROBLEM.value,

        IncidentType.DRIVER_BEHAVIOR.value,

        IncidentType.PASSENGER_BEHAVIOR.value,
    }

    if incident_type in critical_types:

        return Severity.CRITICAL.value

    if incident_type in high_types:

        return Severity.HIGH.value

    if incident_type in medium_types:

        return Severity.MEDIUM.value

    return Severity.LOW.value


# ============================================================
# CREATE SAFETY INCIDENT
# ============================================================

def create_safety_incident(
    ride_id: str,
    reporter_id: str,
    reporter_type: str,
    incident_type: str,
    description: str,
    severity: Optional[str] = None,
    location: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    target_user_id: Optional[str] = None,
    vehicle_number: Optional[str] = None,
    evidence: Optional[list[dict]] = None,
    emergency: bool = False,
) -> SafetyResult:
    """
    Create a validated safety incident.
    """

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    if not ride_id:

        return SafetyResult(
            success=False,
            error="ride_id is required"
        )

    if not reporter_id:

        return SafetyResult(
            success=False,
            error="reporter_id is required"
        )

    # --------------------------------------------------------
    # Reporter type
    # --------------------------------------------------------

    if not validate_reporter_type(
        reporter_type
    ):

        return SafetyResult(
            success=False,
            error="Invalid reporter_type"
        )

    # --------------------------------------------------------
    # Incident type
    # --------------------------------------------------------

    if not validate_incident_type(
        incident_type
    ):

        return SafetyResult(
            success=False,
            error="Invalid incident_type"
        )

    # --------------------------------------------------------
    # Description
    # --------------------------------------------------------

    if not validate_description(
        description
    ):

        return SafetyResult(
            success=False,
            error="Invalid description"
        )

    # --------------------------------------------------------
    # Coordinates
    # --------------------------------------------------------

    if not validate_coordinates(
        latitude,
        longitude
    ):

        return SafetyResult(
            success=False,
            error="Invalid coordinates"
        )

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    if not validate_evidence(
        evidence
    ):

        return SafetyResult(
            success=False,
            error="Invalid evidence"
        )

    # --------------------------------------------------------
    # Severity
    # --------------------------------------------------------

    if severity is None:

        severity = classify_severity(
            incident_type,
            emergency
        )

    elif not validate_severity(
        severity
    ):

        return SafetyResult(
            success=False,
            error="Invalid severity"
        )

    # --------------------------------------------------------
    # Create incident
    # --------------------------------------------------------

    now = datetime.now(
        timezone.utc
    )

    incident = SafetyIncident(

        incident_id=(
            "SAFE-"
            +
            uuid.uuid4()
            .hex[:16]
            .upper()
        ),

        ride_id=ride_id,

        reporter_id=reporter_id,

        reporter_type=reporter_type,

        incident_type=incident_type,

        severity=severity,

        description=description.strip(),

        location=location,

        latitude=latitude,

        longitude=longitude,

        target_user_id=target_user_id,

        vehicle_number=vehicle_number,

        evidence=evidence or [],

        emergency=emergency,

        status=IncidentStatus.OPEN.value,

        created_at=now,

        updated_at=now,
    )

    return SafetyResult(
        success=True,
        incident=incident
    )


# ============================================================
# SOS / EMERGENCY
# ============================================================

def create_emergency_incident(
    ride_id: str,
    reporter_id: str,
    reporter_type: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    description: str = "Emergency SOS activated",
    vehicle_number: Optional[str] = None,
) -> SafetyResult:
    """
    Create a critical emergency incident.
    """

    return create_safety_incident(

        ride_id=ride_id,

        reporter_id=reporter_id,

        reporter_type=reporter_type,

        incident_type=(
            IncidentType.OTHER.value
        ),

        description=description,

        severity=Severity.CRITICAL.value,

        latitude=latitude,

        longitude=longitude,

        vehicle_number=vehicle_number,

        emergency=True
    )


# ============================================================
# ESCALATION
# ============================================================

def should_escalate(
    incident: SafetyIncident
) -> bool:
    """
    Determine whether incident requires escalation.
    """

    if incident.emergency:

        return True

    if incident.severity in {

        Severity.HIGH.value,

        Severity.CRITICAL.value

    }:

        return True

    return False


def escalation_level(
    incident: SafetyIncident
) -> str:
    """
    Determine initial escalation level.
    """

    if incident.emergency:

        return "emergency"

    if incident.severity == Severity.CRITICAL.value:

        return "critical"

    if incident.severity == Severity.HIGH.value:

        return "high"

    if incident.severity == Severity.MEDIUM.value:

        return "normal"

    return "low"


# ============================================================
# STATUS MANAGEMENT
# ============================================================

def update_incident_status(
    incident: SafetyIncident,
    status: str
) -> SafetyResult:
    """
    Update incident status.
    """

    valid_statuses = {
        item.value
        for item in IncidentStatus
    }

    if status not in valid_statuses:

        return SafetyResult(

            success=False,

            incident=incident,

            error="Invalid incident status"
        )

    incident.status = status

    incident.updated_at = (
        datetime.now(
            timezone.utc
        )
    )

    return SafetyResult(

        success=True,

        incident=incident
    )


# ============================================================
# ADD EVIDENCE
# ============================================================

def add_evidence(
    incident: SafetyIncident,
    evidence_type: str,
    reference: str,
    description: Optional[str] = None
) -> SafetyResult:
    """
    Add evidence metadata.

    `reference` should normally point to secure object
    storage rather than storing large files in PostgreSQL.
    """

    if not evidence_type:

        return SafetyResult(

            success=False,

            incident=incident,

            error="evidence_type is required"
        )

    if not reference:

        return SafetyResult(

            success=False,

            incident=incident,

            error="evidence reference is required"
        )

    if len(
        incident.evidence
    ) >= MAX_EVIDENCE_ITEMS:

        return SafetyResult(

            success=False,

            incident=incident,

            error="Maximum evidence limit reached"
        )

    item = {

        "evidence_id": (
            "EVID-"
            +
            uuid.uuid4()
            .hex[:12]
            .upper()
        ),

        "type": evidence_type,

        "reference": reference,

        "description": description,

        "created_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        )
    }

    incident.evidence.append(
        item
    )

    incident.updated_at = (
        datetime.now(
            timezone.utc
        )
    )

    return SafetyResult(

        success=True,

        incident=incident
    )


# ============================================================
# INCIDENT FLAGS
# ============================================================

def generate_safety_flags(
    incident: SafetyIncident
) -> list[str]:
    """
    Generate internal safety flags.
    """

    flags = []

    if incident.emergency:

        flags.append(
            "EMERGENCY"
        )

    if incident.severity == Severity.CRITICAL.value:

        flags.append(
            "CRITICAL"
        )

    if incident.severity == Severity.HIGH.value:

        flags.append(
            "HIGH_PRIORITY"
        )

    if incident.incident_type == (
        IncidentType.ACCIDENT.value
    ):

        flags.append(
            "ACCIDENT"
        )

    if incident.incident_type == (
        IncidentType.ASSAULT.value
    ):

        flags.append(
            "ASSAULT"
        )

    if incident.incident_type == (
        IncidentType.HARASSMENT.value
    ):

        flags.append(
            "HARASSMENT"
        )

    if incident.incident_type == (
        IncidentType.UNSAFE_DRIVING.value
    ):

        flags.append(
            "UNSAFE_DRIVING"
        )

    if incident.incident_type == (
        IncidentType.ROUTE_DEVIATION.value
    ):

        flags.append(
            "ROUTE_DEVIATION"
        )

    return flags


# ============================================================
# INCIDENT SUMMARY
# ============================================================

def incident_summary(
    incidents: list[SafetyIncident]
) -> dict:
    """
    Generate safety incident statistics.
    """

    summary = {

        "total": len(incidents),

        "open": 0,

        "investigating": 0,

        "escalated": 0,

        "resolved": 0,

        "critical": 0,

        "high": 0,

        "medium": 0,

        "low": 0,

        "emergency": 0,
    }

    for incident in incidents:

        if incident.status == (
            IncidentStatus.OPEN.value
        ):

            summary["open"] += 1

        elif incident.status == (
            IncidentStatus.INVESTIGATING.value
        ):

            summary["investigating"] += 1

        elif incident.status == (
            IncidentStatus.ESCALATED.value
        ):

            summary["escalated"] += 1

        elif incident.status == (
            IncidentStatus.RESOLVED.value
        ):

            summary["resolved"] += 1

        if incident.severity == (
            Severity.CRITICAL.value
        ):

            summary["critical"] += 1

        elif incident.severity == (
            Severity.HIGH.value
        ):

            summary["high"] += 1

        elif incident.severity == (
            Severity.MEDIUM.value
        ):

            summary["medium"] += 1

        elif incident.severity == (
            Severity.LOW.value
        ):

            summary["low"] += 1

        if incident.emergency:

            summary["emergency"] += 1

    return summary


# ============================================================
# LOCATION STATUS
# ============================================================

def has_valid_location(
    incident: SafetyIncident
) -> bool:

    return validate_coordinates(

        incident.latitude,

        incident.longitude
    )


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    incidents = []

    # --------------------------------------------------------
    # Normal safety report
    # --------------------------------------------------------

    result = create_safety_incident(

        ride_id="RIDE-1001",

        reporter_id="PASSENGER-001",

        reporter_type=(
            ReporterType.PASSENGER.value
        ),

        incident_type=(
            IncidentType.UNSAFE_DRIVING.value
        ),

        description=(
            "Driver was driving "
            "above the safe speed."
        ),

        latitude=17.4483,

        longitude=78.3915,

        vehicle_number="TS09AB1234"
    )

    if result.success:

        incidents.append(
            result.incident
        )

        print(
            "Safety Incident:"
        )

        print(
            result.incident
        )

        print(
            "\nFlags:"
        )

        print(
            generate_safety_flags(
                result.incident
            )
        )

        print(
            "\nEscalation:"
        )

        print(
            escalation_level(
                result.incident
            )
        )

    # --------------------------------------------------------
    # Emergency SOS
    # --------------------------------------------------------

    result = create_emergency_incident(

        ride_id="RIDE-1002",

        reporter_id="PASSENGER-002",

        reporter_type=(
            ReporterType.PASSENGER.value
        ),

        latitude=17.3850,

        longitude=78.4867,

        vehicle_number="TS10XY5678"
    )

    if result.success:

        incidents.append(
            result.incident
        )

        print(
            "\nEmergency Incident:"
        )

        print(
            result.incident
        )

        print(
            "\nFlags:"
        )

        print(
            generate_safety_flags(
                result.incident
            )
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print(
        "\nSafety Summary:"
    )

    print(
        incident_summary(
            incidents
        )
    )
