from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Iterable, Protocol

from importlib import resources


_KEY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def is_valid_key(key: str) -> bool:
    """Return True if ``key`` matches the allowed slug pattern."""
    return bool(_KEY_RE.fullmatch(key))


@dataclass(frozen=True)
class _WordList:
    words: tuple[str, ...]


def _load_wordlist() -> _WordList:
    # Load the embedded wordlist from package data
    with resources.files("promptorium.data").joinpath("wordlist.txt").open("r", encoding="utf-8") as f:
        words = tuple(w.strip() for w in f if w.strip() and not w.startswith("#"))
    return _WordList(words=words)


_WORDS = _load_wordlist()


def _random_words(n: int) -> Iterable[str]:
    for _ in range(n):
        yield random.choice(_WORDS.words)


def generate_human_key(num_words: int = 3) -> str:
    """Generate a human-readable slug like ``battery-horse-staple``."""
    return "-".join(_random_words(num_words))


class KeyExistenceChecker(Protocol):
    def key_exists(self, key: str) -> bool:  # pragma: no cover - protocol definition only
        ...


def generate_unique_key(store: KeyExistenceChecker, *, max_attempts: int = 256) -> str:
    """Generate a unique key not present in ``store``.

    Attempts up to ``max_attempts`` combinations before raising ``RuntimeError``.
    """
    for _ in range(max_attempts):
        candidate = generate_human_key()
        if not store.key_exists(candidate):
            return candidate
    raise RuntimeError("Could not generate a unique key after many attempts")


