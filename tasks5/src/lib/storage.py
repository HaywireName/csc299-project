from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, List, Dict


TASKS_FILE_NAME = ".tasks.json"


def tasks_file_path(cwd: str | None = None) -> Path:
    base = Path(cwd) if cwd else Path.cwd()
    return base / TASKS_FILE_NAME


def _atomic_write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=path.parent, encoding="utf-8") as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)
    os.replace(tmp_path, path)


def load_tasks(cwd: str | None = None) -> List[Dict[str, Any]]:
    """Load tasks from .tasks.json. Create empty file if missing.
    On JSON error, back up corrupt file and recreate empty file.
    """
    path = tasks_file_path(cwd)
    if not path.exists():
        _atomic_write(path, "[]\n")
        return []
    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text or "[]")
        if isinstance(data, list):
            return data
        # Non-list content -> treat as corrupt
        raise ValueError("Tasks file is not a JSON array")
    except Exception:
        # Backup corrupt file
        try:
            backup = path.with_suffix(path.suffix + ".bak")
            path.replace(backup)
        except Exception:
            pass
        _atomic_write(path, "[]\n")
        return []


def save_tasks(tasks: List[Dict[str, Any]], cwd: str | None = None) -> None:
    path = tasks_file_path(cwd)
    _atomic_write(path, json.dumps(tasks, indent=2, ensure_ascii=False) + "\n")
