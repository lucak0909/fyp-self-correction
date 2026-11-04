from __future__ import annotations

from ..benchmarks.base import Problem
from ..sandbox.base import ExecutionResult


class NoCorrectionStrategy:
    """Baseline condition: a single generation attempt, never repaired."""

    name = "no_correction"

    def build_feedback_message(
        self, problem: Problem, solution_code: str, execution_result: ExecutionResult
    ) -> str | None:
        return None
