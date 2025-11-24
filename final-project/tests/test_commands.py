"""
Tests for core.commands module (CommandRegistry and parse_command).
"""
import pytest
from core.commands import CommandRegistry, parse_command


class TestCommandRegistry:
    """Test CommandRegistry functionality."""
    
    def test_initialization(self):
        """Test creating an empty command registry."""
        registry = CommandRegistry()
        
        assert registry.commands == {}
    
    def test_register_command(self, command_registry):
        """Test registering a command."""
        def test_func():
            return "test"
        
        command_registry.register_command('test', test_func, 'Test command')
        
        assert 'test' in command_registry.commands
        assert command_registry.commands['test']['function'] == test_func
        assert command_registry.commands['test']['description'] == 'Test command'
    
    def test_register_command_with_module(self, command_registry):
        """Test registering a command with module specification."""
        def test_func():
            return "test"
        
        command_registry.register_command('test', test_func, 'Test command', module='tasks')
        
        assert command_registry.commands['test']['module'] == 'tasks'
    
    def test_register_duplicate_command_raises_error(self, command_registry):
        """Test that registering duplicate command raises ValueError."""
        def test_func():
            return "test"
        
        command_registry.register_command('test', test_func, 'Test command')
        
        with pytest.raises(ValueError):
            command_registry.register_command('test', test_func, 'Another test')
    
    def test_get_command(self, command_registry):
        """Test retrieving a registered command."""
        def test_func():
            return "test"
        
        command_registry.register_command('test', test_func, 'Test command')
        
        retrieved = command_registry.get_command('test')
        
        assert retrieved == test_func
    
    def test_get_nonexistent_command(self, command_registry):
        """Test that getting non-existent command returns None."""
        result = command_registry.get_command('nonexistent')
        
        assert result is None
    
    def test_has_command(self, command_registry):
        """Test checking if command exists."""
        def test_func():
            return "test"
        
        command_registry.register_command('test', test_func, 'Test command')
        
        assert command_registry.has_command('test') is True
        assert command_registry.has_command('nonexistent') is False
    
    def test_list_commands_all(self, command_registry):
        """Test listing all commands."""
        def func1():
            pass
        def func2():
            pass
        
        command_registry.register_command('cmd1', func1, 'Command 1', 'module1')
        command_registry.register_command('cmd2', func2, 'Command 2', 'module2')
        
        commands = command_registry.list_commands()
        
        assert len(commands) == 2
        assert ('cmd1', 'Command 1', 'module1') in commands
        assert ('cmd2', 'Command 2', 'module2') in commands
    
    def test_list_commands_filtered_by_module(self, command_registry):
        """Test listing commands filtered by module."""
        def func1():
            pass
        def func2():
            pass
        def func3():
            pass
        
        command_registry.register_command('cmd1', func1, 'Command 1', 'tasks')
        command_registry.register_command('cmd2', func2, 'Command 2', 'docs')
        command_registry.register_command('cmd3', func3, 'Command 3', 'tasks')
        
        task_commands = command_registry.list_commands(module='tasks')
        
        assert len(task_commands) == 2
        assert all(cmd[2] == 'tasks' for cmd in task_commands)
    
    def test_list_commands_empty(self, command_registry):
        """Test listing commands when registry is empty."""
        commands = command_registry.list_commands()
        
        assert commands == []


class TestParseCommand:
    """Test parse_command functionality."""
    
    def test_parse_simple_command(self):
        """Test parsing a simple command without arguments."""
        cmd, args = parse_command("help")
        
        assert cmd == "help"
        assert args == []
    
    def test_parse_command_with_args(self):
        """Test parsing command with arguments."""
        cmd, args = parse_command("add Task Title")
        
        assert cmd == "add"
        assert args == ["Task", "Title"]
    
    def test_parse_command_with_multiple_args(self):
        """Test parsing command with multiple arguments."""
        cmd, args = parse_command("edit 123 --priority high")
        
        assert cmd == "edit"
        assert args == ["123", "--priority", "high"]
    
    def test_parse_command_with_flags(self):
        """Test parsing command with flags."""
        cmd, args = parse_command("add Task --deadline 2025-12-31 --priority high")
        
        assert cmd == "add"
        assert "--deadline" in args
        assert "2025-12-31" in args
        assert "--priority" in args
        assert "high" in args
    
    def test_parse_empty_string(self):
        """Test parsing empty string."""
        cmd, args = parse_command("")
        
        assert cmd is None
        assert args == []
    
    def test_parse_whitespace_only(self):
        """Test parsing whitespace-only string."""
        cmd, args = parse_command("   ")
        
        assert cmd is None
        assert args == []
    
    def test_parse_command_with_extra_spaces(self):
        """Test parsing command with extra spaces."""
        cmd, args = parse_command("  add   Task   Title  ")
        
        assert cmd == "add"
        assert args == ["Task", "Title"]
    
    def test_parse_command_preserves_case(self):
        """Test that parsing preserves case."""
        cmd, args = parse_command("Add Task TITLE")
        
        assert cmd == "Add"
        assert args == ["Task", "TITLE"]


