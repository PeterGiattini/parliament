"""LangGraph-based debate orchestrator for managing multi-agent debates."""

import asyncio
import json
import logging
import os
import random
from collections.abc import AsyncGenerator
from typing import Any, TypedDict

from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import END, StateGraph

import models
from debate_spec import (
    DebateSpec,
    RoundContextStrategy,
    RoundType,
    load_default_debate_spec,
)

logger = logging.getLogger(__name__)


LLM_CONFIG = {
    "model_name": "gemini-2.0-flash",
    "temperature": 0.7,
    "max_output_tokens": 2048,
    "location": "us-central1",
    "max_retries": 3,
}

MODEL_CONFIG = {
    "timeout": 30,
}


class DebateState(TypedDict):
    """Represent the state for the LangGraph debate workflow."""

    topic: str
    agents: list[models.Agent]
    debate_transcript: list[dict[str, Any]]
    current_round: int
    round_agent_order: list[models.Agent]
    current_agent_index: int
    status_context: dict[str, Any] | None
    # The agent ID who spoke last in the previous round (used to avoid
    # back-to-back turns)
    last_speaker_id: str | None


class LangGraphDebateOrchestrator:
    """Orchestrate debates using a supervisor-based, DebateSpec-driven LangGraph.

    The graph is compiled from a DebateSpec that defines:
    - rounds (order and titles)
    - round type (parallel | sequential | moderator)
    - context strategy per round
    - prompt template per round
    """

    def __init__(
        self,
        agents: list[models.Agent],
        debate_spec: DebateSpec | None = None,
        llm: BaseLanguageModel | None = None,
    ) -> None:
        """Initialize the debate orchestrator."""
        self.agents = agents
        self.llm = llm or ChatVertexAI(
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            **LLM_CONFIG,
            model_kwargs=MODEL_CONFIG,
        )
        self.debate_spec: DebateSpec = debate_spec or load_default_debate_spec()
        self.graph = self._build_debate_graph()
        self.round_titles = {r: p.title for r, p in self.debate_spec.rounds.items()}
        self._ordered_rounds: list[int] = sorted(self.debate_spec.rounds.keys())
        self._first_sequential_round: int | None = next(
            (
                r
                for r in self._ordered_rounds
                if self.debate_spec.type_for_round(r) == RoundType.sequential
            ),
            None,
        )

    def _build_debate_graph(self) -> StateGraph:
        """Build the LangGraph workflow for the debate structure."""
        workflow = StateGraph(DebateState)

        workflow.add_node("route_debate", self._route_debate)
        workflow.add_node(
            "execute_parallel_round",
            self._execute_parallel_round,
        )
        workflow.add_node("setup_sequential_round", self._setup_sequential_round)
        workflow.add_node("execute_sequential_turn", self._execute_sequential_turn)
        workflow.add_node("execute_moderator_round", self._execute_moderator_round)

        workflow.set_entry_point("route_debate")

        workflow.add_conditional_edges(
            "route_debate",
            lambda state: state["status_context"]["code"],
            {
                "OPENING_STATEMENTS": "execute_parallel_round",
                "SETUP_SEQUENTIAL_ROUND": "setup_sequential_round",
                "SEQUENTIAL_TURN": "execute_sequential_turn",
                "MODERATOR_ROUND": "execute_moderator_round",
                "END": END,
            },
        )

        workflow.add_edge("execute_parallel_round", "route_debate")
        workflow.add_edge("setup_sequential_round", "route_debate")
        workflow.add_edge("execute_sequential_turn", "route_debate")
        # Allow moderator rounds to chain; routing will END when no next round exists
        workflow.add_edge("execute_moderator_round", "route_debate")

        return workflow.compile()

    async def run_debate(self, topic: str) -> AsyncGenerator[str, None]:
        """Run the debate and yield streaming, structured SSE responses."""
        initial_state = DebateState(
            topic=topic,
            agents=self.agents,
            debate_transcript=[],
            current_round=self._ordered_rounds[0],
            round_agent_order=[],
            current_agent_index=0,
            status_context=None,
            last_speaker_id=None,
        )

        last_status_context = None
        last_transcript_index = 0

        async for state_update in self.graph.astream(initial_state):
            # Use the latest node's state in this update batch.
            _, state = next(reversed(state_update.items()))
            if not state:
                continue

            status_context = state.get("status_context")
            if status_context and status_context != last_status_context:
                yield self._create_sse_event("status_update", status_context)
                last_status_context = status_context
                await asyncio.sleep(0.1)

            transcript = state.get("debate_transcript", [])
            if len(transcript) > last_transcript_index:
                for i in range(last_transcript_index, len(transcript)):
                    yield self._create_sse_event("agent_response", transcript[i])
                    await asyncio.sleep(0.5)
                last_transcript_index = len(transcript)

        yield self._create_sse_event("debate_complete", {})

    def _route_debate(self, state: DebateState) -> dict:
        """Route the debate by setting the next status code in state."""
        round_num = state["current_round"]

        if round_num not in self.debate_spec.rounds:
            return {"status_context": {"code": "END"}}

        round_type = self.debate_spec.type_for_round(round_num)
        if round_type == RoundType.parallel:
            return {"status_context": {"code": "OPENING_STATEMENTS"}}
        if round_type == RoundType.sequential:
            if not state.get("round_agent_order"):
                return {"status_context": {"code": "SETUP_SEQUENTIAL_ROUND"}}
            return {"status_context": {"code": "SEQUENTIAL_TURN"}}
        if round_type == RoundType.moderator:
            return {"status_context": {"code": "MODERATOR_ROUND"}}

        return {"status_context": {"code": "END"}}

    async def _execute_parallel_round(self, state: DebateState) -> dict:
        """Node for the parallel opening statements round."""
        status_context = {
            "code": "ROUND_STARTING",
            "round_number": state["current_round"],
            "round_title": self._title_for(state["current_round"]),
            "round_type": self.debate_spec.type_for_round(state["current_round"])
            or "parallel",
        }
        round_cfg = self.debate_spec.rounds[state["current_round"]]
        content = self._build_round_context(state, round_cfg.context_strategy)
        tasks = [
            self._invoke_agent(agent, round_cfg.prompt_template, content)
            for agent in self.agents
        ]
        results = await asyncio.gather(*tasks)

        current_transcript = state.get("debate_transcript", [])
        for agent, response in zip(self.agents, results, strict=True):
            current_transcript.append(
                self._create_transcript_entry(agent, response, state["current_round"])
            )

        return {
            "debate_transcript": current_transcript,
            "current_round": self._next_round_number(state["current_round"]),
            "status_context": status_context,
        }

    def _setup_sequential_round(self, state: DebateState) -> dict:
        """Node to set up the agent order for a sequential round."""
        round_num = state["current_round"]
        status_context = {
            "code": "ROUND_STARTING",
            "round_number": round_num,
            "round_title": self._title_for(round_num),
            "round_type": self.debate_spec.type_for_round(round_num) or "sequential",
        }
        # Avoid back-to-back turns by not starting with the prior round's last
        # speaker (if available)
        exclude_first = state.get("last_speaker_id")
        return {
            "round_agent_order": self._get_randomized_agents(
                exclude_first_agent_id=exclude_first,
            ),
            "status_context": status_context,
        }

    async def _execute_sequential_turn(self, state: DebateState) -> dict:
        """Execute a single turn in a sequential round.

        Also handles transitioning to the next round when the current one is
        complete.
        """
        round_num = state["current_round"]
        agent_index = state["current_agent_index"]
        agent = state["round_agent_order"][agent_index]

        status_context = {
            "code": "AGENT_TURN_STARTING",
            "round_number": round_num,
            "round_title": self.round_titles[round_num],
            "agent": {
                "name": agent.name,
                "icon": agent.icon,
            },
        }

        round_cfg = self.debate_spec.rounds[round_num]
        content = self._build_round_context(state, round_cfg.context_strategy)
        response = await self._invoke_agent(agent, round_cfg.prompt_template, content)

        current_transcript = state.get("debate_transcript", [])
        current_transcript.append(
            self._create_transcript_entry(agent, response, round_num)
        )

        next_agent_index = agent_index + 1

        # If this was the last agent, transition to the next round.
        if next_agent_index >= len(state["round_agent_order"]):
            return {
                "debate_transcript": current_transcript,
                "current_round": self._next_round_number(round_num),
                "current_agent_index": 0,
                "round_agent_order": [],  # Clear order for the next round
                "status_context": status_context,
                # Record the last speaker so the next sequential round can avoid
                # starting with them
                "last_speaker_id": agent.id,
            }

        # Otherwise, just advance the agent index.
        return {
            "debate_transcript": current_transcript,
            "current_agent_index": next_agent_index,
            "status_context": status_context,
        }

    async def _execute_moderator_round(self, state: DebateState) -> dict:
        """Node for a moderator round."""
        status_context = {
            "code": "ROUND_STARTING",
            "round_number": state["current_round"],
            "round_title": self._title_for(state["current_round"]),
            "round_type": self.debate_spec.type_for_round(state["current_round"])
            or "moderator",
        }
        round_cfg = self.debate_spec.rounds[state["current_round"]]
        content = self._build_round_context(state, round_cfg.context_strategy)
        response = await self._invoke_agent(None, round_cfg.prompt_template, content)

        current_transcript = state.get("debate_transcript", [])
        current_transcript.append(
            self._create_transcript_entry("Moderator", response, state["current_round"])
        )

        return {
            "debate_transcript": current_transcript,
            "current_round": self._next_round_number(state["current_round"]),
            "status_context": status_context,
        }

    def _get_randomized_agents(
        self, *, exclude_first_agent_id: str | None = None
    ) -> list[models.Agent]:
        """Get agents in randomized order.

        If ``exclude_first_agent_id`` is provided and there is more than one
        agent, the returned order will not start with that agent. This avoids a
        single agent speaking at the end of one round and immediately again at
        the start of the next.

        In single-agent "debates", the constraint cannot be satisfied and the
        lone agent will be returned as-is.
        """
        if not self.agents:
            return []
        agents_copy = self.agents.copy()
        random.shuffle(agents_copy)

        if (
            exclude_first_agent_id
            and len(agents_copy) > 1
            and agents_copy[0].id == exclude_first_agent_id
        ):
            # Rotate the list so the excluded agent is not first
            first = agents_copy.pop(0)
            agents_copy.append(first)
        return agents_copy

    def _create_transcript_entry(
        self, agent: models.Agent | str, response: str, round_num: int
    ) -> dict[str, Any]:
        """Create a standardized dictionary for a transcript entry."""
        if isinstance(agent, models.Agent):
            return {
                "agent": agent.name,
                "role": agent.tags[0] if agent.tags else "debater",
                "round": round_num,
                "content": response,
                "color": agent.color,
                "icon": agent.icon,
            }
        return {
            "agent": "Moderator",
            "role": "moderator",
            "round": round_num,
            "content": response,
            "color": "#6B7280",
            "icon": "🎤",
        }

    def _create_sse_event(self, event_type: str, data: dict) -> str:
        """Create a server-sent event (SSE) string payload."""
        payload = {"type": event_type, **data}
        return f"data: {json.dumps(payload)}\n\n"

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------
    def _next_round_number(self, current_round: int) -> int:
        """Return the next round number defined in the spec or a sentinel value.

        If no later round exists, return a number not in the spec so the router
        will send execution to END on the next tick.
        """
        for r in self._ordered_rounds:
            if r > current_round:
                return r
        return current_round + 1

    def _title_for(self, round_number: int) -> str:
        """Resolve a round title from spec or fallbacks for compatibility."""
        return (
            self.debate_spec.title_for_round(round_number)
            or self.round_titles.get(round_number)
            or f"Round {round_number}"
        )

    # ---------------------------------------------------------------------
    # Round utilities
    # ---------------------------------------------------------------------
    def _build_round_context(
        self, state: DebateState, strategy: RoundContextStrategy
    ) -> str:
        topic = state["topic"]
        transcript = state.get("debate_transcript", [])

        if strategy == RoundContextStrategy.topic_only:
            return topic

        if strategy == RoundContextStrategy.full_transcript:
            lines = [
                f"Original Topic: {topic}",
                "",
                "Full Debate Transcript So Far:",
            ]
            for entry in transcript:
                lines.extend(
                    [
                        "",
                        f"{entry['agent']} (Round {entry['round']}):",
                        f"{entry['content']}",
                    ]
                )
            return "\n".join(lines)

        return topic

    async def _invoke_agent(
        self,
        agent: models.Agent | None,
        prompt_template: str,
        content: str,
    ) -> str:
        messages = []

        # Add system message for agent instructions if available
        if agent is not None:
            messages.append(SystemMessage(content=agent.system_prompt))

        # Add the round-specific prompt template as a system message
        messages.append(SystemMessage(content=prompt_template))

        # Add the actual debate content as a human message
        messages.append(HumanMessage(content=content))

        try:
            response = await self.llm.ainvoke(messages)
        except (ValueError, RuntimeError, ConnectionError) as e:
            who = "Moderator" if agent is None else agent.name
            logger.exception("Error generating response for %s", who)
            return f"Error generating response for {who}: {e!s}"
        else:
            return response.content
