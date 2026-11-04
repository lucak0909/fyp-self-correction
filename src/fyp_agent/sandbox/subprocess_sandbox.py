"""Process-isolated sandbox: runs code as a separate `python` subprocess in
a scratch temp directory, with a wall-clock timeout and a stripped-down
environment.

This is NOT a strong security boundary -- a subprocess on the same OS can
still, e.g., read the filesystem or make network calls. It isolates crashes,
infinite loops and stdout/stderr pollution, which is enough for trusted
development and small pilot runs. Swap to DockerSandbox (same interface)
before running at scale or on a shared/untrusted machine.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from .base import ExecutionResult


class SubprocessSandbox:
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

            env = {
                "PATH": os.environ.get("PATH", ""),
                "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
                "PYTHONIOENCODING": "utf-8",
            }

            start = time.monotonic()
            timed_out = False
            try:
                proc = subprocess.run(
                    [sys.executable, str(script_path)],
                    cwd=tmp,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=timeout_s,
                )
                stdout, stderr, exit_code = proc.stdout, proc.stderr, proc.returncode
            except subprocess.TimeoutExpired as e:
                timed_out = True
                stdout = e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
                stderr = e.stderr.decode("utf-8", "replace") if isinstance(e.stderr, bytes) else (e.stderr or "")
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
