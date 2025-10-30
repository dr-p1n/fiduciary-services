"""
Unit Tests for Agents

Tests for individual agent functionality.
"""

import pytest
from src.core.mcp import SystemEvent
from src.agents import LaSecretaria, ElCalendista, LaArchivista, ElEstratega


class TestLaSecretaria:
    """Tests for La Secretaria agent."""

    @pytest.fixture
    def agent(self):
        return LaSecretaria()

    @pytest.mark.asyncio
    async def test_process_email_event(self, agent, sample_email_data):
        """Test email processing."""
        event = SystemEvent(
            type="email_received",
            payload=sample_email_data
        )

        result = await agent.process(event)

        assert result["status"] == "processed"
        assert "priority" in result
        assert "action_items" in result

    def test_train_agent(self, agent):
        """Test agent training."""
        training_data = {
            "sender_priorities": {
                "important@example.com": "high"
            }
        }

        agent.train(training_data)
        assert len(agent.sender_priority_map) > 0


class TestElCalendista:
    """Tests for El Calendista agent."""

    @pytest.fixture
    def agent(self):
        return ElCalendista()

    @pytest.mark.asyncio
    async def test_process_email_for_deadlines(self, agent, sample_email_data):
        """Test deadline extraction from email."""
        event = SystemEvent(
            type="email_received",
            payload=sample_email_data
        )

        result = await agent.process(event)

        assert result["status"] == "processed"
        assert "deadlines_found" in result


class TestLaArchivista:
    """Tests for La Archivista agent."""

    @pytest.fixture
    def agent(self):
        return LaArchivista()

    @pytest.mark.asyncio
    async def test_process_document_upload(self, agent, sample_document_data):
        """Test document processing."""
        event = SystemEvent(
            type="document_uploaded",
            payload=sample_document_data
        )

        result = await agent.process(event)

        assert result["status"] == "processed"
        assert "classification" in result
        assert "suggested_tags" in result


class TestElEstratega:
    """Tests for El Estratega agent."""

    @pytest.fixture
    def agent(self):
        return ElEstratega()

    @pytest.mark.asyncio
    async def test_learn_from_event(self, agent):
        """Test pattern learning."""
        event = SystemEvent(
            type="document_uploaded",
            payload={"test": "data"}
        )

        result = await agent.process(event)

        assert result["status"] == "processed"
        assert "event_recorded" in result
