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
task> add Buy groceries -d milk, eggs, bread
task> add "Buy groceries" -d "milk, eggs, bread"
task> list
task> search groceries
task> complete 1
task> complete 2 3 4
task> delete 1
task> delete 5 6 7
task> delete --all
task> clean
task> help
task> help add
task> exit
```

### Add a task

```bash
# With quotes (traditional)
python task.py add "Buy groceries"
python task.py add "Finish project" -d "Complete the CLI app by Friday"

# Without quotes (new feature)
python task.py add Buy groceries
python task.py add Finish project -d Complete the CLI app by Friday
python task.py add Multi word task title -d Multi word description here
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
python task.py search groceries
python task.py search project
```

### Complete tasks

```bash
# Complete a single task
python task.py complete 1

# Complete multiple tasks
python task.py complete 1 2 3
```

### Delete tasks

```bash
# Delete a single task
python task.py delete 1

# Delete multiple tasks
python task.py delete 1 3 5

# Delete ALL tasks (complete and incomplete)
python task.py delete --all
```

### Clean completed tasks

```bash
python task.py clean
```

Tip: Use "clean" to remove only completed tasks. Use "delete --all" to remove everything.

### Get help

```bash
python task.py --help
python task.py add --help
```

## Data Storage

Tasks are stored in `tasks.json` in this directory (`tasks3/`). Each task contains:
- `id`: Unique identifier
- `title`: Task title
- `description`: Optional description
- `completed`: Boolean status
- `created_at`: ISO timestamp of creation
- `completed_at`: ISO timestamp of completion (null if incomplete)

## ID Numbering

The app uses display IDs for user interaction:
- `task list`: Shows incomplete tasks numbered 1, 2, 3, etc.
- `task list --all`: Shows all tasks numbered 1, 2, 3, etc.
- Commands like `complete`, `delete` use these display IDs
- When using `delete --completed-only`, use IDs from `list --all`

## Example Workflow

```bash
# Add some tasks
python task.py add Learn Python -d Complete the tutorial
python task.py add Build a project
python task.py add Write documentation

# List tasks
python task.py list

# Complete a task
python task.py complete 1

# Search for tasks
python task.py search project

# List all tasks including completed
python task.py list --all

# Delete a task
python task.py delete 2
```

## License

MIT
