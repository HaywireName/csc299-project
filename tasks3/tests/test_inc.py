from __future__ import annotations

from pathlib import Path
import importlib.util
import types
from typing import Tuple

import pytest

from tasks3 import inc


def load_task_module() -> types.ModuleType:
    """Dynamically load the CLI module at tasks3/task.py for testing."""
    base_dir = Path(__file__).resolve().parents[1]
    task_path = base_dir / "task.py"
    spec = importlib.util.spec_from_file_location("task_cli", task_path)
    assert spec and spec.loader, "Failed to load task.py"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[assignment]
    return module


@pytest.fixture()
def cli(tmp_path: Path):
    """Provide a fresh TodoApp and parser using a temporary JSON file."""
    task = load_task_module()
    data_file = tmp_path / "tasks.json"
    app = task.TodoApp(data_file=str(data_file))
    parser = task.build_parser()
    return task, app, parser


def test_inc():
    # Keep the simple increment test from the template
    assert inc(5) == 6


def test_add(cli):
    task, app, _ = cli
    app.add_todo("Buy groceries", "milk, eggs, bread")
    assert len(app.todos) == 1
    t = app.todos[0]
    assert t["title"] == "Buy groceries"
    assert t["description"] == "milk, eggs, bread"
    assert t["completed"] is False


def test_list(cli, capsys):
    task, app, _ = cli
    app.add_todo("Alpha")
    app.add_todo("Bravo")
    app.list_todos()  # incomplete only
    out = capsys.readouterr().out
    assert "ID" in out and "Status" in out and "Total" in out
    # Show all should include the same two tasks
    app.list_todos(show_all=True)
    out = capsys.readouterr().out
    assert "Alpha" in out and "Bravo" in out


def test_search(cli, capsys):
    task, app, _ = cli
    app.add_todo("Buy groceries", "milk, eggs, bread")
    app.add_todo("Write docs")
    app.search_todos("groceries")
    out = capsys.readouterr().out
    assert "Found 1 task" in out
    assert "Buy groceries" in out


def test_complete(cli):
    task, app, _ = cli
    app.add_todo("Task A")
    app.add_todo("Task B")
    # Complete display ID 1 (Task A)
    app.complete_todo(1)
    assert sum(1 for t in app.todos if t["completed"]) == 1


def test_delete(cli):
    task, app, _ = cli
    app.add_todo("One")
    app.add_todo("Two")
    app.add_todo("Three")
    # Delete display ID 2 (Two)
    app.delete_todo(2)
    titles = [t["title"] for t in app.todos]
    assert titles == ["One", "Three"]


def test_delete_all(cli):
    task, app, parser = cli
    # Seed some tasks
    app.add_todo("X")
    app.add_todo("Y")
    # Exercise the CLI dispatch path for --all
    args = parser.parse_args(["delete", "--all"])  # type: ignore[arg-type]
    task.dispatch_command(app, args)
    assert app.todos == []


def test_clean(cli):
    task, app, parser = cli
    app.add_todo("Keep me")
    app.add_todo("Done")
    # Mark second as completed via API
    app.complete_todo(2)  # completes display id 2
    # Clean completed tasks via dispatch
    args = parser.parse_args(["clean"])  # type: ignore[arg-type]
    task.dispatch_command(app, args)
    assert len(app.todos) == 1
    assert app.todos[0]["title"] == "Keep me"

