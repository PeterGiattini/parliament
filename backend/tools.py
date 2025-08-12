"""Research tools for ReAct agents.

This module exposes a function to construct research tools used by ReAct
subgraphs. Currently it provides Tavily web search via LangChain's integration.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from langchain_tavily import TavilySearch

if TYPE_CHECKING:
    from langchain_core.tools import BaseTool


def get_research_tools() -> list[BaseTool]:
    """Return a list of research tools available to ReAct agents.

    Configuration is provided via environment variables:
      - TAVILY_API_KEY: API key for Tavily (required to enable the tool)
      - TAVILY_MAX_RESULTS: optional, default 5
      - TAVILY_TOPIC: optional, default "general"
    """
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        # No key present: return an empty toolset so the system still runs.
        return []

    max_results_str = os.getenv("TAVILY_MAX_RESULTS", "5")
    topic = os.getenv("TAVILY_TOPIC", "general")

    try:
        max_results = int(max_results_str)
    except ValueError:
        max_results = 5

    tavily_search_tool = TavilySearch(
        max_results=max_results,
        topic=topic,
    )

    return [tavily_search_tool]
