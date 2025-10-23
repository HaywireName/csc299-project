#!/usr/bin/env python3
"""
A simple CLI todo application with JSON storage.
Supports add, list, search, complete, and delete operations.
"""

import argparse
import shlex
import json
import os
import sys
import shlex
from datetime import datetime
from typing import List, Dict, Optional


class TodoApp:
    """Main todo application class."""
    
    def __init__(self, data_file: str = "todos.json"):
        """Initialize the todo app with a data file."""
        self.data_file = data_file
        self.todos: List[Dict] = []
        self.load_todos()
    
    def load_todos(self) -> None:
        """Load todos from JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.todos = json.load(f)
            except json.JSONDecodeError:
                print(f"Error: Could not parse {self.data_file}. Starting with empty todo list.")
                self.todos = []
        else:
            self.todos = []
    
    def save_todos(self) -> None:
        """Save todos to JSON file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.todos, f, indent=2)
        except IOError as e:
            print(f"Error saving todos: {e}")
            sys.exit(1)
    
    def get_next_id(self) -> int:
        """Get the next available ID for a new todo."""
        if not self.todos:
            return 1
        return max(todo['id'] for todo in self.todos) + 1
    
    def add_todo(self, title: str, description: str = "") -> None:
        """Add a new todo item."""
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
        print(f"✓ Added todo #{todo['id']}: {title}")
    
    def list_todos(self, show_all: bool = False) -> None:
        """List all todos or only incomplete ones."""
        if not self.todos:
            print("No todos found. Add one with 'todo add <title>'")
            return
        
        todos_to_show = self.todos if show_all else [t for t in self.todos if not t['completed']]
        
        if not todos_to_show:
            print("No incomplete todos. Great job! 🎉")
            return
        
        print(f"\n{'ID':<5} {'Status':<12} {'Title':<40} {'Description':<30}")
        print("-" * 90)
        
        for todo in todos_to_show:
            status = "✓ Completed" if todo['completed'] else "○ Incomplete"
            title = todo['title'][:37] + "..." if len(todo['title']) > 40 else todo['title']
            desc = todo['description'][:27] + "..." if len(todo['description']) > 30 else todo['description']
            print(f"{todo['id']:<5} {status:<12} {title:<40} {desc:<30}")
        
        completed_count = sum(1 for t in self.todos if t['completed'])
        total_count = len(self.todos)
        print(f"\nTotal: {total_count} ({completed_count} completed, {total_count - completed_count} incomplete)")
    
    def search_todos(self, query: str) -> None:
        """Search todos by title or description."""
        query_lower = query.lower()
        matches = [
            todo for todo in self.todos
            if query_lower in todo['title'].lower() or query_lower in todo['description'].lower()
        ]
        
        if not matches:
            print(f"No todos found matching '{query}'")
            return
        
        print(f"\nFound {len(matches)} todo(s) matching '{query}':\n")
        print(f"{'ID':<5} {'Status':<12} {'Title':<40} {'Description':<30}")
        print("-" * 90)
        
        for todo in matches:
            status = "✓ Completed" if todo['completed'] else "○ Incomplete"
            title = todo['title'][:37] + "..." if len(todo['title']) > 40 else todo['title']
            desc = todo['description'][:27] + "..." if len(todo['description']) > 30 else todo['description']
            print(f"{todo['id']:<5} {status:<12} {title:<40} {desc:<30}")
    
    def complete_todo(self, todo_id: int) -> None:
        """Mark a todo as completed."""
        todo = self._find_todo(todo_id)
        if not todo:
            print(f"Error: Todo #{todo_id} not found")
            return
        
        if todo['completed']:
            print(f"Todo #{todo_id} is already completed")
            return
        
        todo['completed'] = True
        todo['completed_at'] = datetime.now().isoformat()
        self.save_todos()
        print(f"✓ Completed todo #{todo_id}: {todo['title']}")
    
    def delete_todo(self, todo_id: int) -> None:
        """Delete a todo by ID."""
        todo = self._find_todo(todo_id)
        if not todo:
            print(f"Error: Todo #{todo_id} not found")
            return
        
        title = todo['title']
        self.todos = [t for t in self.todos if t['id'] != todo_id]
        self.save_todos()
        print(f"✗ Deleted todo #{todo_id}: {title}")
    
    def _find_todo(self, todo_id: int) -> Optional[Dict]:
        """Find a todo by ID."""
        for todo in self.todos:
            if todo['id'] == todo_id:
                return todo
        return None


def build_parser() -> argparse.ArgumentParser:
    """Construct and return the argument parser (without parsing)."""
    parser = argparse.ArgumentParser(
        description="A simple CLI todo application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  todo add "Buy groceries" -d "milk, eggs, bread"
  todo list
  todo list --all
  todo search "groceries"
  todo complete 1
  todo delete 1
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new todo')
    add_parser.add_argument('title', help='Todo title')
    add_parser.add_argument('-d', '--description', default='', help='Todo description')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List todos')
    list_parser.add_argument('-a', '--all', action='store_true', 
                            help='Show all todos including completed ones')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search todos')
    search_parser.add_argument('query', help='Search query')
    
    # Complete command
    complete_parser = subparsers.add_parser('complete', help='Mark a todo as completed')
    complete_parser.add_argument('id', type=int, help='Todo ID to complete')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a todo')
    delete_parser.add_argument('id', type=int, help='Todo ID to delete')
    
    return parser


def dispatch_command(app: TodoApp, args: argparse.Namespace) -> None:
    """Dispatch a parsed argparse Namespace to the appropriate handler."""
    if args.command == 'add':
        app.add_todo(args.title, args.description)
    elif args.command == 'list':
        app.list_todos(show_all=getattr(args, 'all', False))
    elif args.command == 'search':
        app.search_todos(args.query)
    elif args.command == 'complete':
        app.complete_todo(args.id)
    elif args.command == 'delete':
        app.delete_todo(args.id)
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
    print("Todo CLI interactive mode. Type 'help' to see commands, 'exit' to quit.\n")
    # Access subcommand names for help
    try:
        sub_map = parser._subparsers._group_actions[0].choices  # type: ignore[attr-defined]
    except Exception:
        sub_map = {}
    
    while True:
        try:
            line = input("todo> ").strip()
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
                print("Commands:", ", ".join(sorted(sub_map.keys())) if sub_map else "add, list, search, complete, delete")
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
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    
    # Initialize the app
    app = TodoApp()
    dispatch_command(app, args)


if __name__ == '__main__':
    main()
