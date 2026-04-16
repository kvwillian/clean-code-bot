"""
Prepare sanitized source for the LLM (metadata + wrapped context).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PreparedInput:
    """Bundle passed to the prompt builder."""

    original_path: Path
    sanitized_source: str
    language_hint: str


def _guess_language(path: Path) -> str:
    """Infer a coarse language label from the file suffix."""
    suffix = path.suffix.lower()
    mapping = {
        ".py": "python",
        ".js": "javascript",
        ".mjs": "javascript",
        ".cjs": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".jsx": "javascript",
        ".rs": "rust",
        ".go": "go",
        ".java": "java",
        ".kt": "kotlin",
        ".cs": "csharp",
    }
    return mapping.get(suffix, "unknown")


def analyze_and_prepare(file_path: Path, sanitized_source: str) -> PreparedInput:
    """
    Build structured input for refactoring from a file path and sanitized text.

    Args:
        file_path: Path to the original file (for language hint only).
        sanitized_source: Already sanitized source code.

    Returns:
        PreparedInput for prompt construction.
    """
    return PreparedInput(
        original_path=file_path,
        sanitized_source=sanitized_source,
        language_hint=_guess_language(file_path),
    )
