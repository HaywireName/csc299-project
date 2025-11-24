class CommandRegistry:
    def __init__(self):
        """Initialize an empty command dictionary."""
        self.commands = {}

    def register_command(self, name, function, description, module='global'):
        """Register a command with its name, function, description, and module."""
        if name in self.commands:
            raise ValueError(f"Command '{name}' is already registered.")
        self.commands[name] = {
            'function': function,
            'description': description,
            'module': module
        }

    def get_command(self, name):
        """Retrieve a command function by its name."""
        return self.commands.get(name, {}).get('function')

    def list_commands(self, module=None):
        """List all commands, optionally filtered by module."""
        return [
            (name, cmd['description'], cmd['module'])
            for name, cmd in self.commands.items()
            if module is None or cmd['module'] == module
        ]

    def has_command(self, name):
        """Check if a command is registered."""
        return name in self.commands

    def get_command_module(self, name):
        """Get the module that a command belongs to."""
        return self.commands.get(name, {}).get('module')

def parse_command(input_string):
    """Parse an input string into a command name and arguments."""
    input_string = input_string.strip()
    if not input_string:
        return None, []
    parts = input_string.split()
    return parts[0], parts[1:]
