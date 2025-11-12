#!/usr/bin/env python3
"""
A simple CLI task application with JSON storage.
Supports add, list, search, complete, delete, and clean operations.
"""

import argparse
import shlex
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional


class TodoApp:
    """Main task application class."""
    
    def __init__(self, data_file: Optional[str] = None):
        """Initialize the task app with a data file.

        Uses tasks.json stored next to this script for consistency.
        Automatically migrates from todos.json if present.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Preferred new location
        default_tasks = os.path.join(base_dir, 'tasks.json')
        # Legacy filename we may migrate from
        legacy_todos = os.path.join(base_dir, 'todos.json')
        # Allow explicit override but default to script-local file
        self.data_file = data_file or default_tasks
        # If using default path and legacy exists but new doesn't, migrate
        if self.data_file == default_tasks and (not os.path.exists(default_tasks)) and os.path.exists(legacy_todos):
            try:
                os.replace(legacy_todos, default_tasks)
            except OSError:
                # Fallback: leave legacy in place; we'll read from legacy path during load
                pass
        self.todos: List[Dict] = []
        self.load_todos()
    
    def load_todos(self) -> None:
        """Load tasks from JSON file."""
        # Try primary file first
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.todos = json.load(f)
            except json.JSONDecodeError:
                print(f"Error: Could not parse {self.data_file}. Starting with empty todo list.")
                self.todos = []
        else:
            # Attempt to read legacy todos.json next to the script if present
            legacy_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'todos.json')
            if os.path.exists(legacy_path):
                try:
                    with open(legacy_path, 'r') as f:
                        self.todos = json.load(f)
                    # Save immediately to migrate to new filename
                    self.save_todos()
                    try:
                        os.remove(legacy_path)
                    except OSError:
                        pass
                except json.JSONDecodeError:
                    print(f"Error: Could not parse {legacy_path}. Starting with empty task list.")
                    self.todos = []
            else:
                self.todos = []
    
    def save_todos(self) -> None:
        """Save tasks to JSON file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.todos, f, indent=2)
        except IOError as e:
            print(f"Error saving todos: {e}")
            sys.exit(1)
    
    def get_next_id(self) -> int:
        """Get the next available ID for a new task."""
        if not self.todos:
            return 1
        return max(todo['id'] for todo in self.todos) + 1
    
    def add_todo(self, title: str, description: str = "") -> None:
        """Add a new task item."""
        todo = {
            'id': self.get_next_id(),
            'title': title,
            'description': description,
            'completed': False,
            'created_at': datetime.now().isoformat(),
            'completed_at': None
        }
        self.todos.append(todo)
        self.save_todos()
        print(f"✓ Added task #{todo['id']}: {title}")
    
    def list_todos(self, show_all: bool = False) -> None:
        """List all tasks or only incomplete ones, with sequential display IDs."""
        if not self.todos:
            print("No tasks found. Add one with 'task add <title>'")
            return
        
        todos_to_show = self.todos if show_all else [t for t in self.todos if not t['completed']]
        # Ensure stable, ascending order by ID
        todos_to_show = sorted(todos_to_show, key=lambda t: t['id'])
        
        if not todos_to_show:
            print("No incomplete tasks. Great job! 🎉")
            return
        
        print(f"\n{'ID':<5} {'Status':<12} {'Title':<40} {'Description':<30}")
        print("-" * 90)
        
        # Display sequential IDs (1, 2, 3...) instead of actual IDs
        for display_id, todo in enumerate(todos_to_show, 1):
            status = "✓ Completed" if todo['completed'] else "○ Incomplete"
            title = todo['title'][:37] + "..." if len(todo['title']) > 40 else todo['title']
            desc = todo['description'][:27] + "..." if len(todo['description']) > 30 else todo['description']
            print(f"{display_id:<5} {status:<12} {title:<40} {desc:<30}")
        
        completed_count = sum(1 for t in self.todos if t['completed'])
        total_count = len(self.todos)
        print(f"\nTotal: {total_count} ({completed_count} completed, {total_count - completed_count} incomplete)")
    
    def search_todos(self, query: str) -> None:
        """Search tasks by title or description."""
        query_lower = query.lower()
        matches = [
            todo for todo in self.todos
            if query_lower in todo['title'].lower() or query_lower in todo['description'].lower()
        ]
        
        if not matches:
            print(f"No tasks found matching '{query}'")
            return
        
        print(f"\nFound {len(matches)} task(s) matching '{query}':\n")
        print(f"{'ID':<5} {'Status':<12} {'Title':<40} {'Description':<30}")
        print("-" * 90)
        
        for todo in matches:
            status = "✓ Completed" if todo['completed'] else "○ Incomplete"
            title = todo['title'][:37] + "..." if len(todo['title']) > 40 else todo['title']
            desc = todo['description'][:27] + "..." if len(todo['description']) > 30 else todo['description']
            print(f"{todo['id']:<5} {status:<12} {title:<40} {desc:<30}")
    
    def complete_todo(self, display_id: int) -> None:
        """Mark a task as completed using display ID."""
        todo = self._get_todo_by_display_id(display_id, show_all=False)
        if not todo:
            print(f"Error: Task #{display_id} not found")
            return
        
        if todo['completed']:
            print(f"Task #{display_id} is already completed")
            return
        
        todo['completed'] = True
        todo['completed_at'] = datetime.now().isoformat()
        # After completion, reindex so oldest incomplete is #1
        self.reindex()
        print(f"✓ Completed task #{display_id}: {todo['title']}")
    
    def complete_todos(self, display_ids: List[int]) -> None:
        """Mark multiple tasks as completed using display IDs."""
        completed_titles = []
        errors = []
        already_completed = []
        
        for display_id in display_ids:
            todo = self._get_todo_by_display_id(display_id, show_all=False)
            if not todo:
                errors.append(str(display_id))
                continue
            
            if todo['completed']:
                already_completed.append(str(display_id))
                continue
            
            todo['completed'] = True
            todo['completed_at'] = datetime.now().isoformat()
            completed_titles.append(f"#{display_id}")
        
        if completed_titles:
            self.reindex()
            if len(completed_titles) == 1:
                print(f"✓ Completed task {completed_titles[0]}")
            elif len(completed_titles) == 2:
                print(f"✓ Completed tasks {completed_titles[0]} and {completed_titles[1]}")
            else:
                print(f"✓ Completed tasks {', '.join(completed_titles[:-1])}, and {completed_titles[-1]}")
        
        if errors:
            print(f"Error: Task(s) {', '.join(errors)} not found")
        
        if already_completed:
            if len(already_completed) == 1:
                print(f"Task #{already_completed[0]} was already completed")
            else:
                print(f"Tasks {', '.join(already_completed)} were already completed")
    
    def delete_todo(self, display_id: int, show_all: bool = False) -> None:
        """Delete a task by display ID."""
        todo = self._get_todo_by_display_id(display_id, show_all)
        if not todo:
            print(f"Error: Task #{display_id} not found")
            return
        
        title = todo['title']
        actual_id = todo['id']
        self.todos = [t for t in self.todos if t['id'] != actual_id]
        # After deletion, reindex so remaining tasks are compacted
        self.reindex()
        print(f"✗ Deleted task #{display_id}: {title}")
    
    def delete_todos(self, display_ids: List[int], show_all: bool = False) -> None:
        """Delete multiple tasks by display ID."""
        deleted_ids = []
        errors = []
        actual_ids_to_delete = []
        
        for display_id in display_ids:
            todo = self._get_todo_by_display_id(display_id, show_all)
            if not todo:
                errors.append(str(display_id))
                continue
            
            deleted_ids.append(f"#{display_id}")
            actual_ids_to_delete.append(todo['id'])
        
        # Delete by actual IDs
        for actual_id in actual_ids_to_delete:
            self.todos = [t for t in self.todos if t['id'] != actual_id]
        
        if deleted_ids:
            self.reindex()
            if len(deleted_ids) == 1:
                print(f"✗ Deleted task {deleted_ids[0]}")
            elif len(deleted_ids) == 2:
                print(f"✗ Deleted tasks {deleted_ids[0]} and {deleted_ids[1]}")
            else:
                print(f"✗ Deleted tasks {', '.join(deleted_ids[:-1])}, and {deleted_ids[-1]}")
        
        if errors:
            print(f"Error: Task(s) {', '.join(errors)} not found")
    
    def _find_todo(self, todo_id: int) -> Optional[Dict]:
        """Find a task by ID."""
        for todo in self.todos:
            if todo['id'] == todo_id:
                return todo
        return None
    
    def _get_todo_by_display_id(self, display_id: int, show_all: bool = False) -> Optional[Dict]:
        """Get a task by its display ID (position in list)."""
        todos_to_show = self.todos if show_all else [t for t in self.todos if not t['completed']]
        todos_to_show = sorted(todos_to_show, key=lambda t: t['id'])
        
        if 1 <= display_id <= len(todos_to_show):
            return todos_to_show[display_id - 1]
        return None

    def reindex(self) -> None:
        """Reset IDs so that oldest incomplete task has ID=1, then remaining tasks.

        Ordering rules:
        - Incomplete tasks first, ascending by created_at (fallback: stable original order)
        - Then completed tasks, ascending by created_at (fallback as above)
        """
        def safe_parse(ts: Optional[str]) -> float:
            try:
                return datetime.fromisoformat(ts).timestamp() if ts else float('inf')
            except Exception:
                return float('inf')

        incompletes = [t for t in self.todos if not t.get('completed')]
        completes = [t for t in self.todos if t.get('completed')]
        incompletes.sort(key=lambda t: (safe_parse(t.get('created_at')), t.get('id', 0)))
        completes.sort(key=lambda t: (safe_parse(t.get('created_at')), t.get('id', 0)))
        new_list = incompletes + completes
        for idx, t in enumerate(new_list, start=1):
            t['id'] = idx
        self.todos = new_list
        self.save_todos()


