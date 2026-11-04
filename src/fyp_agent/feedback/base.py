"""The experimental variable: what signal (if any) the agent gets before
repairing a solution. Key Aim 1 in the proposal -- swap one of these in
without touching the agent loop, sandbox or evaluation harness.

Every strategy is handed the ground-truth ExecutionResult so the harness can
log full trajectories uniformly, but a strategy is only allowed to leak into
the model prompt what its condition actually represents: e.g.
SelfReflectionStrategy must not look at execution_result at all.
"""

from __future__ import annotations

from typing import Protocol

from ..benchmarks.base import Problem
from ..sandbox.base import ExecutionResult


class FeedbackStrategy(Protocol):
    name: str

    def build_feedback_message(
        self,
        problem: Problem,
        solution_code: str,
        execution_result: ExecutionResult,
    ) -> str | None:
        """Return the message to send back to the model asking it to repair
        its solution, or None to signal that no further repair should be
        attempted (ends the agent's iteration loop early)."""
        ...
