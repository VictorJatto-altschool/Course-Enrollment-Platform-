"""Create database tables from SQLAlchemy models.

Usage:
    python -m app.init_db

This uses DATABASE_URL from your .env / environment.
"""

from app.database import Base, get_engine


def init_db() -> None:
    # Import models so they are registered on Base.metadata
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=get_engine())


if __name__ == "__main__":
    init_db()
    print("Tables created (if they did not already exist).")
