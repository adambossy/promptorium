from __future__ import annotations

from pathlib import Path


def find_repo_root(start: Path | None = None) -> Path:
    """Locate the repository root directory.

    Heuristics: ascend from ``start`` (or CWD) until a directory containing one of
    these markers is found: ``.git`` directory, ``.prompts`` directory, ``pyproject.toml``.
    If none is found, return the starting directory.
    """
    current = (start or Path.cwd()).resolve()

    def has_markers(p: Path) -> bool:
        return (p / ".git").exists() or (p / ".prompts").exists() or (p / "pyproject.toml").exists()

    if has_markers(current):
        return current

    for parent in [*current.parents]:
        if has_markers(parent):
            return parent

    return current
