"""Container-isolated sandbox: runs code inside a disposable Docker
container (network disabled, memory-capped, read-only script mount).

Same interface as SubprocessSandbox -- this is the stronger-isolation
backend the proposal calls for once Docker Desktop is installed. Until then,
`DockerSandbox()` raises RuntimeError at construction time rather than
failing confusingly mid-run.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from .base import ExecutionResult, decode_stream


class DockerSandbox:
    def __init__(self, image: str = "python:3.11-slim", memory: str = "256m") -> None:
        if shutil.which("docker") is None:
            raise RuntimeError(
                "Docker is not installed or not on PATH. Install Docker Desktop, "
                "or use SubprocessSandbox in the meantime (see sandbox/subprocess_sandbox.py)."
            )
        self.image = image
        self.memory = memory

    def run(
        self,
        solution_code: str,
        test_code: str,
        timeout_s: float = 10.0,
    ) -> ExecutionResult:
        script = f"{solution_code}\n\n{test_code}\n"

        with tempfile.TemporaryDirectory(prefix="fyp_sandbox_") as tmp:
            script_path = Path(tmp) / "run_me.py"
            script_path.write_text(script, encoding="utf-8")

            cmd = [
                "docker", "run", "--rm",
                "--network", "none",
                "--memory", self.memory,
                "--cpus", "1",
                "-v", f"{tmp}:/sandbox:ro",
                "-w", "/sandbox",
                self.image,
                "python", "run_me.py",
            ]

            start = time.monotonic()
            timed_out = False
            try:
                proc = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=timeout_s + 5,
                )
                stdout, stderr, exit_code = proc.stdout, proc.stderr, proc.returncode
            except subprocess.TimeoutExpired as e:
                timed_out = True
                stdout = decode_stream(e.stdout)
                stderr = decode_stream(e.stderr)
                exit_code = None
            duration_s = time.monotonic() - start

            passed = (not timed_out) and exit_code == 0
            return ExecutionResult(
                passed=passed,
                stdout=stdout,
                stderr=stderr if not timed_out else stderr + "\n[sandbox] execution timed out",
                exit_code=exit_code,
                timed_out=timed_out,
                duration_s=duration_s,
            )
