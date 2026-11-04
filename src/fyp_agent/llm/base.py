"""LLM client interface. The agent and feedback strategies talk to this,
never to a specific provider's SDK, so a second provider can be added later
without touching agent/feedback code (per the proposal's pluggable design).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int
    latency_s: float
    model: str

    def estimated_cost_usd(self, price_per_mtok_in: float, price_per_mtok_out: float) -> float:
        return (self.input_tokens / 1_000_000) * price_per_mtok_in + (
            self.output_tokens / 1_000_000
        ) * price_per_mtok_out


class LLMClient(Protocol):
    model: str

    def generate(self, system: str, user_message: str, max_tokens: int = 2048) -> LLMResponse:
        ...
