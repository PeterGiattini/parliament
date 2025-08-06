"""FastAPI application for the Parliament multi-agent debate system."""

from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

import models
from agent_service import agent_manager
from agent_templates import get_default_agents
from debate_orchestrator import DebateOrchestrator

load_dotenv()

app = FastAPI(title="Parliament", description="Multi-agent AI debate system")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# API Routes
# =============================================================================


@app.get("/")
async def root() -> models.MessageResponse:
    """Return basic API information."""
    return models.MessageResponse(message="Parliament API - Multi-agent debate system")


@app.get("/agents")
async def get_agents() -> models.AgentsResponse:
    """Get all available agents."""
    return models.AgentsResponse(agents=agent_manager.get_all_agents())


@app.get("/agents/search")
async def search_agents(query: str) -> models.AgentsResponse:
    """Search agents by name, description, or tags."""
    return models.AgentsResponse(agents=agent_manager.search_agents(query))


@app.post("/agents/generate")
async def generate_agent(
    request: models.AgentGenerationRequest,
) -> models.AgentResponse:
    """Generate a new agent from a natural language description."""
    try:
        agent = agent_manager.generate_agent_from_prompt(request.prompt, request.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    else:
        return models.AgentResponse(agent=agent)


@app.post("/agents")
async def create_agent(request: models.AgentCreationRequest) -> models.AgentResponse:
    """Create a custom agent."""
    try:
        agent = agent_manager.create_agent(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    else:
        return models.AgentResponse(agent=agent)


@app.get("/panels")
async def get_panels() -> models.PanelsResponse:
    """Get all available panels."""
    return models.PanelsResponse(panels=agent_manager.get_all_panels())


@app.post("/panels")
async def create_panel(request: models.PanelCreationRequest) -> models.PanelResponse:
    """Create a new panel."""
    try:
        panel = agent_manager.create_panel(
            name=request.name,
            description=request.description,
            agent_ids=request.agent_ids,
            tags=request.tags,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    else:
        return models.PanelResponse(panel=panel)


@app.get("/export")
async def export_data() -> models.ExportResponse:
    """Export all data as JSON string."""
    return models.ExportResponse(data=agent_manager.export_data())


@app.post("/import")
async def import_data(request: models.ExportRequest) -> models.ImportResponse:
    """Import data from JSON string."""
    success = agent_manager.import_data(request.json_data)
    return models.ImportResponse(success=success)


# =============================================================================
# Utility Functions
# =============================================================================


def _validate_agents(agent_ids: list[str] | None) -> list[dict[str, Any]]:
    """Validate and retrieve agents by IDs."""
    if not agent_ids:
        return []

    agents = agent_manager.get_agents_by_ids(agent_ids)
    if not agents:
        raise HTTPException(status_code=400, detail="No valid agents found")
    # Convert Agent objects to dicts for debate orchestrator compatibility
    return [agent.model_dump() for agent in agents]


@app.post("/debate")
async def start_debate(request: models.DebateRequest) -> StreamingResponse:
    """Start a new debate with the given topic and optional agent selection.

    Returns a streaming response with the debate progress.
    """
    try:
        # Increment panel usage if panel_id is provided
        if request.panel_id:
            agent_manager.increment_panel_usage(request.panel_id)

        # Use selected agents if provided, otherwise use default agents
        if request.agent_ids:
            agents = _validate_agents(request.agent_ids)
        else:
            # Convert default agents to the expected format
            default_agents = get_default_agents()
            agents = []
            for agent_data in default_agents:
                agents.append(
                    {
                        "name": agent_data["name"],
                        "role": agent_data["role"],
                        "system_prompt": agent_data["system_prompt"],
                        "color": agent_data["color"],
                        "icon": agent_data["icon"],
                        "tags": [agent_data["role"], "built-in"],
                    }
                )

        orchestrator = DebateOrchestrator(agents)
        return StreamingResponse(
            orchestrator.run_debate(request.topic),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/health")
async def health_check() -> models.MessageResponse:
    """Return health status of the API."""
    return models.MessageResponse(message="healthy")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
