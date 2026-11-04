"""Core agent loop (Key Aim 1): generate an initial solution, then repair it
for up to `max_repair_rounds` using whichever FeedbackStrategy is plugged
in. The strategy is the only thing that changes between experimental
conditions -- this loop is shared by all of them.
"""

from __future__ import annotations

from ..benchmarks.base import Problem
from ..feedback.base import FeedbackStrategy
from ..llm.base import LLMClient
from ..sandbox.base import Sandbox
from .codeblocks import extract_code
from .trajectory import Attempt, Trajectory

_SYSTEM_PROMPT = (
    "You are an expert Python programmer. You will be given a function "
    "signature and docstring. Implement the function correctly and "
    "efficiently. Respond with only a single Python code block containing "
    "the complete function definition -- no explanation."
)


class CodingAgent:
    def __init__(
        self,
        llm: LLMClient,
        sandbox: Sandbox,
        feedback_strategy: FeedbackStrategy,
        max_repair_rounds: int = 2,
        timeout_s: float = 10.0,
        max_tokens: int = 2048,
    ) -> None:
        self.llm = llm
        self.sandbox = sandbox
        self.feedback_strategy = feedback_strategy
        self.max_repair_rounds = max_repair_rounds
        self.timeout_s = timeout_s
        self.max_tokens = max_tokens

    def solve(self, problem: Problem) -> Trajectory:
        trajectory = Trajectory(
            problem_id=problem.problem_id,
            condition=self.feedback_strategy.name,
            model=self.llm.model,
        )

        user_message = (
            f"{problem.prompt}\n\n"
            "Implement this function. Respond with only the code."
        )

        for round_index in range(self.max_repair_rounds + 1):
            response = self.llm.generate(_SYSTEM_PROMPT, user_message, self.max_tokens)
            solution_code = extract_code(response.text)
            execution_result = self.sandbox.run(
                solution_code, problem.test_code, self.timeout_s
            )

            trajectory.attempts.append(
                Attempt(
                    round_index=round_index,
                    solution_code=solution_code,
                    execution_result=execution_result,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    latency_s=response.latency_s,
                )
            )

            if round_index == self.max_repair_rounds:
                break

            feedback_message = self.feedback_strategy.build_feedback_message(
                problem, solution_code, execution_result
            )
            if feedback_message is None:
                break

            user_message = (
                f"{problem.prompt}\n\n"
                f"Your previous attempt:\n```python\n{solution_code}\n```\n\n"
                f"{feedback_message}"
            )

        return trajectory
