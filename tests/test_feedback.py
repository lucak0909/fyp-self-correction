from fyp_agent.benchmarks.base import Problem
from fyp_agent.feedback.binary import BinaryFeedbackStrategy
from fyp_agent.feedback.execution import ExecutionFeedbackStrategy
from fyp_agent.feedback.none import NoCorrectionStrategy
from fyp_agent.feedback.self_reflection import SelfReflectionStrategy
from fyp_agent.sandbox.base import ExecutionResult

PROBLEM = Problem(
    problem_id="p1", source="fixture", prompt="def f(): ...",
    entry_point="f", test_code="assert f() == 1",
)

PASS_RESULT = ExecutionResult(
    passed=True, stdout="", stderr="", exit_code=0, timed_out=False, duration_s=0.1
)
FAIL_RESULT = ExecutionResult(
    passed=False,
    stdout="",
    stderr="AssertionError: boom",
    exit_code=1,
    timed_out=False,
    duration_s=0.1,
)


def test_no_correction_never_repairs():
    strategy = NoCorrectionStrategy()
    assert strategy.build_feedback_message(PROBLEM, "code", PASS_RESULT) is None
    assert strategy.build_feedback_message(PROBLEM, "code", FAIL_RESULT) is None


def test_self_reflection_does_not_leak_execution_result():
    strategy = SelfReflectionStrategy()
    msg_pass = strategy.build_feedback_message(PROBLEM, "code", PASS_RESULT)
    msg_fail = strategy.build_feedback_message(PROBLEM, "code", FAIL_RESULT)
    assert msg_pass == msg_fail
    assert "pass" not in msg_pass.lower()
    assert "fail" not in msg_pass.lower()


def test_binary_feedback_hides_error_detail():
    strategy = BinaryFeedbackStrategy()
    msg = strategy.build_feedback_message(PROBLEM, "code", FAIL_RESULT)
    assert "FAILED" in msg
    assert "boom" not in msg


def test_execution_feedback_includes_error_detail():
    strategy = ExecutionFeedbackStrategy()
    msg = strategy.build_feedback_message(PROBLEM, "code", FAIL_RESULT)
    assert "FAILED" in msg
    assert "boom" in msg
