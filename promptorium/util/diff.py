from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from difflib import SequenceMatcher

from ..domain import DiffSegment


def _tokenize(text: str, *, granularity: str) -> list[str]:
    if granularity == "char":
        return list(text)
    # word granularity: keep whitespace and punctuation as separate tokens to preserve layout
    pattern = re.compile(r"\s+|\w+|[^\w\s]", flags=re.UNICODE)
    return [m.group(0) for m in pattern.finditer(text)]


def _coalesce(op: str, tokens: Iterable[str]) -> str:
    # Simply join token sequence; whitespace tokens already preserved
    return "".join(tokens)


def build_inline_diff(a: str, b: str, *, granularity: str = "word") -> Sequence[DiffSegment]:
    """Build inline diff segments inserting/deleting minimal spans.

    ``granularity`` is either ``"word"`` or ``"char"``.
    """
    g = "char" if granularity == "char" else "word"
    a_tokens = _tokenize(a, granularity=g)
    b_tokens = _tokenize(b, granularity=g)
    sm = SequenceMatcher(None, a_tokens, b_tokens, autojunk=False)

    segments: list[DiffSegment] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            text = _coalesce(tag, a_tokens[i1:i2])
            if text:
                segments.append(DiffSegment(op="equal", text=text))
        elif tag == "replace":
            del_text = _coalesce(tag, a_tokens[i1:i2])
            ins_text = _coalesce(tag, b_tokens[j1:j2])
            if del_text:
                segments.append(DiffSegment(op="delete", text=del_text))
            if ins_text:
                segments.append(DiffSegment(op="insert", text=ins_text))
        elif tag == "delete":
            text = _coalesce(tag, a_tokens[i1:i2])
            if text:
                segments.append(DiffSegment(op="delete", text=text))
        elif tag == "insert":
            text = _coalesce(tag, b_tokens[j1:j2])
            if text:
                segments.append(DiffSegment(op="insert", text=text))

    # Merge adjacent segments of the same op to reduce noise
    if not segments:
        return []
    merged: list[DiffSegment] = [segments[0]]
    for seg in segments[1:]:
        last = merged[-1]
        if seg.op == last.op:
            merged[-1] = DiffSegment(op=last.op, text=last.text + seg.text)
        else:
            merged.append(seg)
    return merged
