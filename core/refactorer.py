"""
Parse and validate LLM responses into structured refactor results.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from llm.prompts import parse_model_json


@dataclass(frozen=True)
class RefactorResult:
    """Structured output from the model."""

    refactored_code: str
    explanation: str
    issues_summary: str
    chain_of_thought: str
    detected_language: str


def parse_refactor_response(raw_text: str) -> RefactorResult:
    """
    Parse the model JSON payload into a RefactorResult.

    Args:
        raw_text: Raw assistant message (should be JSON).

    Returns:
        Populated RefactorResult.

    Raises:
        ValueError: If required keys are missing or JSON is invalid.
    """
    data: dict[str, Any] = parse_model_json(raw_text)
    required = (
        "refactored_code",
        "explanation",
        "issues_summary",
        "chain_of_thought",
        "detected_language",
    )
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"Missing JSON keys: {missing}")

    return RefactorResult(
        refactored_code=str(data["refactored_code"]),
        explanation=str(data["explanation"]),
        issues_summary=str(data["issues_summary"]),
        chain_of_thought=str(data["chain_of_thought"]),
        detected_language=str(data["detected_language"]),
    )
