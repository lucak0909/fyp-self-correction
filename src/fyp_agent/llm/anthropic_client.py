"""Anthropic Claude backend for the LLMClient interface."""

from __future__ import annotations

import os
import time

from .base import LLMResponse


class AnthropicClient:
    def __init__(self, model: str = "claude-sonnet-5", api_key: str | None = None) -> None:
        import anthropic

        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not set. Copy .env.example to .env and fill it in, "
                "or export the variable in your shell."
            )
        self.model = model
        self._client = anthropic.Anthropic(api_key=key)

    def generate(self, system: str, user_message: str, max_tokens: int = 2048) -> LLMResponse:
        start = time.monotonic()
        response = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user_message}],
        )
        latency_s = time.monotonic() - start

        text = "".join(block.text for block in response.content if block.type == "text")
        return LLMResponse(
            text=text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            latency_s=latency_s,
            model=self.model,
        )
