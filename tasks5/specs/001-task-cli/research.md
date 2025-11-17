# Research: Task Management CLI (Phase 0)

## Goals
- Validate simple architecture: CLI parsing → services → storage
- Decide on CLI parsing library and color handling
- Confirm JSON schema for `.tasks.json`

## CLI Parsing Options
- argparse (stdlib):
  - Pros: zero extra dependency, simple
  - Cons: less ergonomic subcommands, more boilerplate
- Typer (optional):
  - Pros: clean subcommands, type hints, great DX
  - Cons: extra dependency

Decision: Start with argparse to keep dependencies minimal per constitution's simplicity principle. We can swap to Typer later without changing storage/services.

## Color Output
- ANSI escape codes work on Unix/macOS by default
- Windows requires enabling VT mode or using colorama
- Libraries:
  - colorama: lightweight, enables ANSI handling on Windows
  - rich: powerful formatting, heavier dependency

Decision: Use colorama for cross‑platform safety; emit simple ANSI colors only when stdout is a TTY; fallback to plain text when redirected.

## Dates & Deadlines
- Input format: strict ISO `YYYY-MM-DD` (from spec FR-011)
- Compute urgency categories:
  - overdue: deadline < today → red
  - soon: 0 ≤ (deadline - today).days ≤ 3 → yellow
  - later: > 3 days or no deadline → white
- Relative strings: "due in N days", "overdue by N days", "No deadline"

Decision: Use Python stdlib `datetime` (no external parser). Validate strict ISO; give clear error on invalid.

## JSON Storage Schema
- File: `.tasks.json` in CWD
- Content: JSON array of task objects
- Fields per task:
  - id: internal UUID string (persisted) to ensure stable identity across edits (not shown to user)
  - description: string
  - deadline: ISO date string `YYYY-MM-DD` or null
  - created_at: ISO timestamp `YYYY-MM-DDTHH:MM:SSZ`
  - completed: boolean (default false)

Rationale: Display identifiers are computed per listing (1..N); internal UUID ensures safe mutation/deletion.

## Error Handling
- Storage missing: create `.tasks.json` with empty array
- Storage corrupt: back up to `.tasks.json.bak` and recreate empty file; print warning to stderr
- Concurrency: out of scope (single‑process assumption)

## Observability
- Structured logs written to stderr only for errors/warnings
- Keep CLI output clean for users
