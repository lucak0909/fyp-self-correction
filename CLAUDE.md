# CLAUDE.md

Instructions for Claude Code (or any AI assistant) working in this repository.

## What this project is

A Final Year Project (ISE, University of Limerick): "When Does Self-Correction
Help? An Empirical Study of Feedback-Driven Repair in LLM Coding Agents."
Student: Luca Knierim. Supervisor: Chris Exton.

It is both (a) a reusable experimental platform and (b) the vehicle for an
empirical research result. Code quality and scientific validity both matter
here — a bug that silently skews results is worse than a bug that crashes,
because it can produce a plausible-looking wrong answer in the dissertation.
See `README.md` for the architecture overview and usage, and the FYP
proposal (not in this repo) for the full research motivation and milestones.

## Non-negotiable invariants

These exist to keep the experiment scientifically valid. Breaking them
silently corrupts results rather than crashing loudly, so treat them as
harder constraints than normal code-quality concerns.

1. **Feedback strategies must only leak what their condition represents.**
   `feedback/self_reflection.py` must never read `execution_result` —
   that's the entire point of the "no external signal" condition. `feedback/binary.py`
   must never include `execution_result.error_message` or stderr/stdout content
   in the message it returns — only "passed" or "failed". If you add a new
   condition, write a test (see `tests/test_feedback.py`'s pattern) proving
   its leak boundary before considering it done.

2. **Every attempt must be logged, including ones after the solution was
   already correct.** The agent loop deliberately keeps running repair
   rounds even after a pass, because measuring whether self-correction
   *breaks* a correct solution (`Trajectory.broke_a_correct_solution`) is
   one of the project's key research aims. Do not "optimize" the loop to
   stop early on success for conditions other than `no_correction` — that
   would silently remove the ability to measure degradation.

3. **The sandbox is the only thing allowed to execute model-generated code.**
   Never `exec()`/`eval()` a model completion directly anywhere outside
   `sandbox/`. Both backends (`SubprocessSandbox`, `DockerSandbox`) must
   keep enforcing a timeout and must not be weakened (e.g. don't silently
   drop the timeout, don't add network access to `DockerSandbox`) without
   explicit sign-off from the user — this code runs arbitrary LLM output.

4. **Don't let a benchmark's ground truth leak into the prompt.**
   `benchmarks/humaneval.py` stores `canonical_solution` in `Problem.metadata`
   for later analysis only. Never pass `metadata` contents into an LLM
   prompt in `agent/core.py` or any `FeedbackStrategy` — that would make
   results meaningless.

5. **API keys live only in `.env` / environment variables.** Never hardcode
   a key, never log a full prompt/response that might contain one, never
   print `.env` contents. If you need to debug an auth failure, check the
   *shape* (e.g. "did the request succeed") rather than the key value.

## Architecture map

See `README.md` for the full diagram. Quick pointers for where to make changes:

| To do this... | Touch this module | Leave alone |
|---|---|---|
| Add a feedback condition | `feedback/your_strategy.py` + register in `feedback/__init__.py`'s `STRATEGIES` | `agent/core.py` |
| Add an LLM provider | `llm/your_provider.py`, implement `LLMClient` protocol from `llm/base.py` | `agent/core.py`, `feedback/` |
| Add a benchmark | `benchmarks/your_benchmark.py`, implement `BenchmarkLoader` protocol, return `Problem`s | `eval/harness.py` |
| Change what gets logged | `eval/storage.py` (schema) + `agent/trajectory.py` (what's recorded) | — |
| Change sandbox isolation | `sandbox/your_backend.py`, implement `Sandbox` protocol from `sandbox/base.py` | — |

Every one of these is a `typing.Protocol`, not an ABC — new implementations
don't need to inherit anything, just match the method signature.

## Conventions

- Python 3.10+, `src/` layout, package name `fyp_agent`.
- Type hints everywhere; dataclasses for data, `Protocol` for interfaces.
- No comments explaining *what* code does — names should do that. A comment
  is only justified for a non-obvious *why* (e.g. the leak-boundary notes
  above, or the subprocess-isolation caveat in `sandbox/subprocess_sandbox.py`).
- No speculative abstraction. This is a research platform for one
  dissertation, not a library for external users — don't add config options,
  providers, or benchmarks that aren't actually being used yet.
- Dependencies are declared in `pyproject.toml` only; don't hand-edit a
  `requirements.txt` (there isn't one).

## Environment

```bash
python -m venv .venv
.venv/Scripts/activate   # .venv/bin/activate on macOS/Linux
pip install -e ".[dev]"
cp .env.example .env     # fill in ANTHROPIC_API_KEY
```

Docker Desktop is optional (`--sandbox docker`, the CLI default) but
`SubprocessSandbox` (`--sandbox subprocess`) always works with no extra setup.

## Testing

- Run `pytest` before every commit. CI (`.github/workflows/ci.yml`) re-runs
  it on every push and PR, and `main` is protected — a PR cannot merge
  with a failing or absent check.
- **Tests must never require `ANTHROPIC_API_KEY` or network access.** They
  exercise `SubprocessSandbox`, feedback strategies, code extraction, and
  `Trajectory` logic directly — no real LLM calls. If you add agent-loop
  tests, use a fake `LLMClient` rather than hitting the real API, so CI
  doesn't need secrets.
- New modules need new tests in the matching `tests/test_*.py`. Follow the
  existing pattern: small, direct, one behaviour per test.

## Git / GitHub workflow

- Commit messages: imperative mood, explain *why* not *what*, no AI
  attribution trailers (the user has opted out of those for this repo —
  don't add `Co-Authored-By` or similar even though that's Claude Code's
  usual default).
- Don't force-push `main`, don't rewrite already-pushed history, don't
  bypass branch protection (`--admin` merges, `--no-verify`) without the
  user explicitly asking.
- Non-trivial changes go through a PR so CI runs as a required check, even
  though this is currently a single-contributor repo.

## Research-integrity notes

- Log everything the harness produces via `ExperimentStore` — don't filter
  out "bad" runs before they're written. Analysis/filtering happens later,
  on the full logged data, not by suppressing attempts at collection time.
- If a run is re-done (e.g. after a bug fix), use a new `run_id` rather than
  overwriting an old one, so the experiment log stays an honest record of
  what actually happened.
- When reporting progress against the proposal's milestones, update the
  "Status" checklist in `README.md` rather than only mentioning it in chat.
