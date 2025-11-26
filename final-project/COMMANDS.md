# COMMANDS.md - Complete Command Reference

This document provides a complete reference for all commands available in PKMS Task Manager.

## Command Structure

Commands are organized by module. At the main menu (`pkms>`), you can only use **Program Commands**. To use module-specific commands, you must first enter the appropriate module.

## Table of Contents

- [Program Commands](#program-commands)
- [Task Module Commands](#task-module-commands)
- [Document Module Commands](#document-module-commands)
- [Chat Module Commands](#chat-module-commands)
- [Agent Module Commands](#agent-module-commands)
- [Settings Module Commands](#settings-module-commands)

---

## Program Commands

These commands work from any module or the main menu.

### `help`

**Description**: Display available commands for current context

**Syntax**:
```
help
```

**Examples**:
```bash
pkms> help
tasks[default]> help
docs> help
```

**Notes**: Shows different commands based on whether you're at main menu or in a module

---

### `status`

**Description**: Display comprehensive usage statistics and program information

**Syntax**:
```
status
```

**Output**:
- Task counts (total, pending, completed, overdue)
- Folder statistics
- Document counts by type (PDFs, DOCX, TXT)
- Storage usage (documents, cache, data, backups)
- API Usage & Costs (current session, previous session, all-time total)
- Backup information

**Examples**:
```bash
pkms> status
```

**Notes**: 
- Replaces the old `stats` command
- Shows color-coded deadline information
- Displays API cost tracking by operation type

---

### `home` / `menu`

**Description**: Return to main menu from any module

**Syntax**:
```
home
menu
```

**Examples**:
```bash
tasks[work]> home
docs> menu
```

---

### `exit` / `quit`

**Description**: Exit the program

**Syntax**:
```
exit
quit
```

**Examples**:
```bash
pkms> exit
```

---

### `backup`

**Description**: Create a manual backup of all data

**Syntax**:
```
backup
```

**Output**: Backup filename and location, file size

**Examples**:
```bash
pkms> backup
# Creates: data/backups/backup_20251124_103045.zip
```

**See Also**: `restore`, `export`

---

### `restore`

**Description**: Restore data from a backup file

**Syntax**:
```
restore [backup_filename]
```

**Arguments**:
- `backup_filename` (optional): Name of backup file to restore

**Behavior**:
- Without arguments: Lists available backups
- With filename: Restores specified backup after confirmation

**Examples**:
```bash
# List backups
pkms> restore

# Restore specific backup
pkms> restore backup_20251124_103045.zip
```

**Warning**: Restoration replaces all current data

**See Also**: `backup`, `import`

---

### `export`

**Description**: Export all data to a ZIP archive

**Syntax**:
```
export
```

**Output**: Creates timestamped ZIP file in `exports/` directory

**Contents**:
- All task data
- All document files and metadata
- Chat history
- Configuration files
- README with export information

**Examples**:
```bash
pkms> export
# Creates: exports/pkms_export_20251124_103045.zip
```

**See Also**: `import`, `backup`

---

### `import`

**Description**: Import data from an export file

**Syntax**:
```
import <export_file>
```

**Arguments**:
- `export_file`: Path to export ZIP file

**Modes**:
- `merge`: Combine with existing data
- `replace`: Replace all current data (creates backup first)

**Examples**:
```bash
pkms> import exports/pkms_export_20251124_103045.zip
pkms> import ~/Downloads/pkms_export.zip
```

**See Also**: `export`, `restore`

---

## Module Entry Commands

### `tasks`

**Description**: Enter tasks module

**Syntax**:
```
tasks
```

**Examples**:
```bash
pkms> tasks
# Prompt changes to: tasks[default]>
```

---

### `docs`

**Description**: Enter documents module

**Syntax**:
```
docs
```

**Examples**:
```bash
pkms> docs
# Prompt changes to: docs>
```

---

### `chat`

**Description**: Enter chat module

**Syntax**:
```
chat
```

**Examples**:
```bash
pkms> chat
# Prompt changes to: chat>
```

---

### `agent`

**Description**: Enter agent module

**Syntax**:
```
agent
```

**Examples**:
```bash
pkms> agent
# Prompt changes to: agent>
```

---

### `settings`

**Description**: Enter settings module

**Syntax**:
```
settings
```

**Examples**:
```bash
pkms> settings
# Prompt changes to: settings>
```

---

## Task Module Commands

First enter the tasks module: `pkms> tasks`

### `add`

**Description**: Create a new task

**Syntax**:
```
add <title> [-p <priority>] [-desc <description>] [-dl <deadline>]
```

**Arguments**:
- `title` (required): Task title (up to 30 characters)
- `-p <priority>` (optional): low, medium, or high (default: medium)
- `-desc <description>` (optional): Detailed description
- `-dl <deadline>` (optional): Due date in various formats

**Deadline Formats**:
- DD-MM-YYYY (e.g., 25-12-2025)
- MM-DD-YYYY (e.g., 12-25-2025)
- MM/DD/YYYY (e.g., 12/25/2025)
- "tomorrow"

**Examples**:
```bash
# Simple task
tasks[default]> add "Buy groceries"

# Task with priority and deadline
tasks[default]> add "Submit report" -p high -dl 2025-12-01

# Task with description
tasks[default]> add "Plan meeting" -desc "Prepare agenda and invite team members"

# Complete task
tasks[default]> add "Finish presentation" -p high -desc "Include Q4 results and projections" -dl tomorrow
```

**See Also**: `edit`, `list`, `view`

---

### `list`

**Description**: Display all tasks in current folder

**Syntax**:
```
list
```

**Output**: Table with ID, Title, Description/Summary, Deadline, Priority

**Task IDs**:
- Pending tasks: Numeric IDs (1, 2, 3...)
- Completed tasks: Letter IDs (a, b, c...)

**Sorting**: 
1. Priority (High → Medium → Low)
2. Deadline (nearest first)
3. Creation date (oldest first)

**Color Coding**:
- 🔴 Red deadline: Overdue
- 🟡 Yellow deadline: Due within 2 days
- Priority: Capitalized (High, Medium, Low)

**Sections**:
- Pending tasks shown first
- Completed tasks in separate section

**Examples**:
```bash
tasks[default]> list
```

**See Also**: `search`, `view`

---

### `view`

**Description**: Display detailed information about a task

**Syntax**:
```
view <task_id>
```

**Arguments**:
- `task_id`: Task ID or partial ID

**Output**: All task fields including ID, title, description, summary, deadline, priority, status, created date

**Examples**:
```bash
tasks[default]> view 1
tasks[default]> view 3a5f
```

**See Also**: `list`, `edit`

---

### `edit`

**Description**: Update task fields

**Syntax**:
```
edit <task_id> [-desc <text>] [-dl <date>] [-p <level>]
```

**Arguments**:
- `task_id` (required): Task ID or partial ID (numeric for pending, letters for completed)
- `-desc <text>` (optional): New description
- `-dl <date>` (optional): New deadline
- `-p <level>` (optional): New priority (low/medium/high or l/m/h)

**Examples**:
```bash
# Update deadline
tasks[default]> edit 1 -dl 2025-12-15

# Update description
tasks[default]> edit 2 -desc New description with more details

# Update multiple fields
tasks[default]> edit 3 -p high -dl tomorrow

# Edit completed task
tasks[default]> edit a -p medium
```

**See Also**: `add`, `view`

---

### `complete`

**Description**: Mark task(s) as completed

**Syntax**:
```
complete <task_id> [task_id ...]
```

**Arguments**:
- `task_id`: One or more task IDs

**Examples**:
```bash
# Complete single task
tasks[default]> complete 1

# Complete multiple tasks
tasks[default]> complete 1 2 3
```

**See Also**: `list`, `remove`

---

### `remove`

**Description**: Delete a task with confirmation

**Syntax**:
```
remove <task_id>
```

**Arguments**:
- `task_id`: Task ID (numeric for pending, letters for completed)

**Confirmation**: Requires "yes" to confirm deletion

**ID Reindexing**: IDs are automatically reindexed after removal

**Examples**:
```bash
# Remove pending task
tasks[default]> remove 1
# Prompt: Delete task 'Task title'? (yes/no):

# Remove completed task
tasks[default]> remove a
# Prompt: Delete task 'Completed task'? (yes/no):
```

**See Also**: `complete`, `list`

---

### `search`

**Description**: Find tasks by keyword

**Syntax**:
```
search <query>
```

**Arguments**:
- `query`: Search term (case-insensitive)

**Search Scope**: Task titles and descriptions

**Examples**:
```bash
tasks[default]> search report
tasks[default]> search urgent meeting
```

**See Also**: `list`, `view`

---

### `summarize`

**Description**: Generate AI summary for task description

**Syntax**:
```
summarize <task_id>
```

**Arguments**:
- `task_id`: Task ID or partial ID

**Requirements**:
- Task must have a description
- Description must be 20+ words
- OpenAI API key required

**Cost**: Uses gpt-4o-mini (~$0.0001 per summary)

**Examples**:
```bash
tasks[default]> summarize 1
```

**See Also**: `view`, `edit`, `cost`

---

### `cost`

**Description**: Show cumulative OpenAI API cost for session

**Syntax**:
```
cost
```

**Output**: Total API cost and pricing breakdown

**Examples**:
```bash
tasks[default]> cost
```

**See Also**: `summarize`

---

### `folders`

**Description**: List all task folders with task counts

**Syntax**:
```
folders
```

**Output**: Folder names with task counts, current folder marked with *

**Examples**:
```bash
tasks[default]> folders
# Output:
# * default (5 tasks)
#   work (3 tasks)
#   personal (2 tasks)
```

**See Also**: `folder`

---

### `folder`

**Description**: Switch to a folder or manage folders

**Syntax**:
```
folder <name>              # Switch to folder
folder -a <name>           # Create new folder
folder -d <name>           # Delete folder
```

**Arguments**:
- `name`: Folder name
- `-a`: Add/create flag
- `-d`: Delete flag

**Examples**:
```bash
# Switch to folder (creates if doesn't exist)
tasks[default]> folder work

# Create new folder explicitly
tasks[default]> folder -a personal

# Delete folder (requires confirmation)
tasks[default]> folder -d old-project
```

**Notes**: Cannot delete the "default" folder

**See Also**: `folders`

---

## Document Module Commands

First enter the docs module: `pkms> docs`

### `add`

**Description**: Add a document to the library

**Syntax**:
```
add <filepath>
```

**Arguments**:
- `filepath`: Path to PDF, DOCX, or TXT file

**Supported Formats**: .pdf, .docx, .txt

**Behavior**:
- Copies file to data directory
- Extracts metadata (title, page count, preview)
- Auto-generates unique filename
- PDF: Extracts title from metadata
- DOCX: Extracts title from properties
- TXT: Uses first non-empty line as title

**Examples**:
```bash
docs> add ~/Documents/research.pdf
docs> add "C:\Users\Name\paper.docx"
docs> add /path/to/notes.txt
```

**See Also**: `list`, `view`

---

### `list`

**Description**: Display all documents

**Syntax**:
```
list
```

**Output**: Table with ID, Title, Type, Size, Added date, Summary status

**Sorting**: Recently accessed documents first

**Examples**:
```bash
docs> list
```

**See Also**: `view`, `search`

---

### `view`

**Description**: Display detailed document information

**Syntax**:
```
view <doc_id>
```

**Arguments**:
- `doc_id`: Document ID or partial ID

**Output**: ID, filename, type, page count, dates, summary (if exists), preview

**Examples**:
```bash
docs> view 1
docs> view a3d5
```

**See Also**: `list`, `extract`

---

### `remove`

**Description**: Delete a document or its summary

**Syntax**:
```
remove <doc_id>
remove -s <doc_id>
```

**Arguments**:
- `doc_id`: Document ID or partial ID
- `-s` (optional): Remove only the summary (not the document)

**Confirmation**: 
- Document removal: Requires "yes" to confirm
- Summary removal: Warns about API costs and requires confirmation

**Behavior**: 
- Without `-s`: Deletes both file and metadata
- With `-s`: Removes only the AI-generated summary

**Examples**:
```bash
# Remove entire document
docs> remove 1
# Prompt: Delete document 'filename.pdf'? (yes/no):

# Remove only summary
docs> remove -s 2
# Warning: Summaries use API costs and are saved to reduce costs
# Prompt: Are you sure you want to remove this summary? (yes/no):
```

**Notes**: Summaries are generated using OpenAI API and cost money, so removing them means you'll need to regenerate them later if needed.

**See Also**: `list`, `view`, `summarize`

---

### `extract`

**Description**: Extract text from a document

**Syntax**:
```
extract <doc_id> [--page N]
```

**Arguments**:
- `doc_id` (required): Document ID or partial ID
- `--page N` (optional): Page number for PDFs only

**Behavior**:
- Extracts and caches text
- Without --page: Extracts entire document
- With --page: Extracts single page (PDF only)

**Examples**:
```bash
# Extract full document
docs> extract 1

# Extract specific page
docs> extract 1 --page 5
```

**See Also**: `view`, `search`

---

### `search`

**Description**: Search across all documents

**Syntax**:
```
search <query>
```

**Arguments**:
- `query`: Search term (case-insensitive)

**Search Scope**: Full text of all documents

**Output**: Document matches with highlighted context

**Examples**:
```bash
docs> search "machine learning"
docs> search methodology
```

**See Also**: `list`, `extract`

---

### `summarize`

**Description**: Generate AI summary for a document

**Syntax**:
```
summarize <doc_id> [--max-words N]
```

**Arguments**:
- `doc_id` (required): Document ID or partial ID
- `--max-words N` (optional): Maximum words (default: 600, max: 2000)

**Requirements**: OpenAI API key

**Behavior**:
- Large documents chunked automatically
- Summaries saved to metadata
- Cost tracked per session

**Cost**: Uses gpt-4o-mini (~$0.001-0.01 per document depending on size)

**Examples**:
```bash
# Default 600-word summary
docs> summarize 1

# Custom length summary
docs> summarize 2 --max-words 300
```

**See Also**: `view`, `extract`

---

### `refresh`

**Description**: Refresh document titles with intelligent extraction

**Syntax**:
```
refresh
```

**Behavior**:
- Re-extracts titles for documents with generic names
- Updates PDFs with "(anonymous)" or "untitled" titles
- Updates DOCX files with "Word Document" titles
- Extracts title from document content (first page/section)
- Falls back to filename if no content-based title found

**Examples**:
```bash
docs> refresh
# Output:
# ✓ 1: '(anonymous)' → 'Research Methodology'
# ✓ 2: 'Word Document' → 'Annual Report 2024'
# ✓ Successfully refreshed 2 document title(s)
```

**Notes**: 
- Only updates documents with generic titles
- Documents with existing meaningful titles are not changed
- Changes are saved immediately

**See Also**: `list`, `view`

---

## Chat Module Commands

First enter the chat module: `pkms> chat`

### `chat`

**Description**: Start interactive chat mode

**Syntax**:
```
chat> /context <type>
```

**Arguments**:
- `/context <type>` (optional): Context type (general, tasks, docs, all)

**Context Types**:
- `general`: No context loaded
- `tasks`: Load all task data
- `docs`: Load all document summaries
- `all`: Load both tasks and documents

**Examples**:
```bash
# General chat
chat> chat

# Chat with task context
chat> /context  tasks

# Chat with all context
chat> /context all
```

**In-Chat Commands**:
- `/exit` or `/quit`: Leave chat mode
- `/clear`: Clear conversation history
- `/context <type>`: Switch context
- `/refresh`: Reload context data
- `/cost`: Show API usage
- `/help`: Show chat commands

**Intelligent Task Creation**:
The AI can intelligently suggest tasks based on your conversation. It will:
- Detect when you're discussing potential tasks
- Ask for clarification on ambiguous references ("a report" vs "the report")
- Use chat history and workspace context to understand your intent
- Distinguish between creation requests and general discussion
- Offer structured task suggestions that you can approve or reject

**Task Creation Examples**:
```bash
# AI asks for clarification
chat> I need to work on a report
Assistant: Which report are you referring to? Can you provide more details?

# AI suggests a task based on context
chat[tasks]> I should finish the quarterly analysis by Friday
Assistant: [suggests task with deadline]
Would you like me to create this task?

# AI understands you want recommendations, not creation
chat> I need to add a task, what do you recommend?
Assistant: [provides recommendations without auto-creating]
```

**Examples**:
```bash
chat> /context tasks
chat[tasks]> What tasks are due this week?
chat[tasks]> /context all
chat[all]> Summarize my documents about AI
chat[all]> /exit
```

**Cost**: Uses gpt-4o ($2.50/1M input, $10/1M output tokens)

**See Also**: `agent`

---

## Agent Module Commands

First enter the agent module: `pkms> agent`

### `analyze`

**Description**: AI analysis of tasks with recommendations

**Syntax**:
```
analyze
```

**Output**:
- Task priority insights
- Overdue task warnings
- Time management suggestions
- Workload balance recommendations

**Requirements**: OpenAI API key

**Examples**:
```bash
agent> analyze
```

**Cost**: Uses gpt-4o-mini

**See Also**: `synthesize`

---

### `synthesize`

**Description**: Combine information from multiple documents

**Syntax**:
```
synthesize <doc_id1> <doc_id2> [...]
```

**Arguments**:
- `doc_id`: One or more document IDs

**Output**: Combined insights and key themes

**Requirements**: OpenAI API key

**Examples**:
```bash
agent> synthesize 1 2 3
```

**Cost**: Uses gpt-4o-mini

**See Also**: `analyze`

---

## Settings Module Commands

First enter the settings module: `pkms> settings`

### `show`

**Description**: Display current settings

**Syntax**:
```
show
```

**Examples**:
```bash
settings> show
```

---

### `set`

**Description**: Update a setting

**Syntax**:
```
set <key> <value>
```

**Examples**:
```bash
settings> set theme dark
```

---

## Tips

### ID Matching

If you have a task with ID `1`, you can use:
```bash
tasks> view 1
```

The system will match the first task that starts with your partial ID.

### Command History

Use ↑/↓ arrow keys to navigate command history (Unix/Mac/Windows).

### Autocomplete

Tab completion is not currently supported but is planned for future releases.

### Error Messages

The system provides helpful error messages that suggest:
- Correct command syntax
- Which module to enter
- Similar commands (fuzzy matching)

---

## Command Cheat Sheet

| Action | Command |
|--------|---------|
| Add task | `add "Title" -p high -dl tomorrow` |
| List tasks | `list` |
| Complete task | `complete 1` |
| Add document | `add ~/file.pdf` |
| Search docs | `search "query"` |
| Start chat | `chat` |
| View stats | `stats` |
| Create backup | `backup` |
| Switch module | `tasks`, `docs`, `chat`, `agent` |
| Get help | `help` |
| Exit | `exit` |

---

For more information, see [USER_GUIDE.md](USER_GUIDE.md) for tutorials and workflows.
