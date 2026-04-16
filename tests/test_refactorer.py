"""Tests for parsing LLM JSON output (no API)."""

from __future__ import annotations

from core.refactorer import parse_refactor_response


def test_parse_refactor_response_plain_json() -> None:
    raw = """
    {
      "chain_of_thought": "Analyzed smells; refactored.",
      "issues_summary": "- Long function",
      "explanation": "Split responsibilities.",
      "refactored_code": "def f():\\n    pass\\n",
      "detected_language": "python"
    }
    """
    r = parse_refactor_response(raw)
    assert r.detected_language == "python"
    assert "def f():" in r.refactored_code
    assert "Long function" in r.issues_summary


def test_parse_refactor_response_strips_markdown_fence() -> None:
    raw = """```json
{"chain_of_thought": "c", "issues_summary": "i", "explanation": "e", "refactored_code": "x", "detected_language": "python"}
```"""
    r = parse_refactor_response(raw)
    assert r.refactored_code == "x"
