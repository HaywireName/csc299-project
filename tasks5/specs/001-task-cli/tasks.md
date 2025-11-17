# Tasks: Task Management CLI

**Input**: Design documents from `/specs/001-task-cli/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL for this feature (spec does not explicitly require them). Include tests only if capacity allows; they should follow the constitution’s test standards when added.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create Python project structure per plan in `src/` and `tests/`
- [ ] T002 Initialize uv project and dependencies (colorama, pytest as dev, optional lint/format) at repo root
- [ ] T003 [P] Configure basic tooling docs in `specs/001-task-cli/quickstart.md` (ensure commands match actual entrypoints)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 [P] Create `src/models/task.py` with Task dataclass (id, description, deadline, created_at, completed)
- [ ] T005 [P] Implement `src/lib/storage.py` for `.tasks.json` read/write (atomic writes, missing/corrupt handling)
- [ ] T006 [P] Implement `src/lib/dates.py` for ISO date parsing, relative string formatting, and urgency classification
- [ ] T007 [P] Implement `src/lib/color.py` for urgency → ANSI color mapping, with TTY detection and no-color fallback
- [ ] T008 Define CLI contract in `specs/001-task-cli/contracts/cli.md` (ensure options/flags are final)
- [ ] T009 Wire minimal CLI entry `src/cli/main.py` with argparse skeleton (subcommands add/list/complete, no behavior yet)

**Checkpoint**: Foundation ready – CLI can parse commands and helpers exist for storage, dates, and colors (even if not fully wired).

---

## Phase 3: User Story 1 - Add Tasks with Deadlines (Priority: P1) 🎯 MVP

**Goal**: Users can add tasks (with optional deadlines) saved to `.tasks.json` in the current directory.

**Independent Test**: Running `add` writes valid task entries to `.tasks.json` and they persist across runs.

### Implementation for User Story 1

- [ ] T010 [US1] Implement `add_task` service in `src/services/task_service.py` (pure function using storage API)
- [ ] T011 [US1] Update `src/lib/storage.py` to append new tasks with generated UUID `id`, current `created_at`, and optional `deadline`
- [ ] T012 [US1] Implement CLI `add` command in `src/cli/main.py` to parse description and optional `--deadline` and call `add_task`
- [ ] T013 [US1] Validate description (non-empty, trimmed, length limit) and deadline format (ISO) with clear error messages (stderr + non-zero exit)
- [ ] T014 [US1] Ensure `.tasks.json` is created when missing and initialized with empty array
- [ ] T015 [US1] Update user docs in `specs/001-task-cli/quickstart.md` for `add` usage and examples

**Checkpoint**: `task-cli add` (via uv run/module) can reliably create and persist tasks.

---

## Phase 4: User Story 2 - List Tasks Sorted by Deadline with Color Coding (Priority: P2)

**Goal**: Users can list tasks sorted by deadline with color-coded urgency and optional JSON output.

**Independent Test**: Adding several tasks then running `list` shows them in the correct order with correct colors and JSON when requested.

### Implementation for User Story 2

- [ ] T020 [US2] Implement `list_tasks` service in `src/services/task_service.py` to load tasks from storage and return sorted domain objects
- [ ] T021 [US2] Implement sorting logic (deadline first, then created_at; tasks without deadlines last) using `src/lib/dates.py`
- [ ] T022 [US2] Generate display IDs (1..N) mapped to internal `id` in `list_tasks`
- [ ] T023 [US2] Use `src/lib/dates.py` to compute relative strings (e.g., "due in 2 days", "overdue by 1 day", "No deadline")
- [ ] T024 [US2] Use `src/lib/color.py` to map urgency categories to ANSI color codes (red/yellow/white) when stdout is TTY
- [ ] T025 [US2] Implement CLI `list` command in `src/cli/main.py` for human-readable output matching contract (id, description, deadline/No deadline, relative)
- [ ] T026 [US2] Implement `--json` flag on `list` to emit array of objects (id, description, deadline|null, created_at, relative, urgency) without ANSI codes
- [ ] T027 [US2] Handle empty list by printing "No tasks found" to stdout and exit code 0
- [ ] T028 [US2] Document `list` behavior and examples (human + JSON) in `specs/001-task-cli/quickstart.md`

**Checkpoint**: `task-cli list` presents tasks clearly, sorted and color-coded, and supports JSON output.

---

## Phase 5: User Story 3 - Complete Finished Tasks (Priority: P3)

**Goal**: Users can mark tasks as complete by display id, removing them from the active list.

**Independent Test**: Adding tasks, listing them, then running `complete <id>` removes the correct task and confirms completion.

### Implementation for User Story 3

- [ ] T030 [US3] Extend `list_tasks` service or add helper to map display id → internal UUID
- [ ] T031 [US3] Implement `complete_task` service in `src/services/task_service.py` that removes (or marks completed and filters out) the selected task and writes updated list via storage
- [ ] T032 [US3] Implement CLI `complete` command in `src/cli/main.py` that accepts display id, resolves to internal id, and calls `complete_task`
- [ ] T033 [US3] Ensure successful completion prints `Task completed: <description>` to stdout and returns exit code 0
- [ ] T034 [US3] Ensure unknown id prints `Task not found: <id>` to stderr and returns specific non-zero exit code (per contract)
- [ ] T035 [US3] Update `specs/001-task-cli/quickstart.md` with `complete` usage and examples

**Checkpoint**: `task-cli complete` reliably removes tasks and provides clear feedback.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T040 [P] Add type hints across `src/` and enable basic type checking (e.g., `python -m compileall` or mypy if added)
- [ ] T041 Code cleanup and refactoring for clarity and duplication removal
- [ ] T042 [P] Optional unit tests for services (`tests/unit/test_task_service.py`, `test_dates.py`, `test_storage.py`) if capacity allows
- [ ] T043 [P] Optional contract/integration test for CLI (`tests/contract/test_cli_contract.py`, `tests/integration/test_end_to_end.py`) using subprocess with uv
- [ ] T044 [P] Run through `specs/001-task-cli/quickstart.md` step-by-step to validate documentation and commands
- [ ] T045 Ensure user documentation is complete and up-to-date before merging to master (constitution requirement)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Uses same storage and services but is independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on `list` behavior to interpret display ids but is independently testable via add+list+complete flow

### Within Each User Story

- Optional tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before CLI wiring
- Core implementation before integration/polish
- Story complete before moving to next priority (for sequential delivery)

### Parallel Opportunities

- Setup tasks marked [P] can run in parallel
- Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational completes, User Stories 1–3 can proceed in parallel if team capacity allows
- Optional tests marked [P] can be developed in parallel with non-dependent code

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Manually test `add` behavior and `.tasks.json` contents
5. Demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Demo
3. Add User Story 2 → Test independently → Demo (shows sorting + colors)
4. Add User Story 3 → Test independently → Demo (shows full flow add/list/complete)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (add)
   - Developer B: User Story 2 (list + colors + JSON)
   - Developer C: User Story 3 (complete)
3. Stories complete and integrate independently
