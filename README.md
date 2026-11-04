# When Does Self-Correction Help?

An empirical study of feedback-driven repair in LLM coding agents — Final Year Project (ISE), Luca Knierim, supervised by Chris Exton.

LLM coding agents are often given a chance to review and revise their own output before returning it ("self-correction" / "self-refinement" / "self-repair"). The literature disagrees on whether this helps: some work reports large gains, other work finds models struggle to recognise their own errors without an external signal, and can even break correct answers while burning extra time and tokens.

This project is a modular platform that generates solutions to coding problems and repairs them under controlled feedback conditions, so those conditions can be compared directly, on current models, on a contamination-resistant benchmark.

## How it's built

The feedback condition is the experimental variable, so it's the one piece designed to be swapped without touching anything else:

```
Problem --> CodingAgent --> Sandbox.run() --> ExecutionResult
                |                                   |
                `------ FeedbackStrategy -----------'
                           |
                   (feeds back into the next prompt, or
                    returns None to stop repairing)
```

- **`agent/`** — the generate → execute → repair loop (`CodingAgent`) and the `Trajectory` record of every attempt made on a problem.
- **`feedback/`** — one `FeedbackStrategy` per experimental condition:
  - `no_correction` — single attempt, baseline.
  - `self_reflection` — asked to review and fix its own solution, with **no** external signal about correctness (Madaan et al. 2023 / Huang et al. 2024's setting).
  - `binary` — told only pass/fail, no detail.
  - `execution` — told pass/fail plus the actual error output (Chen et al. 2024's self-debug setting).
- **`sandbox/`** — isolated code execution behind one interface, two backends: `SubprocessSandbox` (process isolation, works everywhere) and `DockerSandbox` (container isolation, stronger guarantees, needs Docker Desktop running).
- **`llm/`** — provider-agnostic `LLMClient` interface; `AnthropicClient` is the first backend.
- **`benchmarks/`** — loaders that adapt a benchmark to a common `Problem` shape. `HumanEvalLoader` pulls the standard set via HuggingFace `datasets`; `LocalFixtureLoader` is a tiny offline set for smoke-testing without network/API calls. LiveCodeBench (contamination-resistant) is planned but not yet wired up.
- **`eval/`** — the harness that runs every problem under every requested condition and logs every attempt (pass/fail, tokens, latency, solution code, error output) to a SQLite `ExperimentStore`, so a run can be analysed or resumed without re-paying for LLM calls.

## Setup

Requires Python 3.10+. Docker Desktop is optional but recommended (falls back to subprocess isolation if unavailable).

```bash
python -m venv .venv
.venv/Scripts/activate        # .venv/bin/activate on macOS/Linux
pip install -e ".[dev]"
cp .env.example .env          # then paste your ANTHROPIC_API_KEY in
```

## Usage

```bash
# Offline smoke test, no benchmark download needed
python -m fyp_agent --benchmark fixture --conditions no_correction,execution --limit 3

# Compare all four conditions on 20 HumanEval problems, via Docker sandbox
python -m fyp_agent --benchmark humaneval --conditions no_correction,self_reflection,binary,execution --limit 20
```

Key options (`python -m fyp_agent --help` for the full list):

| Flag | Default | Meaning |
|---|---|---|
| `--benchmark` | `fixture` | `fixture` or `humaneval` |
| `--conditions` | all four | comma-separated feedback strategy names |
| `--limit` | `5` | max problems pulled from the benchmark |
| `--model` | `claude-sonnet-5` | Anthropic model id |
| `--max-repair-rounds` | `2` | repair attempts after the initial generation |
| `--sandbox` | `docker` | `docker` or `subprocess` |
| `--db` | `data/runs/experiments.db` | SQLite log path |

Every run is logged under a `run_id` in the SQLite database — query it directly (`runs` / `trajectories` / `attempts` tables) for analysis.

## Tests

```bash
pytest
```

Covers sandbox isolation (pass/fail/syntax-error/timeout), every feedback strategy's leak boundaries (e.g. `self_reflection` must never see the execution result), code-block extraction, and trajectory analysis (including detecting when a repair round breaks an already-correct solution).

## Status

Tracking the proposal's milestones:

- [x] Month 1 — literature review, research design
- [x] Month 2 — core agent loop + sandboxed execution environment
- [ ] Month 3 — pluggable feedback system (done) + evaluation harness (done) + pilot cost estimate (next)
- [ ] Month 4 — LiveCodeBench integration, interim report
- [ ] Months 5-8 — full experiments, analysis, dissertation
