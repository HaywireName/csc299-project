import sys
import json
import os
import random
import difflib
import traceback
from datetime import datetime
from pathlib import Path

# Try to import readline for command history (Unix/Mac)
try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    # Try pyreadline3 for Windows
    try:
        import pyreadline3 as readline
        READLINE_AVAILABLE = True
    except ImportError:
        READLINE_AVAILABLE = False

from config import check_api_key
from core.commands import CommandRegistry, parse_command
from core.errors import PKMSError, TaskNotFoundError, PDFNotFoundError, InvalidInputError, APIError, StorageError, ValidationError
from core.utils import format_error, format_success, format_warning, format_info, format_tip, get_tips, confirm_action, pluralize
from core.backup import BackupManager
from core.cost_tracker import CostTracker
from core.colors import get_color_theme
from modules.task_module import TaskManager
from modules.docs_module import DocumentManager
from modules.chat_module import ChatManager
from modules.agent_module import AgentManager
from modules.settings_module import SettingsManager

class SessionState:
    """Manages session state for module switching and context.
    
    Tracks the current active module, session start time, and command execution
    statistics for the PKMS application.
    
    Attributes:
        current_module (str | None): Name of the currently active module (tasks, docs, chat, agent, settings) or None for main menu.
        session_start (datetime): Timestamp when the session was initiated.
        first_run (bool): True if no commands have been executed yet.
        commands_executed (int): Count of commands executed in this session.
    """
    def __init__(self):
        """Initialize session state with default values."""
        self.current_module = None  # None = main menu
        self.session_start = datetime.now()
        self.first_run = True  # Track if this is first command
        self.commands_executed = 0
    
    def set_module(self, module_name: str) -> None:
        """Set current active module.
        
        Args:
            module_name: Name of module to activate (tasks, docs, chat, agent, settings).
        """
        self.current_module = module_name
    
    def reset_module(self) -> None:
        """Return to main menu by clearing current module."""
        self.current_module = None
    
    def increment_commands(self) -> None:
        """Increment command counter and clear first_run flag if needed."""
        self.commands_executed += 1
        if self.first_run:
            self.first_run = False

class DataManager:
    """Data manager for persisting data to JSON files.
    
    Provides centralized data storage operations for the PKMS application,
    handling JSON file persistence in the data/ directory.
    
    Attributes:
        data_dir (str): Absolute path to the data directory.
    """
    def __init__(self):
        """Initialize DataManager and ensure data directory exists."""
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)

    def get_current_folder(self) -> str:
        """Return the current folder name.
        
        Returns:
            str: The current folder name (always 'tasks').
        """
        return "tasks"

    def load(self, filename: str) -> dict | list | None:
        """Load data from JSON file.
        
        Args:
            filename: Name of the JSON file to load (e.g., 'tasks.json').
        
        Returns:
            Parsed JSON data as dict or list, or None if file doesn't exist or loading fails.
        
        Raises:
            Prints warning message if loading fails.
        """
        try:
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load {filename}: {e}")
        return None

    def save(self, filename: str, data: dict | list) -> None:
        """Save data to JSON file with pretty formatting.
        
        Args:
            filename: Name of the JSON file to save (e.g., 'tasks.json').
            data: Data to serialize to JSON (dict or list).
        
        Raises:
            Prints error message if saving fails.
        """
        try:
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error: Could not save {filename}: {e}")

def get_quick_stats(task_manager: 'TaskManager', document_manager: 'DocumentManager') -> dict:
    """Get quick statistics for main menu display.
    
    Collects task and document statistics across all folders and libraries.
    
    Args:
        task_manager: TaskManager instance for task statistics.
        document_manager: DocumentManager instance for document statistics.
    
    Returns:
        dict: Statistics dictionary with keys:
            - total_tasks: Total number of tasks across all folders
            - pending_tasks: Count of tasks with 'pending' status
            - completed_tasks: Count of tasks with 'completed' status
            - folder_count: Number of task folders
            - folder_names: List of folder names
            - pdf_count: Number of PDF documents
            - docx_count: Number of DOCX documents
            - txt_count: Number of TXT documents
            - total_docs: Total document count
    """
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

