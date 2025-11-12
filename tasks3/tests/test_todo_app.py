import importlib.util
import pathlib
import json
from datetime import datetime

import pytest


def load_task_module():
    """Dynamically load the tasks2/task.py module and return it."""
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    task_path = repo_root / 'tasks2' / 'task.py'
    spec = importlib.util.spec_from_file_location('task_module', str(task_path))
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader, f"Could not load spec from {task_path}"
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


@pytest.fixture()
def Todo(tmp_path):
    """Fixture returning a fresh TodoApp bound to a temp JSON file."""
    m = load_task_module()
    data_file = tmp_path / 'tasks.json'
    app = m.TodoApp(data_file=str(data_file))
    return app


def test_add_and_persist(Todo, tmp_path):
    Todo.add_todo('Task A', 'desc')
    Todo.add_todo('Task B')

    # Validate in-memory state
    assert len(Todo.todos) == 2
    assert Todo.todos[0]['title'] == 'Task A'

    # Validate persisted JSON
    data = json.loads(tmp_path.joinpath('tasks.json').read_text())
    assert len(data) == 2
    assert data[1]['title'] == 'Task B'


def test_complete_multiple_two_pass(Todo):
    for i in range(1, 6):
        Todo.add_todo(f'Task {i}')

    # Complete display IDs 2, 3, and 4 in one call
    Todo.complete_todos([2, 3, 4])

    # Incomplete should be 1 and 5
    incompletes = [t['title'] for t in Todo.todos if not t['completed']]
    completes = [t['title'] for t in Todo.todos if t['completed']]

    assert incompletes == ['Task 1', 'Task 5']
    assert set(completes) == {'Task 2', 'Task 3', 'Task 4'}


def test_delete_multiple_two_pass(Todo):
    for i in range(1, 6):
        Todo.add_todo(f'D{i}')

    # Delete display IDs 1, 3, and 5 in one call
    Todo.delete_todos([1, 3, 5], show_all=False)

    remaining = [t['title'] for t in Todo.todos]
    # Expect D2 and D4 to remain
    assert remaining == ['D2', 'D4']


def test_delete_show_all_respects_mapping(Todo):
    # Create three, complete the middle one
    Todo.add_todo('A')
    Todo.add_todo('B')
    Todo.add_todo('C')

    Todo.complete_todos([2])  # complete B

    # In --all view, display IDs: [A, C, B]
    # Delete B by its display ID in --all (which should be 3)
    Todo.delete_todos([3], show_all=True)

    titles = [t['title'] for t in Todo.todos]
    assert titles == ['A', 'C']
