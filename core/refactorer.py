"""
Parse and validate LLM responses into structured refactor results.
"""

from __future__ import annotations

import base64
import binascii
import re
from dataclasses import dataclass
from typing import Any

from llm.prompts import (
    BEGIN_REFACTORED_CODE,
    END_REFACTORED_CODE,
    extract_first_json_object,
    parse_model_json,
)

_BASE64ISH: re.Pattern[str] = re.compile(r"^[A-Za-z0-9+/=\s]+$")
_MIN_B64_LEN: int = 16

_META_KEYS: frozenset[str] = frozenset(
    {"chain_of_thought", "issues_summary", "explanation", "detected_language"}
)
_LEGACY_KEYS: frozenset[str] = _META_KEYS | {"refactored_code"}


def _decode_refactored_code(raw: str) -> str:
    """
    Decode ``refactored_code`` from legacy JSON-only responses.

    Supports Base64 (UTF-8) or plain escaped source strings.
    """
    s = raw.strip()
    if not s:
        return ""
    compact = "".join(s.split())
    if len(compact) >= _MIN_B64_LEN and _BASE64ISH.fullmatch(compact):
        try:
            decoded = base64.b64decode(compact, validate=True)
            return decoded.decode("utf-8")
        except (ValueError, binascii.Error, UnicodeDecodeError):
            pass
    return raw


def _validate_keys(data: dict[str, Any], required: frozenset[str]) -> None:
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"Missing JSON keys: {missing}")


def _parse_delimited_format(raw_text: str) -> RefactorResult | None:
    """If markers are present, parse JSON head + raw code block."""
    if BEGIN_REFACTORED_CODE not in raw_text:
        return None
    head, rest = raw_text.split(BEGIN_REFACTORED_CODE, 1)
    if END_REFACTORED_CODE in rest:
        code, _trailing = rest.split(END_REFACTORED_CODE, 1)
    else:
        code = rest
    data = extract_first_json_object(head)
    _validate_keys(data, _META_KEYS)
    return RefactorResult(
        refactored_code=code.strip("\n"),
        explanation=str(data["explanation"]),
        issues_summary=str(data["issues_summary"]),
        chain_of_thought=str(data["chain_of_thought"]),
        detected_language=str(data["detected_language"]),
    )


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
    Parse the model response into a :class:`RefactorResult`.

    Preferred format: small JSON (metadata only) plus ``---BEGIN_REFACTORED_CODE---``
    / ``---END_REFACTORED_CODE---`` around the full file (avoids huge Base64 inside JSON).

    Legacy format: a single JSON object including ``refactored_code`` (plain or Base64).

    Args:
        raw_text: Raw assistant message.

    Returns:
        Populated RefactorResult.

    Raises:
        ValueError: If required keys are missing or parsing fails.
    """
    delimited = _parse_delimited_format(raw_text)
    if delimited is not None:
        return delimited

    data: dict[str, Any] = parse_model_json(raw_text)
    _validate_keys(data, _LEGACY_KEYS)

    return RefactorResult(
        refactored_code=_decode_refactored_code(str(data["refactored_code"])),
        explanation=str(data["explanation"]),
        issues_summary=str(data["issues_summary"]),
        chain_of_thought=str(data["chain_of_thought"]),
        detected_language=str(data["detected_language"]),
    )
