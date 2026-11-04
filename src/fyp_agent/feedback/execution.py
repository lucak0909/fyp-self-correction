from __future__ import annotations

from ..benchmarks.base import Problem
from ..sandbox.base import ExecutionResult


class ExecutionFeedbackStrategy:
    """Full external signal: pass/fail plus the actual error message or
    failing test output (Chen et al. 2024's "self-debug" condition).
    """

    name = "execution"

    def build_feedback_message(
        self, problem: Problem, solution_code: str, execution_result: ExecutionResult
    ) -> str | None:
        if execution_result.passed:
            return (
                "Your solution PASSED the hidden tests. You may resubmit it "
                "unchanged or improve it. Respond with only the code."
            )
        return (
            "Your solution FAILED the hidden tests. Here is the output:\n\n"
            f"```\n{execution_result.error_message}\n```\n\n"
            "Fix the bug(s) and provide a corrected, complete solution. "
            "Respond with only the code."
        )
