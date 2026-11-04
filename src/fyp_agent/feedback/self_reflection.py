from __future__ import annotations

from ..benchmarks.base import Problem
from ..sandbox.base import ExecutionResult


class SelfReflectionStrategy:
    """Intrinsic self-correction: the model is asked to review and possibly
    revise its own solution with NO external signal about correctness
    (Madaan et al. 2023 / Huang et al. 2024's "no external feedback" setting).

    Deliberately never reads `execution_result` -- that is the point of this
    condition.
    """

    name = "self_reflection"

    def build_feedback_message(
        self, problem: Problem, solution_code: str, execution_result: ExecutionResult
    ) -> str | None:
        return (
            "Review your solution carefully for correctness, edge cases, and "
            "bugs. If you find a problem, provide a corrected, complete "
            "solution. If you believe it is already correct, you may "
            "resubmit it unchanged. Respond with only the code."
        )
