"""Benchmark problem schema and loader protocol.

Every benchmark (HumanEval, MBPP, LiveCodeBench, ...) is adapted to this
common shape so the rest of the platform (agent, sandbox, harness) never
needs to know which benchmark a problem came from.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class Problem:
    """A single coding problem in the benchmark-agnostic format."""

    problem_id: str
    source: str  # e.g. "humaneval", "mbpp", "livecodebench"
    prompt: str  # natural-language task description / function signature + docstring
    entry_point: str  # name of the function the solution must define
    test_code: str  # executable test code; must raise/assert on failure
    starter_code: str = ""  # optional boilerplate to prepend to the model's completion
    metadata: dict = field(default_factory=dict)


class BenchmarkLoader(Protocol):
    """Anything that can yield a list of Problems implements this."""

    def load(self, limit: int | None = None) -> list[Problem]:
        ...
