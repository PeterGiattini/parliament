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


# Tests for _get_randomized_agents internal function
# Testing internal function directly due to complex setup required by public API
@patch("langgraph_debate_orchestrator.ChatVertexAI")
class TestGetRandomizedAgents:
    """Test the _get_randomized_agents internal function."""

    def test_empty_agents_list(self, mock_chat_vertex, mock_llm):
        """Test behavior with empty agents list."""
        mock_chat_vertex.return_value = mock_llm
        orchestrator = LangGraphDebateOrchestrator([])

        result = orchestrator._get_randomized_agents()  # noqa: SLF001
        assert result == []

    def test_single_agent_no_exclusion(self, mock_chat_vertex, mock_llm):
        """Test single agent without exclusion constraint."""
        mock_chat_vertex.return_value = mock_llm
        agent = Agent(
            id="single-agent",
            name="Single Agent",
            description="A single agent",
            system_prompt="You are a single agent.",
            color="#000000",
            icon="🤖",
            tags=["test"],
            is_built_in=False,
            created_at=1234567890,
            usage_count=0,
        )
        orchestrator = LangGraphDebateOrchestrator([agent])

        result = orchestrator._get_randomized_agents()  # noqa: SLF001
        assert result == [agent]

    def test_single_agent_with_exclusion(self, mock_chat_vertex, mock_llm):
        """Test single agent with exclusion constraint (should ignore constraint)."""
        mock_chat_vertex.return_value = mock_llm
        agent = Agent(
            id="single-agent",
            name="Single Agent",
            description="A single agent",
            system_prompt="You are a single agent.",
            color="#000000",
            icon="🤖",
            tags=["test"],
            is_built_in=False,
            created_at=1234567890,
            usage_count=0,
        )
        orchestrator = LangGraphDebateOrchestrator([agent])

        # Even though we exclude the only agent, it should still be returned
        result = orchestrator._get_randomized_agents(  # noqa: SLF001
            exclude_first_agent_id="single-agent"
        )
        assert result == [agent]

    @patch("random.shuffle")
    def test_exclude_first_agent_triggered(
        self, mock_shuffle, mock_chat_vertex, mock_llm
    ):
        """Test that excluded agent is moved from first position when constraint applies."""
        mock_chat_vertex.return_value = mock_llm

        agent1 = Agent(
            id="agent-1",
            name="Agent 1",
            description="First agent",
            system_prompt="You are agent 1.",
            color="#FF0000",
            icon="🤖",
            tags=["test"],
            is_built_in=False,
            created_at=1234567890,
            usage_count=0,
        )
        agent2 = Agent(
            id="agent-2",
            name="Agent 2",
            description="Second agent",
            system_prompt="You are agent 2.",
            color="#00FF00",
            icon="🧠",
            tags=["test"],
            is_built_in=False,
            created_at=1234567891,
            usage_count=0,
        )
        agent3 = Agent(
            id="agent-3",
            name="Agent 3",
            description="Third agent",
            system_prompt="You are agent 3.",
            color="#0000FF",
            icon="👾",
            tags=["test"],
            is_built_in=False,
            created_at=1234567892,
            usage_count=0,
        )

        orchestrator = LangGraphDebateOrchestrator([agent1, agent2, agent3])

        # Mock shuffle to put agent1 first (the one we want to exclude)
        def shuffle_side_effect(agent_list) -> None:
            agent_list[:] = [agent1, agent2, agent3]

        mock_shuffle.side_effect = shuffle_side_effect

        result = orchestrator._get_randomized_agents(exclude_first_agent_id="agent-1")  # noqa: SLF001

        # Expected: agent1 moved from front to back
        assert result == [agent2, agent3, agent1]
        mock_shuffle.assert_called_once()

    @patch("random.shuffle")
    def test_exclude_first_agent_not_triggered(
        self, mock_shuffle, mock_chat_vertex, mock_llm
    ):
        """Test that order is preserved when excluded agent is not first."""
        mock_chat_vertex.return_value = mock_llm

        agent1 = Agent(
            id="agent-1",
            name="Agent 1",
            description="First agent",
            system_prompt="You are agent 1.",
            color="#FF0000",
            icon="🤖",
            tags=["test"],
            is_built_in=False,
            created_at=1234567890,
            usage_count=0,
        )
        agent2 = Agent(
            id="agent-2",
            name="Agent 2",
            description="Second agent",
            system_prompt="You are agent 2.",
            color="#00FF00",
            icon="🧠",
            tags=["test"],
            is_built_in=False,
            created_at=1234567891,
            usage_count=0,
        )
        agent3 = Agent(
            id="agent-3",
            name="Agent 3",
            description="Third agent",
            system_prompt="You are agent 3.",
            color="#0000FF",
            icon="👾",
            tags=["test"],
            is_built_in=False,
            created_at=1234567892,
            usage_count=0,
        )

        orchestrator = LangGraphDebateOrchestrator([agent1, agent2, agent3])

        # Mock shuffle to put agent1 in middle (not first)
        def shuffle_side_effect(agent_list) -> None:
            agent_list[:] = [agent2, agent1, agent3]

        mock_shuffle.side_effect = shuffle_side_effect

        result = orchestrator._get_randomized_agents(exclude_first_agent_id="agent-1")  # noqa: SLF001

        # Expected: order preserved as agent1 is not first
        assert result == [agent2, agent1, agent3]
        mock_shuffle.assert_called_once()

    @patch("random.shuffle")
    def test_exclude_nonexistent_agent(self, mock_shuffle, mock_chat_vertex, mock_llm):
        """Test behavior when excluding an agent that doesn't exist."""
        mock_chat_vertex.return_value = mock_llm

        agent1 = Agent(
            id="agent-1",
            name="Agent 1",
            description="First agent",
            system_prompt="You are agent 1.",
            color="#FF0000",
            icon="🤖",
            tags=["test"],
            is_built_in=False,
            created_at=1234567890,
            usage_count=0,
        )
        agent2 = Agent(
            id="agent-2",
            name="Agent 2",
            description="Second agent",
            system_prompt="You are agent 2.",
            color="#00FF00",
            icon="🧠",
            tags=["test"],
            is_built_in=False,
            created_at=1234567891,
            usage_count=0,
        )

        orchestrator = LangGraphDebateOrchestrator([agent1, agent2])

        # Mock shuffle to put agent1 first
        def shuffle_side_effect(agent_list) -> None:
            agent_list[:] = [agent1, agent2]

        mock_shuffle.side_effect = shuffle_side_effect

        result = orchestrator._get_randomized_agents(  # noqa: SLF001
            exclude_first_agent_id="nonexistent-agent"
        )

        # Expected: order preserved as excluded agent doesn't exist
        assert result == [agent1, agent2]
        mock_shuffle.assert_called_once()

    @patch("random.shuffle")
    def test_no_exclusion_parameter(self, mock_shuffle, mock_chat_vertex, mock_llm):
        """Test behavior when no exclusion parameter is provided."""
        mock_chat_vertex.return_value = mock_llm

        agent1 = Agent(
            id="agent-1",
            name="Agent 1",
            description="First agent",
            system_prompt="You are agent 1.",
            color="#FF0000",
            icon="🤖",
            tags=["test"],
            is_built_in=False,
            created_at=1234567890,
            usage_count=0,
        )
        agent2 = Agent(
            id="agent-2",
            name="Agent 2",
            description="Second agent",
            system_prompt="You are agent 2.",
            color="#00FF00",
            icon="🧠",
            tags=["test"],
            is_built_in=False,
            created_at=1234567891,
            usage_count=0,
        )

        orchestrator = LangGraphDebateOrchestrator([agent1, agent2])

        # Mock shuffle to put agent1 first
        def shuffle_side_effect(agent_list) -> None:
            agent_list[:] = [agent1, agent2]

        mock_shuffle.side_effect = shuffle_side_effect

        result = orchestrator._get_randomized_agents()  # noqa: SLF001

        # Expected: shuffled order preserved
        assert result == [agent1, agent2]
        mock_shuffle.assert_called_once()

    @patch("random.shuffle")
    def test_exclude_first_agent_with_none_parameter(
        self, mock_shuffle, mock_chat_vertex, mock_llm
    ):
        """Test behavior when exclude_first_agent_id is None."""
        mock_chat_vertex.return_value = mock_llm

        agent1 = Agent(
            id="agent-1",
            name="Agent 1",
            description="First agent",
            system_prompt="You are agent 1.",
            color="#FF0000",
            icon="🤖",
            tags=["test"],
            is_built_in=False,
            created_at=1234567890,
            usage_count=0,
        )
        agent2 = Agent(
            id="agent-2",
            name="Agent 2",
            description="Second agent",
            system_prompt="You are agent 2.",
            color="#00FF00",
            icon="🧠",
            tags=["test"],
            is_built_in=False,
            created_at=1234567891,
            usage_count=0,
        )

        orchestrator = LangGraphDebateOrchestrator([agent1, agent2])

        # Mock shuffle to put agent1 first
        def shuffle_side_effect(agent_list) -> None:
            agent_list[:] = [agent1, agent2]

        mock_shuffle.side_effect = shuffle_side_effect

        result = orchestrator._get_randomized_agents(exclude_first_agent_id=None)  # noqa: SLF001

        # Expected: shuffled order preserved as no exclusion is specified
        assert result == [agent1, agent2]
        mock_shuffle.assert_called_once()
