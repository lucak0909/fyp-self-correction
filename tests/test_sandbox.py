from fyp_agent.sandbox.subprocess_sandbox import SubprocessSandbox

SANDBOX = SubprocessSandbox()


def test_passing_solution():
    result = SANDBOX.run(
        solution_code="def add(a, b):\n    return a + b\n",
        test_code="assert add(2, 3) == 5\n",
    )
    assert result.passed
    assert result.exit_code == 0


def test_failing_solution():
    result = SANDBOX.run(
        solution_code="def add(a, b):\n    return a - b\n",
        test_code="assert add(2, 3) == 5\n",
    )
    assert not result.passed
    assert "AssertionError" in result.stderr


def test_syntax_error_solution():
    result = SANDBOX.run(
        solution_code="def add(a, b)\n    return a + b\n",
        test_code="assert add(2, 3) == 5\n",
    )
    assert not result.passed
    assert "SyntaxError" in result.stderr


def test_timeout():
    result = SANDBOX.run(
        solution_code="while True:\n    pass\n",
        test_code="",
        timeout_s=1.0,
    )
    assert not result.passed
    assert result.timed_out
