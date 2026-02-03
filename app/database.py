from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
from dotenv import load_dotenv


_ENGINE = None
_SESSIONMAKER = None


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Create a .env file (or set it in your shell) with DATABASE_URL, e.g. "
            "postgresql://postgres:<password>@localhost:5432/course_enrollment "
            "(URL-encode special characters in the password, e.g. @ -> %40)."
        )
    return value

load_dotenv()


def get_engine():
    """Return a lazily-initialized SQLAlchemy Engine.

    Avoids requiring DATABASE_URL at import-time so tools/tests can import modules
    without a fully configured environment.
    """
    global _ENGINE
    if _ENGINE is None:
        database_url = _require_env("DATABASE_URL")
        _ENGINE = create_engine(
            database_url,
            pool_pre_ping=True,
        )
    return _ENGINE


def get_sessionmaker():
    global _SESSIONMAKER
    if _SESSIONMAKER is None:
        _SESSIONMAKER = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine(),
        )
    return _SESSIONMAKER

class Base(DeclarativeBase):
    pass


def get_db():
    db = get_sessionmaker()()
    try:
        yield db
    finally:
        db.close()
