"""
Database Connection Management

Provides database session management and connection utilities.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from ..config import settings


# Create database engine
engine = create_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.debug  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database sessions.

    Yields:
        Database session

    Example:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize the database.

    Creates all tables defined in the models.
    """
    from .models import Base

    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")


def reset_db():
    """
    Reset the database.

    WARNING: This will drop all tables and recreate them!
    Only use in development.
    """
    from .models import Base

    if not settings.is_development():
        raise RuntimeError("Cannot reset database in production!")

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✓ Database reset complete")
