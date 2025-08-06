"""Shared data models for the Parliament API."""

from dataclasses import dataclass

from pydantic import BaseModel

# =============================================================================
# Core Entity Models
# =============================================================================


class Agent(BaseModel):
    """Agent entity for storage and management."""

    id: str
    name: str
    description: str
    system_prompt: str
    tags: list[str]
    is_built_in: bool
    created_at: int
    usage_count: int
    color: str
    icon: str


class Panel(BaseModel):
    """Panel entity for storage and management."""

    id: str
    name: str
    description: str
    agent_ids: list[str]
    tags: list[str]
    is_built_in: bool
    created_at: int
    usage_count: int


# =============================================================================
# API Request Models
# =============================================================================


class AgentCreationRequest(BaseModel):
    """Request model for creating a custom agent."""

    name: str
    description: str
    system_prompt: str
    tags: list[str]
    color: str
    icon: str


class AgentGenerationRequest(BaseModel):
    """Request model for generating a new agent."""

    prompt: str
    name: str | None = None


class PanelCreationRequest(BaseModel):
    """Request model for creating a panel."""

    name: str
    description: str
    agent_ids: list[str]
    tags: list[str]


class DebateRequest(BaseModel):
    """Request model for starting a new debate."""

    topic: str
    agent_ids: list[str] | None = None
    panel_id: str | None = None


class ExportRequest(BaseModel):
    """Request model for data export."""

    json_data: str


# =============================================================================
# API Response Models
# =============================================================================


class AgentResponse(BaseModel):
    """Response model for a single agent."""

    agent: Agent


class AgentsResponse(BaseModel):
    """Response model for multiple agents."""

    agents: list[Agent]


class PanelResponse(BaseModel):
    """Response model for a single panel."""

    panel: Panel


class PanelsResponse(BaseModel):
    """Response model for multiple panels."""

    panels: list[Panel]


class ExportResponse(BaseModel):
    """Response model for data export."""

    data: str


class ImportResponse(BaseModel):
    """Response model for data import."""

    success: bool


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


# =============================================================================
# Configuration Models
# =============================================================================


@dataclass
class AgentConfig:
    """Configuration for creating an agent template."""

    name: str
    role: str
    specialization: str
    primary_goal: str
    key_principles: list[str]
    scope: str
    communication_style: str
    color: str
    icon: str
