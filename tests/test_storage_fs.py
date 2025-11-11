from __future__ import annotations

from pathlib import Path

from promptorium.storage.fs import FileSystemPromptStorage


def test_default_add_and_versioning(tmp_path: Path) -> None:
    s = FileSystemPromptStorage(tmp_path)
    s.ensure_initialized()
    ref = s.add_prompt("alpha", None)
    assert ref.managed_by_root is True
    assert ref.base_dir == tmp_path / ".prompts" / "alpha"

    v1 = s.write_new_version("alpha", "hello")
    v2 = s.write_new_version("alpha", "hello world")
    assert v1.version == 1
    assert v2.version == 2
    assert (ref.base_dir / "1.md").exists()
    assert (ref.base_dir / "2.md").exists()
    assert s.read_version("alpha", None) == "hello world"


def test_custom_dir_naming_and_listing(tmp_path: Path) -> None:
    s = FileSystemPromptStorage(tmp_path)
    s.ensure_initialized()
    custom = tmp_path / "prompts" / "system"
    ref = s.add_prompt("onboarding", custom)
    assert ref.managed_by_root is False
    assert ref.base_dir == custom

    v1 = s.write_new_version("onboarding", "v1 text")
    v2 = s.write_new_version("onboarding", "v2 text")
    assert v1.path.name == "onboarding-1.md"
    assert v2.path.name == "onboarding-2.md"

    infos = s.list_prompts()
    keys = {i.ref.key for i in infos}
    assert "onboarding" in keys
    info = next(i for i in infos if i.ref.key == "onboarding")
    assert [v.version for v in info.versions] == [1, 2]


def test_delete_latest_and_all(tmp_path: Path) -> None:
    s = FileSystemPromptStorage(tmp_path)
    s.ensure_initialized()
    s.add_prompt("alpha", None)
    s.write_new_version("alpha", "a")
    s.write_new_version("alpha", "b")

    latest = s.delete_latest("alpha")
    assert latest.version == 2
    assert not (tmp_path / ".prompts" / "alpha" / "2.md").exists()

    count = s.delete_all("alpha")
    assert count == 1
    # default-managed directory removed
    assert not (tmp_path / ".prompts" / "alpha").exists()

    # custom-managed: directory preserved, metadata entry removed
    custom = tmp_path / "customdir"
    s.add_prompt("beta", custom)
    s.write_new_version("beta", "x")
    assert (custom / "beta-1.md").exists()
    count2 = s.delete_all("beta")
    assert count2 == 1
    assert custom.exists()
    assert not (custom / "beta-1.md").exists()
