"""
AGENTTA FastAPI Application

Main FastAPI application providing REST API endpoints for the AGENTTA system.
"""

from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..core.mcp import MasterControlProgram, SystemEvent, AgentType
from ..agents import LaSecretaria, ElCalendista, LaArchivista, ElEstratega


# Pydantic Models for API
class EventPayload(BaseModel):
    """Request model for processing events."""
    type: str = Field(..., description="Type of event to process")
    payload: Dict[str, Any] = Field(..., description="Event data")
    priority: Optional[int] = Field(5, ge=1, le=10, description="Event priority (1-10)")


class EventResponse(BaseModel):
    """Response model for event processing."""
    status: str
    event: str
    agents_processed: int
    results: Dict[str, Any]


class SystemStatsResponse(BaseModel):
    """Response model for system statistics."""
    registered_agents: int
    agent_types: List[str]
    total_events_processed: int
    event_types: List[str]
    shared_context_keys: int


class AgentMetricsResponse(BaseModel):
    """Response model for agent metrics."""
    agent_name: str
    events_processed: int
    errors_encountered: int
    last_active: Optional[str]
    average_processing_time: float


# Initialize FastAPI app
app = FastAPI(
    title="AGENTTA API",
    description="Agents Enhancing Natural Task Technology Automation",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global MCP instance
mcp = MasterControlProgram()


@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup."""
    print("🚀 Starting AGENTTA System...")

    # Register all agents
    mcp.register_agent(AgentType.LA_SECRETARIA, LaSecretaria())
    mcp.register_agent(AgentType.EL_CALENDISTA, ElCalendista())
    mcp.register_agent(AgentType.LA_ARCHIVISTA, LaArchivista())
    mcp.register_agent(AgentType.EL_ESTRATEGA, ElEstratega())

    print("✓ AGENTTA System initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("🛑 Shutting down AGENTTA System...")
    await mcp.shutdown()
    print("✓ AGENTTA System shutdown complete")


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - health check."""
    return {
        "message": "AGENTTA API is running",
        "version": "0.1.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents": {
            agent_type.name: "active"
            for agent_type in mcp.agents.keys()
        }
    }


@app.post("/events", response_model=EventResponse, tags=["Events"])
async def process_event(event_data: EventPayload):
    """
    Process a system event through the MCP.

    This endpoint accepts events and routes them to appropriate agents
    for processing.
    """
    try:
        # Create SystemEvent
        system_event = SystemEvent(
            type=event_data.type,
            payload=event_data.payload,
            priority=event_data.priority
        )

        # Process through MCP
        result = await mcp.process_event(system_event)

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing event: {str(e)}"
        )


@app.post("/events/email", tags=["Events", "Email"])
async def process_email(email_data: Dict[str, Any]):
    """
    Process an incoming email event.

    Specialized endpoint for email processing.
    """
    event = SystemEvent(
        type="email_received",
        payload=email_data,
        priority=email_data.get("priority", 5)
    )

    result = await mcp.process_event(event)
    return result


@app.post("/events/document", tags=["Events", "Documents"])
async def process_document(document_data: Dict[str, Any]):
    """
    Process a document upload event.

    Specialized endpoint for document processing.
    """
    event = SystemEvent(
        type="document_uploaded",
        payload=document_data,
        priority=document_data.get("priority", 5)
    )

    result = await mcp.process_event(event)
    return result


@app.post("/events/deadline", tags=["Events", "Calendar"])
async def create_deadline(deadline_data: Dict[str, Any]):
    """
    Create a deadline tracking event.

    Specialized endpoint for deadline management.
    """
    event = SystemEvent(
        type="deadline_approaching",
        payload=deadline_data,
        priority=deadline_data.get("priority", 7)
    )

    result = await mcp.process_event(event)
    return result


@app.get("/system/stats", response_model=SystemStatsResponse, tags=["System"])
async def get_system_stats():
    """
    Get system statistics and metrics.

    Returns information about registered agents, processed events, etc.
    """
    stats = mcp.get_system_stats()
    return stats


@app.get("/system/events", tags=["System"])
async def get_event_history(
    event_type: Optional[str] = None,
    limit: int = 100
):
    """
    Retrieve event history.

    Optionally filter by event type and limit results.
    """
    events = mcp.get_event_history(event_type=event_type, limit=limit)

    # Convert SystemEvent objects to dicts
    return {
        "total": len(events),
        "events": [
            {
                "type": event.type,
                "timestamp": event.timestamp,
                "priority": event.priority,
                "agent_origin": event.agent_origin.name if event.agent_origin else None
            }
            for event in events
        ]
    }


@app.get("/agents", tags=["Agents"])
async def list_agents():
    """
    List all registered agents and their capabilities.
    """
    agents_info = []

    for agent_type, agent in mcp.agents.items():
        agents_info.append({
            "type": agent_type.name,
            "name": agent.agent_name,
            "capabilities": agent.get_capabilities(),
            "metrics": agent.get_metrics()
        })

    return {
        "total_agents": len(agents_info),
        "agents": agents_info
    }


@app.get("/agents/{agent_type}/metrics", response_model=AgentMetricsResponse, tags=["Agents"])
async def get_agent_metrics(agent_type: str):
    """
    Get metrics for a specific agent.
    """
    try:
        # Convert string to AgentType enum
        agent_enum = AgentType[agent_type.upper()]

        if agent_enum not in mcp.agents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_type} not found"
            )

        agent = mcp.agents[agent_enum]
        metrics = agent.get_metrics()

        return {
            "agent_name": agent.agent_name,
            **metrics
        }

    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent type {agent_type} not found"
        )


@app.post("/agents/{agent_type}/train", tags=["Agents"])
async def train_agent(agent_type: str, training_data: Dict[str, Any]):
    """
    Train a specific agent with new data.
    """
    try:
        agent_enum = AgentType[agent_type.upper()]

        if agent_enum not in mcp.agents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_type} not found"
            )

        agent = mcp.agents[agent_enum]
        agent.train(training_data)

        return {
            "status": "success",
            "message": f"Agent {agent.agent_name} trained successfully",
            "training_data_keys": list(training_data.keys())
        }

    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent type {agent_type} not found"
        )


@app.get("/context", tags=["Context"])
async def get_shared_context():
    """
    Get all shared context data.
    """
    context = mcp.shared_context.get_all()

    return {
        "total_keys": len(context),
        "context": context
    }


@app.get("/context/{key}", tags=["Context"])
async def get_context_value(key: str):
    """
    Get a specific value from shared context.
    """
    value = mcp.shared_context.get(key)

    if value is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Context key '{key}' not found"
        )

    return {
        "key": key,
        "value": value
    }


@app.post("/context/{key}", tags=["Context"])
async def set_context_value(key: str, value: Any):
    """
    Set a value in shared context.
    """
    mcp.shared_context.set(key, value)

    return {
        "status": "success",
        "key": key,
        "message": "Context value set successfully"
    }


@app.delete("/context/{key}", tags=["Context"])
async def delete_context_value(key: str):
    """
    Delete a value from shared context.
    """
    deleted = mcp.shared_context.delete(key)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Context key '{key}' not found"
        )

    return {
        "status": "success",
        "key": key,
        "message": "Context value deleted successfully"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
