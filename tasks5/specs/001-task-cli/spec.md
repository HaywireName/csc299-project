# Feature Specification: Task Management CLI

**Feature Branch**: `001-task-cli`  
**Created**: 2025-11-17  
**Status**: Draft  
**Input**: User description: "This project should allow storage of a list of tasks given from a CLI to add, list, and remove tasks, as well as assign deadlines to the tasks. The tasks should be stored locally in a file, and sorted from soonest deadline to furthest deadline. Make sure that the CLI component is logically separate from the task storage component."

## Clarifications

### Session 2025-11-17

- Q: How should tasks be visually differentiated based on urgency? → A: Color-coded by deadline - overdue tasks in red, tasks due within 3 days in yellow, all other tasks in white
- Q: Should there be a dedicated command to mark tasks as complete? → A: Yes, a "complete" command should remove finished tasks from the list
- Q: Where should the task storage file be located? → A: Always in current working directory where CLI is executed
- Q: What format should task identifiers use? → A: Sequential, consecutive numbers based on current display order (1, 2, 3...)
- Q: When user doesn't provide a deadline, should the system prompt or use a default? → A: Allow tasks without deadlines, display them last in the list
- Q: What should the storage file be named? → A: `.tasks.json` (hidden file with JSON extension)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add Tasks with Deadlines (Priority: P1)

Users need to capture tasks quickly with deadlines so they can track what needs to be done and when.

**Why this priority**: This is the core value proposition - without the ability to add tasks with deadlines, the system has no purpose. This is the minimum viable product.

**Independent Test**: Can be fully tested by running the add command with a task description and deadline, then verifying the task is stored. Delivers immediate value as users can start tracking their work.

**Acceptance Scenarios**:

1. **Given** no existing tasks, **When** user adds a task "Write report" with deadline "2025-11-20", **Then** the task is stored with the correct description and deadline
2. **Given** existing tasks in the system, **When** user adds a new task "Review code" with deadline "2025-11-18", **Then** the new task is added without affecting existing tasks
3. **Given** user wants to add a task, **When** user provides task description but no deadline, **Then** the task is stored without a deadline
4. **Given** user provides an invalid deadline format, **When** attempting to add task, **Then** system displays clear error message with expected format example

---

### User Story 2 - List Tasks Sorted by Deadline with Color Coding (Priority: P2)

Users need to see all their tasks ordered by urgency with visual color indicators so they can quickly identify which tasks require immediate attention.

**Why this priority**: Once users can add tasks (P1), the next most critical need is viewing them in priority order with clear visual urgency indicators. Color coding enables instant recognition of critical tasks without reading details.

**Independent Test**: Can be tested by adding multiple tasks with different deadlines (overdue, within 3 days, and future), then running the list command and verifying tasks appear in chronological order with correct colors (red for overdue, yellow for due within 3 days, white for others). Delivers value as users can immediately see what's most urgent through both sorting and color.

**Acceptance Scenarios**:

1. **Given** multiple tasks with different deadlines, **When** user lists all tasks, **Then** tasks are displayed sorted by deadline (soonest first) with color coding applied
2. **Given** an overdue task (deadline before today), **When** user lists tasks, **Then** the overdue task is displayed in red color
3. **Given** a task due within 3 days from today, **When** user lists tasks, **Then** the task is displayed in yellow color
4. **Given** a task due more than 3 days from today, **When** user lists tasks, **Then** the task is displayed in white color
5. **Given** tasks with the same deadline, **When** user lists tasks, **Then** tasks with same deadline are displayed in creation order with the same color
6. **Given** tasks without deadlines exist, **When** user lists tasks, **Then** tasks without deadlines are displayed last (after all tasks with deadlines) in white color
7. **Given** no tasks exist, **When** user lists tasks, **Then** system displays a friendly message like "No tasks found"
8. **Given** tasks are listed, **When** display is shown, **Then** each task shows description, deadline (or "No deadline"), and relative time (e.g., "due in 2 days", "overdue by 1 day") with appropriate color

---

### User Story 3 - Complete Finished Tasks (Priority: P3)

Users need to mark tasks as complete and remove them from the active list, keeping their task list manageable and focused on remaining work.

**Why this priority**: While important for maintenance, users can still get value from adding and viewing tasks even without completion tracking. This can be added after core functionality is proven.

**Independent Test**: Can be tested by adding tasks, listing them to get identifiers, then marking specific tasks as complete and verifying they no longer appear in the list. Delivers value by preventing task list bloat and providing a sense of accomplishment.

**Acceptance Scenarios**:

1. **Given** existing tasks in the list, **When** user completes a task by its identifier, **Then** the task is permanently removed from storage
2. **Given** user attempts to complete a non-existent task, **When** complete command is executed, **Then** system displays clear error message indicating task not found
3. **Given** multiple tasks exist, **When** user completes one task, **Then** only that task is removed and others remain unchanged
4. **Given** user completes the last task, **When** listing tasks, **Then** system displays "No tasks found" message
5. **Given** user completes a task, **When** completion is successful, **Then** system displays confirmation message (e.g., "Task completed: Write report")

