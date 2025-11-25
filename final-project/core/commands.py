class CommandRegistry:
    """Registry for managing application commands.
    
    Provides a central registry for registering, retrieving, and managing
    commands throughout the application. Commands can be organized by module
    and queried by name.
    
    Attributes:
        commands (dict): Dictionary mapping command names to command metadata
            including function, description, and module.
    """
    
    def __init__(self):
        """Initialize an empty command dictionary.
        
        Creates a new CommandRegistry with no registered commands.
        """
        self.commands = {}

    def register_command(self, name, function, description, module='global'):
        """Register a command with its name, function, description, and module.
        
        Args:
            name (str): The unique name identifier for the command.
            function (callable): The function to execute when the command is invoked.
            description (str): Human-readable description of what the command does.
            module (str): The module category this command belongs to. Defaults to 'global'.
        
        Raises:
            ValueError: If a command with the given name is already registered.
        """
        if name in self.commands:
            raise ValueError(f"Command '{name}' is already registered.")
        self.commands[name] = {
            'function': function,
            'description': description,
            'module': module
        }

    def get_command(self, name):
        """Retrieve a command function by its name.
        
        Args:
            name (str): The name of the command to retrieve.
        
        Returns:
            callable or None: The command function if found, None otherwise.
        """
        return self.commands.get(name, {}).get('function')

    def list_commands(self, module=None):
        """List all commands, optionally filtered by module.
        
        Args:
            module (str, optional): Filter commands by this module name.
                If None, returns all commands. Defaults to None.
        
        Returns:
            list[tuple]: List of tuples containing (name, description, module)
                for each command matching the filter criteria.
        """
        return [
            (name, cmd['description'], cmd['module'])
            for name, cmd in self.commands.items()
            if module is None or cmd['module'] == module
        ]

    def has_command(self, name):
        """Check if a command is registered.
        
        Args:
            name (str): The name of the command to check.
        
        Returns:
            bool: True if the command exists in the registry, False otherwise.
        """
        return name in self.commands

    def get_command_module(self, name):
        """Get the module that a command belongs to.
        
        Args:
            name (str): The name of the command.
        
        Returns:
            str or None: The module name if the command exists, None otherwise.
        """
        return self.commands.get(name, {}).get('module')

def parse_command(input_string):
    """Parse an input string into a command name and arguments.
    
    Splits a user input string into a command name and list of arguments.
    Handles empty strings and whitespace appropriately.
    
    Args:
        input_string (str): The raw input string to parse.
    
    Returns:
        tuple: A tuple containing:
            - command_name (str or None): The first word as the command name,
                or None if input is empty.
            - arguments (list[str]): List of remaining words as arguments,
                or empty list if no arguments or empty input.
    
    Examples:
        >>> parse_command("add Buy milk")
        ('add', ['Buy', 'milk'])
        >>> parse_command("  list  ")
        ('list', [])
        >>> parse_command("")
        (None, [])
    """
    input_string = input_string.strip()
    if not input_string:
        return None, []
    parts = input_string.split()
    return parts[0], parts[1:]
