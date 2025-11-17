from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    id: str
    description: str
    deadline: Optional[str]  # ISO date YYYY-MM-DD or None
    created_at: str  # ISO timestamp UTC
    completed: bool = False
