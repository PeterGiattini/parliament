from types import SimpleNamespace
from typing import Any

import pytest
from langgraph.errors import GraphRecursionError

from agent_templates import get_default_agents
from langgraph_debate_orchestrator import LangGraphDebateOrchestrator


class FakeLLM:
    def __init__(self, content: str = "TEST-RESPONSE") -> None:
        self._content = content

    async def ainvoke(self, messages: list[Any]) -> Any:  # pragma: no cover - trivial
        return SimpleNamespace(content=self._content)


@pytest.mark.asyncio
async def test_budget_guard_with_tiny_graph_recursion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    agents = get_default_agents()[:2]
    orch = LangGraphDebateOrchestrator(agents, llm=FakeLLM())

    # With a very small recursion_limit, the graph should raise a GraphRecursionError
    with pytest.raises(GraphRecursionError):
        async for _ in orch.graph.astream(
            {
                "topic": "T",
                "agents": agents,
                "debate_transcript": [],
                "current_round": sorted(orch.debate_spec.rounds.keys())[0],
                "round_agent_order": [],
                "current_agent_index": 0,
                "status_context": None,
                "last_speaker_id": None,
            },
            config={"recursion_limit": 5},
        ):
            pass
