from __future__ import annotations

import uuid
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from src.lib import storage
from src.lib import dates as dateutil
from src.models.task import Task


def add_task(description: str, deadline_iso: Optional[str]) -> Task:
    description = description.strip()
    if not description:
        raise ValueError("Description cannot be empty")
    if deadline_iso is not None:
        # Validate ISO date format strictly
        try:
            dateutil.parse_iso_date(deadline_iso)
        except Exception as e:
            raise ValueError("Invalid deadline format. Use YYYY-MM-DD.") from e

    t = Task(
        id=str(uuid.uuid4()),
        description=description,
        deadline=deadline_iso,
        created_at=dateutil.now_iso_utc(),
        completed=False,
    )
    tasks = storage.load_tasks()
    tasks.append(asdict(t))
    storage.save_tasks(tasks)
    return t


def _sorted_with_display(tasks: List[Dict[str, Any]]) -> List[Tuple[int, Dict[str, Any]]]:
    # Sort: deadlines first; by deadline asc; within same day by created_at asc; then tasks without deadlines
    enriched = []
    for t in tasks:
        deadline = None
        if t.get("deadline"):
            try:
                deadline = dateutil.parse_iso_date(t["deadline"])  # type: ignore[arg-type]
            except Exception:
                deadline = None
        created = dateutil.parse_created_at(t.get("created_at"))
        enriched.append((deadline, created, t))
    enriched.sort(key=lambda x: dateutil.sort_key(x[0], x[1]))
    # Assign display ids 1..N
    with_ids: List[Tuple[int, Dict[str, Any]]] = []
    for idx, (_, __, t) in enumerate(enriched, start=1):
        with_ids.append((idx, t))
    return with_ids


def list_tasks() -> List[Tuple[int, Dict[str, Any]]]:
    tasks = storage.load_tasks()
    return _sorted_with_display(tasks)


def complete_task(display_id: int) -> Dict[str, Any]:
    with_ids = list_tasks()
    mapping = {disp_id: t for disp_id, t in with_ids}
    if display_id not in mapping:
        raise KeyError(display_id)
    target = mapping[display_id]
    # Remove from storage by internal id
    tasks = storage.load_tasks()
    tasks = [t for t in tasks if t.get("id") != target.get("id")]
    storage.save_tasks(tasks)
    return target