def show_main_menu(stats: dict) -> None:
    """Display the main menu with quick statistics and module information.
    
    Args:
        stats: Statistics dictionary from get_quick_stats() containing task and document counts.
    """
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
    print("\n\033[1mMODULES\033[0m")
    print("  tasks      (Type 'tasks' to enter task mode)")
    print("  docs       (Type 'docs' to enter docs mode)")
    print("  chat       (Type 'chat' to enter interactive chat mode)")
    
    print("\n\033[1mPROGRAM\033[0m")
    print("  help       Show all commands")
    print("  status     Show program statistics")
    print("  settings   Application configuration")
    print("  backup     Create manual backup")
    print("  restore    Restore from backup")
    print("  exit       Exit program")
    print("=" * 60 + "\n")

def help_command_main_menu(registry: 'CommandRegistry') -> None:
    """Show available commands organized by module for main menu.
    
    Displays categorized command list including global commands, module entry points,
    and data management commands.
    
    Args:
        registry: CommandRegistry instance containing all registered commands.
    """
    commands = registry.list_commands()
    
    # Organize commands by category
    global_cmds = []
    task_cmds = []
    doc_cmds = []
    chat_cmds = []
    agent_cmds = []
    
    settings_cmds = []
    
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
        elif category == 'settings':
            settings_cmds.append((name, description))
    
    print("\n" + "=" * 60)
    print("Available Commands")
    print("=" * 60)
    
    print("\n🌐 Program Commands:")
    data_mgmt_cmds = []
    for name, desc in global_cmds:
        if name == 'quit' or name == 'chat':
            continue
        if name == 'exit':
            print("  exit, quit     - Exit program")
        elif name in ['backup', 'restore']:
            data_mgmt_cmds.append((name, desc))
        else:
            print(f"  {name:<14} - {desc}")
    
    # Add settings command
    if settings_cmds:
        for name, desc in settings_cmds:
            print(f"  {name:<14} - {desc}")
    
    # Add data management commands to program section
    if data_mgmt_cmds:
        for name, desc in data_mgmt_cmds:
            print(f"  {name:<14} - {desc}")
    
    print("\n📋 Task Module Commands:")
    print("  (Type 'tasks' to enter task module)")
    for name, desc in task_cmds[:5]:  # Show first 5
        print(f"  {name:<14} - {desc}")
    if len(task_cmds) > 5:
        print(f"  ... and {len(task_cmds) - 5} more (enter module to see all)")
    
    print("\n📚 Document Module Commands:")
    print("  (Type 'docs' to enter docs module)")
    for name, desc in doc_cmds[:5]:
        display_name = name.replace('docs-', '')
        print(f"  {display_name:<14} - {desc}")
    if len(doc_cmds) > 5:
        print(f"  ... and {len(doc_cmds) - 5} more (enter module to see all)")
    
    print("\n💬 Chat Module:")
    print("  (Type 'docs' to enter docs module)")
    print("\n  Slash Commands (in chat mode):")
    print("  /home          - Return to main menu")
    print("  /clear         - Clear conversation history")
    print("  /context       - Switch context (general, tasks, pdfs, all)")
    print("  /refresh       - Reload context data")
    print("  /cost          - Show API usage and costs")
    print("  /analyze       - Analyze tasks with AI insights")
    print("  /synthesize    - Synthesize knowledge about a topic")
    print("  /connections   - Show connections between documents and tasks")
    print("  /help          - Show chat help")
    
    print("\n" + "=" * 60 + "\n")