---

### Edge Cases

- What happens when storage file is corrupted or contains invalid data?
- How does system handle extremely long task descriptions (e.g., 10,000 characters)?
- What happens when deadline date is in the past when task is added?
- How does system behave with thousands of tasks (performance considerations)?
- What happens when storage file is locked by another process?
- How does system handle special characters or emojis in task descriptions?
- What if user tries to add duplicate tasks (same description and deadline)?
- How does system handle concurrent access (multiple CLI instances running)?
- What happens when terminal doesn't support color output (e.g., redirected to file or non-color terminal)?
- How does system handle tasks due exactly 3 days from today (boundary case for yellow vs white color)?
- What happens when system clock changes or timezone differs between CLI invocations?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a command to add a new task with description and optional deadline
- **FR-002**: System MUST store tasks persistently in a file named `.tasks.json` in the current working directory between CLI sessions
- **FR-003**: System MUST provide a command to list all tasks sorted by deadline (soonest first), with tasks without deadlines displayed last
- **FR-004**: System MUST provide a command to complete a task by identifier, removing it from the list
- **FR-005**: System MUST maintain logical separation between CLI interface and storage operations
- **FR-006**: System MUST display tasks with human-readable relative time indicators (e.g., "due in 3 days", "overdue by 1 day")
- **FR-007**: System MUST validate deadline format and provide clear error messages for invalid input
- **FR-008**: System MUST handle missing or corrupted `.tasks.json` files gracefully (create new file if needed)
- **FR-009**: System MUST assign sequential numeric identifiers (1, 2, 3...) to tasks based on their display order for completion operations
- **FR-010**: System MUST preserve task order by deadline when adding, completing, or listing tasks
- **FR-011**: System MUST support standard date formats (ISO 8601 recommended: YYYY-MM-DD)
- **FR-012**: System MUST display appropriate messages when no tasks exist
- **FR-013**: System MUST provide usage help information when invoked incorrectly or with --help flag
- **FR-014**: System MUST display tasks with color coding based on urgency: red for overdue tasks, yellow for tasks due within 3 days, white for all other tasks
- **FR-015**: System MUST calculate urgency based on current date when list command is executed
- **FR-016**: System MUST handle terminals that don't support color output gracefully (fallback to plain text)
- **FR-017**: System MUST display confirmation message when a task is successfully completed
- **FR-018**: System MUST display sequential numeric identifiers (starting at 1) next to each task when listing
- **FR-019**: System MUST allow tasks to be created without deadlines (deadline is optional)
- **FR-020**: System MUST display "No deadline" or similar indicator for tasks without deadlines

### Key Entities

- **Task**: Represents a single item to be completed
  - Display identifier (sequential number 1, 2, 3... based on sorted order, recalculated each time list is displayed)
  - Description (text summary of what needs to be done)
  - Deadline (optional date/time when task should be completed; null/empty if not provided)
  - Creation timestamp (for secondary sorting and audit trail)

- **Task Storage**: Manages persistence of tasks
  - Reads tasks from local file
  - Writes tasks to local file
  - Maintains data integrity and handles file errors
  - Independent of CLI interface (logical separation requirement)

### Assumptions

- Storage file is always named `.tasks.json` and located in the current working directory where the CLI is executed (this allows different task lists per directory/project)
- Storage file format is JSON for human-readability and easy debugging
- Hidden file (dot prefix) reduces visual clutter in directory listings
- Single-user system (no multi-user authentication or authorization needed)
- Tasks are personal/local to the user's machine (no cloud sync or sharing)
- Deadlines are optional; when provided, they are date-only (not time-specific) unless otherwise specified
- Tasks without deadlines are valid and useful for capturing ideas or non-time-sensitive work
- System clock is reasonably accurate for relative time calculations and color determination
- Terminal supports UTF-8 for task descriptions
- Users have read/write permissions in the directory where storage file resides
- Most terminals support ANSI color codes, but system will gracefully degrade for non-color terminals
- "Within 3 days" means tasks due in 3 days or fewer from current date (inclusive boundary)
- Tasks without deadlines are displayed in white color (no urgency indicator)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can add a new task with deadline in under 10 seconds (including typing time)
- **SC-002**: Task list displays instantly (under 1 second) for up to 1,000 tasks with color coding applied
- **SC-003**: 95% of users successfully complete their first task addition without referring to documentation
- **SC-004**: System maintains 100% data persistence (no task loss between CLI sessions under normal conditions)
- **SC-005**: Users can identify their most urgent task within 2 seconds of listing tasks (due to clear sorting and color coding)
- **SC-006**: Task completion operations complete in under 2 seconds
- **SC-007**: System handles corrupted storage files gracefully without data loss of recoverable tasks in 90% of corruption scenarios
- **SC-008**: CLI interface and storage components can be tested independently (architectural separation verified)
- **SC-009**: 90% of users can correctly distinguish task urgency levels by color without reading deadline text
- **SC-010**: System correctly applies color coding in 100% of cases when terminal supports colors
