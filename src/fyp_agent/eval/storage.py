"""Experiment log storage (Key Aim 3): every attempt, for every problem,
under every condition, persisted to SQLite so a run can be analysed,
resumed, or re-queried without re-running expensive LLM calls.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from ..agent.trajectory import Trajectory

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    model TEXT NOT NULL,
    benchmark TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS trajectories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES runs(run_id),
    problem_id TEXT NOT NULL,
    condition TEXT NOT NULL,
    model TEXT NOT NULL,
    first_passed INTEGER NOT NULL,
    final_passed INTEGER NOT NULL,
    broke_a_correct_solution INTEGER NOT NULL,
    num_attempts INTEGER NOT NULL,
    total_input_tokens INTEGER NOT NULL,
    total_output_tokens INTEGER NOT NULL,
    total_latency_s REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trajectory_id INTEGER NOT NULL REFERENCES trajectories(id),
    round_index INTEGER NOT NULL,
    passed INTEGER NOT NULL,
    timed_out INTEGER NOT NULL,
    duration_s REAL NOT NULL,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    latency_s REAL NOT NULL,
    solution_code TEXT NOT NULL,
    stderr_tail TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_trajectories_run ON trajectories(run_id);
CREATE INDEX IF NOT EXISTS idx_attempts_trajectory ON attempts(trajectory_id);
"""


class ExperimentStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def create_run(self, run_id: str, model: str, benchmark: str, notes: str = "") -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO runs (run_id, started_at, model, benchmark, notes) "
            "VALUES (?, ?, ?, ?, ?)",
            (run_id, datetime.now(timezone.utc).isoformat(), model, benchmark, notes),
        )
        self._conn.commit()

    def save_trajectory(self, run_id: str, trajectory: Trajectory) -> None:
        cur = self._conn.execute(
            "INSERT INTO trajectories (run_id, problem_id, condition, model, first_passed, "
            "final_passed, broke_a_correct_solution, num_attempts, total_input_tokens, "
            "total_output_tokens, total_latency_s) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                run_id,
                trajectory.problem_id,
                trajectory.condition,
                trajectory.model,
                int(trajectory.first_passed),
                int(trajectory.final_passed),
                int(trajectory.broke_a_correct_solution),
                len(trajectory.attempts),
                trajectory.total_input_tokens,
                trajectory.total_output_tokens,
                trajectory.total_latency_s,
            ),
        )
        trajectory_id = cur.lastrowid

        self._conn.executemany(
            "INSERT INTO attempts (trajectory_id, round_index, passed, timed_out, duration_s, "
            "input_tokens, output_tokens, latency_s, solution_code, stderr_tail) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    trajectory_id,
                    a.round_index,
                    int(a.execution_result.passed),
                    int(a.execution_result.timed_out),
                    a.execution_result.duration_s,
                    a.input_tokens,
                    a.output_tokens,
                    a.latency_s,
                    a.solution_code,
                    a.execution_result.error_message,
                )
                for a in trajectory.attempts
            ],
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "ExperimentStore":
        return self

    def __exit__(self, *exc) -> None:
        self.close()