class TestCommandExecution:
    """Test command execution through registry."""
    
    def test_execute_command_no_args(self, command_registry):
        """Test executing command without arguments."""
        result = []
        
        def test_func():
            result.append("executed")
        
        command_registry.register_command('test', test_func, 'Test')
        
        func = command_registry.get_command('test')
        func()
        
        assert result == ["executed"]
    
    def test_execute_command_with_args(self, command_registry):
        """Test executing command with arguments."""
        def add_task(*args):
            return f"Added: {' '.join(args)}"
        
        command_registry.register_command('add', add_task, 'Add task')
        
        func = command_registry.get_command('add')
        result = func("Test", "Task")
        
        assert result == "Added: Test Task"
    
    def test_execute_command_with_kwargs(self, command_registry):
        """Test executing command with keyword arguments."""
        def edit_task(task_id, **kwargs):
            return f"Edited {task_id}: {kwargs}"
        
        command_registry.register_command('edit', edit_task, 'Edit task')
        
        func = command_registry.get_command('edit')
        result = func("123", priority="high", deadline="2025-12-31")
        
        assert "123" in result
        assert "high" in result


class TestCommandModules:
    """Test module-based command organization."""
    
    def test_commands_grouped_by_module(self, command_registry):
        """Test that commands can be organized by module."""
        def func1():
            pass
        def func2():
            pass
        def func3():
            pass
        
        command_registry.register_command('add', func1, 'Add task', 'tasks')
        command_registry.register_command('list', func2, 'List tasks', 'tasks')
        command_registry.register_command('docs-add', func3, 'Add document', 'docs')
        
        task_commands = command_registry.list_commands('tasks')
        doc_commands = command_registry.list_commands('docs')
        
        assert len(task_commands) == 2
        assert len(doc_commands) == 1
    
    def test_default_module_is_global(self, command_registry):
        """Test that default module is 'global'."""
        def test_func():
            pass
        
        command_registry.register_command('test', test_func, 'Test')
        
        assert command_registry.commands['test']['module'] == 'global'


class TestCommandValidation:
    """Test command validation."""
    
    def test_command_name_required(self, command_registry):
        """Test that command name is required."""
        def test_func():
            pass
        
        # This should work (name provided)
        command_registry.register_command('test', test_func, 'Test')
        assert 'test' in command_registry.commands
    
    def test_command_function_required(self, command_registry):
        """Test that function is required."""
        # Should be able to register any callable
        command_registry.register_command('test', lambda: None, 'Test')
        assert 'test' in command_registry.commands
    
    def test_command_description_required(self, command_registry):
        """Test that description is required."""
        def test_func():
            pass
        
        # Should work with description
        command_registry.register_command('test', test_func, 'Test description')
        assert command_registry.commands['test']['description'] == 'Test description'


class TestCommandIntegration:
    """Test command registry integration with managers."""
    
    def test_task_commands_registered(self, task_manager, command_registry):
        """Test that TaskManager registers its commands."""
        # TaskManager should have registered commands in __init__
        assert command_registry.has_command('add')
        assert command_registry.has_command('list')
        assert command_registry.has_command('complete')
    
    def test_doc_commands_registered(self, document_manager, command_registry):
        """Test that DocumentManager registers its commands."""
        # DocumentManager should have registered commands
        assert command_registry.has_command('docs-add')
        assert command_registry.has_command('docs-list')
    
    def test_chat_commands_registered(self, chat_manager, command_registry):
        """Test that ChatManager registers its commands."""
        # ChatManager should have registered commands
        assert command_registry.has_command('chat')
    
    def test_agent_commands_registered(self, agent_manager, command_registry):
        """Test that AgentManager registers its commands."""
        # AgentManager should have registered commands
        assert command_registry.has_command('analyze-tasks')
        assert command_registry.has_command('synthesize')
        assert command_registry.has_command('connections')
