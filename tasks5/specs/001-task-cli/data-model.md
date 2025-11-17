# Data Model: Task Management CLI (Phase 1)

## JSON File: `.tasks.json`
- Location: current working directory
- Encoding: UTF-8
- Structure: JSON array of task objects

### Task Object Schema

```json
{
  "id": "uuid-string",              // internal persistent ID (not shown to user)
  "description": "string",          // required, trimmed, 1..1000 chars
  "deadline": "YYYY-MM-DD" | null,  // optional ISO date
  "created_at": "YYYY-MM-DDTHH:MM:SSZ", // ISO 8601 UTC timestamp
  "completed": false                 // boolean, default false
}
```

### Invariants
- `id` is unique across the file
- `description` non-empty after trim; max length 1000
- `deadline` is either null or a valid ISO date string
- `created_at` is set at creation and never modified
- `completed` becomes true when task is completed; completed tasks are removed from file per spec (P3). If we choose to keep history later, we can filter instead of removing.

### Sorting Rules (for list command)
1. Tasks with deadlines first, sorted ascending by `deadline`
2. Tasks without deadlines next, preserving creation order
3. Within same deadline date, secondary sort by `created_at`

### Display Identifier
- Calculated at runtime as 1..N based on sorted order
- Mapped to internal `id` for complete operations

### Validation
- On read: validate array; skip malformed entries with warning to stderr
- On write: atomic write via temp file + replace to avoid corruption
