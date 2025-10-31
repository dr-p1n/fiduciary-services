"""
Base Agent - Abstract Foundation for All AGENTTA Agents

Provides the core interface and common functionality that all specialized
agents inherit from.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
import asyncio


class BaseAgent(ABC):
    """
    Abstract base class for all AGENTTA agents.

    All specialized agents must inherit from this class and implement
    the required abstract methods.
    """

    def __init__(self, agent_name: str):
        """
        Initialize the base agent.

        Args:
            agent_name: Human-readable name for the agent
        """
        self.agent_name = agent_name
        self.capabilities: Dict[str, Any] = {}
        self.training_data: Dict[str, Any] = {}
        self.metrics = {
            "events_processed": 0,
            "errors_encountered": 0,
            "last_active": None,
            "average_processing_time": 0.0
        }
        self._processing_times: list = []

    @abstractmethod
    async def process(self, event) -> Dict[str, Any]:
        """
        Process a system event.

        This is the main entry point for agent processing. Each agent
        must implement its own processing logic.

        Args:
            event: The SystemEvent to process

        Returns:
            Dictionary containing processing results
        """
        pass

    @abstractmethod
    def train(self, training_data: Dict[str, Any]):
        """
        Enable continuous learning mechanism.

        Agents can be trained with new data to improve their performance
        and adapt to changing patterns.

        Args:
            training_data: Training data specific to the agent
        """
        pass

    async def _track_processing(self, event) -> Dict[str, Any]:
        """
        Wrapper to track processing metrics.

        Args:
            event: The event being processed

        Returns:
            Processing results
        """
        start_time = datetime.now()

        try:
            result = await self.process(event)

            # Update metrics on success
            self.metrics["events_processed"] += 1
            self.metrics["last_active"] = datetime.now().isoformat()

            # Track processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            self._processing_times.append(processing_time)

            # Keep only last 100 processing times
            if len(self._processing_times) > 100:
                self._processing_times = self._processing_times[-100:]

            # Update average
            self.metrics["average_processing_time"] = (
                sum(self._processing_times) / len(self._processing_times)
            )

            return result

        except Exception as e:
            self.metrics["errors_encountered"] += 1
            raise

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the agent's capabilities.

        Returns:
            Dictionary describing agent capabilities
        """
        return self.capabilities.copy()

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get agent performance metrics.

        Returns:
            Dictionary of agent metrics
        """
        return self.metrics.copy()

    def set_capability(self, capability_name: str, capability_value: Any):
        """
        Set or update an agent capability.

        Args:
            capability_name: Name of the capability
            capability_value: Value or description of the capability
        """
        self.capabilities[capability_name] = capability_value

    async def shutdown(self):
        """
        Gracefully shutdown the agent.

        Override this method if your agent needs cleanup logic.
        """
        print(f"Shutting down agent: {self.agent_name}")

    def __repr__(self) -> str:
        """String representation of the agent."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.agent_name}', "
            f"events_processed={self.metrics['events_processed']})"
        )


class AgentCapability:
    """Enumeration of common agent capabilities."""

    EMAIL_PROCESSING = "email_processing"
    DEADLINE_TRACKING = "deadline_tracking"
    DOCUMENT_ORGANIZATION = "document_organization"
    PATTERN_LEARNING = "pattern_learning"
    METADATA_EXTRACTION = "metadata_extraction"
    INTELLIGENT_SEARCH = "intelligent_search"
    CALENDAR_MANAGEMENT = "calendar_management"
    PRIORITY_ASSESSMENT = "priority_assessment"
