from __future__ import annotations

from rich.console import Console
from rich.text import Text

from ..domain import DiffResult


def render_diff_to_console(result: DiffResult) -> None:
    """Render inline diff to the terminal, coloring inserts and deletions."""
    console = Console()
    out = Text()
    for seg in result.segments:
        if seg.op == "equal":
            out.append(seg.text)
        elif seg.op == "insert":
            out.append(seg.text, style="green")
        elif seg.op == "delete":
            out.append(seg.text, style="red strike")
    console.print(out)
