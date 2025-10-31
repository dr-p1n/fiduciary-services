"""
Pytest Configuration and Fixtures

Shared fixtures and configuration for all tests.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.api.main import app
from src.database.models import Base
from src.database.connection import get_db


# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create a new database session for each test."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create FastAPI test client."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_email_data():
    """Sample email data for testing."""
    return {
        "id": "test-email-1",
        "from": "sender@example.com",
        "to": ["recipient@example.com"],
        "subject": "Urgent: Contract Review Needed",
        "body": "Please review the attached contract by Friday. This is time-sensitive.",
        "priority": 8
    }


@pytest.fixture
def sample_document_data():
    """Sample document data for testing."""
    return {
        "id": "test-doc-1",
        "filename": "contract_2024.pdf",
        "file_type": "PDF Document",
        "size": 1024000,
        "source": "upload",
        "created_date": "2024-01-15"
    }
