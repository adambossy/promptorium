from __future__ import annotations

import os
import tempfile
from pathlib import Path


def ensure_parent_dir(path: Path) -> None:
    """Ensure the parent directory of ``path`` exists."""
    path.parent.mkdir(parents=True, exist_ok=True)


def atomic_write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
    """Atomically write text to ``path``.

    Writes to a temporary file in the same directory and then replaces the target.
    """
    ensure_parent_dir(path)
    directory = str(path.parent)
    fd, tmp_name = tempfile.mkstemp(prefix=".tmp_", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding=encoding) as tmp:
            tmp.write(content)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_name, path)
    finally:
        # Clean up temp file if something went wrong prior to replace
        try:
            if os.path.exists(tmp_name):
                os.remove(tmp_name)
        except OSError:
            pass
