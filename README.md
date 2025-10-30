<div align="center">

# Promptorium

CLI and Python library for managing versioned prompts: add, update, list, diff, load, and delete prompt versions on your filesystem.

<br/>

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-%E2%89%A53.12-blue)
![Typer](https://img.shields.io/badge/CLI-Typer-4E9A06)
![Rich](https://img.shields.io/badge/Output-Rich-8A2BE2)

</div>

---

## Table of Contents

1. About the Project
   - Features
   - How it works
2. Getting Started
   - Prerequisites
   - Installation
3. Usage (CLI)
4. Usage (Library)
5. Data Layout & Conventions
6. Development
7. Roadmap
8. Contributing
9. License
10. Acknowledgments

---

## About the Project

Promptorium helps you keep your prompts versioned alongside your code. It stores each prompt as an incrementing Markdown file and gives you a clean CLI to add, edit, list, diff, load, and delete versions. You can use a repo-local `.prompts` folder or map each key to a custom directory you control.

### Features

- Versioned prompt storage with simple, readable files
  - Default-managed: `.prompts/<key>/<n>.md`
  - Custom-managed: `<custom_dir>/<key>-<n>.md`
- Human-friendly keys (e.g., `battery-horse-staple`) with validation
- Update via file, STDIN, or your `$EDITOR` (`VISUAL`/`EDITOR` respected)
- Inline diffs with colorized output (word or character granularity)
- Safe, atomic writes to avoid partial files
- Repository-root detection (works anywhere inside your project tree)

### How it works

- Storage is provided by a filesystem backend that keeps a small metadata file at `.prompts/_meta.json` mapping keys to custom directories.
- Default-managed keys live under `.prompts/<key>/<n>.md` and are removed entirely on `--all` deletion.
- Custom-managed keys write as `<custom_dir>/<key>-<n>.md`; deleting `--all` versions preserves the directory and removes only the metadata mapping.

---

## Getting Started

### Prerequisites

- Python 3.12+
- Optional: [`uv`](https://github.com/astral-sh/uv) for fast environments and installs

### Installation

Using `pip` (from source):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
```

Using `uv`:

```bash
uv venv --python 3.12
source .venv/bin/activate
uv sync --extra dev
uv run pre-commit install
```

Verify the CLI is available:

```bash
prompts --help
```

---

## Usage (CLI)

Common workflows:

```bash
# 1) Add a new prompt. Omit --key to auto-generate a human-readable key.
prompts add --key onboarding --dir prompts/system

# 2) Create versions
prompts update onboarding --file docs/onboarding_v1.md   # from file
echo "hello world" | prompts update onboarding           # from STDIN
prompts update onboarding --edit                         # open $EDITOR

# 3) Inspect and read
prompts list
prompts load onboarding --version 2

# 4) Compare versions
prompts diff onboarding 1 2 --granularity word  # or: --granularity char

# 5) Delete
prompts delete onboarding            # removes latest version only
prompts delete onboarding --all      # removes all versions
```

Notes:

- Keys must match `^[a-z0-9]+(?:-[a-z0-9]+)*$` (lowercase slug with hyphens).
- `update` flags `--file` and `--edit` are mutually exclusive; using both exits with code 64.
- Errors like missing keys or versions exit with code 1 and a helpful message.
- `$VISUAL`/`$EDITOR` is respected for `--edit` (defaults to `nano` on Unix, `notepad` on Windows).

---

## Usage (Library)

```python
from promptorium.services import PromptService
from promptorium.storage.fs import FileSystemPromptStorage
from promptorium.util.repo_root import find_repo_root

storage = FileSystemPromptStorage(find_repo_root())
svc = PromptService(storage)

# Ensure a key exists (create with custom directory or default .prompts)
ref = storage.add_prompt("onboarding", custom_dir=None)

# Write versions
v1 = svc.update_prompt("onboarding", "hello")
v2 = svc.update_prompt("onboarding", "hello world")

# Read latest or specific version
latest_text = svc.load_prompt("onboarding")
v1_text = svc.load_prompt("onboarding", version=1)

# Build an inline diff result (rendered by CLI with rich colors)
res = svc.diff_versions("onboarding", 1, 2, granularity="word")
```

---

## Data Layout & Conventions

- Default-managed keys live at: `.prompts/<key>/<n>.md` (e.g., `.prompts/onboarding/1.md`).
- Custom-managed keys live at: `<custom_dir>/<key>-<n>.md` (e.g., `prompts/system/onboarding-1.md`).
- Metadata file: `.prompts/_meta.json` with schema `1` containing `{ "custom_dirs": { "<key>": "<dir>" } }`.
- Deletion semantics:
  - `prompts delete <key>` removes only the latest version.
  - `prompts delete <key> --all` removes all versions and:
    - For default-managed keys, attempts to remove the now-empty directory.
    - For custom-managed keys, preserves the directory and removes the metadata entry.

---

## Development

Run tests:

```bash
pytest -q
```

Project configuration highlights:

- CLI: [`Typer`](https://typer.tiangolo.com/)
- TUI diff rendering: [`Rich`](https://rich.readthedocs.io/)
- Linting/format: `ruff`
- Type checking: `mypy`

---

## Roadmap

- Additional storage backends (e.g., Git-backed, SQLite)
- Prompt metadata (titles, tags) and search
- Import/export helpers (JSON/YAML)
- Batch operations and partial diffs

---

## Contributing

Contributions are welcome!

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/your-feature`)
3. Install dev deps and run tests
4. Submit a PR with a clear description and rationale

---

## License

Distributed under the MIT License. See `LICENSE` for details.

---

## Acknowledgments

- README structure inspired by the excellent Best-README-Template by Othneil Drew ([link](https://github.com/othneildrew/Best-README-Template?utm_source=chatgpt.com)).

