import sys
import json
import os
from datetime import datetime
from config import check_api_key
from core.commands import CommandRegistry, parse_command
from modules.task_module import TaskManager
from modules.docs_module import DocumentManager
from modules.chat_module import ChatManager
from modules.agent_module import AgentManager

class SessionState:
    """Manages session state for module switching and context."""
    def __init__(self):
        self.current_module = None  # None = main menu
        self.session_start = datetime.now()
    
    def set_module(self, module_name):
        """Set current active module."""
        self.current_module = module_name
    
    def reset_module(self):
        """Return to main menu."""
        self.current_module = None

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

def get_quick_stats(task_manager, document_manager):
    """Get quick statistics for main menu."""
    stats = {}
    
    # Task stats
    tasks_data = task_manager.data
    total_tasks = 0
    pending_tasks = 0
    completed_tasks = 0
    folders = tasks_data.get('folders', {})
    
    for folder_tasks in folders.values():
        total_tasks += len(folder_tasks)
        for task in folder_tasks:
            if task.get('status') == 'completed':
                completed_tasks += 1
            elif task.get('status') == 'pending':
                pending_tasks += 1
    
    stats['total_tasks'] = total_tasks
    stats['pending_tasks'] = pending_tasks
    stats['completed_tasks'] = completed_tasks
    stats['folder_count'] = len(folders)
    stats['folder_names'] = list(folders.keys())
    
    # Document stats
    docs_data = document_manager.data_manager.load("docs_metadata.json")
    if docs_data:
        pdf_count = sum(1 for doc in docs_data if doc.get('extension') == '.pdf')
        docx_count = sum(1 for doc in docs_data if doc.get('extension') == '.docx')
        txt_count = sum(1 for doc in docs_data if doc.get('extension') == '.txt')
        stats['pdf_count'] = pdf_count
        stats['docx_count'] = docx_count
        stats['txt_count'] = txt_count
        stats['total_docs'] = len(docs_data)
    else:
        stats['pdf_count'] = 0
        stats['docx_count'] = 0
        stats['txt_count'] = 0
        stats['total_docs'] = 0
    
    return stats

def show_main_menu(stats):
    """Display the main menu with quick stats."""
    print("\n" + "=" * 60)
    print("Welcome to PKMS Task Manager!")
    print("=" * 60)
    print("\n📊 Quick Stats:")
    print(f"  Tasks:     {stats['total_tasks']} ({stats['pending_tasks']} pending, {stats['completed_tasks']} completed)")
    
    doc_parts = []
    if stats['pdf_count'] > 0:
        doc_parts.append(f"{stats['pdf_count']} PDF{'s' if stats['pdf_count'] != 1 else ''}")
    if stats['docx_count'] > 0:
        doc_parts.append(f"{stats['docx_count']} DOCX")
    if stats['txt_count'] > 0:
        doc_parts.append(f"{stats['txt_count']} TXT")
    
    if doc_parts:
        print(f"  Documents: {', '.join(doc_parts)}")
    else:
        print(f"  Documents: 0")
    
    print(f"  Folders:   {stats['folder_count']} ({', '.join(stats['folder_names'])})")
    
    print("\n" + "=" * 60)
    print("\n📦 Available Modules:")
    print("  tasks  - Task management and organization")
    print("  docs   - Document library (PDF, DOCX, TXT)")
    print("  chat   - AI chatbot assistant")
    print("  agent  - AI analysis and synthesis")
    print("\n💡 Commands:")
    print("  Type module name to enter (e.g., 'tasks', 'docs')")
    print("  status         - Show current context")
    print("  help           - Show all commands")
    print("  exit, quit     - Exit program")
    print("=" * 60 + "\n")