def help_command_module(registry: 'CommandRegistry', module_name: str, color_theme=None) -> None:
    """Show available commands for specific module.
    
    Displays module-specific commands along with program commands available
    within the module context.
    
    Args:
        registry: CommandRegistry instance containing all registered commands.
        module_name: Name of the module to show help for (tasks, docs, chat, agent, settings).
        color_theme: ColorTheme instance for colored output (optional).
    """
    commands = registry.list_commands()
    
    # Filter commands for current module
    module_cmds = []
    program_cmds = []
    data_mgmt_cmds = []
    
    # Category mapping - some modules have multiple categories
    category_map = {
        'tasks': ['tasks', 'folders', 'task'],  # tasks module includes folder commands
        'docs': ['docs', 'doc'],
        'chat': ['chat'],
        'settings': ['settings']
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
            if name not in ['tasks', 'docs', 'chat', 'agent', 'settings']:
                # Separate data management commands
                if name in ['export', 'import', 'backup', 'restore']:
                    data_mgmt_cmds.append((name, description))
                else:
                    program_cmds.append((name, description))
        elif category in target_categories:
            # Remove module prefix for display
            display_name = name.replace(module_prefix, '') if module_prefix else name
            module_cmds.append((display_name, description, name))  # Keep original name for reference
    
    print(f"\n{'=' * 60}")
    print(f"{module_name.capitalize()} Module - Available Commands")
    print("=" * 60)
    
    # Choose appropriate icon for module
    module_icons = {
        'tasks': '📋',
        'docs': '📚',
        'chat': '💬',
        'settings': '⚙️'
    }
    icon = module_icons.get(module_name, '📦')
    
    if module_cmds:
        if color_theme:
            if module_name == 'tasks':
                print(color_theme.tasks_header(f"\n{icon} {module_name.capitalize()} Commands:"))
            elif module_name == 'docs':
                print(color_theme.docs_header(f"\n{icon} {module_name.capitalize()} Commands:"))
            elif module_name == 'chat':
                print(color_theme.chat_header(f"\n{icon} {module_name.capitalize()} Commands:"))
            else:
                print(f"\n{icon} {module_name.capitalize()} Commands:")
        else:
            print(f"\n{icon} {module_name.capitalize()} Commands:")
        
        for display_name, desc, _ in module_cmds:
            if color_theme:
                if module_name == 'tasks':
                    print(color_theme.tasks_text(f"  {display_name:<14} - {desc}"))
                elif module_name == 'docs':
                    print(color_theme.docs_text(f"  {display_name:<14} - {desc}"))
                elif module_name == 'chat':
                    print(f"  {display_name:<14} - {desc}")  # Keep white for chat
                else:
                    print(f"  {display_name:<14} - {desc}")
            else:
                print(f"  {display_name:<14} - {desc}")
    else:
        print(f"\nNo commands found for {module_name} module.")
    
    print("\n🌐 Program Commands:")
    for name, desc in program_cmds:
        if name == 'quit':
            continue
        if name == 'exit':
            print("  exit, quit     - Exit program")
        else:
            print(f"  {name:<14} - {desc}")
    
    # Merge data management into program commands section
    if data_mgmt_cmds:
        for name, desc in data_mgmt_cmds:
            print(f"  {name:<14} - {desc}")
    
    print("=" * 60 + "\n")

def setup_command_history() -> Path | None:
    """Setup readline command history if available.
    
    Configures readline for command history with 100-command limit and loads
    existing history from data/.history file.
    
    Returns:
        Path to history file if readline is available, None otherwise.
    """
    if not READLINE_AVAILABLE:
        return
    
    # Create history file path
    data_dir = Path(__file__).parent / 'data'
    history_file = data_dir / '.history'
    
    # Configure readline
    readline.set_history_length(100)
    
    # Load existing history if it exists
    if history_file.exists():
        try:
            readline.read_history_file(str(history_file))
        except Exception:
            pass  # Ignore errors loading history
    
    return history_file


def save_command_history(history_file: Path | None) -> None:
    """Save command history to file.
    
    Args:
        history_file: Path to history file, or None if readline unavailable.
    """
    if not READLINE_AVAILABLE or not history_file:
        return
    
    try:
        readline.write_history_file(str(history_file))
    except Exception:
        pass  # Ignore errors saving history


def show_random_tip(color_theme=None) -> None:
    """Display a random helpful tip from the tip library.
    
    Args:
        color_theme: Optional ColorTheme instance for colored output.
    """
    tips = get_tips()
    tip = random.choice(tips)
    print(format_tip(tip, color_theme))


def find_similar_commands(command_name: str, registry: 'CommandRegistry') -> list[str]:
    """Find similar commands using fuzzy matching.
    
    Uses difflib to find commands with similar names, useful for typo correction.
    
    Args:
        command_name: The mistyped or unknown command name.
        registry: CommandRegistry instance containing all registered commands.
    
    Returns:
        List of up to 3 similar command names with similarity >= 0.6.
    """
    all_commands = [name for name, _, _ in registry.list_commands()]
    
    # Use difflib to find close matches
    matches = difflib.get_close_matches(command_name, all_commands, n=3, cutoff=0.6)
    return matches


def log_error_to_file(error: Exception, context: str = "") -> None:
    """Log error details to error log file.
    
    Writes detailed error information including timestamp, context, error type,
    and full traceback to data/error.log.
    
    Args:
        error: The exception that occurred.
        context: Optional context string (e.g., command name) for debugging.
    """
    data_dir = Path(__file__).parent / 'data'
    error_log = data_dir / 'error.log'
    
    try:
        with open(error_log, 'a') as f:
            f.write(f"\n{'=' * 60}\n")
            f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            if context:
                f.write(f"Context: {context}\n")
            f.write(f"Error: {str(error)}\n")
            f.write(f"Type: {type(error).__name__}\n")
            f.write(f"Traceback:\n{traceback.format_exc()}\n")
    except Exception:
        pass  # Silently fail if can't write to log


def exit_command(cost_tracker=None) -> None:
    """Exit the program gracefully with session cost summary.
    
    Args:
        cost_tracker: CostTracker instance for session summary.
    """
    # Show session summary if cost tracker available
    if cost_tracker:
        session = cost_tracker.get_session_summary()
        
        print("\n" + "=" * 60)
        print("Session Summary")
        print("=" * 60)
        
        if session['total_cost'] > 0:
            print("\nAPI Usage This Session:")
            for operation, data in session['by_operation'].items():
                if data['count'] > 0:
                    op_name = operation.replace('_', ' ').title()
                    print(f"  {op_name:20} {data['count']:3} calls  ${data['cost']:.4f}")
            print(f"\nTotal Session Cost: ${session['total_cost']:.4f}")
            print(f"  Input tokens:  {session['total_input_tokens']:,}")
            print(f"  Output tokens: {session['total_output_tokens']:,}")
        else:
            print("\nNo API calls this session - $0.00")
        
        print("\n" + "=" * 60)
        print("Goodbye!")
        print("=" * 60 + "\n")
        
        # Save session to history
        cost_tracker.save_session()
    else:
        print("Goodbye!")
    
    exit()

def main() -> None:
    """Main entry point for PKMS Task Manager.
    
    Initializes all managers, sets up command registry, displays main menu,
    and runs the main command processing loop. Handles user input, command
    execution, error handling, and graceful shutdown.
    
    Raises:
        SystemExit: If OpenAI API key is not found or invalid.
    """
    # Check API key first
    if not check_api_key():
        sys.exit(1)

    # API key is valid, continue with program
    print("\n✓ OpenAI API key found and validated")

    # Create session state, registry, and data manager
    session = SessionState()
    registry = CommandRegistry()
    data_manager = DataManager()
    
    # Initialize cost tracker
    cost_tracker = CostTracker(data_manager.data_dir)

    # Initialize SettingsManager first (other modules may use settings)
    settings_manager = SettingsManager(data_manager, registry)
    
    # Initialize color theme (depends on settings)
    color_theme = get_color_theme(settings_manager)
    
    # Initialize TaskManager (this will register task commands)
    task_manager = TaskManager(data_manager, registry, cost_tracker)
    task_manager.color_theme = color_theme  # Inject color theme
    
    # Initialize DocumentManager (this will register document commands)
    document_manager = DocumentManager(data_manager, registry, cost_tracker)
    document_manager.color_theme = color_theme  # Inject color theme
    
    # Initialize AgentManager first (needed by ChatManager)
    agent_manager = AgentManager(data_manager, task_manager, registry, document_manager, cost_tracker)
    agent_manager.color_theme = color_theme  # Inject color theme
    
    # Initialize ChatManager with agent_manager and module managers (this will register chat commands)
    chat_manager = ChatManager(data_manager, registry, agent_manager, cost_tracker, task_manager, document_manager)
    chat_manager.color_theme = color_theme  # Inject color theme
    
    # Inject color theme into settings manager
    settings_manager.color_theme = color_theme
    
    # Initialize BackupManager
    backup_manager = BackupManager(data_manager.data_dir)
    
    # Perform auto-backup on startup
    created, backup_path = backup_manager.auto_backup()
    if created:
        print(format_info(f"Auto-backup created: {backup_path.name}", color_theme))

    # Command functions with closures
    def enter_module(module_name):
        """Enter a specific module and show help."""
        session.set_module(module_name)
        
        # Colorize entry message based on module
        if module_name == 'tasks':
            print(color_theme.tasks_header(f"\nEntering {module_name} module..."))
            current_folder = task_manager.data.get('current_folder', 'default')
            print(color_theme.tasks_text(f"Current folder: {current_folder}\n"))
        elif module_name == 'docs':
            print(color_theme.docs_header(f"\nEntering {module_name} module..."))
            docs_count = len(document_manager.data_manager.load("docs_metadata.json") or [])
            print(color_theme.docs_text(f"Document library: {docs_count} documents\n"))
        elif module_name == 'chat':
            print(color_theme.chat_header(f"\nEntering {module_name} module..."))
            print("Type 'chat' to start interactive chat mode\n")
        elif module_name == 'agent':
            print(f"\nEntering {module_name} module...")
            print("AI-powered analysis and synthesis tools\n")
        else:
            print(f"\nEntering {module_name} module...")
        
        # Show help for the module
        help_command_module(registry, module_name, color_theme)
    
    def cmd_tasks(*args):
        """Enter tasks module."""
        enter_module('tasks')
    
    def cmd_docs(*args):
        """Enter docs module."""
        enter_module('docs')
    
    def cmd_chat_module(*args):
        """Enter chat module."""
        enter_module('chat')
        # Show chat slash commands
        print("Chat Module Commands:")
        print("  chat             - Start interactive chat mode")
        print("  /help            - Show chat slash commands (in chat mode)")
        print("  Type 'help' for all available commands\n")
    
    def cmd_agent_module(*args):
        """Enter agent module."""
        enter_module('agent')

    def cmd_home(*args):
        """Return to main menu."""
        if session.current_module:
            print(color_theme.info("Returning to main menu...") + "\n")
            session.reset_module()
            stats = get_quick_stats(task_manager, document_manager)
            show_main_menu(stats)
        else:
            print(color_theme.info("Already at main menu."))

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
            help_command_module(registry, session.current_module, color_theme)
        else:
            help_command_main_menu(registry)
    
    def cmd_stats(*args):
        """Show comprehensive usage statistics."""
        print("\n" + "=" * 60)
        print("PKMS Statistics")
        print("=" * 60)
        
        # Task statistics
        tasks_data = task_manager.data
        folders = tasks_data.get('folders', {})
        total_tasks = 0
        pending_tasks = 0
        completed_tasks = 0
        overdue_tasks = 0
        
        for folder_tasks in folders.values():
            for task in folder_tasks:
                total_tasks += 1
                if task.get('status') == 'completed':
                    completed_tasks += 1
                elif task.get('status') == 'pending':
                    pending_tasks += 1
                    # Check if overdue
                    deadline = task.get('deadline')
                    if deadline:
                        try:
                            from dateutil import parser as date_parser
                            deadline_date = date_parser.parse(deadline)
                            if deadline_date < datetime.now():
                                overdue_tasks += 1
                        except:
                            pass
        
        print(f"\nTasks:")
        print(f"  Total:     {total_tasks}")
        print(f"  Pending:   {pending_tasks}")
        print(f"  Completed: {completed_tasks}")
        if overdue_tasks > 0:
            print(f"  Overdue:   {overdue_tasks}")
        
        # Folder statistics
        print(f"\nFolders: {len(folders)}")
        if folders:
            folder_stats = []
            for folder_name, folder_tasks in folders.items():
                folder_stats.append(f"{folder_name} ({len(folder_tasks)})")
            print(f"  {', '.join(folder_stats)}")
        
        # Document statistics
        docs_data = document_manager.data_manager.load("docs_metadata.json")
        if docs_data:
            total_docs = len(docs_data)
            pdf_count = sum(1 for doc in docs_data if doc.get('extension') == '.pdf')
            docx_count = sum(1 for doc in docs_data if doc.get('extension') == '.docx')
            txt_count = sum(1 for doc in docs_data if doc.get('extension') == '.txt')
            summarized = sum(1 for doc in docs_data if doc.get('summary'))
            
            print(f"\nDocuments:")
            print(f"  Total PDFs:    {pdf_count}")
            print(f"  Total DOCX:    {docx_count}")
            print(f"  Total TXT:     {txt_count}")
            print(f"  Summaries:     {summarized}")
        else:
            print(f"\nDocuments:")
            print(f"  Total: 0")
        
        # Storage statistics
        storage_stats = backup_manager.get_storage_stats()
        print(f"\nStorage:")
        print(f"  Documents:  {storage_stats['docs_mb']:.2f} MB")
        print(f"  Cache:      {storage_stats['cache_mb']:.2f} MB")
        print(f"  Data:       {storage_stats['json_mb']:.2f} MB")
        print(f"  Backups:    {storage_stats['backups_mb']:.2f} MB")
        print(f"  Total:      {storage_stats['total_mb']:.2f} MB")
        print("  " + "-" * 56)
        
        # API Usage & Costs
        print(f"\nAPI Usage & Costs:")
        session = cost_tracker.get_session_summary()
        if session['total_cost'] > 0:
            print("  Current Session:")
            for operation, data in session['by_operation'].items():
                if data['count'] > 0:
                    # Format operation name nicely
                    op_name = operation.replace('_', ' ').title()
                    print(f"    {op_name:20} {data['count']:3} calls  ${data['cost']:.4f}")
            print(f"    {'Session Total:':20} {'-':>3}        ${session['total_cost']:.4f}")
        else:
            print("  Current Session: No API calls yet")
        
        # Previous session cost
        prev_cost = cost_tracker.get_previous_session_cost()
        if prev_cost > 0:
            print(f"  Previous Session: ${prev_cost:.4f}")
        
        # All-time total
        all_time = cost_tracker.get_all_time_cost()
        session_count = cost_tracker.get_session_count()
        if session_count > 0:
            print(f"  All-Time Total:   ${all_time:.4f} ({session_count} sessions)")
        
        # Backup statistics
        backups = backup_manager.list_backups()
        if backups:
            latest_backup = backups[0]
            print(f"\nBackups:")
            print(f"  Total:        {len(backups)}")
            print(f"  Last Backup:  {latest_backup[2].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Backup Size:  {latest_backup[1]:.2f} MB")
        
        print("=" * 60 + "\n")
    
    def cmd_export(*args):
        """Create full export of all data."""
        print("\nCreating export archive...")
        
        try:
            # Count items for display
            tasks_data = task_manager.data
            folders = tasks_data.get('folders', {})
            total_tasks = sum(len(tasks) for tasks in folders.values())
            
            print(format_info(f"✓ Exporting {pluralize(total_tasks, 'task', color_theme)} across {len(folders)} {pluralize(len(folders), 'folder')}"))
            
            docs_data = document_manager.data_manager.load("docs_metadata.json")
            if docs_data:
                storage_stats = backup_manager.get_storage_stats()
                print(format_info(f"✓ Exporting {len(docs_data, color_theme)} {pluralize(len(docs_data), 'document')}, {storage_stats['docs_mb']:.1f} MB"))
            
            print(format_info("✓ Exporting configuration", color_theme))
            print(format_info("✓ Creating README", color_theme))
            
            # Create export
            export_path = backup_manager.export_data()
            
            # Get file size
            size_mb = export_path.stat().st_size / (1024 * 1024)
            
            print(format_success(f"\nExport complete: {export_path}", color_theme))
            print(format_info(f"Size: {size_mb:.1f} MB", color_theme))
        
        except Exception as e:
            print(format_error(f"Export failed: {str(e, color_theme)}"))
    
    def cmd_import(*args):
        """Import data from export file."""
        if not args:
            print(format_error("Usage: import <export_file>", color_theme))
            print(format_info("Example: import exports/pkms_export_20251122_103000.zip", color_theme))
            return
        
        import_file = ' '.join(args)
        
        try:
            # Check if file exists
            import_path = Path(import_file)
            if not import_path.exists():
                # Try in exports directory
                import_path = backup_manager.export_dir / import_file
                if not import_path.exists():
                    print(format_error(f"Import file not found: {import_file}", color_theme))
                    return
            
            # Ask for import mode
            print("\nImport mode:")
            print("  merge   - Combine with existing data (recommended)")
            print("  replace - Replace all current data (creates backup first)")
            print("  cancel  - Cancel import")
            
            mode = input("\nSelect mode (merge/replace/cancel): ").strip().lower()
            
            if mode not in ['merge', 'replace']:
                print(format_warning("Import cancelled", color_theme))
                return
            
            if mode == 'replace':
                if not confirm_action("This will replace ALL data. Continue?", require_yes=True):
                    print(format_warning("Import cancelled", color_theme))
                    return
            
            print(f"\nImporting data in '{mode}' mode...")
            
            # Perform import
            stats = backup_manager.import_data(str(import_path), mode)
            
            print(format_success("\nImport complete!", color_theme))
            print(format_info(f"Imported: {pluralize(stats['tasks'], 'task', color_theme)}, {pluralize(stats['documents'], 'document')}"))
            if stats['settings']:
                print(format_info("Settings imported", color_theme))
            
            # Reload managers
            print(format_info("\nReloading data...", color_theme))
            task_manager.data = task_manager.data_manager.load("tasks.json") or {"folders": {"default": []}, "current_folder": "default"}
            task_manager.tasks = task_manager.data["folders"].get(task_manager.data["current_folder"], [])
            document_manager.documents = document_manager.data_manager.load("docs_metadata.json") or []
        
        except Exception as e:
            print(format_error(f"Import failed: {str(e, color_theme)}"))
    
    def cmd_backup(*args):
        """Create manual backup with optional custom name."""
        custom_name = None
        if args:
            # Join all args to support names with spaces
            custom_name = ' '.join(args)
        
        print("\nCreating backup...")
        
        try:
            backup_path = backup_manager.create_backup(auto=False, custom_name=custom_name)
            size_mb = backup_path.stat().st_size / (1024 * 1024)
            
            print(format_success(f"Backup saved: {backup_path.name}", color_theme))
            print(format_info(f"Location: {backup_path}", color_theme))
            print(format_info(f"Size: {size_mb:.2f} MB", color_theme))
        
        except Exception as e:
            print(format_error(f"Backup failed: {str(e, color_theme)}"))
    
    def cmd_restore(*args):
        """Restore from backup."""
        if not args:
            # List available backups
            backups = backup_manager.list_backups()
            if not backups:
                print(format_info("No backups available", color_theme))
                return
            
            print("\nAvailable backups:")
            print("=" * 60)
            for filename, size_mb, created, is_auto in backups:
                backup_type = "[AUTO]" if is_auto else "[MANUAL]"
                print(f"  {backup_type} {filename}")
                print(f"    Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"    Size: {size_mb:.2f} MB")
                print()
            
            print(format_info("Usage: restore <backup_filename>", color_theme))
            return
        
        backup_file = args[0]
        
        try:
            # Confirm restoration
            if not confirm_action(f"Restore from '{backup_file}'? This will replace current data.", require_yes=True):
                print(format_warning("Restore cancelled", color_theme))
                return
            
            print(f"\nRestoring from backup...")
            
            # Perform restoration
            backup_manager.restore_backup(backup_file)
            
            print(format_success("Restore complete!", color_theme))
            print(format_info("Please restart the program to load restored data.", color_theme))
        
        except Exception as e:
            print(format_error(f"Restore failed: {str(e, color_theme)}"))

    # Create exit command with cost_tracker closure
    def cmd_exit(*args):
        """Exit program with session summary."""
        exit_command(cost_tracker)
    
    # Register global commands
    registry.register_command('help', cmd_help, 'Show available commands', 'global')
    registry.register_command('home', cmd_home, 'Return to main menu', 'global')
    registry.register_command('menu', cmd_home, 'Return to main menu', 'global')
    registry.register_command('status', cmd_status, 'Show program statistics', 'global')
    registry.register_command('backup', cmd_backup, 'Create manual backup', 'global')
    registry.register_command('restore', cmd_restore, 'Restore from backup', 'global')
    registry.register_command('exit', cmd_exit, 'Exit program', 'global')
    registry.register_command('quit', cmd_exit, 'Exit program', 'global')
    
    # Register module entry commands
    registry.register_command('tasks', cmd_tasks, 'Enter tasks module', 'global')
    registry.register_command('docs', cmd_docs, 'Enter docs module', 'global')
    # Note: 'chat' command is registered by ChatManager to enter interactive mode directly

    # Setup command history
    history_file = setup_command_history()
    
    # Show initial main menu
    stats = get_quick_stats(task_manager, document_manager)
    show_main_menu(stats)
    
    # Show tip on first run
    if session.first_run:
        print()
        show_random_tip(color_theme)
        print()

    # Main loop
    while True:
        try:
            # Generate dynamic prompt with colors
            if session.current_module == 'tasks':
                current_folder = task_manager.data.get('current_folder', 'default')
                prompt = color_theme.tasks_prompt(current_folder)
            elif session.current_module == 'docs':
                prompt = color_theme.docs_prompt()
            elif session.current_module == 'chat':
                prompt = color_theme.chat_prompt()
            elif session.current_module == 'settings':
                prompt = color_theme.settings_prompt()
            else:
                prompt = color_theme.main_prompt()
            
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
                # Check if command is valid in current context
                command_module = registry.get_command_module(actual_command_name)
                
                # At main menu (no module), only allow global commands
                if session.current_module is None and command_module != 'global':
                    print(format_error(f"Command '{command_name}' is not available at the main menu.", color_theme))
                    # Suggest which module to enter
                    module_map = {
                        'tasks': 'tasks',
                        'folders': 'tasks',
                        'docs': 'docs',
                        'chat': 'chat',
                        'settings': 'settings'
                    }
                    
                    # Check if command exists in multiple modules
                    common_commands = ['add', 'list', 'remove', 'view', 'search', 'summarize']
                    if command_name in common_commands:
                        print(format_info(f"To use this command, enter the 'tasks' or 'docs' module first.", color_theme))
                        print(format_tip(f"Type: tasks or docs", color_theme))
                    else:
                        suggested_module = module_map.get(command_module)
                        if suggested_module:
                            print(format_info(f"To use this command, enter the '{suggested_module}' module first.", color_theme))
                            print(format_tip(f"Type: {suggested_module}", color_theme))
                    continue
                
                # In a module, check if command belongs to current module or is global
                if session.current_module and command_module not in ['global', session.current_module]:
                    # Special handling for tasks/folders since they're both in tasks module
                    if session.current_module == 'tasks' and command_module in ['tasks', 'folders']:
                        pass  # Allow it
                    else:
                        print(format_error(f"Command '{command_name}' is not available in the {session.current_module} module.", color_theme))
                        if command_module == 'global':
                            print(format_info("This is a program command available from any module.", color_theme))
                        else:
                            module_map = {
                                'tasks': 'tasks',
                                'folders': 'tasks',
                                'docs': 'docs',
                                'chat': 'chat',
                                'settings': 'settings'
                            }
                            suggested_module = module_map.get(command_module)
                            if suggested_module:
                                print(format_info(f"This command belongs to the '{suggested_module}' module.", color_theme))
                                print(format_tip(f"Type: {suggested_module}", color_theme))
                        continue
                
                try:
                    # Execute command
                    command_function(*args)
                    session.increment_commands()
                    
                    # Show random tip every 10 commands
                    if session.commands_executed % 10 == 0 and session.commands_executed > 0:
                        print()
                        show_random_tip(color_theme)
                        print()
                
                except TaskNotFoundError as e:
                    print(format_error(str(e), color_theme))
                
                except PDFNotFoundError as e:
                    print(format_error(str(e), color_theme))
                
                except InvalidInputError as e:
                    print(format_error(str(e), color_theme))
                
                except ValidationError as e:
                    print(format_error(str(e), color_theme))
                
                except APIError as e:
                    print(format_error(str(e), color_theme))
                
                except StorageError as e:
                    print(format_error(str(e), color_theme))
                    log_error_to_file(e, f"Command: {actual_command_name}")
                
                except PKMSError as e:
                    # Catch any other custom PKMS errors
                    print(format_error(str(e), color_theme))
                
                except KeyboardInterrupt:
                    # Ctrl+C during command execution - cancel operation
                    print("\n" + format_warning("Operation cancelled", color_theme))
                    continue
                
                except Exception as e:
                    # Unexpected error - log it and show generic message
                    print(format_error(f"An unexpected error occurred: {str(e, color_theme)}", color_theme))
                    log_error_to_file(e, f"Command: {actual_command_name} {' '.join(args)}")
                    print(format_info("Error details have been logged to data/error.log", color_theme))
            
            else:
                # Command not found - suggest similar commands
                print(format_error(f"Unknown command: '{command_name}'", color_theme))
                
                similar = find_similar_commands(command_name, registry)
                if similar:
                    if len(similar) == 1:
                        print(format_tip(f"Did you mean '{similar[0]}'?", color_theme))
                    else:
                        suggestions = ', '.join([f"'{cmd}'" for cmd in similar])
                        print(format_tip(f"Did you mean: {suggestions}?", color_theme))
                else:
                    print(format_info("Type 'help' for available commands", color_theme))
        
        except KeyboardInterrupt:
            # Ctrl+C at prompt - ask to exit
            try:
                print()
                response = input("Exit program? (y/n): ").strip().lower()
                if response in ['y', 'yes']:
                    # Show session summary before exit
                    session = cost_tracker.get_session_summary()
                    if session['total_cost'] > 0:
                        print(f"\nSession Cost: ${session['total_cost']:.4f}")
                    print("Goodbye!")
                    cost_tracker.save_session()
                    break
            except (KeyboardInterrupt, EOFError):
                # Double Ctrl+C or Ctrl+D - exit immediately
                print("\n\nInterrupted!")
                session = cost_tracker.get_session_summary()
                if session['total_cost'] > 0:
                    print(f"Session Cost: ${session['total_cost']:.4f}")
                print("Goodbye!")
                cost_tracker.save_session()
                break
        
        except EOFError:
            # Ctrl+D - exit immediately
            print("\nGoodbye!")
            cost_tracker.save_session()
            break
    
    # Save command history before exiting
    save_command_history(history_file)
    
    # Final save of cost tracking (in case exit wasn't through command)
    cost_tracker.save_session()

if __name__ == '__main__':
    main()