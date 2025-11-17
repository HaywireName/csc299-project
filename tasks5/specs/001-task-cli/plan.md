# Implementation Plan: Task Management CLI

**Branch**: `001-task-cli` | **Date**: 2025-11-17 | **Spec**: ./spec.md
**Input**: Feature specification from `/specs/001-task-cli/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a simple, clear CLI to add, list, and complete tasks stored in a local JSON file `.tasks.json` in the current working directory. Tasks have optional deadlines; list output is sorted by deadline (soonest first), with tasks without deadlines displayed last. Urgency is shown via colors: red (overdue), yellow (due within 3 days), white (otherwise). The CLI must be logically separate from the storage layer.

Implementation will use Python 3.14+ and uv for project initialization, dependency management, and running scripts. Color output will use a lightweight cross‑platform approach with ANSI codes and colorama for Windows compatibility. Tests will be written with pytest following constitution gates when tests are requested.

## Technical Context

**Language/Version**: Python 3.14+
**Primary Dependencies**: 
- colorama (cross‑platform color support)
- typer or argparse (CLI parsing; default: argparse to minimize deps)
- python-dateutil (robust date parsing) — if we stick to strict ISO input, this can be avoided

**Storage**: Local JSON file `.tasks.json` in current working directory (array of task records)
**Testing**: pytest (unit + integration), no tests unless requested by spec (constitution allows optional tests when not required)
**Target Platform**: macOS/Linux/Windows terminals
**Project Type**: single project (CLI tool)
**Performance Goals**: 
- List under 1s for up to 1,000 tasks
- Complete/add operations under 2s
**Constraints**:
- Simple, dependency‑light; clarity over cleverness
- Text I/O: stdout for data, stderr for errors; exit code 0 on success, non‑zero on failure
**Scale/Scope**: Single‑user local only; no networking; no concurrency guarantees beyond single process

## Constitution Check

Must pass prior to implementation:
- Clarity & Simplicity (NON‑NEGOTIABLE):
  - Single responsibility functions; low cyclomatic complexity
  - Boring, explicit code; descriptive names
- Code Quality Standards (NON‑NEGOTIABLE):
  - Linting/formatting configured (ruff/black optional via uv extras)
  - Type hints added for public functions
  - Code review prior to merge
  - User documentation complete and up‑to‑date before merge to master
- Testing Standards (NON‑NEGOTIABLE when tests requested):
  - Red‑Green‑Refactor; deterministic and independent tests
  - Contract tests for CLI commands if tests are part of scope
- User Experience Consistency (NON‑NEGOTIABLE):
  - CLI I/O: args/stdin → stdout; errors → stderr
  - JSON and human‑readable outputs where applicable (list default is human‑readable; `--json` optional flag)
  - Color coding: red overdue, yellow ≤3 days, white otherwise; graceful no‑color fallback

Status: All gates can be satisfied with the plan above. No violations anticipated.

## Project Structure

### Documentation (this feature)

```text
specs/001-task-cli/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── cli/
│   └── main.py          # Entry point (argparse or Typer commands)
├── models/
│   └── task.py          # Task dataclass (description, deadline, created_at)
├── services/
│   └── task_service.py  # Add/list/complete logic (pure, no I/O)
└── lib/
    ├── storage.py       # JSON read/write (.tasks.json path handling)
    ├── color.py         # Color decisions + ANSI codes
    └── dates.py         # Date parsing/formatting, urgency calc

tests/
├── contract/
│   └── test_cli_contract.py
├── integration/
│   └── test_end_to_end.py
└── unit/
    ├── test_task_service.py
    ├── test_storage.py
    └── test_dates.py
```

**Structure Decision**: Single project layout with explicit separation:
- `src/cli` only parses args and formats output
- `src/lib/storage.py` owns file I/O; no CLI logic
- `src/services` contains business operations (pure functions)
- Utilities (`color.py`, `dates.py`) isolate presentation and time logic, simplifying tests

## Complexity Tracking

No constitution violations expected. If Typer is adopted instead of argparse, justify as improved DX with minimal complexity; otherwise stay stdlib.
