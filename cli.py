#!/usr/bin/env python3
"""
Clean Code Bot — CLI entry point.

Automated refactorer: sends sanitized source to an LLM and writes structured results.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from core.analyzer import analyze_and_prepare
from core.refactorer import parse_refactor_response
from core.sanitizer import sanitize_source
from llm.client import create_llm_client
from llm.prompts import SYSTEM_PROMPT, build_user_prompt
from utils.file_handler import read_text_file, write_text_file


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Write refactored code to this file (optional).",
)
@click.option(
    "--explain",
    is_flag=True,
    help="Include detailed chain-of-thought reasoning in the printed report.",
)
@click.option(
    "--provider",
    type=click.Choice(["openai", "groq"], case_sensitive=False),
    default=None,
    help="LLM provider (default: env LLM_PROVIDER or openai).",
)
@click.option(
    "--model",
    default=None,
    help="Model name (default: env LLM_MODEL or provider default).",
)
@click.option(
    "--max-bytes",
    type=int,
    default=200_000,
    help="Maximum input size in bytes after UTF-8 encoding (default: 200000).",
)
def main(
    input_file: Path,
    output: Path | None,
    explain: bool,
    provider: str | None,
    model: str | None,
    max_bytes: int,
) -> None:
    """
    Refactor INPUT_FILE using an LLM and print explanation and issue summary.

    Requires OPENAI_API_KEY or GROQ_API_KEY depending on provider.
    """
    try:
        raw = read_text_file(input_file)
    except OSError as e:
        raise click.ClickException(f"Cannot read input: {e}") from e

    san = sanitize_source(raw, max_bytes=max_bytes)
    if san.truncated:
        click.echo(
            click.style("Warning: input was truncated to max-bytes limit.", fg="yellow"),
            err=True,
        )
    if san.redactions:
        click.echo(
            click.style(
                f"Warning: sanitized {san.redactions} suspicious pattern(s) in input.",
                fg="yellow",
            ),
            err=True,
        )

    prepared = analyze_and_prepare(input_file, san.text)
    user_prompt = build_user_prompt(
        prepared.sanitized_source,
        include_full_cot_in_output=explain,
    )

    # Append language hint as neutral metadata (still data, not instructions).
    user_prompt = (
        f"{user_prompt}\n\n[Metadata only] Filename suffix suggests language hint: "
        f"{prepared.language_hint!r}."
    )

    try:
        client, cfg = create_llm_client(provider=provider, model=model)
    except ValueError as e:
        raise click.ClickException(str(e)) from e

    try:
        raw_response = client.complete(SYSTEM_PROMPT, user_prompt, cfg)
    except Exception as e:
        raise click.ClickException(f"LLM request failed: {e}") from e

    try:
        result = parse_refactor_response(raw_response)
    except (ValueError, json.JSONDecodeError) as e:
        click.echo(raw_response, file=sys.stderr)
        raise click.ClickException(f"Failed to parse model output as JSON: {e}") from e

    if output:
        try:
            write_text_file(output, result.refactored_code)
        except OSError as e:
            raise click.ClickException(f"Cannot write output: {e}") from e
        click.echo(click.style(f"Wrote refactored code to {output}", fg="green"))

    click.echo("=" * 72)
    click.echo(click.style("ISSUES SUMMARY", bold=True))
    click.echo(result.issues_summary)
    click.echo()
    click.echo("=" * 72)
    click.echo(click.style("EXPLANATION OF IMPROVEMENTS", bold=True))
    click.echo(result.explanation)
    if explain:
        click.echo()
        click.echo("=" * 72)
        click.echo(click.style("CHAIN OF THOUGHT (DETAIL)", bold=True))
        click.echo(result.chain_of_thought)
    click.echo()
    click.echo(f"Detected language (model): {result.detected_language}")

    if not output:
        click.echo()
        click.echo("=" * 72)
        click.echo(click.style("REFACTORED CODE", bold=True))
        click.echo(result.refactored_code)


if __name__ == "__main__":
    main()
