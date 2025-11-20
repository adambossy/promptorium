# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2025-11-20

### Changed
- Improved error message when adding a prompt with an existing key:
  - Now includes guidance on how to resolve the conflict.
  - Shows the directory where the existing prompt is stored.

## [0.1.1] - 2025-11-18

### Added
- Keywords to `pyproject.toml` for better PyPI discoverability
- Repository URL in project metadata
- MIT License file (`LICENSE`)
- Changelog file (`CHANGELOG.md`)

## [0.1.0] - 2025-11-18

### Added
- CLI tool (`prompts`) for managing versioned prompts
- Library API (`promptorium.load_prompt`) for loading prompts in code
- Versioned prompt storage with Markdown files
  - Default-managed prompts: `.prompts/<key>/<n>.md`
  - Custom-managed prompts: `<custom_dir>/<key>-<n>.md`
- Human-friendly key generation and validation (lowercase slug format)
- Multiple input methods for prompt updates:
  - From file (`--file`)
  - From STDIN
  - From editor (`--edit`, respects `$VISUAL`/`$EDITOR`)
- Prompt version management:
  - Add new prompts with optional custom directory
  - Update prompts to create new versions
  - List all prompts and versions
  - Load specific versions or latest version
  - Delete latest version or all versions (`--all`)
- Diff functionality with granularity options:
  - Word-level diffs
  - Character-level diffs
  - Colorized output using Rich
- Repository-root detection (works anywhere inside project tree)
- Safe, atomic file writes to prevent partial files
- Filesystem-based storage backend with metadata management
- Type hints throughout the codebase (`py.typed` marker included)

[0.1.2]: https://github.com/adambossy/promptorium-python/releases/tag/v0.1.2
[0.1.1]: https://github.com/adambossy/promptorium-python/releases/tag/v0.1.1
[0.1.0]: https://github.com/adambossy/promptorium-python/releases/tag/v0.1.0

