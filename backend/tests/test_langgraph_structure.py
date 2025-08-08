"""Unit tests for LangGraph debate orchestrator structure."""

from unittest.mock import Mock, patch

import pytest

from agent_templates import get_default_agents
from langgraph_debate_orchestrator import DebateState, LangGraphDebateOrchestrator
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
def test_orchestrator_creation(mock_chat_vertex, test_agents, mock_llm):
    """Test that LangGraph orchestrator can be created."""
    mock_chat_vertex.return_value = mock_llm

    orchestrator = LangGraphDebateOrchestrator(test_agents)
    assert orchestrator is not None
    assert orchestrator.agents == test_agents


@patch("langgraph_debate_orchestrator.ChatVertexAI")
def test_graph_structure(mock_chat_vertex, test_agents, mock_llm):
    """Test that the graph has the expected structure."""
    mock_chat_vertex.return_value = mock_llm

    orchestrator = LangGraphDebateOrchestrator(test_agents)

    # Check that graph has the expected nodes for the supervisor-based design
    expected_nodes = {
        "route_debate",
        "execute_opening_statements",
        "setup_sequential_round",
        "execute_sequential_turn",
        "execute_synthesis",
    }
    actual_nodes = set(orchestrator.graph.nodes.keys())

    assert expected_nodes.issubset(actual_nodes)


@patch("langgraph_debate_orchestrator.ChatVertexAI")
def test_graph_compilation(mock_chat_vertex, test_agents, mock_llm):
    """Test that the graph compiles successfully."""
    mock_chat_vertex.return_value = mock_llm

    orchestrator = LangGraphDebateOrchestrator(test_agents)

    # Check that graph is compiled
    assert hasattr(orchestrator.graph, "nodes")
    assert hasattr(orchestrator.graph, "astream")


def test_debate_state_creation(test_agents):
    """Test that DebateState can be created with valid data."""
    state = DebateState(
        topic="Test topic",
        agents=test_agents,
        debate_transcript=[],
        current_round=1,
        round_agent_order=[],
        current_agent_index=0,
        status_context=None,
    )

    assert state["topic"] == "Test topic"
    assert state["agents"] == test_agents
    assert state["debate_transcript"] == []
    assert state["current_round"] == 1
    assert state["round_agent_order"] == []
    assert state["current_agent_index"] == 0
    assert state["status_context"] is None


def test_debate_state_structure(test_agents):
    """Test that DebateState has the expected structure."""
    state = DebateState(
        topic="Test topic",
        agents=test_agents,
        debate_transcript=[],
        current_round=1,
        round_agent_order=[],
        current_agent_index=0,
        status_context=None,
    )

    expected_keys = [
        "topic",
        "agents",
        "debate_transcript",
        "current_round",
        "round_agent_order",
        "current_agent_index",
        "status_context",
    ]
    for key in expected_keys:
        assert key in state


@patch("langgraph_debate_orchestrator.ChatVertexAI")
def test_orchestrator_prompts_and_structure(mock_chat_vertex, test_agents, mock_llm):
    """Test that orchestrator has access to prompts and structure."""
    mock_chat_vertex.return_value = mock_llm

    orchestrator = LangGraphDebateOrchestrator(test_agents)

    assert hasattr(orchestrator, "prompts")
    assert hasattr(orchestrator, "structure")
    assert orchestrator.prompts is not None
    assert orchestrator.structure is not None


@patch("langgraph_debate_orchestrator.ChatVertexAI")
def test_llm_initialization(mock_chat_vertex, test_agents, mock_llm):
    """Test that LLM is properly initialized."""
    mock_chat_vertex.return_value = mock_llm

    orchestrator = LangGraphDebateOrchestrator(test_agents)

    # LLM should be initialized
    assert orchestrator.llm is not None


@patch("langgraph_debate_orchestrator.ChatVertexAI")
def test_orchestrator_with_minimal_agents(mock_chat_vertex, mock_llm):
    """Test orchestrator with minimal agent data."""
    mock_chat_vertex.return_value = mock_llm

    # Create a test agent using the Agent model
    minimal_agents = [
        Agent(
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
    ]

    orchestrator = LangGraphDebateOrchestrator(minimal_agents)
    assert orchestrator.agents == minimal_agents
    assert len(orchestrator.graph.nodes) > 0


@patch("langgraph_debate_orchestrator.ChatVertexAI")
def test_orchestrator_with_empty_agents(mock_chat_vertex, mock_llm):
    """Test orchestrator behavior with empty agents list."""
    mock_chat_vertex.return_value = mock_llm

    orchestrator = LangGraphDebateOrchestrator([])
    assert orchestrator.agents == []
    # Should still be able to create the graph structure
    assert hasattr(orchestrator, "graph")
