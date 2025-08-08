"""Unit tests for debate orchestrator methods."""

from unittest.mock import Mock, patch

import pytest

from agent_templates import get_default_agents
from debate_orchestrator import DebateOrchestrator
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


@patch("debate_orchestrator.ChatVertexAI")
def test_legacy_orchestrator_creation(mock_chat_vertex, test_agents, mock_llm):
    """Test legacy orchestrator creation."""
    mock_chat_vertex.return_value = mock_llm

    orchestrator = DebateOrchestrator(test_agents)
    assert orchestrator.agents == test_agents
    assert orchestrator.llm is not None


@patch("langgraph_debate_orchestrator.ChatVertexAI")
def test_langgraph_orchestrator_creation(mock_chat_vertex, test_agents, mock_llm):
    """Test LangGraph orchestrator creation."""
    mock_chat_vertex.return_value = mock_llm

    orchestrator = LangGraphDebateOrchestrator(test_agents)
    assert orchestrator.agents == test_agents
    assert orchestrator.llm is not None


@patch("debate_orchestrator.ChatVertexAI")
@patch("langgraph_debate_orchestrator.ChatVertexAI")
def test_orchestrator_has_prompts_and_structure(
    mock_langgraph_chat, mock_legacy_chat, test_agents, mock_llm
):
    """Test that orchestrators have the expected prompts and structure."""
    mock_legacy_chat.return_value = mock_llm
    mock_langgraph_chat.return_value = mock_llm

    legacy_orchestrator = DebateOrchestrator(test_agents)
    langgraph_orchestrator = LangGraphDebateOrchestrator(test_agents)

    # Both should have prompts and structure
    assert hasattr(legacy_orchestrator, "prompts")
    assert hasattr(legacy_orchestrator, "structure")
    assert hasattr(langgraph_orchestrator, "prompts")
    assert hasattr(langgraph_orchestrator, "structure")

    # Should have expected prompt keys
    expected_keys = ["opening_statement", "rebuttal", "surrebuttal", "synthesis"]
    for key in expected_keys:
        assert key in legacy_orchestrator.prompts
        assert key in langgraph_orchestrator.prompts

    # Should have expected rounds
    expected_rounds = [1, 2, 3, 4]
    for round_num in expected_rounds:
        assert round_num in legacy_orchestrator.structure
        assert round_num in langgraph_orchestrator.structure


@patch("debate_orchestrator.ChatVertexAI")
@patch("langgraph_debate_orchestrator.ChatVertexAI")
def test_orchestrator_interface_consistency(
    mock_langgraph_chat, mock_legacy_chat, test_agents, mock_llm
):
    """Test that both orchestrators have consistent interfaces."""
    mock_legacy_chat.return_value = mock_llm
    mock_langgraph_chat.return_value = mock_llm

    legacy_orchestrator = DebateOrchestrator(test_agents)
    langgraph_orchestrator = LangGraphDebateOrchestrator(test_agents)

    # Both should have the same public interface
    assert hasattr(legacy_orchestrator, "run_debate")
    assert hasattr(langgraph_orchestrator, "run_debate")

    # Both should have agents, prompts, and structure
    assert legacy_orchestrator.agents == langgraph_orchestrator.agents
    assert legacy_orchestrator.prompts == langgraph_orchestrator.prompts
    assert legacy_orchestrator.structure == langgraph_orchestrator.structure


@patch("debate_orchestrator.ChatVertexAI")
@patch("langgraph_debate_orchestrator.ChatVertexAI")
def test_orchestrator_accepts_agent_objects(
    mock_langgraph_chat, mock_legacy_chat, mock_llm
):
    """Test that orchestrators accept Agent objects."""
    mock_legacy_chat.return_value = mock_llm
    mock_langgraph_chat.return_value = mock_llm

    # Create a test agent using the Agent model
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

    # Both orchestrators should accept Agent objects
    legacy_orchestrator = DebateOrchestrator([test_agent])
    langgraph_orchestrator = LangGraphDebateOrchestrator([test_agent])

    assert len(legacy_orchestrator.agents) == 1
    assert len(langgraph_orchestrator.agents) == 1
    assert legacy_orchestrator.agents[0].name == "Test Agent"
    assert langgraph_orchestrator.agents[0].name == "Test Agent"


@patch("debate_orchestrator.ChatVertexAI")
@patch("langgraph_debate_orchestrator.ChatVertexAI")
def test_orchestrator_with_duplicate_names(
    mock_langgraph_chat, mock_legacy_chat, mock_llm
):
    """Test that orchestrators work correctly with agents that have duplicate names but different IDs."""
    mock_legacy_chat.return_value = mock_llm
    mock_langgraph_chat.return_value = mock_llm

    # Create agents with duplicate names but different IDs
    agent1 = Agent(
        id="agent-1",
        name="Test Agent",  # Same name
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
        name="Test Agent",  # Same name
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

    # Both orchestrators should accept agents with duplicate names
    legacy_orchestrator = DebateOrchestrator(agents)
    langgraph_orchestrator = LangGraphDebateOrchestrator(agents)

    # Verify both agents are included
    assert len(legacy_orchestrator.agents) == 2
    assert len(langgraph_orchestrator.agents) == 2

    # Verify agents have same names but different IDs
    assert legacy_orchestrator.agents[0].name == legacy_orchestrator.agents[1].name
    assert legacy_orchestrator.agents[0].id != legacy_orchestrator.agents[1].id
    assert (
        langgraph_orchestrator.agents[0].name == langgraph_orchestrator.agents[1].name
    )
    assert langgraph_orchestrator.agents[0].id != langgraph_orchestrator.agents[1].id

    # Verify IDs are unique
    legacy_ids = [agent.id for agent in legacy_orchestrator.agents]
    langgraph_ids = [agent.id for agent in langgraph_orchestrator.agents]
    assert len(set(legacy_ids)) == 2
    assert len(set(langgraph_ids)) == 2


@patch("debate_orchestrator.ChatVertexAI")
@patch("langgraph_debate_orchestrator.ChatVertexAI")
def test_agent_comparison_with_duplicate_names(
    mock_langgraph_chat, mock_legacy_chat, mock_llm
):
    """Test that agent comparison logic works correctly with duplicate names."""
    mock_legacy_chat.return_value = mock_llm
    mock_langgraph_chat.return_value = mock_llm

    # Create agents with duplicate names but different IDs
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
        name="Test Agent",  # Same name as agent1
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

    # Test that ID-based comparison correctly identifies different agents
    assert agent1.name == agent2.name  # Names are the same
    assert agent1.id != agent2.id  # IDs are different

    # Test that we can find the correct agent by ID
    agent1_by_id = next((a for a in agents if a.id == "agent-1"), None)
    agent2_by_id = next((a for a in agents if a.id == "agent-2"), None)

    assert agent1_by_id is not None
    assert agent2_by_id is not None
    assert agent1_by_id.id == "agent-1"
    assert agent2_by_id.id == "agent-2"
    assert agent1_by_id.name == agent2_by_id.name  # Names are still the same

    # Test that name-based lookup would be ambiguous (this is why we use IDs)
    agents_by_name = [a for a in agents if a.name == "Test Agent"]
    assert len(agents_by_name) == 2  # Both agents have the same name
