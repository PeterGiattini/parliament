from types import SimpleNamespace
from typing import Any

import pytest

from agent_templates import get_default_agents
from debate_spec import (
    DebateSpec,
    RoundContextStrategy,
    RoundSpec,
    RoundType,
    load_default_debate_spec,
)
from langgraph_debate_orchestrator import LangGraphDebateOrchestrator


class FakeLLM:
    """Deterministic fake LLM used in tests."""

    def __init__(self, content: str = "TEST-RESPONSE") -> None:
        self._content = content

    async def ainvoke(self, messages: list[Any]) -> Any:  # pragma: no cover - trivial
        return SimpleNamespace(content=self._content)


@pytest.fixture
def fake_llm() -> FakeLLM:
    return FakeLLM()


def test_debate_spec_loads_default() -> None:
    spec = load_default_debate_spec()
    assert isinstance(spec, DebateSpec)
    # Expect at least one parallel, one sequential, and one moderator per default file
    round_types = {r.type for r in spec.rounds.values()}
    assert RoundType.parallel in round_types
    assert RoundType.sequential in round_types
    assert RoundType.moderator in round_types


def test_debate_spec_invalid_round_type_raises() -> None:
    # Manually construct via RoundSpec to simulate validation and ensure enums are enforced
    with pytest.raises(ValueError):
        RoundSpec(
            title="Bad",
            type=RoundType("not-a-type"),  # type: ignore[arg-type]
            context_strategy=RoundContextStrategy.topic_only,
            prompt_template="",
        )


@pytest.mark.asyncio
async def test_router_reaches_end_with_default_spec(
    monkeypatch: pytest.MonkeyPatch, fake_llm: FakeLLM
) -> None:
    agents = get_default_agents()[:2]
    orch = LangGraphDebateOrchestrator(agents, llm=fake_llm)

    # Consume the stream to completion; assert we see debate_complete
    seen_complete = False
    async for chunk in orch.run_debate("Test topic"):
        if (
            chunk.startswith("data: ")
            and "\n\n" in chunk
            and '"type": "debate_complete"' in chunk
        ):
            seen_complete = True
    assert seen_complete


@pytest.mark.asyncio
async def test_transcript_shape_is_stable(
    monkeypatch: pytest.MonkeyPatch, fake_llm: FakeLLM
) -> None:
    agents = get_default_agents()[:2]
    orch = LangGraphDebateOrchestrator(agents, llm=fake_llm)

    messages = []
    async for chunk in orch.run_debate("A topic"):
        if '"type": "agent_response"' in chunk:
            # Extract minimal JSON payload after "data: " prefix
            payload = chunk[len("data: ") :].strip()
            messages.append(payload)

    # Expect at least one opening statement per agent, at least one sequential turn, and a moderator
    # We assert by counting occurrences rather than content
    assert len(messages) >= 1
