"""Loader for the HumanEval benchmark (Chen et al. 2021), via HuggingFace datasets."""

from __future__ import annotations

from .base import Problem


class HumanEvalLoader:
    """Loads the standard 164-problem HumanEval set."""

    def load(self, limit: int | None = None) -> list[Problem]:
        from datasets import load_dataset

        ds = load_dataset("openai_humaneval", split="test")
        if limit is not None:
            ds = ds.select(range(min(limit, len(ds))))

        problems: list[Problem] = []
        for row in ds:
            problems.append(
                Problem(
                    problem_id=row["task_id"],
                    source="humaneval",
                    prompt=row["prompt"],
                    entry_point=row["entry_point"],
                    test_code=row["test"] + f"\ncheck({row['entry_point']})\n",
                    starter_code=row["prompt"],
                    metadata={"canonical_solution": row.get("canonical_solution", "")},
                )
            )
        return problems
