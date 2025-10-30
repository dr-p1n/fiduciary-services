"""
Database Models

SQLAlchemy models for the AGENTTA application.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, Integer, String, DateTime, Text, JSON, Boolean,
    ForeignKey, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class EventType(str, enum.Enum):
    """Event type enumeration."""
    EMAIL_RECEIVED = "email_received"
    DOCUMENT_UPLOADED = "document_uploaded"
    DEADLINE_APPROACHING = "deadline_approaching"
    CALENDAR_EVENT_CREATED = "calendar_event_created"
    PATTERN_DETECTED = "pattern_detected"
    DOCUMENT_ANALYZED = "document_analyzed"


class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = relationship("Document", back_populates="owner")
    events = relationship("Event", back_populates="user")


class Document(Base):
    """Document model."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000))
    file_type = Column(String(50))
    file_size = Column(Integer)

    # Metadata
    title = Column(String(500))
    description = Column(Text)
    document_type = Column(String(100))
    classification = Column(JSON)
    metadata = Column(JSON)
    tags = Column(JSON)

    # AI Analysis
    ai_analysis = Column(JSON)
    extracted_entities = Column(JSON)

    # Ownership
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="documents")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    analyzed_at = Column(DateTime)

    # Status
    is_processed = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)


class Event(Base):
    """System event model."""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(SQLEnum(EventType), nullable=False, index=True)
    payload = Column(JSON, nullable=False)
    priority = Column(Integer, default=5)

    # Processing
    status = Column(String(50), default="pending")
    result = Column(JSON)
    error_message = Column(Text)

    # Agent tracking
    agent_origin = Column(String(100))
    processed_by_agents = Column(JSON)

    # User
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="events")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)


class Email(Base):
    """Email model."""
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)

    # Email data
    from_address = Column(String(255), nullable=False)
    to_addresses = Column(JSON)
    cc_addresses = Column(JSON)
    subject = Column(String(1000))
    body = Column(Text)
    html_body = Column(Text)

    # Analysis
    priority = Column(String(20))
    urgency = Column(String(20))
    sentiment = Column(String(20))
    categories = Column(JSON)
    action_items = Column(JSON)
    requires_response = Column(Boolean, default=False)

    # Status
    is_read = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)

    # User
    user_id = Column(Integer, ForeignKey("users.id"))

    # Timestamps
    received_at = Column(DateTime, default=datetime.utcnow)
    analyzed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class Deadline(Base):
    """Deadline model."""
    __tablename__ = "deadlines"

    id = Column(Integer, primary_key=True, index=True)

    # Deadline data
    title = Column(String(500), nullable=False)
    description = Column(Text)
    deadline_date = Column(DateTime, nullable=False, index=True)

    # Classification
    deadline_type = Column(String(100))
    jurisdiction = Column(String(100))
    matter_number = Column(String(100))

    # Source
    source_type = Column(String(50))  # email, document, manual
    source_id = Column(Integer)

    # Status
    is_completed = Column(Boolean, default=False)
    is_cancelled = Column(Boolean, default=False)
    completed_at = Column(DateTime)

    # Reminders
    reminders = Column(JSON)

    # User
    user_id = Column(Integer, ForeignKey("users.id"))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AgentMetric(Base):
    """Agent metrics model for tracking agent performance."""
    __tablename__ = "agent_metrics"

    id = Column(Integer, primary_key=True, index=True)

    # Agent identification
    agent_type = Column(String(100), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False)

    # Metrics
    events_processed = Column(Integer, default=0)
    errors_encountered = Column(Integer, default=0)
    average_processing_time = Column(Integer)  # milliseconds

    # Timestamp
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)


class Pattern(Base):
    """Learned pattern model."""
    __tablename__ = "patterns"

    id = Column(Integer, primary_key=True, index=True)

    # Pattern data
    pattern_type = Column(String(100), nullable=False, index=True)
    pattern_data = Column(JSON, nullable=False)
    confidence = Column(Integer)  # 0-100

    # Learning
    times_confirmed = Column(Integer, default=1)
    times_rejected = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)

    # Agent
    discovered_by_agent = Column(String(100))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_confirmed_at = Column(DateTime)
