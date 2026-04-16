"""
Input validation and prompt-injection mitigation.

User content is treated strictly as data: suspicious instruction-like phrases
are removed or neutralized, and size is capped.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

# Phrases that commonly appear in prompt-injection attempts (case-insensitive).
_INJECTION_PATTERNS: Final[tuple[tuple[re.Pattern[str], str], ...]] = (
    (
        re.compile(
            r"\bignore\s+(all\s+)?(previous|prior|above)\s+(instructions?|prompts?|rules?)\b",
            re.IGNORECASE,
        ),
        "[redacted: instruction override attempt]",
    ),
    (
        re.compile(
            r"\bdisregard\s+(the\s+)?(above|previous|prior)\b",
            re.IGNORECASE,
        ),
        "[redacted: instruction override attempt]",
    ),
    (
        re.compile(
            r"\b(system|developer)\s*:\s*",
            re.IGNORECASE,
        ),
        "[redacted: fake role marker]",
    ),
    (
        re.compile(
            r"\b(system\s+override|override\s+system|jailbreak)\b",
            re.IGNORECASE,
        ),
        "[redacted: system override phrase]",
    ),
    (
        re.compile(
            r"\bexecute\s+(this\s+)?(command|shell|bash|powershell)\b",
            re.IGNORECASE,
        ),
        "[redacted: execution phrase]",
    ),
    (
        re.compile(
            r"\b(run|sudo)\s+`[^`]+`",
            re.IGNORECASE,
        ),
        "[redacted: command snippet]",
    ),
    (
        re.compile(
            r"<\s*/?\s*(system|assistant|instruction)\s*>",
            re.IGNORECASE,
        ),
        "[redacted: pseudo tag]",
    ),
)

# Dangerous patterns that might appear in code comments trying to hijack the model.
_META_INSTRUCTION_HINTS: Final[tuple[tuple[re.Pattern[str], str], ...]] = (
    (
        re.compile(
            r"\byou\s+are\s+now\s+(a|the)\b[^.\n]{0,80}",
            re.IGNORECASE,
        ),
        "[redacted: meta-instruction]",
    ),
    (
        re.compile(
            r"\bforget\s+(everything|all)\s+(you|your)\b[^.\n]{0,80}",
            re.IGNORECASE,
        ),
        "[redacted: meta-instruction]",
    ),
)

_DEFAULT_MAX_BYTES: Final[int] = 200_000


@dataclass(frozen=True)
class SanitizationResult:
    """Outcome of sanitizing user-supplied source text."""

    text: str
    truncated: bool
    redactions: int


def sanitize_source(
    raw: str,
    *,
    max_bytes: int = _DEFAULT_MAX_BYTES,
) -> SanitizationResult:
    """
    Limit size and strip/neutralize known injection shapes.

    Args:
        raw: Raw file contents.
        max_bytes: Maximum encoded size in UTF-8.

    Returns:
        SanitizationResult with cleaned text and metadata.
    """
    truncated = False
    b = raw.encode("utf-8", errors="replace")
    if len(b) > max_bytes:
        b = b[:max_bytes]
        truncated = True
        text = b.decode("utf-8", errors="replace")
    else:
        text = raw

    redactions = 0
    for pattern, repl in _INJECTION_PATTERNS + _META_INSTRUCTION_HINTS:
        new_text, n = pattern.subn(repl, text)
        if n:
            redactions += n
            text = new_text

    # Normalize excessive repeated newlines that sometimes wrap payloads.
    text = re.sub(r"\n{20,}", "\n" * 10, text)

    return SanitizationResult(text=text, truncated=truncated, redactions=redactions)
