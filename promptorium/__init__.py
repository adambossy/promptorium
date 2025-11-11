from __future__ import annotations

from .services import PromptService
from .storage.fs import FileSystemPromptStorage
from .util.repo_root import find_repo_root


def load_prompt(key: str, version: int | None = None) -> str:
    """Library API: load prompt content for a key and optional version.

    This is a thin convenience wrapper that constructs a filesystem-backed storage
    rooted at the repository and delegates to the service layer.
    """
    storage = FileSystemPromptStorage(find_repo_root())
    service = PromptService(storage)
    return service.load_prompt(key, version)


__all__ = ["load_prompt", "PromptService"]