def build_parser() -> argparse.ArgumentParser:
    """Construct and return the argument parser (without parsing)."""
    parser = argparse.ArgumentParser(
        description="A simple CLI task application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  task add Buy groceries -d milk, eggs, bread
  task list
  task list --all
  task search groceries
  task complete 1
  task delete 1
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('title', nargs='*', help='Task title (can be multiple words)')
    add_parser.add_argument('-d', '--description', nargs='*', default=[], help='Task description (can be multiple words)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('-a', '--all', action='store_true', 
                            help='Show all tasks including completed ones')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search tasks')
    search_parser.add_argument('query', help='Search query')
    
    # Complete command
    complete_parser = subparsers.add_parser('complete', help='Mark a task as completed')
    complete_parser.add_argument('id', type=int, nargs='+', help='Task ID(s) to complete')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete tasks by ID (supports multiple). Use --completed-only to restrict to completed tasks')
    delete_parser.add_argument('id', type=int, nargs='+', help='Task ID(s) to delete')
    delete_parser.add_argument('--completed-only', action='store_true', help='Only delete if the task is completed')

    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Remove all completed tasks')
    
    return parser


def parse_add_command(argv: List[str]) -> tuple:
    """Custom parser for add command to handle unquoted multi-word titles and descriptions."""
    if not argv or argv[0] != 'add':
        raise ValueError("Not an add command")
    
    # Find -d flag position
    d_index = -1
    for i, arg in enumerate(argv[1:], 1):
        if arg == '-d' or arg == '--description':
            d_index = i
            break
    
    if d_index == -1:
        # No description flag, everything after 'add' is the title
        title = ' '.join(argv[1:]).strip()
        description = ''
    else:
        # Title is everything between 'add' and '-d'
        title = ' '.join(argv[1:d_index]).strip()
        # Description is everything after '-d'
        description = ' '.join(argv[d_index + 1:]).strip()
    
    return title, description


def dispatch_command(app: TodoApp, args: argparse.Namespace) -> None:
    """Dispatch a parsed argparse Namespace to the appropriate handler."""
    if args.command == 'add':
        # Handle multi-word title and description
        title = ' '.join(args.title) if isinstance(args.title, list) else args.title
        description = ' '.join(args.description) if isinstance(args.description, list) else args.description
        app.add_todo(title, description)
    elif args.command == 'list':
        app.list_todos(show_all=getattr(args, 'all', False))
    elif args.command == 'search':
        app.search_todos(args.query)
    elif args.command == 'complete':
        if isinstance(args.id, list):
            app.complete_todos(args.id)
        else:
            app.complete_todo(args.id)
    elif args.command == 'delete':
        # Support deleting multiple IDs, optionally only completed
        if getattr(args, 'completed_only', False):
            # Handle completed-only filtering for multiple display IDs from --all list
            valid_ids = []
            for display_id in args.id:
                t = app._get_todo_by_display_id(display_id, show_all=True)
                if not t:
                    print(f"Error: Task #{display_id} not found")
                    continue
                if not t['completed']:
                    print(f"Skip: Task #{display_id} is not completed (use without --completed-only to force)")
                    continue
                valid_ids.append(display_id)
            if valid_ids:
                if len(valid_ids) == 1:
                    app.delete_todo(valid_ids[0], show_all=True)
                else:
                    app.delete_todos(valid_ids, show_all=True)
        else:
            # Default behavior: delete from incomplete tasks list
            if len(args.id) == 1:
                app.delete_todo(args.id[0], show_all=False)
            else:
                app.delete_todos(args.id, show_all=False)
    elif args.command == 'clean':
        before = len(app.todos)
        app.todos = [t for t in app.todos if not t['completed']]
        removed = before - len(app.todos)
        # After cleaning, reindex automatically
        app.reindex()
        print(f"🧹 Removed {removed} completed task(s)")
    else:
        print("Unknown command. Type 'help' for usage.")


def _print_help_with_repl_options(parser: argparse.ArgumentParser) -> None:
    """Print argparse help text, injecting REPL-only options under 'options:'."""
    help_text = parser.format_help()
    marker = "\noptions:\n"
    insert_line = "  quit, exit, q         exit the interactive prompt\n"
    if marker in help_text:
        idx = help_text.find(marker) + len(marker)
        help_text = help_text[:idx] + insert_line + help_text[idx:]
    else:
        help_text = help_text + "\nREPL options:\n" + insert_line
    print(help_text)


def repl(parser: argparse.ArgumentParser, app: TodoApp) -> None:
    """Start an interactive REPL to accept commands repeatedly."""
    print("Task CLI interactive mode. Type 'help' to see commands, 'exit' to quit.\n")
    # Access subcommand names for help
    try:
        sub_map = parser._subparsers._group_actions[0].choices  # type: ignore[attr-defined]
    except Exception:
        sub_map = {}
    
    while True:
        try:
            line = input("task> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if line.lower() in {"exit", "quit", "q"}:
            break
        if line.lower().startswith("help"):
            parts = line.split(maxsplit=1)
            if len(parts) == 1:
                _print_help_with_repl_options(parser)
                print("Commands:", ", ".join(sorted(sub_map.keys())) if sub_map else "add, list, search, complete, delete, clean")
            else:
                cmd = parts[1].strip()
                sub = sub_map.get(cmd)
                if sub is not None:
                    print(sub.format_help())
                else:
                    print(f"No such command: {cmd}")
            continue
        
        # Parse and execute command line
        try:
            argv = shlex.split(line)
        except ValueError as e:
            print(f"Parse error: {e}")
            continue
        
        # Handle add command with custom parsing for multi-word titles/descriptions
        if argv and argv[0] == 'add':
            try:
                title, description = parse_add_command(argv)
                if not title:
                    print("Error: Task title cannot be empty")
                    continue
                app.add_todo(title, description)
            except ValueError as e:
                print(f"Parse error: {e}")
            continue
        
        try:
            args = parser.parse_args(argv)
        except SystemExit:
            # argparse attempted to exit on error; show help-like message and continue
            continue
        if not getattr(args, 'command', None):
            print("Please enter a command. Type 'help' for usage.")
            continue
        dispatch_command(app, args)


def main():
    """Main entry point for the CLI application."""
    parser = build_parser()
    
    # If no args provided, start REPL; else process one-shot command
    if len(sys.argv) == 1:
        app = TodoApp()
        repl(parser, app)
        return
    
    # Handle add command with custom parsing for multi-word titles/descriptions
    if len(sys.argv) > 1 and sys.argv[1] == 'add':
        app = TodoApp()
        try:
            title, description = parse_add_command(sys.argv[1:])
            if not title:
                print("Error: Task title cannot be empty")
                return
            app.add_todo(title, description)
        except ValueError as e:
            print(f"Parse error: {e}")
        return
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    
    # Initialize the app
    app = TodoApp()
    dispatch_command(app, args)


if __name__ == '__main__':
    main()
