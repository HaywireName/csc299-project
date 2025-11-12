from __future__ import annotations

from pathlib import Path
import importlib.util as _import_util
from typing import Optional as _Optional


def inc(n: int) -> int:
    return n + 1


def _load_cli_module():
    """Load the repository-local CLI module (task.py) and return it.

    This keeps task.py as the single source of truth for the CLI implementation
    while allowing the package entry point `tasks3:main` to invoke it.
    """
    # __file__ = .../tasks3/src/tasks3/__init__.py
    # project root (containing task.py) is two levels up from 'src/tasks3'
    # parents[0] = .../src/tasks3, parents[1] = .../src, parents[2] = .../tasks3
    project_root = Path(__file__).resolve().parents[2]
    cli_path = project_root / "task.py"
    if not cli_path.exists():
        raise FileNotFoundError(f"Could not find CLI script at {cli_path}")

    spec = _import_util.spec_from_file_location("tasks3_cli", str(cli_path))
    if not spec or not spec.loader:
        raise RuntimeError("Failed to create import spec for CLI module")
    module = _import_util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[arg-type]
    return module


def main() -> None:
    """Package entry point used by the `tasks3` console script.

    Delegates to the CLI main defined in task.py so `uv run tasks3` works.
    """
    cli = _load_cli_module()
    # Call the CLI's main function; it will read sys.argv and run accordingly
    if hasattr(cli, "main") and callable(cli.main):  # type: ignore[attr-defined]
        cli.main()  # type: ignore[attr-defined]
    else:
        raise AttributeError("Loaded CLI module has no callable 'main' function")

