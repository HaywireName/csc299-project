# CLI Contract (Phase 1)

All commands follow text I/O conventions: data to stdout, errors to stderr. Exit code 0 on success; non-zero on failure.

## Commands

### add
- Description: Add a new task with description and optional deadline
- Usage: `task-cli add "<description>" [--deadline YYYY-MM-DD]`
- Input:
  - description: required string
  - --deadline: optional ISO date
- Output (stdout): confirmation message `Added: <description> [deadline <date>|No deadline]`
- Errors (stderr): invalid date format, empty description
- Exit codes: 0 on success; 2 on validation error

### list
- Description: List tasks sorted by deadline; color-coded by urgency
- Usage: `task-cli list [--json]`
- Input:
  - --json: optional flag for JSON output
- Output (stdout):
  - Human-readable lines: `<id>. <description> [<deadline|No deadline>] — <relative>`
    - Colors:
      - red: overdue (deadline < today)
      - yellow: due within 3 days (inclusive)
      - white: other or no deadline
  - JSON mode: array of task objects with fields {id (display int), description, deadline|null, created_at}
- Errors (stderr): none (empty state prints "No tasks found")
- Exit codes: 0 success

### complete
- Description: Mark a task complete by its display identifier and remove it
- Usage: `task-cli complete <id>`
- Input:
  - id: required integer (display id from `list`)
- Output (stdout): `Task completed: <description>`
- Errors (stderr): `Task not found: <id>`
- Exit codes: 0 success; 3 not found

## File Behavior
- Storage file: `.tasks.json` in current working directory
- On missing file: create with empty array
- On corruption: write backup `.tasks.json.bak` and recreate empty file (warn)

## Color Behavior
- Apply colors only when stdout is a TTY
- No-color terminals or `--json` mode: no ANSI codes

## JSON Output Schema (list --json)
```json
[
  {
    "id": 1,
    "description": "Write report",
    "deadline": "2025-11-20",
    "created_at": "2025-11-17T10:00:00Z",
    "relative": "due in 3 days",
    "urgency": "overdue|soon|later|none"
  }
]
```
