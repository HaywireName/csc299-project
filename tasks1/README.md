# Task CLI App

A simple command-line task application built with Python, using argparse for CLI handling and JSON for data storage.

## Features

- ✅ **Add** tasks with title and optional description
- 📋 **List** tasks (all or just incomplete ones)
- 🔍 **Search** tasks by title or description
- ✓ **Complete** tasks
- ✗ **Delete** tasks
- 🧹 **Clean** completed tasks (remove all completed)
- 💾 Persistent storage using JSON

## Installation

No external dependencies required! Just Python 3.6+.

This is a standalone project - no version control setup needed.

```bash
# Make the script executable (optional)
chmod +x task.py
```

## Usage

### Interactive mode (REPL)

Run without arguments to start an interactive prompt:

```bash
python task.py
```

Examples in the prompt:

```
task> add "Buy groceries" -d "milk, eggs, bread"
task> list
task> search groceries
task> complete 1
task> delete 1
task> clean
task> help
task> help add
task> exit
```

### Add a task

```bash
python task.py add "Buy groceries"
python task.py add "Finish project" -d "Complete the CLI app by Friday"
```

### List tasks

```bash
# List incomplete tasks only
python task.py list

# List all tasks (including completed)
python task.py list --all
python task.py list -a
```

### Search tasks

```bash
python task.py search "groceries"
python task.py search "project"
```

### Complete a task

```bash
python task.py complete 1
```

### Delete tasks

```bash
# Delete specific IDs (one or many)
python task.py delete 1 3 5

# Only delete if completed
python task.py delete 2 --completed-only
```

### Clean completed tasks

```bash
python task.py clean
```

### Get help

```bash
python task.py --help
python task.py add --help
```

## Data Storage

Tasks are stored in `tasks.json` in this directory (`tasks1/`). Each task contains:
- `id`: Unique identifier
- `title`: Task title
- `description`: Optional description
- `completed`: Boolean status
- `created_at`: ISO timestamp of creation
- `completed_at`: ISO timestamp of completion (null if incomplete)

## Example Workflow

```bash
# Add some tasks
python task.py add "Learn Python" -d "Complete the tutorial"
python task.py add "Build a project"
python task.py add "Write documentation"

# List tasks
python task.py list

# Complete a task
python task.py complete 1

# Search for tasks
python task.py search "project"

# List all tasks including completed
python task.py list --all

# Delete a task
python task.py delete 2
```

## License

MIT
