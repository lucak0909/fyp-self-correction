"""Sandbox interface: anything that can execute untrusted generated code
against a test suite and report back what happened, safely and reproducibly.

Two backends implement this: SubprocessSandbox (process isolation, timeout,
restricted env -- works everywhere, weaker isolation) and DockerSandbox
(container isolation -- stronger isolation, requires Docker). The rest of
the platform depends only on this interface, so swapping backends is a
one-line change in config.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class ExecutionResult:
    """Outcome of running a candidate solution against a problem's tests."""

    passed: bool
    stdout: str
    stderr: str
    exit_code: int | None
    timed_out: bool
    duration_s: float

    @property
    def error_message(self) -> str:
        """The signal fed to execution-feedback strategies: whatever the
        interpreter printed on failure, truncated to keep prompts bounded."""
        if self.passed:
            return ""
        text = self.stderr.strip() or self.stdout.strip()
        max_chars = 4000
        return text if len(text) <= max_chars else text[-max_chars:]


class Sandbox(Protocol):
    def run(
        self,
        solution_code: str,
        test_code: str,
        timeout_s: float = 10.0,
    ) -> ExecutionResult:
        """Execute `solution_code` followed by `test_code` in an isolated
        environment and report whether the tests passed."""
        ...
