from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from pathlib import Path

from ..domain import PromptInfo, PromptRef, PromptVersion


class StoragePort(ABC):
    @abstractmethod
    def ensure_initialized(self) -> None:  # pragma: no cover - interface only
        ...

    @abstractmethod
    def key_exists(self, key: str) -> bool:  # pragma: no cover - interface only
        ...

    @abstractmethod
    def add_prompt(
        self, key: str, custom_dir: Path | None
    ) -> PromptRef:  # pragma: no cover - interface only
        ...

    @abstractmethod
    def get_prompt_ref(self, key: str) -> PromptRef:  # pragma: no cover - interface only
        ...

    @abstractmethod
    def list_prompts(self) -> Sequence[PromptInfo]:  # pragma: no cover - interface only
        ...

    @abstractmethod
    def write_new_version(
        self, key: str, content: str
    ) -> PromptVersion:  # pragma: no cover - interface only
        ...

    @abstractmethod
    def delete_latest(self, key: str) -> PromptVersion:  # pragma: no cover - interface only
        ...

    @abstractmethod
    def delete_all(self, key: str) -> int:  # pragma: no cover - interface only
        ...

    @abstractmethod
    def read_version(
        self, key: str, version: int | None
    ) -> str:  # pragma: no cover - interface only
        ...
