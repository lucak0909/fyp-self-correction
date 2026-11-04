"""CLI entry point. Example:

    python -m fyp_agent run --benchmark fixture --conditions no_correction,execution --limit 3
"""

from __future__ import annotations

import uuid
from pathlib import Path

import typer
from dotenv import load_dotenv

from .benchmarks.base import BenchmarkLoader
from .eval.harness import run_experiment
from .eval.storage import ExperimentStore
from .llm.anthropic_client import AnthropicClient
from .sandbox.subprocess_sandbox import SubprocessSandbox

app = typer.Typer(add_completion=False)

_BENCHMARKS = {"fixture": "local_fixture.LocalFixtureLoader", "humaneval": "humaneval.HumanEvalLoader"}


def _load_benchmark(name: str) -> BenchmarkLoader:
    if name == "fixture":
        from .benchmarks.local_fixture import LocalFixtureLoader

        return LocalFixtureLoader()
    if name == "humaneval":
        from .benchmarks.humaneval import HumanEvalLoader

        return HumanEvalLoader()
    raise typer.BadParameter(f"Unknown benchmark '{name}'. Choices: {list(_BENCHMARKS)}")


def _load_sandbox(name: str):
    if name == "subprocess":
        return SubprocessSandbox()
    if name == "docker":
        from .sandbox.docker_sandbox import DockerSandbox

        return DockerSandbox()
    raise typer.BadParameter(f"Unknown sandbox '{name}'. Choices: subprocess, docker")


@app.command()
def run(
    benchmark: str = typer.Option("fixture", help="fixture (offline smoke test) or humaneval"),
    conditions: str = typer.Option(
        "no_correction,self_reflection,binary,execution",
        help="Comma-separated feedback conditions to compare",
    ),
    limit: int | None = typer.Option(5, help="Max problems to pull from the benchmark"),
    model: str = typer.Option("claude-sonnet-5", help="Anthropic model id"),
    max_repair_rounds: int = typer.Option(2, help="Repair attempts after the initial generation"),
    timeout_s: float = typer.Option(10.0, help="Per-execution sandbox timeout, seconds"),
    sandbox: str = typer.Option("docker", help="docker or subprocess"),
    db: Path = typer.Option(Path("data/runs/experiments.db"), help="SQLite log path"),
    run_id: str = typer.Option(None, help="Defaults to a fresh UUID"),
) -> None:
    """Run a batch of problems through the agent under each condition."""
    load_dotenv()

    loader = _load_benchmark(benchmark)
    problems = loader.load(limit=limit)
    if not problems:
        typer.echo("No problems loaded.", err=True)
        raise typer.Exit(code=1)

    llm = AnthropicClient(model=model)
    sbx = _load_sandbox(sandbox)
    store = ExperimentStore(db)
    rid = run_id or str(uuid.uuid4())[:8]

    print(f"Run {rid}: {len(problems)} problems x {len(conditions.split(','))} conditions, model={model}")
    run_experiment(
        run_id=rid,
        problems=problems,
        conditions=conditions.split(","),
        llm=llm,
        sandbox=sbx,
        store=store,
        benchmark_name=benchmark,
        max_repair_rounds=max_repair_rounds,
        timeout_s=timeout_s,
    )
    store.close()
    print(f"Done. Logged to {db} under run_id={rid}")


if __name__ == "__main__":
    app()
