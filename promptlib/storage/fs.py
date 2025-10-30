from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from ..domain import (
    PromptInfo,
    PromptNotFound,
    PromptRef,
    PromptVersion,
    VersionNotFound,
)
from ..util.io_safety import atomic_write_text
from .base import StoragePort


_SCHEMA_VERSION = 1


@dataclass
class _Meta:
    schema: int
    custom_dirs: Dict[str, str]


class FileSystemPromptStorage(StoragePort):
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root.resolve()
        self.root = self.repo_root / ".prompts"
        self._meta_path = self.root / "_meta.json"

    # --- helpers ---
    def _load_meta(self) -> _Meta:
        if not self._meta_path.exists():
            return _Meta(schema=_SCHEMA_VERSION, custom_dirs={})
        data = json.loads(self._meta_path.read_text(encoding="utf-8"))
        schema = int(data.get("schema", 0))
        if schema != _SCHEMA_VERSION:
            # For now, treat mismatch as empty mapping
            return _Meta(schema=_SCHEMA_VERSION, custom_dirs=dict(data.get("custom_dirs", {})))
        return _Meta(schema=schema, custom_dirs=dict(data.get("custom_dirs", {})))

    def _save_meta(self, meta: _Meta) -> None:
        payload = {"schema": meta.schema, "custom_dirs": meta.custom_dirs}
        atomic_write_text(self._meta_path, json.dumps(payload, indent=2) + "\n")

    def _resolve_dir_value(self, value: str) -> Path:
        p = Path(value)
        if p.is_absolute():
            return p
        return (self.repo_root / p).resolve()

    def _store_dir_value(self, path: Path) -> str:
        try:
            rel = path.resolve().relative_to(self.repo_root)
            return rel.as_posix()
        except Exception:
            return str(path.resolve())

    def _default_key_dir(self, key: str) -> Path:
        return self.root / key

    def _is_default_managed(self, base_dir: Path) -> bool:
        try:
            base_dir.resolve().relative_to(self.root)
            return True
        except Exception:
            return False

    def _custom_dir_for_key(self, key: str) -> Optional[Path]:
        meta = self._load_meta()
        d = meta.custom_dirs.get(key)
        if d is None:
            return None
        return self._resolve_dir_value(d)

    def _scan_default_versions(self, key: str) -> List[Tuple[int, Path]]:
        base = self._default_key_dir(key)
        if not base.exists():
            return []
        versions: List[Tuple[int, Path]] = []
        for p in base.iterdir():
            if not p.is_file():
                continue
            if re.fullmatch(r"\d+\.md", p.name):
                n = int(p.stem)
                versions.append((n, p))
        versions.sort(key=lambda t: t[0])
        return versions

    def _scan_custom_versions(self, key: str, base_dir: Path) -> List[Tuple[int, Path]]:
        pattern = re.compile(rf"^{re.escape(key)}-(\d+)\.md$")
        versions: List[Tuple[int, Path]] = []
        if not base_dir.exists():
            return []
        for p in base_dir.iterdir():
            if not p.is_file():
                continue
            m = pattern.fullmatch(p.name)
            if m:
                n = int(m.group(1))
                versions.append((n, p))
        versions.sort(key=lambda t: t[0])
        return versions

    # --- API ---
    def ensure_initialized(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        if not self._meta_path.exists():
            self._save_meta(_Meta(schema=_SCHEMA_VERSION, custom_dirs={}))

    def key_exists(self, key: str) -> bool:
        if (self.root / key).is_dir():
            return True
        meta = self._load_meta()
        return key in meta.custom_dirs

    def add_prompt(self, key: str, custom_dir: Optional[Path]) -> PromptRef:
        self.ensure_initialized()
        if custom_dir is None:
            base = self._default_key_dir(key)
            base.mkdir(parents=True, exist_ok=True)
            return PromptRef(key=key, base_dir=base, managed_by_root=True)

        base = (self.repo_root / custom_dir).resolve() if not custom_dir.is_absolute() else custom_dir.resolve()
        base.mkdir(parents=True, exist_ok=True)
        meta = self._load_meta()
        meta.custom_dirs[key] = self._store_dir_value(base)
        self._save_meta(meta)
        return PromptRef(key=key, base_dir=base, managed_by_root=False)

    def get_prompt_ref(self, key: str) -> PromptRef:
        custom = self._custom_dir_for_key(key)
        if custom is not None:
            return PromptRef(key=key, base_dir=custom, managed_by_root=False)
        base = self._default_key_dir(key)
        if base.exists():
            return PromptRef(key=key, base_dir=base, managed_by_root=True)
        raise PromptNotFound(key)

    def list_prompts(self) -> Sequence[PromptInfo]:
        self.ensure_initialized()
        meta = self._load_meta()

        keys: Dict[str, PromptRef] = {}
        # default-managed keys
        if self.root.exists():
            for p in self.root.iterdir():
                if p.is_dir() and p.name != "__pycache__":
                    keys[p.name] = PromptRef(key=p.name, base_dir=p, managed_by_root=True)
        # custom-managed keys
        for key, dirval in meta.custom_dirs.items():
            base = self._resolve_dir_value(dirval)
            keys[key] = PromptRef(key=key, base_dir=base, managed_by_root=False)

        infos: List[PromptInfo] = []
        for key, ref in sorted(keys.items(), key=lambda kv: kv[0]):
            if ref.managed_by_root:
                pairs = self._scan_default_versions(key)
            else:
                pairs = self._scan_custom_versions(key, ref.base_dir)
            versions = [PromptVersion(key=key, version=n, path=path) for n, path in pairs]
            infos.append(PromptInfo(ref=ref, versions=versions))
        return infos

    def _next_version(self, key: str, ref: PromptRef) -> int:
        if ref.managed_by_root:
            pairs = self._scan_default_versions(key)
        else:
            pairs = self._scan_custom_versions(key, ref.base_dir)
        return (pairs[-1][0] + 1) if pairs else 1

    def write_new_version(self, key: str, content: str) -> PromptVersion:
        ref = self.get_prompt_ref(key)
        next_ver = self._next_version(key, ref)
        if ref.managed_by_root:
            path = ref.base_dir / f"{next_ver}.md"
        else:
            path = ref.base_dir / f"{key}-{next_ver}.md"
        atomic_write_text(path, content)
        return PromptVersion(key=key, version=next_ver, path=path)

    def _latest_version_pair(self, key: str, ref: PromptRef) -> Tuple[int, Path]:
        pairs = self._scan_default_versions(key) if ref.managed_by_root else self._scan_custom_versions(key, ref.base_dir)
        if not pairs:
            raise VersionNotFound(f"No versions for key: {key}")
        return pairs[-1]

    def delete_latest(self, key: str) -> PromptVersion:
        ref = self.get_prompt_ref(key)
        ver, path = self._latest_version_pair(key, ref)
        path.unlink(missing_ok=False)
        return PromptVersion(key=key, version=ver, path=path)

    def delete_all(self, key: str) -> int:
        ref = self.get_prompt_ref(key)
        if ref.managed_by_root:
            pairs = self._scan_default_versions(key)
            for _, p in pairs:
                p.unlink(missing_ok=False)
            # remove directory afterwards
            try:
                ref.base_dir.rmdir()
            except OSError:
                # Non-empty or in use; ignore
                pass
            return len(pairs)
        # custom-managed
        pairs = self._scan_custom_versions(key, ref.base_dir)
        for _, p in pairs:
            p.unlink(missing_ok=False)
        # remove metadata entry but never the directory
        meta = self._load_meta()
        if key in meta.custom_dirs:
            del meta.custom_dirs[key]
            self._save_meta(meta)
        return len(pairs)

    def read_version(self, key: str, version: Optional[int]) -> str:
        ref = self.get_prompt_ref(key)
        if version is None:
            v, path = self._latest_version_pair(key, ref)
            return path.read_text(encoding="utf-8")
        # specific version
        if ref.managed_by_root:
            path = ref.base_dir / f"{version}.md"
        else:
            path = ref.base_dir / f"{key}-{version}.md"
        if not path.exists():
            raise VersionNotFound(f"Version {version} not found for key: {key}")
        return path.read_text(encoding="utf-8")


