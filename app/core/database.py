from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from app.core.config import get_settings

settings = get_settings()

# Create database engine
engine = create_engine(
    settings.database.url,
    pool_pre_ping=True,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for database models
Base = declarative_base()


@contextmanager
def get_db() -> Session:
    """Get a database session.

    Yields:
        Session: Database session.

    Raises:
        Exception: If an error occurs during the session.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Initialize the database."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
