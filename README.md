# Promptorium

CLI + library for managing versioned prompts.

## Setup

```bash
uv venv --python 3.12
source .venv/bin/activate
uv sync --extra dev
uv run pre-commit install
```

## Usage

```bash
prompts add --key onboarding --dir prompts/system
prompts update onboarding --file docs/onboarding_v1.md
prompts update onboarding --edit
prompts list
prompts diff onboarding 1 2
prompts load onboarding
prompts delete onboarding --all
```
