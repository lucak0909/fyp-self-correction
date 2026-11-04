"""Evaluation harness (Key Aim 3): runs every problem under every requested
feedback condition, logging each trajectory to the experiment store.
"""

from __future__ import annotations

from collections.abc import Iterable

from ..agent.core import CodingAgent
from ..benchmarks.base import Problem
from ..feedback import STRATEGIES
from ..llm.base import LLMClient
from ..sandbox.base import Sandbox
from .storage import ExperimentStore


def run_experiment(
    run_id: str,
    problems: Iterable[Problem],
    conditions: list[str],
    llm: LLMClient,
    sandbox: Sandbox,
    store: ExperimentStore,
    benchmark_name: str,
    max_repair_rounds: int = 2,
    timeout_s: float = 10.0,
) -> None:
    problems = list(problems)
    store.create_run(run_id, model=llm.model, benchmark=benchmark_name)

    unknown = [c for c in conditions if c not in STRATEGIES]
    if unknown:
        raise ValueError(f"Unknown condition(s) {unknown}. Known: {list(STRATEGIES)}")

    total = len(problems) * len(conditions)
    done = 0
    for condition in conditions:
        strategy = STRATEGIES[condition]()
        agent = CodingAgent(
            llm=llm,
            sandbox=sandbox,
            feedback_strategy=strategy,
            max_repair_rounds=max_repair_rounds,
            timeout_s=timeout_s,
        )
        for problem in problems:
            trajectory = agent.solve(problem)
            store.save_trajectory(run_id, trajectory)
            done += 1
            status = "PASS" if trajectory.final_passed else "FAIL"
            print(
                f"[{done}/{total}] {condition:16s} {problem.problem_id:24s} "
                f"{status} (round {len(trajectory.attempts) - 1}, "
                f"{trajectory.total_input_tokens + trajectory.total_output_tokens} tok)"
            )
