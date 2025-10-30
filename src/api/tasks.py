"""
Celery Tasks for Asynchronous Processing

Handles background task processing using Celery for long-running operations.
"""

from celery import Celery
from typing import Dict, Any
import os

from ..core.mcp import MasterControlProgram, SystemEvent, AgentType
from ..agents import LaSecretaria, ElCalendista, LaArchivista, ElEstratega


# Celery configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

# Initialize Celery app
celery_app = Celery(
    "agentta",
    broker=BROKER_URL,
    backend=RESULT_BACKEND
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3300,  # 55 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Initialize MCP for background tasks
# Note: In production, this should be properly managed per worker
_mcp_instance = None


def get_mcp() -> MasterControlProgram:
    """
    Get or initialize the MCP instance for Celery workers.

    Returns:
        MasterControlProgram instance
    """
    global _mcp_instance

    if _mcp_instance is None:
        _mcp_instance = MasterControlProgram()

        # Register agents
        _mcp_instance.register_agent(AgentType.LA_SECRETARIA, LaSecretaria())
        _mcp_instance.register_agent(AgentType.EL_CALENDISTA, ElCalendista())
        _mcp_instance.register_agent(AgentType.LA_ARCHIVISTA, LaArchivista())
        _mcp_instance.register_agent(AgentType.EL_ESTRATEGA, ElEstratega())

    return _mcp_instance


@celery_app.task(name="agentta.process_event", bind=True)
def process_event_task(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a system event asynchronously.

    Args:
        event_data: Dictionary containing event information
            - type: Event type
            - payload: Event payload
            - priority: Event priority (optional)

    Returns:
        Dictionary with processing results
    """
    try:
        # Get MCP instance
        mcp = get_mcp()

        # Create SystemEvent
        event = SystemEvent(
            type=event_data["type"],
            payload=event_data["payload"],
            priority=event_data.get("priority", 5)
        )

        # Process event synchronously in the worker
        # Note: The async process_event needs to be run in an event loop
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(mcp.process_event(event))
            return result
        finally:
            loop.close()

    except Exception as e:
        # Log error and re-raise
        self.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "event_type": event_data.get("type", "unknown")
            }
        )
        raise


@celery_app.task(name="agentta.process_email_batch", bind=True)
def process_email_batch_task(self, emails: list) -> Dict[str, Any]:
    """
    Process a batch of emails asynchronously.

    Args:
        emails: List of email data dictionaries

    Returns:
        Dictionary with batch processing results
    """
    results = []
    errors = []

    mcp = get_mcp()

    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        for idx, email_data in enumerate(emails):
            try:
                event = SystemEvent(
                    type="email_received",
                    payload=email_data,
                    priority=email_data.get("priority", 5)
                )

                result = loop.run_until_complete(mcp.process_event(event))
                results.append({
                    "index": idx,
                    "email_id": email_data.get("id"),
                    "status": "success",
                    "result": result
                })

            except Exception as e:
                errors.append({
                    "index": idx,
                    "email_id": email_data.get("id"),
                    "error": str(e)
                })

            # Update progress
            self.update_state(
                state="PROGRESS",
                meta={
                    "processed": idx + 1,
                    "total": len(emails),
                    "errors": len(errors)
                }
            )

        return {
            "total": len(emails),
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors
        }

    finally:
        loop.close()


@celery_app.task(name="agentta.analyze_document", bind=True)
def analyze_document_task(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze a document asynchronously (for AI processing).

    Args:
        document_data: Document data including content for analysis

    Returns:
        Analysis results
    """
    try:
        mcp = get_mcp()

        event = SystemEvent(
            type="document_uploaded",
            payload=document_data,
            priority=document_data.get("priority", 5)
        )

        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(mcp.process_event(event))
            return result
        finally:
            loop.close()

    except Exception as e:
        self.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "document_id": document_data.get("id", "unknown")
            }
        )
        raise


@celery_app.task(name="agentta.train_agent", bind=True)
def train_agent_task(
    self,
    agent_type: str,
    training_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Train an agent with new data asynchronously.

    Args:
        agent_type: Type of agent to train (e.g., "LA_SECRETARIA")
        training_data: Training data dictionary

    Returns:
        Training results
    """
    try:
        mcp = get_mcp()

        # Get agent
        agent_enum = AgentType[agent_type.upper()]

        if agent_enum not in mcp.agents:
            raise ValueError(f"Agent {agent_type} not found")

        agent = mcp.agents[agent_enum]

        # Train the agent
        agent.train(training_data)

        return {
            "status": "success",
            "agent": agent.agent_name,
            "training_data_keys": list(training_data.keys())
        }

    except Exception as e:
        self.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "agent_type": agent_type
            }
        )
        raise


@celery_app.task(name="agentta.generate_report")
def generate_report_task(report_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a system report asynchronously.

    Args:
        report_type: Type of report to generate
        parameters: Report parameters

    Returns:
        Report data
    """
    mcp = get_mcp()

    if report_type == "system_stats":
        return mcp.get_system_stats()

    elif report_type == "agent_metrics":
        metrics = {}
        for agent_type, agent in mcp.agents.items():
            metrics[agent_type.name] = agent.get_metrics()
        return metrics

    elif report_type == "event_history":
        events = mcp.get_event_history(
            event_type=parameters.get("event_type"),
            limit=parameters.get("limit", 1000)
        )

        return {
            "total": len(events),
            "events": [
                {
                    "type": event.type,
                    "timestamp": event.timestamp,
                    "priority": event.priority
                }
                for event in events
            ]
        }

    else:
        raise ValueError(f"Unknown report type: {report_type}")


@celery_app.task(name="agentta.cleanup_old_data")
def cleanup_old_data_task(days_old: int = 30) -> Dict[str, Any]:
    """
    Clean up old data from the system.

    Args:
        days_old: Delete data older than this many days

    Returns:
        Cleanup results
    """
    from datetime import datetime, timedelta

    mcp = get_mcp()

    # Calculate cutoff time
    cutoff_time = (datetime.now() - timedelta(days=days_old)).timestamp()

    # Clean old events from history
    original_count = len(mcp._event_history)

    mcp._event_history = [
        event for event in mcp._event_history
        if event.timestamp > cutoff_time
    ]

    events_removed = original_count - len(mcp._event_history)

    return {
        "status": "success",
        "events_removed": events_removed,
        "events_remaining": len(mcp._event_history),
        "days_old": days_old
    }


# Periodic tasks configuration
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Set up periodic tasks.

    These tasks run automatically on a schedule.
    """
    # Clean up old data daily at 2 AM
    sender.add_periodic_task(
        86400.0,  # 24 hours
        cleanup_old_data_task.s(days_old=30),
        name="Daily cleanup"
    )

    # Generate system stats report every hour
    sender.add_periodic_task(
        3600.0,  # 1 hour
        generate_report_task.s(report_type="system_stats", parameters={}),
        name="Hourly stats"
    )
