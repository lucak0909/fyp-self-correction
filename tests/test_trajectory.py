from fyp_agent.agent.trajectory import Attempt, Trajectory
from fyp_agent.sandbox.base import ExecutionResult


def _attempt(round_index: int, passed: bool) -> Attempt:
    return Attempt(
        round_index=round_index,
        solution_code="code",
        execution_result=ExecutionResult(
            passed=passed, stdout="", stderr="", exit_code=0 if passed else 1,
            timed_out=False, duration_s=0.1,
        ),
        input_tokens=10,
        output_tokens=20,
        latency_s=0.5,
    )


def test_broke_a_correct_solution_detects_pass_then_fail():
    traj = Trajectory(problem_id="p", condition="execution", model="m")
    traj.attempts = [_attempt(0, True), _attempt(1, False)]
    assert traj.broke_a_correct_solution
    assert traj.first_passed
    assert not traj.final_passed


def test_broke_a_correct_solution_false_when_always_passing():
    traj = Trajectory(problem_id="p", condition="execution", model="m")
    traj.attempts = [_attempt(0, True), _attempt(1, True)]
    assert not traj.broke_a_correct_solution


def test_token_and_latency_totals():
    traj = Trajectory(problem_id="p", condition="execution", model="m")
    traj.attempts = [_attempt(0, False), _attempt(1, True)]
    assert traj.total_input_tokens == 20
    assert traj.total_output_tokens == 40
    assert traj.total_latency_s == 1.0
