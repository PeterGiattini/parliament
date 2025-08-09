"""Declarative debate specification models and helpers.

Defines a schema for a debate and utilities to load a default spec from YAML.
The spec is the single source of truth for round order, types, context
strategies, and prompt templates.
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import TypeAlias

from pydantic import BaseModel
from yaml import safe_load


class RoundType(StrEnum):
    """Enumerated round types for clarity and schema safety."""

    parallel = "parallel"
    sequential = "sequential"
    moderator = "moderator"


class RoundContextStrategy(StrEnum):
    """How to assemble context for a round."""

    topic_only = "topic_only"
    full_transcript = "full_transcript"


class RoundSpec(BaseModel):
    """Specification for a single debate round."""

    title: str
    type: RoundType
    context_strategy: RoundContextStrategy
    prompt_template: str


RoundsByNumber: TypeAlias = dict[int, RoundSpec]


class DebateSpec(BaseModel):
    """Declarative specification for a complete debate."""

    rounds: RoundsByNumber

    def title_for_round(self, round_number: int) -> str | None:
        """Return the display title for a given round number if present."""
        round_cfg = self.rounds.get(round_number)
        return round_cfg.title if round_cfg else None

    def type_for_round(self, round_number: int) -> RoundType | None:
        """Return the type (parallel|sequential|moderator) for a round if present."""
        round_cfg = self.rounds.get(round_number)
        return round_cfg.type if round_cfg else None


def load_debate_spec_from_yaml(file_path: str) -> DebateSpec:
    """Load a DebateSpec from a YAML file containing a rounds dict.

    Expected shape:
    rounds:
      "1":
        title: str
        type: parallel|sequential|moderator
        context_strategy: topic_only|full_transcript
        prompt_template: str
      ...
    """
    path = Path(file_path)
    text = path.read_text(encoding="utf-8")
    raw = safe_load(text) or {}
    raw_rounds = raw.get("rounds", {})
    rounds: RoundsByNumber = {}
    for key, cfg in raw_rounds.items():
        round_number = int(key)
        rounds[round_number] = RoundSpec(
            title=cfg["title"],
            type=RoundType(cfg["type"]),
            context_strategy=RoundContextStrategy(cfg["context_strategy"]),
            prompt_template=cfg["prompt_template"],
        )
    return DebateSpec(rounds=rounds)


def load_default_debate_spec() -> DebateSpec:
    """Load the default DebateSpec from a YAML file in the defaults directory."""
    current_dir = Path(__file__).resolve().parent
    default_path = current_dir / "defaults" / "debate_spec_default.yaml"
    return load_debate_spec_from_yaml(str(default_path))
