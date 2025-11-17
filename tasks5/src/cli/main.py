from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

from src.lib import color as colorutil
from src.lib import dates as dateutil
from src.services import task_service


EXIT_OK = 0
EXIT_VALIDATION = 2
EXIT_NOT_FOUND = 3


def cmd_add(args: argparse.Namespace) -> int:
    try:
        t = task_service.add_task(args.description, args.deadline)
        deadline_str = t.deadline if t.deadline else "No deadline"
        print(f"Added: {t.description} [deadline {deadline_str}]")
        return EXIT_OK
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return EXIT_VALIDATION


def _format_task_line(disp_id: int, t: Dict[str, Any], enable_color: bool) -> str:
    deadline = t.get("deadline")
    deadline_date = None
    if deadline:
        try:
            deadline_date = dateutil.parse_iso_date(deadline)
        except Exception:
            # Treat invalid stored date as no deadline for display safety
            deadline_date = None
    rel = dateutil.relative_due_string(deadline_date)
    urg = dateutil.urgency(deadline_date)
    base = f"{disp_id}. {t.get('description')} [{deadline or 'No deadline'}] — {rel}"
    return colorutil.colorize(base, urg, enable_color)


def cmd_list(args: argparse.Namespace) -> int:
    tasks = task_service.list_tasks()
    if args.json:
        # JSON output without ANSI codes
        out = []
        for disp_id, t in tasks:
            deadline = t.get("deadline")
            deadline_date = None
            if deadline:
                try:
                    deadline_date = dateutil.parse_iso_date(deadline)
                except Exception:
                    deadline_date = None
            out.append(
                {
                    "id": disp_id,
                    "description": t.get("description"),
                    "deadline": deadline if deadline else None,
                    "created_at": t.get("created_at"),
                    "relative": dateutil.relative_due_string(deadline_date),
                    "urgency": dateutil.urgency(deadline_date),
                }
            )
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return EXIT_OK

    if not tasks:
        print("No tasks found")
        return EXIT_OK
    enable_color = colorutil.supports_color() and not args.json
    for disp_id, t in tasks:
        print(_format_task_line(disp_id, t, enable_color))
    return EXIT_OK


def cmd_complete(args: argparse.Namespace) -> int:
    try:
        t = task_service.complete_task(args.id)
        print(f"Task completed: {t.get('description')}")
        return EXIT_OK
    except KeyError:
        print(f"Task not found: {args.id}", file=sys.stderr)
        return EXIT_NOT_FOUND


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="task-cli")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("description", type=str, help="Task description")
    p_add.add_argument("--deadline", type=str, help="Deadline YYYY-MM-DD", default=None)
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="List tasks")
    p_list.add_argument("--json", action="store_true", help="Output as JSON")
    p_list.set_defaults(func=cmd_list)

    p_complete = sub.add_parser("complete", help="Complete a task by display id")
    p_complete.add_argument("id", type=int, help="Display id from list output")
    p_complete.set_defaults(func=cmd_complete)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)  # type: ignore[misc]


if __name__ == "__main__":
    raise SystemExit(main())
