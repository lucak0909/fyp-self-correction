"""Mirrors test_sandbox.py's coverage for the Docker-backed sandbox -- same
behavioural contract, different isolation backend. Skipped (not failed)
when Docker isn't available, since DockerSandbox is optional for local dev
but always available on the CI runner.
"""

import shutil
import subprocess

import pytest

from fyp_agent.sandbox.docker_sandbox import DockerSandbox


def _docker_available() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        subprocess.run(["docker", "info"], capture_output=True, timeout=5, check=True)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


pytestmark = pytest.mark.skipif(not _docker_available(), reason="Docker is not available")


@pytest.fixture(scope="module")
def sandbox():
    return DockerSandbox()


def test_passing_solution(sandbox):
    result = sandbox.run(
        solution_code="def add(a, b):\n    return a + b\n",
        test_code="assert add(2, 3) == 5\n",
    )
    assert result.passed
    assert result.exit_code == 0


def test_failing_solution(sandbox):
    result = sandbox.run(
        solution_code="def add(a, b):\n    return a - b\n",
        test_code="assert add(2, 3) == 5\n",
    )
    assert not result.passed
    assert "AssertionError" in result.stderr


def test_syntax_error_solution(sandbox):
    result = sandbox.run(
        solution_code="def add(a, b)\n    return a + b\n",
        test_code="assert add(2, 3) == 5\n",
    )
    assert not result.passed
    assert "SyntaxError" in result.stderr


def test_timeout(sandbox):
    result = sandbox.run(
        solution_code="while True:\n    pass\n",
        test_code="",
        timeout_s=2.0,
    )
    assert not result.passed
    assert result.timed_out


def test_no_network_access(sandbox):
    result = sandbox.run(
        solution_code="",
        test_code=(
            "import socket\n"
            "s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n"
            "s.settimeout(3)\n"
            "s.connect(('8.8.8.8', 53))\n"
        ),
    )
    assert not result.passed
