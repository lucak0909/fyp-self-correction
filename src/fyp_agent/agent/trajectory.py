"""Record of a single run of the agent against a single problem: every
attempt it made, in order. This is what the evaluation harness persists --
it's the unit of analysis for "did correction help, hurt, or do nothing,
and at what cost".
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..sandbox.base import ExecutionResult


@dataclass
class Attempt:
    round_index: int  # 0 = initial generation, 1+ = repair rounds
    solution_code: str
    execution_result: ExecutionResult
    input_tokens: int
    output_tokens: int
    latency_s: float


@dataclass
class Trajectory:
    problem_id: str
    condition: str  # feedback strategy name
    model: str
    attempts: list[Attempt] = field(default_factory=list)

    @property
    def final_passed(self) -> bool:
        return bool(self.attempts) and self.attempts[-1].execution_result.passed

    @property
    def first_passed(self) -> bool:
        return bool(self.attempts) and self.attempts[0].execution_result.passed

    @property
    def broke_a_correct_solution(self) -> bool:
        """True if any attempt passed but a later attempt in the same
        trajectory failed -- the degradation case Key Aim 5 asks about."""
        seen_pass = False
        for attempt in self.attempts:
            if seen_pass and not attempt.execution_result.passed:
                return True
            seen_pass = seen_pass or attempt.execution_result.passed
        return False

    @property
    def total_input_tokens(self) -> int:
        return sum(a.input_tokens for a in self.attempts)

    @property
    def total_output_tokens(self) -> int:
        return sum(a.output_tokens for a in self.attempts)

    @property
    def total_latency_s(self) -> float:
        return sum(a.latency_s for a in self.attempts)
