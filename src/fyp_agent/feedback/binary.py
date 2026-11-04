from __future__ import annotations

from ..benchmarks.base import Problem
from ..sandbox.base import ExecutionResult


class BinaryFeedbackStrategy:
    """External but minimal signal: the model is told only whether its
    solution passed or failed the hidden tests -- no error text, no failing
    case. Isolates the value of knowing "wrong" from knowing "why wrong".
    """

    name = "binary"

    def build_feedback_message(
        self, problem: Problem, solution_code: str, execution_result: ExecutionResult
    ) -> str | None:
        if execution_result.passed:
            verdict = "Your solution PASSED the hidden tests."
        else:
            verdict = "Your solution FAILED the hidden tests."
        return (
            f"{verdict} No further details are available. If it failed, "
            "revise your solution. If it passed, you may resubmit it "
            "unchanged or improve it. Respond with only the code."
        )
