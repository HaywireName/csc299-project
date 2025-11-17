"""Interactive REPL for task management.
Type commands like:
  add "Write report" [--deadline YYYY-MM-DD]
  list [--json]
  complete 2
  help
  exit | quit

Runs continuously until exit/quit or EOF (Ctrl-D).
"""
from __future__ import annotations

import shlex
import sys
import json
from typing import Any, Dict

from src.lib import dates as dateutil
from src.lib import color as colorutil
from src.services import task_service


PROMPT = "task> "


def _format_task_line(disp_id: int, t: Dict[str, Any], enable_color: bool) -> str:
    deadline = t.get("deadline")
    deadline_date = None
    if deadline:
        try:
            deadline_date = dateutil.parse_iso_date(deadline)
        except Exception:
            deadline_date = None
    rel = dateutil.relative_due_string(deadline_date)
    urg = dateutil.urgency(deadline_date)
    base = f"{disp_id}. {t.get('description')} [{deadline or 'No deadline'}] — {rel}"
    return colorutil.colorize(base, urg, enable_color)


def cmd_add(args: list[str]) -> int:
    # Syntax: add "description" [--deadline YYYY-MM-DD]
    if not args:
        print("Description required", file=sys.stderr)
        return 2
    description_parts = []
    deadline = None
    i = 0
    while i < len(args):
        token = args[i]
        if token == "--deadline":
            if i + 1 >= len(args):
                print("--deadline requires a value", file=sys.stderr)
                return 2
            deadline = args[i + 1]
            i += 2
            continue
        description_parts.append(token)
        i += 1
    description = " ".join(description_parts).strip()
    if not description:
        print("Empty description", file=sys.stderr)
        return 2
    try:
        t = task_service.add_task(description, deadline)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2
    print(f"Added: {t.description} [deadline {t.deadline or 'No deadline'}]")
    return 0


def cmd_list(args: list[str]) -> int:
    json_mode = False
    for a in args:
        if a == "--json":
            json_mode = True
        else:
            print(f"Unknown argument for list: {a}", file=sys.stderr)
            return 2
    tasks = task_service.list_tasks()
    if json_mode:
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
        return 0
    if not tasks:
        print("No tasks found")
        return 0
    enable_color = colorutil.supports_color()
    for disp_id, t in tasks:
        print(_format_task_line(disp_id, t, enable_color))
    return 0


def cmd_complete(args: list[str]) -> int:
    if len(args) != 1:
        print("complete requires exactly one id", file=sys.stderr)
        return 2
    try:
        disp_id = int(args[0])
    except ValueError:
        print("id must be an integer", file=sys.stderr)
        return 2
    try:
        t = task_service.complete_task(disp_id)
    except KeyError:
        print(f"Task not found: {disp_id}", file=sys.stderr)
        return 3
    print(f"Task completed: {t.get('description')}")
    return 0


def cmd_help(_: list[str]) -> int:
    print(
        """Commands:\n  add <description> [--deadline YYYY-MM-DD]\n  list [--json]\n  complete <display_id>\n  help | ?\n  exit | quit (or Ctrl-D)\n"""
    )
    return 0


COMMANDS = {
    "add": cmd_add,
    "list": cmd_list,
    "complete": cmd_complete,
    "help": cmd_help,
    "?": cmd_help,
}


def dispatch(line: str) -> int:
    try:
        tokens = shlex.split(line)
    except ValueError as e:
        print(f"Parse error: {e}", file=sys.stderr)
        return 2
    if not tokens:
        return 0
    cmd, *args = tokens
    if cmd in ("exit", "quit"):
        return 99  # sentinel to exit loop
    handler = COMMANDS.get(cmd)
    if not handler:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        return 2
    return handler(args)


def main(argv: list[str] | None = None) -> int:
    # Ignore argv; REPL mode only
    print("Task REPL. Type 'help' for commands. Ctrl-D to exit.")
    while True:
        try:
            line = input(PROMPT)
        except EOFError:
            print()  # newline on exit
            break
        code = dispatch(line)
        if code == 99:
            break
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
