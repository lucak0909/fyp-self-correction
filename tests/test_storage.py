import sqlite3

from fyp_agent.agent.trajectory import Attempt, Trajectory
from fyp_agent.eval.storage import ExperimentStore
from fyp_agent.sandbox.base import ExecutionResult


def _trajectory() -> Trajectory:
    traj = Trajectory(problem_id="fixture/add", condition="execution", model="claude-sonnet-5")
    traj.attempts = [
        Attempt(
            round_index=0,
            solution_code="def add(a, b): return a + b",
            execution_result=ExecutionResult(
                passed=True, stdout="", stderr="", exit_code=0, timed_out=False, duration_s=0.1
            ),
            input_tokens=10,
            output_tokens=20,
            latency_s=0.5,
        )
    ]
    return traj


def test_context_manager_opens_and_closes(tmp_path):
    db_path = tmp_path / "experiments.db"
    with ExperimentStore(db_path) as store:
        store.create_run("run1", model="claude-sonnet-5", benchmark="fixture")

    # The connection is closed after the `with` block; a fresh one can still
    # read what was written.
    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT run_id, model, benchmark FROM runs").fetchone()
    assert row == ("run1", "claude-sonnet-5", "fixture")


def test_save_trajectory_round_trips_attempts(tmp_path):
    store = ExperimentStore(tmp_path / "experiments.db")
    store.create_run("run1", model="claude-sonnet-5", benchmark="fixture")
    store.save_trajectory("run1", _trajectory())

    conn = store._conn
    trajectory_row = conn.execute(
        "SELECT problem_id, condition, final_passed, num_attempts FROM trajectories"
    ).fetchone()
    assert trajectory_row == ("fixture/add", "execution", 1, 1)

    attempt_row = conn.execute("SELECT round_index, passed FROM attempts").fetchone()
    assert attempt_row == (0, 1)

    store.close()
