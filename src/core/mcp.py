"""
Master Control Program (MCP) - Core Orchestration System

The MCP is the central nervous system of AGENTTA, coordinating multi-agent
workflows, managing shared context, and routing events intelligently.
"""

import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from .event_bus import EventBus
from .shared_context import SharedContextManager


class AgentType(Enum):
    """Enumeration of specialized agents in the AGENTTA system."""
    LA_SECRETARIA = auto()  # Email Intelligence
    EL_CALENDISTA = auto()  # Deadline Management
    LA_ARCHIVISTA = auto()  # Document Organization
    EL_ESTRATEGA = auto()  # Process Learning


@dataclass
class SystemEvent:
    """
    Represents a system event that can be processed by agents.

    Attributes:
        type: The type of event (e.g., 'email_received', 'document_uploaded')
        payload: The event data
        timestamp: When the event was created
        agent_origin: Which agent originated the event (if any)
        priority: Event priority (1-10, higher is more urgent)
    """
    type: str
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    agent_origin: Optional[AgentType] = None
    priority: int = 5

    def __post_init__(self):
        """Validate event after initialization."""
        if not self.type:
            raise ValueError("Event type cannot be empty")
        if not isinstance(self.payload, dict):
            raise ValueError("Event payload must be a dictionary")
        if not 1 <= self.priority <= 10:
            raise ValueError("Priority must be between 1 and 10")


class MasterControlProgram:
    """
    The Master Control Program orchestrates multi-agent workflows,
    manages shared context, and routes events intelligently across the system.
    """

    def __init__(self):
        """Initialize the MCP with event bus, shared context, and agents."""
        self.agents = {}
        self.event_bus = EventBus()
        self.shared_context = SharedContextManager()
        self._routing_rules = self._initialize_routing_rules()
        self._event_history: List[SystemEvent] = []
        self._max_history_size = 1000

    def _initialize_routing_rules(self) -> Dict[str, List[AgentType]]:
        """
        Define intelligent routing rules for different event types.

        Returns:
            Dictionary mapping event types to relevant agent types
        """
        return {
            'email_received': [
                AgentType.LA_SECRETARIA,
                AgentType.EL_CALENDISTA
            ],
            'document_uploaded': [
                AgentType.LA_ARCHIVISTA,
                AgentType.EL_ESTRATEGA
            ],
            'deadline_approaching': [
                AgentType.EL_CALENDISTA,
                AgentType.LA_SECRETARIA
            ],
            'document_analyzed': [
                AgentType.LA_ARCHIVISTA,
                AgentType.EL_ESTRATEGA
            ],
            'pattern_detected': [
                AgentType.EL_ESTRATEGA
            ],
            'calendar_event_created': [
                AgentType.EL_CALENDISTA
            ],
            'search_query': [
                AgentType.LA_ARCHIVISTA
            ]
        }

    def register_agent(self, agent_type: AgentType, agent_instance):
        """
        Register an agent with the MCP.

        Args:
            agent_type: The type of agent being registered
            agent_instance: The agent instance
        """
        self.agents[agent_type] = agent_instance
        print(f"✓ Registered agent: {agent_type.name}")

    async def process_event(self, event: SystemEvent) -> Dict[str, Any]:
        """
        Orchestrate multi-agent workflow for processing an event.

        Args:
            event: The system event to process

        Returns:
            Dictionary containing processing results from all relevant agents
        """
        # Store event in history
        self._add_to_history(event)

        # Publish event to event bus
        self.event_bus.publish(event.type, event)

        # Determine relevant agents for this event
        relevant_agents = self._determine_relevant_agents(event)

        if not relevant_agents:
            return {
                "status": "no_agents",
                "message": f"No agents configured for event type: {event.type}",
                "event": event.type
            }

        # Parallel processing of event by relevant agents
        try:
            results = await asyncio.gather(
                *[agent.process(event) for agent in relevant_agents],
                return_exceptions=True
            )

            # Process results and update shared context
            processed_results = self._process_agent_results(
                relevant_agents,
                results
            )

            # Update shared context with results
            self.shared_context.update({
                f"last_{event.type}": {
                    "timestamp": event.timestamp,
                    "results": processed_results
                }
            })

            return {
                "status": "success",
                "event": event.type,
                "agents_processed": len(relevant_agents),
                "results": processed_results
            }

        except Exception as e:
            return {
                "status": "error",
                "event": event.type,
                "error": str(e)
            }

    def _determine_relevant_agents(self, event: SystemEvent) -> List:
        """
        Intelligently determine which agents should process an event.

        Args:
            event: The system event

        Returns:
            List of agent instances that should process the event
        """
        agent_types = self._routing_rules.get(event.type, [])

        # Filter to only registered agents
        return [
            self.agents[agent_type]
            for agent_type in agent_types
            if agent_type in self.agents
        ]

    def _process_agent_results(
        self,
        agents: List,
        results: List[Any]
    ) -> Dict[str, Any]:
        """
        Process and structure results from multiple agents.

        Args:
            agents: List of agents that processed the event
            results: List of results from each agent

        Returns:
            Structured dictionary of agent results
        """
        processed = {}

        for agent, result in zip(agents, results):
            agent_name = type(agent).__name__

            if isinstance(result, Exception):
                processed[agent_name] = {
                    "status": "error",
                    "error": str(result)
                }
            else:
                processed[agent_name] = result

        return processed

    def _add_to_history(self, event: SystemEvent):
        """
        Add event to history, maintaining maximum size.

        Args:
            event: The event to add to history
        """
        self._event_history.append(event)

        # Trim history if it exceeds max size
        if len(self._event_history) > self._max_history_size:
            self._event_history = self._event_history[-self._max_history_size:]

    def get_event_history(
        self,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[SystemEvent]:
        """
        Retrieve event history, optionally filtered by type.

        Args:
            event_type: Optional event type to filter by
            limit: Maximum number of events to return

        Returns:
            List of historical events
        """
        if event_type:
            filtered = [
                event for event in self._event_history
                if event.type == event_type
            ]
            return filtered[-limit:]

        return self._event_history[-limit:]

    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get statistics about system operation.

        Returns:
            Dictionary of system statistics
        """
        return {
            "registered_agents": len(self.agents),
            "agent_types": [agent_type.name for agent_type in self.agents.keys()],
            "total_events_processed": len(self._event_history),
            "event_types": list(self._routing_rules.keys()),
            "shared_context_keys": len(self.shared_context._context)
        }

    async def shutdown(self):
        """Gracefully shutdown the MCP and all agents."""
        print("Shutting down Master Control Program...")

        # Allow agents to clean up
        for agent_type, agent in self.agents.items():
            if hasattr(agent, 'shutdown'):
                await agent.shutdown()

        print("✓ MCP shutdown complete")
