import sys
import json
import os
from config import check_api_key
from core.commands import CommandRegistry, parse_command
from modules.task_module import TaskManager
from modules.docs_module import DocumentManager
from modules.chat_module import ChatManager
from modules.agent_module import AgentManager

class DataManager:
    """Data manager for persisting data to JSON files."""
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)

    def get_current_folder(self):
        """Return the current folder name."""
        return "tasks"

    def load(self, filename):
        """Load data from JSON file."""
        try:
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load {filename}: {e}")
        return None

    def save(self, filename, data):
        """Save data to JSON file."""
        try:
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error: Could not save {filename}: {e}")

# Define command functions
def help_command(registry):
    """Show available commands."""
    commands = registry.list_commands()
    print("Available commands:")
    for name, description in commands:
        if name == 'quit':
            continue  # Skip 'quit' since it will be grouped with 'exit'
        if name == 'exit':
            print("  exit, quit: Exit program")
        else:
            print(f"  {name}: {description}")

def exit_command():
    """Exit the program."""
    print("Goodbye!")
    exit()

def main():
    # Check API key first
    if not check_api_key():
        sys.exit(1)

    # API key is valid, continue with program
    print("\n✓ OpenAI API key found and validated")

    # Create registry and data manager
    registry = CommandRegistry()
    data_manager = DataManager()

    # Initialize TaskManager (this will register task commands)
    task_manager = TaskManager(data_manager, registry)
    
    # Initialize DocumentManager (this will register document commands)
    document_manager = DocumentManager(data_manager, registry)
    
    # Initialize ChatManager (this will register chat commands)
    chat_manager = ChatManager(data_manager, registry)
    
    # Initialize AgentManager (this will register agent commands)
    agent_manager = AgentManager(data_manager, task_manager, registry, document_manager)

    # Register global commands
    registry.register_command('help', lambda: help_command(registry), 'Show available commands', 'global')
    registry.register_command('exit', exit_command, 'Exit program', 'global')
    # Register 'quit' command with the same functionality as 'exit'
    registry.register_command('quit', exit_command, 'Exit program', 'global')

    print("Welcome to PKMS Task Manager!")
    print("Type 'help' for available commands.\n")

    while True:
        try:
            current_folder = task_manager.data["current_folder"]
            user_input = input(f"pkms[{current_folder}]> ")
            command_name, args = parse_command(user_input)

            if not command_name:
                continue

            command_function = registry.get_command(command_name)

            if command_function:
                try:
                    command_function(*args)
                except Exception as e:
                    print(f"Error executing command '{command_name}': {e}")
            else:
                print(f"Unknown command: {command_name}. Type 'help' for available commands.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == '__main__':
    main()