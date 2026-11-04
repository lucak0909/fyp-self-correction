from typer.testing import CliRunner

from fyp_agent.cli import app

runner = CliRunner()


def test_exits_cleanly_when_no_problems_loaded():
    # limit=0 short-circuits before any LLM/sandbox/API-key setup, so this
    # is safe to run without ANTHROPIC_API_KEY or network access.
    result = runner.invoke(app, ["--benchmark", "fixture", "--limit", "0"])

    assert result.exit_code == 1
    assert "No problems loaded." in result.output
