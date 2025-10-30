from __future__ import annotations

from promptorium.util.diff import build_inline_diff


def test_build_inline_diff_word() -> None:
    a = "hello world"
    b = "hello brave world"
    segs = build_inline_diff(a, b, granularity="word")
    ops = [s.op for s in segs]
    texts = [s.text for s in segs]
    assert ops == ["equal", "insert", "equal"]
    assert texts[0] == "hello "
    assert texts[1] == "brave "
    assert texts[2] == "world"


def test_build_inline_diff_char() -> None:
    a = "abc"
    b = "axc"
    segs = build_inline_diff(a, b, granularity="char")
    ops = [s.op for s in segs]
    texts = [s.text for s in segs]
    assert ops == ["equal", "delete", "insert", "equal"]
    assert texts == ["a", "b", "x", "c"]