def help_command_main_menu(registry):
    """Show available commands organized by module for main menu."""
    commands = registry.list_commands()
    
    # Organize commands by category
    global_cmds = []
    task_cmds = []
    doc_cmds = []
    chat_cmds = []
    agent_cmds = []
    
    for name, description, category in commands:
        if category == 'global':
            global_cmds.append((name, description))
        elif category in ['task', 'tasks', 'folders']:
            task_cmds.append((name, description))
        elif category in ['doc', 'docs']:
            doc_cmds.append((name, description))
        elif category == 'chat':
            chat_cmds.append((name, description))
        elif category == 'agent':
            agent_cmds.append((name, description))
    
    print("\n" + "=" * 60)
    print("Available Commands")
    print("=" * 60)
    
    print("\n🌐 Global Commands:")
    for name, desc in global_cmds:
        if name == 'quit':
            continue
        if name == 'exit':
            print("  exit, quit     - Exit program")
        else:
            print(f"  {name:<14} - {desc}")
    
    print("\n📋 Task Module Commands:")
    print("  (Type 'tasks' to enter task module)")
    for name, desc in task_cmds[:5]:  # Show first 5
        print(f"  {name:<14} - {desc}")
    if len(task_cmds) > 5:
        print(f"  ... and {len(task_cmds) - 5} more (enter module to see all)")
    
    print("\n📄 Document Module Commands:")
    print("  (Type 'docs' to enter docs module)")
    for name, desc in doc_cmds[:5]:
        print(f"  {name:<14} - {desc}")
    if len(doc_cmds) > 5:
        print(f"  ... and {len(doc_cmds) - 5} more (enter module to see all)")
    
    print("\n💬 Chat Module:")
    print("  chat           - Enter interactive chat mode")
    
    print("\n🤖 Agent Module Commands:")
    print("  (Type 'agent' to enter agent module)")
    for name, desc in agent_cmds:
        print(f"  {name:<14} - {desc}")
    
    print("\n" + "=" * 60 + "\n")

