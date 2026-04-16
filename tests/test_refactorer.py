"""Tests for parsing LLM JSON output (no API)."""

from __future__ import annotations

import base64

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


def test_parse_refactor_response_delimiter_format() -> None:
    raw = r'''{"chain_of_thought": "c", "issues_summary": "i", "explanation": "e", "detected_language": "python"}
---BEGIN_REFACTORED_CODE---
def x():
    """triple"""
    pass
---END_REFACTORED_CODE---
'''
    r = parse_refactor_response(raw)
    assert r.detected_language == "python"
    assert '"""triple"""' in r.refactored_code
    assert "def x():" in r.refactored_code


def test_parse_refactor_response_base64_refactored_code() -> None:
    code = 'def f():\n    """Doc."""\n    pass\n'
    b64 = base64.b64encode(code.encode("utf-8")).decode("ascii")
    raw = f"""
    {{
      "chain_of_thought": "c",
      "issues_summary": "i",
      "explanation": "e",
      "refactored_code": "{b64}",
      "detected_language": "python"
    }}
    """
    r = parse_refactor_response(raw)
    assert '"""Doc."""' in r.refactored_code
    assert r.refactored_code == code
