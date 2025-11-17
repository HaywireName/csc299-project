# Quickstart: Task Management CLI (Phase 1)

This project uses Python 3.14+ and `uv` for dependency management and running scripts.

## Prerequisites
- Python 3.14 or newer installed
- `uv` installed: https://docs.astral.sh/uv/

## Setup

```bash
# Initialize project (creates .venv managed by uv if not present)
uv init

# Add runtime dependencies
uv add colorama

# Add dev dependencies (optional)
uv add --dev pytest ruff black
```

## Run

```bash
# Help
uv run python -m src.cli.main --help

# Add a task (with deadline)
uv run python -m src.cli.main add "Write report" --deadline 2025-11-20

# Add a task (without deadline)
uv run python -m src.cli.main add "Plan weekend"

# List tasks (human-readable)
uv run python -m src.cli.main list

# List tasks as JSON
uv run python -m src.cli.main list --json

# Complete a task by display id
uv run python -m src.cli.main complete 2
```

## Tests

```bash
# Run all tests
uv run pytest -q
```

## Notes
- Tasks are stored in `.tasks.json` in the current directory
- Color output appears only in TTY terminals; plain text when redirected
- Exit codes: 0 success; non-zero on errors
