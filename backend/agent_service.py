"""Agent management system for Parliament with localStorage persistence."""

import json
import random
import uuid
from datetime import UTC, datetime
from typing import Any

from agent_templates import get_agent_template, get_default_agents
from models import Agent, AgentConfig, AgentCreationRequest, Panel


class AgentManager:
    """Manages agents and panels with localStorage persistence."""

    def __init__(self) -> None:
        """Initialize the agent manager."""
        self._load_data()

    def _load_data(self) -> None:
        """Load data from localStorage or initialize with defaults."""
        # In a real implementation, this would read from localStorage
        # For now, we'll use in-memory storage with default agents
        self.agents: dict[str, Agent] = {}
        self.panels: dict[str, Panel] = {}

        # Load built-in agents
        default_agents = get_default_agents()
        for agent in default_agents:
            # Set creation timestamp for built-in agents
            agent.created_at = int(datetime.now(UTC).timestamp())
            self.agents[agent.id] = agent

    def get_all_agents(self) -> list[Agent]:
        """Get all agents for API response."""
        return list(self.agents.values())

    def get_agent_by_id(self, agent_id: str) -> Agent | None:
        """Get an agent by ID."""
        return self.agents.get(agent_id)

    def search_agents(self, query: str) -> list[Agent]:
        """Search agents by name, description, or tags."""
        query_lower = query.lower()

        return [
            agent
            for agent in self.agents.values()
            if (
                query_lower in agent.name.lower()
                or query_lower in agent.description.lower()
                or any(query_lower in tag.lower() for tag in agent.tags)
            )
        ]

    def create_agent(self, request: AgentCreationRequest) -> Agent:
        """Create a new user agent."""
        agent = Agent(
            id=str(uuid.uuid4()),
            name=request.name,
            description=request.description,
            system_prompt=request.system_prompt,
            tags=request.tags,
            is_built_in=False,
            created_at=int(datetime.now(UTC).timestamp()),
            usage_count=0,
            color=request.color,
            icon=request.icon,
        )
        self.agents[agent.id] = agent
        return agent

    def generate_agent_from_prompt(self, prompt: str, name: str | None = None) -> Agent:
        """Generate an agent from a natural language description."""
        # Use provided name or extract from prompt
        if name and name.strip():
            agent_name = name.strip()
        else:
            agent_name = prompt.split()[0] if prompt else "Custom Agent"

        description = f"An AI agent with the following characteristics: {prompt}"

        # Create a generic AgentConfig for the custom agent
        # This ensures it gets the same base system prompt and directives
        # as the built-in agents.
        agent_config = AgentConfig(
            name=agent_name,
            role="custom agent",
            specialization=f"AI agent that embodies the following persona: {prompt}",
            primary_goal="Engage in the debate according to the user-defined persona.",
            key_principles=[
                "Adhere to the user-defined persona and instructions.",
                "Argue logically and consistently from that persona's perspective.",
            ],
            scope="The scope is defined by the user's prompt and the debate topic.",
            communication_style=(
                f"The communication style is defined by the user's prompt: {prompt}"
            ),
            color=random.choice(  # noqa: S311
                ["#2563eb", "#7c3aed", "#059669", "#dc2626", "#ea580c", "#0891b2"]
            ),
            icon=random.choice(["🤖", "🧠", "💡", "🎯", "⚡", "🌟"]),  # noqa: S311
        )

        # Generate the agent details from the standard template
        template = get_agent_template(agent_config)

        tags = ["custom", "generated"] + [word.lower() for word in prompt.split()[:3]]

        # Create AgentCreationRequest object
        request = AgentCreationRequest(
            name=agent_name,
            description=description,
            system_prompt=template["system_prompt"],
            tags=tags,
            color=template["color"],
            icon=template["icon"],
        )

        return self.create_agent(request)

    def get_agents_by_ids(self, agent_ids: list[str]) -> list[Agent]:
        """Get multiple agents by their IDs."""
        agents = []
        for agent_id in agent_ids:
            agent = self.agents.get(agent_id)
            if agent:
                agents.append(agent)
        return agents

    def get_all_panels(self) -> list[Panel]:
        """Get all panels for API response."""
        return list(self.panels.values())

    def create_panel(
        self, name: str, description: str, agent_ids: list[str], tags: list[str]
    ) -> Panel:
        """Create a new panel."""
        panel = Panel(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            agent_ids=agent_ids,
            tags=tags,
            is_built_in=False,
            created_at=int(datetime.now(UTC).timestamp()),
            usage_count=0,
        )
        self.panels[panel.id] = panel
        return panel

    def get_panel_by_id(self, panel_id: str) -> Panel | None:
        """Get a panel by ID."""
        return self.panels.get(panel_id)

    def increment_panel_usage(self, panel_id: str) -> None:
        """Increment the usage count for a panel."""
        if panel := self.panels.get(panel_id):
            panel.usage_count += 1

    def export_data(self) -> str:
        """Export all data as JSON string."""
        data = {
            "version": "1.0",
            "agents": [agent.model_dump() for agent in self.agents.values()],
            "panels": [panel.model_dump() for panel in self.panels.values()],
            "exported_at": datetime.now(UTC).isoformat(),
        }
        return json.dumps(data, indent=2)

    def _import_entity(
        self, entity_data: dict[str, Any], entity_type: type, storage: dict[str, Any]
    ) -> None:
        """Import a single entity (agent or panel) with built-in protection."""
        # Don't overwrite built-ins - check if ID already exists as built-in
        existing_entity = storage.get(entity_data.get("id"))
        if existing_entity and existing_entity.is_built_in:
            # Skip import if this would overwrite a built-in entity
            return

        # Force custom entities to be marked as non-built-in
        entity_data["is_built_in"] = False
        entity = entity_type(**entity_data)
        storage[entity.id] = entity

    def import_data(self, json_data: str) -> bool:
        """Import data from JSON string."""
        try:
            data = json.loads(json_data)

            # Import agents
            for agent_data in data.get("agents", []):
                self._import_entity(agent_data, Agent, self.agents)

            # Import panels
            for panel_data in data.get("panels", []):
                self._import_entity(panel_data, Panel, self.panels)
        except (json.JSONDecodeError, KeyError, TypeError):
            return False
        else:
            return True


# Global instance
agent_manager = AgentManager()
