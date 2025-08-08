"""Unit tests for LangGraph debate orchestrator methods."""

from unittest.mock import Mock, patch

import pytest

from agent_templates import get_default_agents
from langgraph_debate_orchestrator import LangGraphDebateOrchestrator
from models import Agent


@pytest.fixture
def test_agents():
    """Test fixture for agents."""
    return get_default_agents()[:2]  # Use first 2 agents for testing


@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    mock = Mock()
    mock.ainvoke.return_value.content = "Mock response"
    return mock


@patch("langgraph_debate_orchestrator.ChatVertexAI")
def test_langgraph_orchestrator_creation(mock_chat_vertex, test_agents, mock_llm):
    """Test LangGraph orchestrator creation."""
    mock_chat_vertex.return_value = mock_llm

    orchestrator = LangGraphDebateOrchestrator(test_agents)
    assert orchestrator.agents == test_agents
    assert orchestrator.llm is not None


@patch("langgraph_debate_orchestrator.ChatVertexAI")
def test_orchestrator_has_prompts_and_structure(
    mock_chat_vertex, test_agents, mock_llm
):
    """Test that orchestrator has the expected prompts and structure."""
    mock_chat_vertex.return_value = mock_llm

    orchestrator = LangGraphDebateOrchestrator(test_agents)

    assert hasattr(orchestrator, "prompts")
    assert hasattr(orchestrator, "structure")

    expected_keys = ["opening_statement", "rebuttal", "surrebuttal", "synthesis"]
    for key in expected_keys:
        assert key in orchestrator.prompts

    expected_rounds = [1, 2, 3, 4]
    for round_num in expected_rounds:
        assert round_num in orchestrator.structure


@patch("langgraph_debate_orchestrator.ChatVertexAI")
def test_orchestrator_accepts_agent_objects(mock_chat_vertex, mock_llm):
    """Test that orchestrator accepts Agent objects."""
    mock_chat_vertex.return_value = mock_llm

    test_agent = Agent(
        id="test-agent",
        name="Test Agent",
        description="A test agent",
        system_prompt="You are a test agent.",
        color="#000000",
        icon="🤖",
        tags=["test"],
        is_built_in=False,
        created_at=1234567890,
        usage_count=0,
    )

    orchestrator = LangGraphDebateOrchestrator([test_agent])

    assert len(orchestrator.agents) == 1
    assert orchestrator.agents[0].name == "Test Agent"


@patch("langgraph_debate_orchestrator.ChatVertexAI")
def test_orchestrator_with_duplicate_names(mock_chat_vertex, mock_llm):
    """Test that orchestrator works correctly with agents that have duplicate names but different IDs."""
    mock_chat_vertex.return_value = mock_llm

    agent1 = Agent(
        id="agent-1",
        name="Test Agent",
        description="First test agent",
        system_prompt="You are the first test agent.",
        color="#FF0000",
        icon="🤖",
        tags=["test", "first"],
        is_built_in=False,
        created_at=1234567890,
        usage_count=0,
    )

    agent2 = Agent(
        id="agent-2",
        name="Test Agent",
        description="Second test agent",
        system_prompt="You are the second test agent.",
        color="#00FF00",
        icon="🧠",
        tags=["test", "second"],
        is_built_in=False,
        created_at=1234567891,
        usage_count=0,
    )

    agents = [agent1, agent2]
    orchestrator = LangGraphDebateOrchestrator(agents)

    assert len(orchestrator.agents) == 2
    assert orchestrator.agents[0].name == orchestrator.agents[1].name
    assert orchestrator.agents[0].id != orchestrator.agents[1].id

    # Test that name-based lookup would be ambiguous (this is why we use IDs)
    agents_by_name = [a for a in agents if a.name == "Test Agent"]
    assert len(agents_by_name) == 2  # Both agents have the same name
