import sys
from config import check_api_key
from core.commands import CommandRegistry, parse_command
from modules.task_module import TaskManager

class DataManager:
    """Simple data manager for storing tasks in memory."""
    def __init__(self):
        self.data = {}

    def get_current_folder(self):
        """Return the current folder name."""
        return "tasks"

    def load(self, folder):
        """Load data from a folder."""
        return self.data.get(folder, [])

    def save(self, folder, tasks):
        """Save data to a folder."""
        self.data[folder] = tasks

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

    # Register global commands
    registry.register_command('help', lambda: help_command(registry), 'Show available commands', 'global')
    registry.register_command('exit', exit_command, 'Exit program', 'global')
    # Register 'quit' command with the same functionality as 'exit'
    registry.register_command('quit', exit_command, 'Exit program', 'global')

    print("Welcome to PKMS Task Manager!")
    print("Type 'help' for available commands.\n")

    while True:
        try:
            user_input = input("pkms> ")
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