from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Literal, overload

from .domain import (
    DiffResult,
    InvalidKey,
    NoContentProvided,
    PromptAlreadyExists,
    PromptInfo,
    PromptRef,
    PromptVersion,
)
from .storage.base import StoragePort
from .util.diff import build_inline_diff
from .util.keygen import generate_unique_key, is_valid_key


class PromptService:
    def __init__(self, storage: StoragePort):
        self.s = storage
        self.s.ensure_initialized()

    def add_prompt(self, key: str | None = None, directory: Path | None = None) -> PromptRef:
        if key is None:
            key = generate_unique_key(self.s)
        if not is_valid_key(key):
            raise InvalidKey(f"Invalid key: {key}")
        if self.s.key_exists(key):
            ref = self.s.get_prompt_ref(key)
            raise PromptAlreadyExists(
                f"Prompt with key '{key}' already exists in directory '{ref.base_dir}'. "
                "Use a different --key or delete the existing prompt using --all first."
            )
        return self.s.add_prompt(key, directory)

    def update_prompt(self, key: str, content: str) -> PromptVersion:
        if not content:
            raise NoContentProvided("No prompt text provided.")
        # Ensure key exists
        self.s.get_prompt_ref(key)
        return self.s.write_new_version(key, content)

    def list_prompts(self) -> Sequence[PromptInfo]:
        return self.s.list_prompts()

    @overload
    def delete_prompt(self, key: str, delete_all: Literal[False] = False) -> PromptVersion: ...

    @overload
    def delete_prompt(self, key: str, delete_all: Literal[True]) -> int: ...

    def delete_prompt(self, key: str, delete_all: bool = False) -> PromptVersion | int:
        # Ensure key exists
        self.s.get_prompt_ref(key)
        return self.s.delete_all(key) if delete_all else self.s.delete_latest(key)

    def load_prompt(self, key: str, version: int | None = None) -> str:
        return self.s.read_version(key, version)

    def diff_versions(self, key: str, v1: int, v2: int, *, granularity: str = "word") -> DiffResult:
        a = self.s.read_version(key, v1)
        b = self.s.read_version(key, v2)
        g = "word" if granularity not in ("word", "char") else granularity
        segs = build_inline_diff(a, b, granularity=g)
        return DiffResult(key=key, v1=v1, v2=v2, segments=segs)
