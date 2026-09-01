"""
RideX Microservice Business Logic

Responsibilities:
    - Business rules
    - Validation
    - CRUD operations
    - Calling database layer
    - Returning application data

Do NOT put FastAPI route definitions here.
"""

from datetime import datetime, timezone
from typing import Any


# ============================================================
# SERVICE CONFIGURATION
# ============================================================

SERVICE_NAME = "ridex-service"


# ============================================================
# IN-MEMORY STORE
# ============================================================
#
# Temporary storage for development.
#
# In production:
#     PostgreSQL / Redis / other persistent storage
#     should be used through database.py.
#

_records: dict[int, dict[str, Any]] = {}

_next_id = 1


# ============================================================
# INTERNAL ID GENERATOR
# ============================================================

def _generate_id() -> int:
    """
    Generate a temporary record ID.
    """

    global _next_id

    record_id = _next_id

    _next_id += 1

    return record_id


# ============================================================
# CREATE
# ============================================================

def create_record(
    data: dict[str, Any]
) -> dict[str, Any]:
    """
    Create a new service record.
    """

    record_id = _generate_id()

    now = datetime.now(
        timezone.utc
    )

    record = {
        "id": record_id,
        "created_at": now,
        "updated_at": now,
        "is_active": True,
        **data
    }

    _records[record_id] = record

    return record


# ============================================================
# GET BY ID
# ============================================================

def get_record(
    record_id: int
) -> dict[str, Any] | None:
    """
    Retrieve a record by ID.
    """

    return _records.get(
        record_id
    )


# ============================================================
# GET ALL
# ============================================================

def get_records(
    page: int = 1,
    page_size: int = 20
) -> dict[str, Any]:
    """
    Return paginated records.
    """

    if page < 1:
        raise ValueError(
            "Page must be greater than 0"
        )

    if page_size < 1:
        raise ValueError(
            "Page size must be greater than 0"
        )

    records = list(
        _records.values()
    )

    total = len(records)

    start = (
        page - 1
    ) * page_size

    end = start + page_size

    results = records[
        start:end
    ]

    total_pages = (
        (total + page_size - 1)
        // page_size
        if total > 0
        else 0
    )

    return {
        "data": results,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages
        }
    }


# ============================================================
# UPDATE
# ============================================================

def update_record(
    record_id: int,
    data: dict[str, Any]
) -> dict[str, Any] | None:
    """
    Update an existing record.
    """

    record = _records.get(
        record_id
    )

    if record is None:
        return None

    # Do not allow ID replacement.
    data.pop(
        "id",
        None
    )

    record.update(data)

    record["updated_at"] = (
        datetime.now(
            timezone.utc
        )
    )

    _records[
        record_id
    ] = record

    return record


# ============================================================
# DELETE
# ============================================================

def delete_record(
    record_id: int
) -> bool:
    """
    Delete a record.
    """

    if record_id not in _records:
        return False

    del _records[
        record_id
    ]

    return True


# ============================================================
# ACTIVATE
# ============================================================

def activate_record(
    record_id: int
) -> dict[str, Any] | None:
    """
    Activate a record.
    """

    record = _records.get(
        record_id
    )

    if record is None:
        return None

    record["is_active"] = True

    record["updated_at"] = (
        datetime.now(
            timezone.utc
        )
    )

    return record


# ============================================================
# DEACTIVATE
# ============================================================

def deactivate_record(
    record_id: int
) -> dict[str, Any] | None:
    """
    Deactivate a record.
    """

    record = _records.get(
        record_id
    )

    if record is None:
        return None

    record["is_active"] = False

    record["updated_at"] = (
        datetime.now(
            timezone.utc
        )
    )

    return record


# ============================================================
# EXISTS
# ============================================================

def record_exists(
    record_id: int
) -> bool:
    """
    Check whether a record exists.
    """

    return record_id in _records


# ============================================================
# COUNT
# ============================================================

def count_records() -> int:
    """
    Return total number of records.
    """

    return len(_records)


# ============================================================
# CLEAR
# ============================================================

def clear_records() -> None:
    """
    Clear temporary in-memory records.

    Useful for testing.
    """

    global _next_id

    _records.clear()

    _next_id = 1


# ============================================================
# SERVICE STATUS
# ============================================================

def get_service_status() -> dict[str, Any]:
    """
    Return service status information.
    """

    return {
        "service": SERVICE_NAME,
        "status": "healthy",
        "records": count_records(),
        "timestamp": datetime.now(
            timezone.utc
        )
    }
