"""
Unit Tests for Master Control Program

Tests for MCP orchestration and event handling.
"""

import pytest
from src.core.mcp import MasterControlProgram, SystemEvent, AgentType
from src.agents import LaSecretaria


class TestMCP:
    """Tests for Master Control Program."""

    @pytest.fixture
    def mcp(self):
        """Create MCP instance with registered agents."""
        mcp = MasterControlProgram()
        mcp.register_agent(AgentType.LA_SECRETARIA, LaSecretaria())
        return mcp

    def test_agent_registration(self, mcp):
        """Test agent registration."""
        assert len(mcp.agents) == 1
        assert AgentType.LA_SECRETARIA in mcp.agents

    @pytest.mark.asyncio
    async def test_process_event(self, mcp, sample_email_data):
        """Test event processing."""
        event = SystemEvent(
            type="email_received",
            payload=sample_email_data
        )

        result = await mcp.process_event(event)

        assert result["status"] == "success"
        assert result["agents_processed"] > 0

    def test_get_system_stats(self, mcp):
        """Test system statistics."""
        stats = mcp.get_system_stats()

        assert "registered_agents" in stats
        assert "total_events_processed" in stats

    def test_event_history(self, mcp):
        """Test event history retrieval."""
        history = mcp.get_event_history(limit=10)

        assert isinstance(history, list)
