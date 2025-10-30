from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer

from .domain import PromptError
from .services import PromptService
from .storage.fs import FileSystemPromptStorage
from .util import editor as editor_util
from .util.render import render_diff_to_console
from .util.repo_root import find_repo_root


app = typer.Typer(add_completion=False)


def _service() -> PromptService:
    storage = FileSystemPromptStorage(find_repo_root())
    return PromptService(storage)


@app.command()
def add(
    key: Optional[str] = typer.Option(None, "--key"),
    directory: Optional[Path] = typer.Option(None, "--dir", help="Custom directory for versions"),
) -> None:
    try:
        ref = _service().add_prompt(key, directory)
        typer.echo(f"Created prompt '{ref.key}' at {ref.base_dir}")
    except PromptError as e:
        typer.secho(str(e), err=True, fg=typer.colors.RED)
        raise typer.Exit(1)


@app.command()
def update(
    key: str,
    file: Optional[Path] = typer.Option(None, "--file", help="Read prompt text from file"),
    edit: bool = typer.Option(False, "--edit", help="Open $EDITOR to edit the prompt text"),
) -> None:
    svc = _service()
    try:
        if file is not None and edit:
            typer.secho("Use either --file or --edit, not both.", err=True, fg=typer.colors.RED)
            raise typer.Exit(64)

        if file is not None:
            text = file.read_text(encoding="utf-8")
        elif edit:
            try:
                seed = svc.load_prompt(key)
            except PromptError:
                seed = ""
            text = editor_util.open_in_editor(seed)
        else:
            if sys.stdin.isatty():
                typer.secho("Provide content via --file, --edit, or STDIN.", err=True, fg=typer.colors.RED)
                raise typer.Exit(64)
            text = sys.stdin.read()

        v = svc.update_prompt(key, text)
        typer.echo(f"Updated {v.key} -> v{v.version} ({v.path})")
    except PromptError as e:
        typer.secho(str(e), err=True, fg=typer.colors.RED)
        raise typer.Exit(1)


@app.command("list")
def list_() -> None:
    infos = _service().list_prompts()
    if not infos:
        typer.echo("No prompts tracked.")
        raise typer.Exit()
    for info in infos:
        typer.echo(f"\n{info.ref.key}  @  {info.ref.base_dir}")
        for v in info.versions:
            typer.echo(f"  - v{v.version}: {v.path}")
    typer.echo("")


@app.command()
def delete(key: str, all: bool = typer.Option(False, "--all")) -> None:  # noqa: A002 - match CLI spec
    svc = _service()
    try:
        if all:
            n = svc.delete_prompt(key, delete_all=True)
            typer.echo(f"Deleted {n} version(s) for '{key}'.")
        else:
            v = svc.delete_prompt(key, delete_all=False)
            typer.echo(f"Deleted latest version v{v.version} for '{key}'.")
    except PromptError as e:
        typer.secho(str(e), err=True, fg=typer.colors.RED)
        raise typer.Exit(1)


@app.command()
def load(key: str, version: Optional[int] = typer.Option(None, "--version")) -> None:
    try:
        typer.echo(_service().load_prompt(key, version))
    except PromptError as e:
        typer.secho(str(e), err=True, fg=typer.colors.RED)
        raise typer.Exit(1)


@app.command()
def diff(
    key: str,
    v1: int,
    v2: int,
    granularity: str = typer.Option("word", "--granularity", "--g"),
) -> None:
    try:
        res = _service().diff_versions(key, v1, v2, granularity=granularity)
        render_diff_to_console(res)
    except PromptError as e:
        typer.secho(str(e), err=True, fg=typer.colors.RED)
        raise typer.Exit(1)


