"""Unit tests for the LangGraphDebateOrchestrator recursion limit functionality."""

from collections.abc import AsyncGenerator
from types import SimpleNamespace
from typing import Any

import pytest
from langchain_core.runnables import Runnable

from agent_templates import get_default_agents
from debate_spec import DebateSpec, RoundContextStrategy, RoundSpec, RoundType
from langgraph_debate_orchestrator import LangGraphDebateOrchestrator


class FakeLLM(Runnable):
    """Deterministic fake LLM used in tests."""

    def __init__(self, content: str = "TEST-RESPONSE") -> None:
        self._content = content

    def invoke(self, messages: list[Any], config: dict | None = None) -> Any:
        return SimpleNamespace(content=self._content)

    async def ainvoke(self, messages: list[Any], config: dict | None = None) -> Any:
        return SimpleNamespace(content=self._content)

    def bind_tools(self, tools: list[Any]) -> "FakeLLM":
        return self


@pytest.fixture
def simple_debate_spec() -> DebateSpec:
    """Create a simple debate spec with minimal complexity for testing."""
    return DebateSpec(
        rounds={
            1: RoundSpec(
                title="Opening",
                type=RoundType.parallel,
                context_strategy=RoundContextStrategy.topic_only,
                prompt_template="Test prompt",
            ),
            2: RoundSpec(
                title="Discussion",
                type=RoundType.sequential,
                context_strategy=RoundContextStrategy.full_transcript,
                prompt_template="Test prompt",
            ),
        }
    )


def test_simple_debate_recursion_limit(simple_debate_spec: DebateSpec) -> None:
    """Test recursion limit calculation for a simple 2-round debate."""
    agents = get_default_agents()[:2]  # 2 agents
    fake_llm = FakeLLM()
    orchestrator = LangGraphDebateOrchestrator(
        agents, debate_spec=simple_debate_spec, llm=fake_llm
    )

    limit = orchestrator._calculate_recursion_limit()

    # Round 1 (parallel): 2 steps
    # Round 2 (sequential): 2 + 2 agents * 2 steps = 2 + 4 = 6 steps
    # Total: 1 + 2 + 6 = 9
    # With 30% buffer: 9 * 1.3 = 11.7, clamped to 25 (min limit)
    assert limit == 25


def test_complex_debate_recursion_limit() -> None:
    """Test recursion limit calculation for a complex debate."""
    complex_spec = DebateSpec(
        rounds={
            1: RoundSpec(
                title="P1",
                type=RoundType.parallel,
                context_strategy=RoundContextStrategy.topic_only,
                prompt_template="",
            ),
            2: RoundSpec(
                title="S1",
                type=RoundType.sequential,
                context_strategy=RoundContextStrategy.full_transcript,
                prompt_template="",
            ),
            3: RoundSpec(
                title="S2",
                type=RoundType.sequential,
                context_strategy=RoundContextStrategy.full_transcript,
                prompt_template="",
            ),
            4: RoundSpec(
                title="M1",
                type=RoundType.moderator,
                context_strategy=RoundContextStrategy.full_transcript,
                prompt_template="",
            ),
        }
    )

    agents = get_default_agents()[:3]  # 3 agents
    fake_llm = FakeLLM()
    orchestrator = LangGraphDebateOrchestrator(
        agents, debate_spec=complex_spec, llm=fake_llm
    )

    limit = orchestrator._calculate_recursion_limit()

    # Round 1 (parallel): 2 steps
    # Round 2 (sequential): 2 + 3 agents * 2 steps = 2 + 6 = 8 steps
    # Round 3 (sequential): 2 + 3 agents * 2 steps = 2 + 6 = 8 steps
    # Round 4 (moderator): 2 steps
    # Total: 1 + 2 + 8 + 8 + 2 = 21
    # With 30% buffer: 21 * 1.3 = 27.3, clamped to 27
    assert limit == 27


def test_recursion_limit_bounds() -> None:
    """Test that recursion limit respects min/max bounds."""
    # Test minimum bound
    single_round_spec = DebateSpec(
        rounds={
            1: RoundSpec(
                title="Single",
                type=RoundType.parallel,
                context_strategy=RoundContextStrategy.topic_only,
                prompt_template="",
            )
        }
    )

    agents = get_default_agents()[:1]  # 1 agent
    fake_llm = FakeLLM()
    orchestrator = LangGraphDebateOrchestrator(
        agents, debate_spec=single_round_spec, llm=fake_llm
    )

    limit = orchestrator._calculate_recursion_limit()
    assert limit == 25  # minimum bound

    # Test maximum bound with many sequential rounds
    many_rounds = {}
    for i in range(1, 21):  # 20 rounds
        many_rounds[i] = RoundSpec(
            title=f"Round {i}",
            type=RoundType.sequential,
            context_strategy=RoundContextStrategy.full_transcript,
            prompt_template="",
        )

    complex_spec = DebateSpec(rounds=many_rounds)
    agents = get_default_agents()[:4]  # 4 agents
    fake_llm2 = FakeLLM()
    orchestrator = LangGraphDebateOrchestrator(
        agents, debate_spec=complex_spec, llm=fake_llm2
    )

    limit = orchestrator._calculate_recursion_limit()
    assert limit == 100  # maximum bound


@pytest.mark.asyncio
async def test_run_debate_uses_calculated_limit(simple_debate_spec: DebateSpec) -> None:
    """Test that run_debate uses the calculated recursion limit."""
    agents = get_default_agents()[:2]  # 2 agents
    fake_llm = FakeLLM()
    orchestrator = LangGraphDebateOrchestrator(
        agents, debate_spec=simple_debate_spec, llm=fake_llm
    )

    # Get the calculated limit
    expected_limit = orchestrator._calculate_recursion_limit()

    # Mock the graph.astream method to capture the config
    original_astream = orchestrator.graph.astream
    captured_config = None

    async def mock_astream(state, config=None) -> AsyncGenerator[dict, None]:
        nonlocal captured_config
        captured_config = config
        yield {"route_debate": state}

    orchestrator.graph.astream = mock_astream

    try:
        # Start the debate (this will call our mocked astream)
        async for _ in orchestrator.run_debate("Test topic"):
            break  # Just get the first iteration

        # Verify the config was passed with the correct recursion limit
        assert captured_config is not None
        assert captured_config["recursion_limit"] == expected_limit

    finally:
        # Restore the original method
        orchestrator.graph.astream = original_astream
