from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from promptorium.cli import app


def test_cli_add_update_list_load_delete() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        # add with custom dir
        result = runner.invoke(app, ["add", "--key", "onboarding", "--dir", "prompts/system"]) 
        assert result.exit_code == 0

        # first version via file
        docs = Path("docs"); docs.mkdir(parents=True, exist_ok=True)
        (docs / "onboarding_v1.md").write_text("hello", encoding="utf-8")
        result = runner.invoke(app, ["update", "onboarding", "--file", str(docs / "onboarding_v1.md")])
        assert result.exit_code == 0

        # second version via stdin
        result = runner.invoke(app, ["update", "onboarding"], input="hello world")
        assert result.exit_code == 0

        # list
        result = runner.invoke(app, ["list"]) 
        assert result.exit_code == 0
        assert "onboarding-1.md" in result.stdout
        assert "onboarding-2.md" in result.stdout

        # load latest
        result = runner.invoke(app, ["load", "onboarding"]) 
        assert result.exit_code == 0
        assert "hello world" in result.stdout

        # diff (just ensure it runs)
        result = runner.invoke(app, ["diff", "onboarding", "1", "2"]) 
        assert result.exit_code == 0

        # delete latest
        result = runner.invoke(app, ["delete", "onboarding"]) 
        assert result.exit_code == 0

        # delete all (custom dir retained)
        result = runner.invoke(app, ["delete", "onboarding", "--all"]) 
        assert result.exit_code == 0
        assert Path("prompts/system").exists()


def test_cli_update_mutually_exclusive_flags() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        _ = runner.invoke(app, ["add", "--key", "alpha"]) 
        result = runner.invoke(app, ["update", "alpha", "--file", "f.txt", "--edit"]) 
        # EX_USAGE
        assert result.exit_code == 64