def help_command_module(registry, module_name):
    """Show available commands for specific module."""
    commands = registry.list_commands()
    
    # Filter commands for current module
    module_cmds = []
    global_cmds = []
    
    # Category mapping - some modules have multiple categories
    category_map = {
        'tasks': ['tasks', 'folders', 'task'],  # tasks module includes folder commands
        'docs': ['docs', 'doc'],
        'chat': ['chat'],
        'agent': ['agent']
    }
    
    target_categories = category_map.get(module_name, [])
    
    # Module prefixes to strip when displaying
    prefix_map = {
        'docs': 'docs-',
        'chat': 'chat-'
    }
    
    module_prefix = prefix_map.get(module_name, '')
    
    for name, description, category in commands:
        if category == 'global':
            # Skip module entry commands in module help
            if name not in ['tasks', 'docs', 'chat', 'agent']:
                global_cmds.append((name, description))
        elif category in target_categories:
            # Remove module prefix for display
            display_name = name.replace(module_prefix, '') if module_prefix else name
            module_cmds.append((display_name, description, name))  # Keep original name for reference
    
    print(f"\n{'=' * 60}")
    print(f"{module_name.capitalize()} Module - Available Commands")
    print("=" * 60)
    
    if module_cmds:
        print(f"\n📦 {module_name.capitalize()} Commands:")
        for display_name, desc, _ in module_cmds:
            print(f"  {display_name:<14} - {desc}")
    else:
        print(f"\nNo commands found for {module_name} module.")
    
    print("\n🌐 Global Commands:")
    for name, desc in global_cmds:
        if name == 'quit':
            continue
        if name == 'exit':
            print("  exit, quit     - Exit program")
        else:
            print(f"  {name:<14} - {desc}")
    
    print("=" * 60 + "\n")

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

    # Create session state, registry, and data manager
    session = SessionState()
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

    # Command functions with closures
    def enter_module(module_name):
        """Enter a specific module and show help."""
        session.set_module(module_name)
        print(f"\nEntering {module_name} module...")
        
        # Show module-specific welcome message
        if module_name == 'tasks':
            current_folder = task_manager.data.get('current_folder', 'default')
            print(f"Current folder: {current_folder}\n")
        elif module_name == 'docs':
            docs_count = len(document_manager.data_manager.load("docs_metadata.json") or [])
            print(f"Document library: {docs_count} documents\n")
        elif module_name == 'chat':
            print("Type 'chat' to start interactive chat mode\n")
        elif module_name == 'agent':
            print("AI-powered analysis and synthesis tools\n")
        
        # Show help for the module
        help_command_module(registry, module_name)
    
    def cmd_tasks(*args):
        """Enter tasks module."""
        enter_module('tasks')
    
    def cmd_docs(*args):
        """Enter docs module."""
        enter_module('docs')
    
    def cmd_chat_module(*args):
        """Enter chat module."""
        enter_module('chat')
    
    def cmd_agent_module(*args):
        """Enter agent module."""
        enter_module('agent')

    def cmd_home(*args):
        """Return to main menu."""
        if session.current_module:
            print("Returning to main menu...\n")
            session.reset_module()
            stats = get_quick_stats(task_manager, document_manager)
            show_main_menu(stats)
        else:
            print("Already at main menu.")

    def cmd_status(*args):
        """Show current context and session information."""
        print("\n" + "=" * 60)
        print("Current Context")
        print("=" * 60)
        
        if session.current_module:
            print(f"Module:  {session.current_module}")
            
            if session.current_module == 'tasks':
                current_folder = task_manager.data.get('current_folder', 'default')
                folders = task_manager.data.get('folders', {})
                task_count = len(folders.get(current_folder, []))
                print(f"Folder:  {current_folder} ({task_count} tasks)")
            elif session.current_module == 'docs':
                docs_data = document_manager.data_manager.load("docs_metadata.json")
                doc_count = len(docs_data) if docs_data else 0
                print(f"Library: {doc_count} documents")
        else:
            print("Module:  none (main menu)")
        
        print(f"Session: {session.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60 + "\n")

    def cmd_help(*args):
        """Show help based on current context."""
        if session.current_module:
            help_command_module(registry, session.current_module)
        else:
            help_command_main_menu(registry)

    # Register global commands
    registry.register_command('help', cmd_help, 'Show available commands', 'global')
    registry.register_command('home', cmd_home, 'Return to main menu', 'global')
    registry.register_command('menu', cmd_home, 'Return to main menu', 'global')
    registry.register_command('status', cmd_status, 'Show current context', 'global')
    registry.register_command('exit', exit_command, 'Exit program', 'global')
    registry.register_command('quit', exit_command, 'Exit program', 'global')
    
    # Register module entry commands
    registry.register_command('tasks', cmd_tasks, 'Enter tasks module', 'global')
    registry.register_command('docs', cmd_docs, 'Enter docs module', 'global')
    registry.register_command('agent', cmd_agent_module, 'Enter agent module', 'global')

    # Show initial main menu
    stats = get_quick_stats(task_manager, document_manager)
    show_main_menu(stats)

    # Main loop
    while True:
        try:
            # Generate dynamic prompt
            if session.current_module == 'tasks':
                current_folder = task_manager.data.get('current_folder', 'default')
                prompt = f"tasks[{current_folder}]> "
            elif session.current_module == 'docs':
                prompt = "docs> "
            elif session.current_module == 'chat':
                prompt = "chat> "
            elif session.current_module == 'agent':
                prompt = "agent> "
            else:
                prompt = "pkms> "
            
            user_input = input(prompt)
            command_name, args = parse_command(user_input)

            if not command_name:
                continue

            # Try to find command, with module-specific prefix if in a module
            command_function = None
            actual_command_name = command_name
            
            # If in a module, try module-prefixed command first
            if session.current_module:
                prefix_map = {
                    'docs': 'docs-',
                    'chat': 'chat-'
                }
                module_prefix = prefix_map.get(session.current_module, '')
                if module_prefix:
                    prefixed_name = f"{module_prefix}{command_name}"
                    command_function = registry.get_command(prefixed_name)
                    if command_function:
                        actual_command_name = prefixed_name
            
            # If not found with prefix, try without prefix
            if not command_function:
                command_function = registry.get_command(command_name)
                actual_command_name = command_name

            if command_function:
                try:
                    command_function(*args)
                except Exception as e:
                    print(f"Error executing command '{actual_command_name}': {e}")
            else:
                print(f"Unknown command: {command_name}. Type 'help' for available commands.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break

if __name__ == '__main__':
    main()