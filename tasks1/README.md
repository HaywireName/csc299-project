# Todo CLI App

A simple command-line todo application built with Python, using argparse for CLI handling and JSON for data storage.

## Features

- ✅ **Add** todos with title and optional description
- 📋 **List** todos (all or just incomplete ones)
- 🔍 **Search** todos by title or description
- ✓ **Complete** todos
- ✗ **Delete** todos
- 💾 Persistent storage using JSON

## Installation

No external dependencies required! Just Python 3.6+.

This is a standalone project - no version control setup needed.

```bash
# Make the script executable (optional)
chmod +x todo.py
```

## Usage

### Interactive mode (REPL)

Run without arguments to start an interactive prompt:

```bash
python todo.py
```

Examples in the prompt:

```
todo> add "Buy groceries" -d "milk, eggs, bread"
todo> list
todo> search groceries
todo> complete 1
todo> delete 1
todo> help
todo> help add
todo> exit
```

### Add a todo

```bash
python todo.py add "Buy groceries"
python todo.py add "Finish project" -d "Complete the CLI app by Friday"
```

### List todos

```bash
# List incomplete todos only
python todo.py list

# List all todos (including completed)
python todo.py list --all
python todo.py list -a
```

### Search todos

```bash
python todo.py search "groceries"
python todo.py search "project"
```

### Complete a todo

```bash
python todo.py complete 1
```

### Delete a todo

```bash
python todo.py delete 1
```

### Get help

```bash
python todo.py --help
python todo.py add --help
```

## Data Storage

Todos are stored in `todos.json` in the current directory. Each todo contains:
- `id`: Unique identifier
- `title`: Todo title
- `description`: Optional description
- `completed`: Boolean status
- `created_at`: ISO timestamp of creation
- `completed_at`: ISO timestamp of completion (null if incomplete)

## Example Workflow

```bash
# Add some todos
python todo.py add "Learn Python" -d "Complete the tutorial"
python todo.py add "Build a project"
python todo.py add "Write documentation"

# List todos
python todo.py list

# Complete a todo
python todo.py complete 1

# Search for todos
python todo.py search "project"

# List all todos including completed
python todo.py list --all

# Delete a todo
python todo.py delete 2
```

## License

MIT
