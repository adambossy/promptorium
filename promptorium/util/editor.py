from __future__ import annotations

import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path


def _default_editor() -> str:
    if sys.platform.startswith("win"):
        return "notepad"
    return "nano"


def _pick_editor() -> str:
    return os.environ.get("VISUAL") or os.environ.get("EDITOR") or _default_editor()


def open_in_editor(seed_text: str = "") -> str:
    """Open a temporary file in user's editor and return the edited content."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "prompt_edit.txt"
        tmp_path.write_text(seed_text, encoding="utf-8")
        editor = _pick_editor()
        # Allow quoted editors/flags
        cmd = shlex.split(editor) + [str(tmp_path)]
        subprocess.run(cmd, check=True)
        return tmp_path.read_text(encoding="utf-8")


