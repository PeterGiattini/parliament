"""Debate orchestrator module for managing multi-agent debates."""

import asyncio
import json
import os
import random
from collections.abc import AsyncGenerator
from typing import Any

from langchain_core.messages import HumanMessage
from langchain_google_vertexai import ChatVertexAI

from debate_constants import DEBATE_PROMPTS, DEBATE_ROUNDS, LLM_CONFIG

# Round constants
ROUND_REBUTTAL = 2
ROUND_SURREBUTTAL = 3


class DebateOrchestrator:
    """Orchestrates the 4-round debate structure.

    1. Opening Statements (parallel)
    2. Rebuttal (sequential, randomized order)
    3. Surrebuttal (sequential, randomized order)
    4. Synthesis (moderator)
    """

    def __init__(self, agents: list[dict[str, Any]]) -> None:
        """Initialize the debate orchestrator.

        Args:
            agents: List of agent configurations.

        """
        self.agents = agents
        self.llm = ChatVertexAI(
            model_name=LLM_CONFIG["model_name"],
            temperature=LLM_CONFIG["temperature"],
            max_output_tokens=LLM_CONFIG["max_output_tokens"],
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=LLM_CONFIG["location"],
        )

        # Load debate prompts and structure from constants
        self.prompts = DEBATE_PROMPTS
        self.structure = DEBATE_ROUNDS

    async def run_debate(self, topic: str) -> AsyncGenerator[str, None]:
        """Run the complete 4-round debate and yield streaming responses."""
        debate_transcript = []
        round_results = {}  # Store results for dependencies

        # Execute each round based on structure
        for round_num in sorted(self.structure.keys()):
            round_config = self.structure[round_num]
            round_type = round_config["type"]

            data = {
                "type": "round_start",
                "round": round_num,
                "title": round_config["title"],
            }
            yield f"data: {json.dumps(data)}\n\n"

            if round_type == "parallel":
                results = await self._execute_parallel_round(
                    round_num,
                    topic,
                    round_results,
                )
                round_results[round_num] = results
                for agent, response in results:
                    debate_transcript.append(
                        self._create_transcript_entry(agent, response, round_num),
                    )
                    yield self._create_response_event(agent, response, round_num)
                    await asyncio.sleep(0.5)

            elif round_type == "sequential":
                results = await self._execute_sequential_round(
                    round_num,
                    topic,
                    round_results,
                )
                round_results[round_num] = results
                for agent, response in results:
                    debate_transcript.append(
                        self._create_transcript_entry(agent, response, round_num),
                    )
                    yield self._create_response_event(agent, response, round_num)
                    await asyncio.sleep(0.5)

            elif round_type == "moderator":
                response = await self._execute_moderator_round(
                    round_num,
                    topic,
                    debate_transcript,
                )
                data = {"type": "synthesis", "content": response}
                yield f"data: {json.dumps(data)}\n\n"

        yield f"data: {json.dumps({'type': 'debate_complete'})}\n\n"

    async def _get_opening_statements(self, topic: str) -> list[tuple]:
        """Get opening statements from all agents in parallel.

        Returns:
            List of (agent, statement) tuples.

        """
        tasks = []
        for agent in self.agents:
            task = self._get_agent_response(agent, topic, "opening_statement")
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        return [
            (agent, result) for agent, result in zip(self.agents, results, strict=False)
        ]

    async def _get_rebuttal(
        self,
        agent: dict[str, Any],
        topic: str,
        opening_statements: list[tuple],
    ) -> str:
        """Get rebuttal from a specific agent based on opening statements."""
        # Find this agent's original opening statement
        agent_statement = None
        for other_agent, statement in opening_statements:
            if other_agent["name"] == agent["name"]:
                agent_statement = statement
                break

        # Build context with all opening statements
        context = f"Original Topic: {topic}\n\n"
        context += f"Your Opening Statement: {agent_statement}\n\n"
        context += "Other Panelists' Opening Statements:\n"
        for other_agent, statement in opening_statements:
            if other_agent["name"] != agent["name"]:
                context += f"\n{other_agent['name']}:\n{statement}\n"

        return await self._get_agent_response(agent, context, "rebuttal")

    async def _get_synthesis(self, topic: str, debate_transcript: list[dict]) -> str:
        """Get synthesis from moderator based on full debate transcript."""
        # Build full transcript
        context = f"Original Topic: {topic}\n\n"
        context += "Full Debate Transcript:\n"
        for entry in debate_transcript:
            context += (
                f"\n{entry['agent']} (Round {entry['round']}):\n{entry['content']}\n"
            )

        # Combine system prompt with context
        full_prompt = f"{self.prompts['synthesis']}\n\n{context}"

        messages = [HumanMessage(content=full_prompt)]

        response = await self.llm.ainvoke(messages)
        return response.content

    def _get_randomized_agents(self) -> list[dict[str, Any]]:
        """Get agents in randomized order for sequential rounds."""
        agents_copy = self.agents.copy()
        random.shuffle(agents_copy)
        return agents_copy

    async def _get_surrebuttal(
        self,
        agent: dict[str, Any],
        topic: str,
        opening_statements: list[tuple],
        rebuttal_statements: list[tuple],
    ) -> str:
        """Get surrebuttal from a specific agent."""
        # Find this agent's original opening statement
        agent_statement = None
        for other_agent, statement in opening_statements:
            if other_agent["name"] == agent["name"]:
                agent_statement = statement
                break

        # Build context with all opening and rebuttal statements
        context = f"Original Topic: {topic}\n\n"
        context += f"Your Opening Statement: {agent_statement}\n\n"
        context += "All Panelists' Opening Statements:\n"
        for other_agent, statement in opening_statements:
            context += f"\n{other_agent['name']}:\n{statement}\n"

        context += "\nAll Panelists' Rebuttal Statements:\n"
        for other_agent, statement in rebuttal_statements:
            context += f"\n{other_agent['name']}:\n{statement}\n"

        return await self._get_agent_response(agent, context, "surrebuttal")

    async def _execute_parallel_round(
        self,
        round_num: int,
        topic: str,
        round_results: dict,  # noqa: ARG002
    ) -> list[tuple]:
        """Execute a parallel round where all agents respond simultaneously."""
        if round_num == 1:  # Opening statements
            return await self._get_opening_statements(topic)
        # For future parallel round types, use round_results for context
        return []

    async def _execute_sequential_round(
        self,
        round_num: int,
        topic: str,
        round_results: dict,
    ) -> list[tuple]:
        """Execute a sequential round with randomized agent order."""
        agents = self._get_randomized_agents()
        results = []

        if round_num == ROUND_REBUTTAL:  # Rebuttal
            for agent in agents:
                response = await self._get_rebuttal(agent, topic, round_results[1])
                results.append((agent, response))
        elif round_num == ROUND_SURREBUTTAL:  # Surrebuttal
            for agent in agents:
                response = await self._get_surrebuttal(
                    agent,
                    topic,
                    round_results[1],
                    round_results[2],
                )
                results.append((agent, response))
        # For future sequential round types, use round_results for context

        return results

    async def _execute_moderator_round(
        self,
        round_num: int,  # noqa: ARG002
        topic: str,
        debate_transcript: list[dict],
    ) -> str:
        """Execute a moderator round (synthesis)."""
        # round_num could be used for different moderator round types in the future
        return await self._get_synthesis(topic, debate_transcript)

    def _create_transcript_entry(
        self,
        agent: dict[str, Any],
        response: str,
        round_num: int,
    ) -> dict[str, Any]:
        """Create a standardized transcript entry."""
        return {
            "agent": agent["name"],
            "role": agent["role"],
            "round": round_num,
            "content": response,
            "color": agent["color"],
            "icon": agent["icon"],
        }

    def _create_response_event(
        self,
        agent: dict[str, Any],
        response: str,
        round_num: int,
    ) -> str:
        """Create a standardized response event."""
        data = {
            "type": "agent_response",
            "agent": agent["name"],
            "role": agent["role"],
            "content": response,
            "round": round_num,
            "color": agent["color"],
            "icon": agent["icon"],
        }
        return f"data: {json.dumps(data)}\n\n"

    async def _get_agent_response(
        self,
        agent: dict[str, Any],
        content: str,
        response_type: str,
    ) -> str:
        """Get response from a specific agent."""
        if (prompt_suffix := self.prompts.get(response_type)) is not None:
            prompt = f"{agent['system_prompt']}\n\n{prompt_suffix}\n\n{content}"
        else:
            prompt = content

        messages = [HumanMessage(content=prompt)]

        try:
            response = await self.llm.ainvoke(messages)
        except (ValueError, RuntimeError, ConnectionError) as e:
            # Log the error and return a fallback response
            return f"Error generating response for {agent['name']}: {e!s}"
        else:
            return response.content
