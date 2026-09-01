"""
RideX Shared Database Module

Provides:
    - Database engine
    - Session factory
    - Base model
    - Database health check
"""

import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./ridex.db"
)


# ============================================================
# DATABASE ENGINE
# ============================================================

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)


# ============================================================
# SESSION
# ============================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ============================================================
# BASE MODEL
# ============================================================

Base = declarative_base()


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db():
    """
    Provide a database session.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# DATABASE HEALTH CHECK
# ============================================================

def check_database() -> bool:
    """
    Check whether the database is reachable.
    """

    try:

        with engine.connect() as connection:

            connection.execute(
                text("SELECT 1")
            )

        return True

    except Exception as exc:

        print(
            f"Database connection failed: {exc}"
        )

        return False


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_database():
    """
    Create all registered database tables.
    """

    Base.metadata.create_all(
        bind=engine
    )


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    print(
        "Database URL:",
        DATABASE_URL
    )

    if check_database():

        print(
            "Database: CONNECTED"
        )

    else:

        print(
            "Database: FAILED"
        )
