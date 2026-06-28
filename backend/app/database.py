"""Database engine, session factory and the declarative base."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import settings

connect_args = {}
if settings.orbes_database_url.startswith("sqlite"):
    # Needed so SQLite can be used across FastAPI's threadpool.
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.orbes_database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables. Import models first so they register with Base."""
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
