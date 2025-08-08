"""LangGraph-based debate orchestrator for managing multi-agent debates."""

import asyncio
import json
import os
import random
from collections.abc import AsyncGenerator
from typing import Any, TypedDict

from langchain_core.messages import HumanMessage
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import END, StateGraph

import models
from debate_constants import DEBATE_PROMPTS, DEBATE_ROUNDS, LLM_CONFIG

# Round constants
ROUND_OPENING = 1
ROUND_REBUTTAL = 2
ROUND_SURREBUTTAL = 3
ROUND_SYNTHESIS = 4
ROUND_COMPLETE = 5


class DebateState(TypedDict):
    """Represent the state for the LangGraph debate workflow."""

    topic: str
    agents: list[models.Agent]
    debate_transcript: list[dict[str, Any]]
    current_round: int
    round_agent_order: list[models.Agent]
    current_agent_index: int
    status_context: dict[str, Any] | None


class LangGraphDebateOrchestrator:
    """Orchestrate debates using a supervisor-based LangGraph.

    Implements the standard four-round structure:
    1. Opening Statements (parallel)
    2. Rebuttal (sequential)
    3. Surrebuttal (sequential)
    4. Synthesis (moderator)
    """

    def __init__(self, agents: list[models.Agent]) -> None:
        """Initialize the debate orchestrator."""
        self.agents = agents
        self.llm = ChatVertexAI(
            model_name=LLM_CONFIG["model_name"],
            temperature=LLM_CONFIG["temperature"],
            max_output_tokens=LLM_CONFIG["max_output_tokens"],
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=LLM_CONFIG["location"],
        )
        self.prompts = DEBATE_PROMPTS
        # For interface compatibility with legacy orchestrator and tests
        self.structure = DEBATE_ROUNDS
        self.graph = self._build_debate_graph()
        self.round_titles = {
            ROUND_OPENING: "Opening Statements",
            ROUND_REBUTTAL: "Rebuttal",
            ROUND_SURREBUTTAL: "Surrebuttal",
            ROUND_SYNTHESIS: "Synthesis",
        }

    def _build_debate_graph(self) -> StateGraph:
        """Build the LangGraph workflow for the debate structure."""
        workflow = StateGraph(DebateState)

        workflow.add_node("route_debate", self._route_debate)
        workflow.add_node(
            "execute_opening_statements",
            self._execute_opening_statements,
        )
        workflow.add_node("setup_sequential_round", self._setup_sequential_round)
        workflow.add_node("execute_sequential_turn", self._execute_sequential_turn)
        workflow.add_node("execute_synthesis", self._execute_synthesis)

        workflow.set_entry_point("route_debate")

        workflow.add_conditional_edges(
            "route_debate",
            lambda state: state["status_context"]["code"],
            {
                "OPENING_STATEMENTS": "execute_opening_statements",
                "SETUP_SEQUENTIAL_ROUND": "setup_sequential_round",
                "SEQUENTIAL_TURN": "execute_sequential_turn",
                "SYNTHESIS": "execute_synthesis",
                "END": END,
            },
        )

        workflow.add_edge("execute_opening_statements", "route_debate")
        workflow.add_edge("setup_sequential_round", "route_debate")
        workflow.add_edge("execute_sequential_turn", "route_debate")
        workflow.add_edge("execute_synthesis", END)

        return workflow.compile()

    async def run_debate(self, topic: str) -> AsyncGenerator[str, None]:
        """Run the debate and yield streaming, structured SSE responses."""
        initial_state = DebateState(
            topic=topic,
            agents=self.agents,
            debate_transcript=[],
            current_round=ROUND_OPENING,
            round_agent_order=[],
            current_agent_index=0,
            status_context=None,
        )

        last_status_context = None
        last_transcript_index = 0

        async for state_update in self.graph.astream(initial_state):
            # Use the latest node's state in this update batch.
            node, state = next(reversed(state_update.items()))
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

        if round_num == ROUND_OPENING:
            return {"status_context": {"code": "OPENING_STATEMENTS"}}

        if round_num in [ROUND_REBUTTAL, ROUND_SURREBUTTAL]:
            # If the round is just starting (no agent order yet), set it up.
            if not state.get("round_agent_order"):
                return {"status_context": {"code": "SETUP_SEQUENTIAL_ROUND"}}
            # Otherwise, execute the next turn.
            return {"status_context": {"code": "SEQUENTIAL_TURN"}}

        if round_num == ROUND_SYNTHESIS:
            return {"status_context": {"code": "SYNTHESIS"}}

        return {"status_context": {"code": "END"}}

    async def _execute_opening_statements(self, state: DebateState) -> dict:
        """Node for the parallel opening statements round."""
        status_context = {
            "code": "ROUND_STARTING",
            "round_number": ROUND_OPENING,
            "round_title": self.round_titles[ROUND_OPENING],
        }
        tasks = [
            self._get_agent_response(agent, state["topic"], "opening_statement")
            for agent in self.agents
        ]
        results = await asyncio.gather(*tasks)

        current_transcript = state.get("debate_transcript", [])
        for agent, response in zip(self.agents, results, strict=True):
            current_transcript.append(
                self._create_transcript_entry(agent, response, ROUND_OPENING)
            )

        return {
            "debate_transcript": current_transcript,
            "current_round": ROUND_REBUTTAL,  # Advance to next round
            "status_context": status_context,
        }

    def _setup_sequential_round(self, state: DebateState) -> dict:
        """Node to set up the agent order for a sequential round."""
        round_num = state["current_round"]
        status_context = {
            "code": "ROUND_STARTING",
            "round_number": round_num,
            "round_title": self.round_titles[round_num],
        }
        return {
            "round_agent_order": self._get_randomized_agents(),
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
            "agent": {"name": agent.name, "icon": agent.icon},
        }

        if round_num == ROUND_REBUTTAL:
            context_entries = [
                e for e in state["debate_transcript"] if e["round"] == ROUND_OPENING
            ]
            response = await self._get_rebuttal(agent, state["topic"], context_entries)
        else:  # SURREBUTTAL
            response = await self._get_surrebuttal(
                agent, state["topic"], state["debate_transcript"]
            )

        current_transcript = state.get("debate_transcript", [])
        current_transcript.append(
            self._create_transcript_entry(agent, response, round_num)
        )

        next_agent_index = agent_index + 1

        # If this was the last agent, transition to the next round.
        if next_agent_index >= len(state["round_agent_order"]):
            return {
                "debate_transcript": current_transcript,
                "current_round": round_num + 1,
                "current_agent_index": 0,
                "round_agent_order": [],  # Clear order for the next round
                "status_context": status_context,
            }

        # Otherwise, just advance the agent index.
        return {
            "debate_transcript": current_transcript,
            "current_agent_index": next_agent_index,
            "status_context": status_context,
        }

    async def _execute_synthesis(self, state: DebateState) -> dict:
        """Node for the final synthesis round."""
        status_context = {
            "code": "ROUND_STARTING",
            "round_number": ROUND_SYNTHESIS,
            "round_title": self.round_titles[ROUND_SYNTHESIS],
        }
        response = await self._get_synthesis(state["topic"], state["debate_transcript"])

        current_transcript = state.get("debate_transcript", [])
        current_transcript.append(
            self._create_transcript_entry("Moderator", response, ROUND_SYNTHESIS)
        )

        return {
            "debate_transcript": current_transcript,
            "current_round": ROUND_COMPLETE,
            "status_context": status_context,
        }

    def _get_randomized_agents(self) -> list[models.Agent]:
        """Get agents in randomized order."""
        agents_copy = self.agents.copy()
        random.shuffle(agents_copy)
        return agents_copy

    async def _get_rebuttal(
        self, agent: models.Agent, topic: str, opening_statements: list[dict]
    ) -> str:
        """Get rebuttal from an agent based on opening statements."""
        agent_statement = next(
            (e["content"] for e in opening_statements if e["agent"] == agent.name),
            "",
        )

        context_lines = [
            f"Original Topic: {topic}",
            "",
            f"Your Opening Statement: {agent_statement}",
            "",
            "Other Panelists' Opening Statements:",
        ]
        for entry in opening_statements:
            if entry["agent"] != agent.name:
                context_lines.extend(
                    [
                        "",
                        f"{entry['agent']}:",
                        f"{entry['content']}",
                    ]
                )
        context = "\n".join(context_lines)
        return await self._get_agent_response(agent, context, "rebuttal")

    async def _get_surrebuttal(
        self, agent: models.Agent, topic: str, transcript: list[dict]
    ) -> str:
        """Get surrebuttal from an agent based on the full transcript so far."""
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
        context = "\n".join(lines)
        return await self._get_agent_response(agent, context, "surrebuttal")

    async def _get_synthesis(self, topic: str, transcript: list[dict]) -> str:
        """Get synthesis from the moderator based on the full transcript."""
        lines = [f"Original Topic: {topic}", "", "Full Debate Transcript:"]
        for entry in transcript:
            lines.extend(
                [
                    "",
                    f"{entry['agent']} (Round {entry['round']}):",
                    f"{entry['content']}",
                ]
            )
        context = "\n".join(lines)
        full_prompt = f"{self.prompts['synthesis']}\n\n{context}"
        messages = [HumanMessage(content=full_prompt)]
        response = await self.llm.ainvoke(messages)
        return response.content

    async def _get_agent_response(
        self, agent: models.Agent, content: str, response_type: str
    ) -> str:
        """Invoke the LLM to get a response from a specific agent."""
        prompt_suffix = self.prompts.get(response_type, "")
        prompt = f"{agent.system_prompt}\n\n{prompt_suffix}\n\n{content}"
        messages = [HumanMessage(content=prompt)]
        try:
            response = await self.llm.ainvoke(messages)
        except (ValueError, RuntimeError, ConnectionError) as e:
            return f"Error generating response for {agent.name}: {e!s}"
        else:
            return response.content

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
