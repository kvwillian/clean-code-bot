"""
Modular LLM client supporting OpenAI and Groq APIs.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Final

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class LLMConfig:
    """Configuration for a single completion request."""

    model: str
    temperature: float = 0.2
    # Refactored output can be long; Groq/OpenAI caps vary by model.
    max_tokens: int = 16384


class LLMClient(ABC):
    """Abstract LLM client."""

    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str, config: LLMConfig) -> str:
        """Return the assistant message content as a string."""


class OpenAIClient(LLMClient):
    """OpenAI Chat Completions API."""

    def __init__(self, api_key: str | None = None) -> None:
        from openai import OpenAI

        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY is not set.")
        self._client = OpenAI(api_key=key)

    def complete(self, system_prompt: str, user_prompt: str, config: LLMConfig) -> str:
        response = self._client.chat.completions.create(
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        choice = response.choices[0]
        content = choice.message.content
        if content is None:
            raise RuntimeError("OpenAI returned empty content.")
        return content


class GroqClient(LLMClient):
    """Groq Chat Completions API (OpenAI-compatible)."""

    def __init__(self, api_key: str | None = None) -> None:
        from groq import Groq

        key = api_key or os.environ.get("GROQ_API_KEY")
        if not key:
            raise ValueError("GROQ_API_KEY is not set.")
        self._client = Groq(api_key=key)

    def complete(self, system_prompt: str, user_prompt: str, config: LLMConfig) -> str:
        response = self._client.chat.completions.create(
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        choice = response.choices[0]
        content = choice.message.content
        if content is None:
            raise RuntimeError("Groq returned empty content.")
        return content


DEFAULT_OPENAI_MODEL: Final[str] = "gpt-4o-mini"
DEFAULT_GROQ_MODEL: Final[str] = "llama-3.3-70b-versatile"


def create_llm_client(
    provider: str | None = None,
    *,
    model: str | None = None,
) -> tuple[LLMClient, LLMConfig]:
    """
    Factory: create client and default config from environment.

    Args:
        provider: ``"openai"`` or ``"groq"``. Defaults to ``LLM_PROVIDER`` env or ``"openai"``.
        model: Override model name; otherwise uses provider default or ``LLM_MODEL`` env.

    Returns:
        Tuple of (client, config with model resolved).
    """
    p = (provider or os.environ.get("LLM_PROVIDER", "openai")).strip().lower()
    env_model = os.environ.get("LLM_MODEL")

    max_tok = int(os.environ.get("LLM_MAX_TOKENS", "16384"))

    if p == "openai":
        resolved_model = model or env_model or DEFAULT_OPENAI_MODEL
        return OpenAIClient(), LLMConfig(model=resolved_model, max_tokens=max_tok)
    if p == "groq":
        resolved_model = model or env_model or DEFAULT_GROQ_MODEL
        return GroqClient(), LLMConfig(model=resolved_model, max_tokens=max_tok)
    raise ValueError(f"Unsupported LLM provider: {provider!r}. Use 'openai' or 'groq'.")
