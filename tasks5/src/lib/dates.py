from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Optional


ISO_DATE_FMT = "%Y-%m-%d"


def parse_iso_date(d: str) -> date:
    return datetime.strptime(d, ISO_DATE_FMT).date()


def today_utc() -> date:
    return datetime.now(timezone.utc).date()


def relative_due_string(deadline: Optional[date], ref: Optional[date] = None) -> str:
    if deadline is None:
        return "No deadline"
    ref_date = ref or today_utc()
    delta = (deadline - ref_date).days
    if delta == 0:
        return "due today"
    if delta > 0:
        return f"due in {delta} day{'s' if delta != 1 else ''}"
    # overdue
    n = abs(delta)
    return f"overdue by {n} day{'s' if n != 1 else ''}"


def urgency(deadline: Optional[date], ref: Optional[date] = None) -> str:
    """Return one of 'overdue', 'soon', 'later', 'none'."""
    if deadline is None:
        return "none"
    ref_date = ref or today_utc()
    delta = (deadline - ref_date).days
    if delta < 0:
        return "overdue"
    if 0 <= delta <= 3:
        return "soon"
    return "later"


def sort_key(deadline: Optional[date], created_at: datetime) -> tuple:
    # Tasks with deadlines first (False sorts before True), then by deadline asc, then created_at asc
    no_deadline = deadline is None
    return (no_deadline, deadline or date.max, created_at)


def parse_created_at(ts: Optional[str]) -> datetime:
    # Expect ISO with Z, e.g., 2025-11-17T10:00:00Z
    if not ts:
        return datetime.now(timezone.utc)
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts)


def now_iso_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
