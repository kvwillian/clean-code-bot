"""
Safe file read/write helpers for the CLI.
"""

from __future__ import annotations

from pathlib import Path


def read_text_file(path: Path) -> str:
    """
    Read a UTF-8 text file.

    Args:
        path: File path.

    Returns:
        File contents as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
        OSError: On read errors.
    """
    return path.read_text(encoding="utf-8")


def write_text_file(path: Path, content: str) -> None:
    """
    Write UTF-8 text, creating parent directories if needed.

    Args:
        path: Destination path.
        content: Text to write.

    Raises:
        OSError: On write errors.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
