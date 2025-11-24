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
from modules.task_module import TaskManager
from modules.docs_module import DocumentManager
from modules.chat_module import ChatManager
from modules.agent_module import AgentManager
from modules.settings_module import SettingsManager

class SessionState:
    """Manages session state for module switching and context."""
    def __init__(self):
        self.current_module = None  # None = main menu
        self.session_start = datetime.now()
        self.first_run = True  # Track if this is first command
        self.commands_executed = 0
    
    def set_module(self, module_name):
        """Set current active module."""
        self.current_module = module_name
    
    def reset_module(self):
        """Return to main menu."""
        self.current_module = None
    
    def increment_commands(self):
        """Increment command counter."""
        self.commands_executed += 1
        if self.first_run:
            self.first_run = False

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
    print("  tasks    - Task management and organization")
    print("  docs     - Document library (PDF, DOCX, TXT)")
    print("  chat     - AI chatbot assistant")
    print("  agent    - AI analysis and synthesis")
    print("  settings - Application configuration")
    print("\n💡 Commands:")
    print("  Type module name to enter (e.g., 'tasks', 'docs')")
    print("  status         - Show current context")
    print("  stats          - Show usage statistics")
    print("  help           - Show all commands")
    print("\n📦 Data Management:")
    print("  export         - Export all data to ZIP")
    print("  import         - Import data from ZIP")
    print("  backup         - Create manual backup")
    print("  restore        - Restore from backup")
    print("\n  exit, quit     - Exit program")
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
    
    print("\n🌐 Global Commands:")
    data_mgmt_cmds = []
    for name, desc in global_cmds:
        if name == 'quit':
            continue
        if name == 'exit':
            print("  exit, quit     - Exit program")
        elif name in ['export', 'import', 'backup', 'restore']:
            data_mgmt_cmds.append((name, desc))
        else:
            print(f"  {name:<14} - {desc}")
    
    if data_mgmt_cmds:
        print("\n📦 Data Management:")
        for name, desc in data_mgmt_cmds:
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
    
    print("\n⚙️  Settings:")
    print("  settings       - Manage application configuration")
    
    print("\n" + "=" * 60 + "\n")

def help_command_module(registry, module_name):
    """Show available commands for specific module."""
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
        'agent': ['agent'],
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
    
    if module_cmds:
        print(f"\n📦 {module_name.capitalize()} Commands:")
        for display_name, desc, _ in module_cmds:
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
    
    if data_mgmt_cmds:
        print("\n📦 Data Management:")
        for name, desc in data_mgmt_cmds:
            print(f"  {name:<14} - {desc}")
    
    print("=" * 60 + "\n")

def setup_command_history():
    """Setup readline command history if available."""
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


def save_command_history(history_file):
    """Save command history to file."""
    if not READLINE_AVAILABLE or not history_file:
        return
    
    try:
        readline.write_history_file(str(history_file))
    except Exception:
        pass  # Ignore errors saving history


def show_random_tip():
    """Display a random helpful tip."""
    tips = get_tips()
    tip = random.choice(tips)
    print(format_tip(tip))


def find_similar_commands(command_name, registry):
    """Find similar commands using fuzzy matching."""
    all_commands = [name for name, _, _ in registry.list_commands()]
    
    # Use difflib to find close matches
    matches = difflib.get_close_matches(command_name, all_commands, n=3, cutoff=0.6)
    return matches


def log_error_to_file(error, context=""):
    """Log error details to error log file."""
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

    # Initialize SettingsManager first (other modules may use settings)
    settings_manager = SettingsManager(data_manager, registry)
    
    # Initialize TaskManager (this will register task commands)
    task_manager = TaskManager(data_manager, registry)
    
    # Initialize DocumentManager (this will register document commands)
    document_manager = DocumentManager(data_manager, registry)
    
    # Initialize ChatManager (this will register chat commands)
    chat_manager = ChatManager(data_manager, registry)
    
    # Initialize AgentManager (this will register agent commands)
    agent_manager = AgentManager(data_manager, task_manager, registry, document_manager)
    
    # Initialize BackupManager
    backup_manager = BackupManager(data_manager.data_dir)
    
    # Perform auto-backup on startup
    created, backup_path = backup_manager.auto_backup()
    if created:
        print(format_info(f"Auto-backup created: {backup_path.name}"))

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
            total_pages = sum(doc.get('page_count', 0) for doc in docs_data)
            summarized = sum(1 for doc in docs_data if doc.get('summary'))
            
            print(f"\nDocuments:")
            print(f"  Total PDFs:    {pdf_count}")
            print(f"  Total DOCX:    {docx_count}")
            print(f"  Total TXT:     {txt_count}")
            print(f"  Total Pages:   {total_pages}")
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
        
        # API cost statistics (from task manager session)
        if hasattr(task_manager, 'session_cost') and task_manager.session_cost > 0:
            print(f"\nAPI Usage (This Session):")
            print(f"  Estimated Cost: ${task_manager.session_cost:.4f}")
        
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
            
            print(format_info(f"✓ Exporting {pluralize(total_tasks, 'task')} across {len(folders)} {pluralize(len(folders), 'folder')}"))
            
            docs_data = document_manager.data_manager.load("docs_metadata.json")
            if docs_data:
                storage_stats = backup_manager.get_storage_stats()
                print(format_info(f"✓ Exporting {len(docs_data)} {pluralize(len(docs_data), 'document')}, {storage_stats['docs_mb']:.1f} MB"))
            
            print(format_info("✓ Exporting configuration"))
            print(format_info("✓ Creating README"))
            
            # Create export
            export_path = backup_manager.export_data()
            
            # Get file size
            size_mb = export_path.stat().st_size / (1024 * 1024)
            
            print(format_success(f"\nExport complete: {export_path}"))
            print(format_info(f"Size: {size_mb:.1f} MB"))
        
        except Exception as e:
            print(format_error(f"Export failed: {str(e)}"))
    
    def cmd_import(*args):
        """Import data from export file."""
        if not args:
            print(format_error("Usage: import <export_file>"))
            print(format_info("Example: import exports/pkms_export_20251122_103000.zip"))
            return
        
        import_file = ' '.join(args)
        
        try:
            # Check if file exists
            import_path = Path(import_file)
            if not import_path.exists():
                # Try in exports directory
                import_path = backup_manager.export_dir / import_file
                if not import_path.exists():
                    print(format_error(f"Import file not found: {import_file}"))
                    return
            
            # Ask for import mode
            print("\nImport mode:")
            print("  merge   - Combine with existing data (recommended)")
            print("  replace - Replace all current data (creates backup first)")
            print("  cancel  - Cancel import")
            
            mode = input("\nSelect mode (merge/replace/cancel): ").strip().lower()
            
            if mode not in ['merge', 'replace']:
                print(format_warning("Import cancelled"))
                return
            
            if mode == 'replace':
                if not confirm_action("This will replace ALL data. Continue?", require_yes=True):
                    print(format_warning("Import cancelled"))
                    return
            
            print(f"\nImporting data in '{mode}' mode...")
            
            # Perform import
            stats = backup_manager.import_data(str(import_path), mode)
            
            print(format_success("\nImport complete!"))
            print(format_info(f"Imported: {pluralize(stats['tasks'], 'task')}, {pluralize(stats['documents'], 'document')}"))
            if stats['settings']:
                print(format_info("Settings imported"))
            
            # Reload managers
            print(format_info("\nReloading data..."))
            task_manager.data = task_manager.data_manager.load("tasks.json") or {"folders": {"default": []}, "current_folder": "default"}
            task_manager.tasks = task_manager.data["folders"].get(task_manager.data["current_folder"], [])
            document_manager.documents = document_manager.data_manager.load("docs_metadata.json") or []
        
        except Exception as e:
            print(format_error(f"Import failed: {str(e)}"))
    
    def cmd_backup(*args):
        """Create manual backup."""
        print("\nCreating backup...")
        
        try:
            backup_path = backup_manager.create_backup(auto=False)
            size_mb = backup_path.stat().st_size / (1024 * 1024)
            
            print(format_success(f"Backup saved: {backup_path.name}"))
            print(format_info(f"Location: {backup_path}"))
            print(format_info(f"Size: {size_mb:.2f} MB"))
        
        except Exception as e:
            print(format_error(f"Backup failed: {str(e)}"))
    
    def cmd_restore(*args):
        """Restore from backup."""
        if not args:
            # List available backups
            backups = backup_manager.list_backups()
            if not backups:
                print(format_info("No backups available"))
                return
            
            print("\nAvailable backups:")
            print("=" * 60)
            for filename, size_mb, created, is_auto in backups:
                backup_type = "[AUTO]" if is_auto else "[MANUAL]"
                print(f"  {backup_type} {filename}")
                print(f"    Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"    Size: {size_mb:.2f} MB")
                print()
            
            print(format_info("Usage: restore <backup_filename>"))
            return
        
        backup_file = args[0]
        
        try:
            # Confirm restoration
            if not confirm_action(f"Restore from '{backup_file}'? This will replace current data.", require_yes=True):
                print(format_warning("Restore cancelled"))
                return
            
            print(f"\nRestoring from backup...")
            
            # Perform restoration
            backup_manager.restore_backup(backup_file)
            
            print(format_success("Restore complete!"))
            print(format_info("Please restart the program to load restored data."))
        
        except Exception as e:
            print(format_error(f"Restore failed: {str(e)}"))

    # Register global commands
    registry.register_command('help', cmd_help, 'Show available commands', 'global')
    registry.register_command('home', cmd_home, 'Return to main menu', 'global')
    registry.register_command('menu', cmd_home, 'Return to main menu', 'global')
    registry.register_command('status', cmd_status, 'Show current context', 'global')
    registry.register_command('stats', cmd_stats, 'Show usage statistics', 'global')
    registry.register_command('export', cmd_export, 'Export all data to ZIP', 'global')
    registry.register_command('import', cmd_import, 'Import data from ZIP', 'global')
    registry.register_command('backup', cmd_backup, 'Create manual backup', 'global')
    registry.register_command('restore', cmd_restore, 'Restore from backup', 'global')
    registry.register_command('exit', exit_command, 'Exit program', 'global')
    registry.register_command('quit', exit_command, 'Exit program', 'global')
    
    # Register module entry commands
    registry.register_command('tasks', cmd_tasks, 'Enter tasks module', 'global')
    registry.register_command('docs', cmd_docs, 'Enter docs module', 'global')
    registry.register_command('agent', cmd_agent_module, 'Enter agent module', 'global')

    # Setup command history
    history_file = setup_command_history()
    
    # Show initial main menu
    stats = get_quick_stats(task_manager, document_manager)
    show_main_menu(stats)
    
    # Show tip on first run
    if session.first_run:
        print()
        show_random_tip()
        print()

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
            elif session.current_module == 'settings':
                prompt = "settings> "
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
                # Check if command is valid in current context
                command_module = registry.get_command_module(actual_command_name)
                
                # At main menu (no module), only allow global commands
                if session.current_module is None and command_module != 'global':
                    print(format_error(f"Command '{command_name}' is not available at the main menu."))
                    # Suggest which module to enter
                    module_map = {
                        'tasks': 'tasks',
                        'folders': 'tasks',
                        'docs': 'docs',
                        'chat': 'chat',
                        'agent': 'agent',
                        'settings': 'settings'
                    }
                    suggested_module = module_map.get(command_module)
                    if suggested_module:
                        print(format_info(f"To use this command, enter the '{suggested_module}' module first."))
                        print(format_tip(f"Type: {suggested_module}"))
                    continue
                
                # In a module, check if command belongs to current module or is global
                if session.current_module and command_module not in ['global', session.current_module]:
                    # Special handling for tasks/folders since they're both in tasks module
                    if session.current_module == 'tasks' and command_module in ['tasks', 'folders']:
                        pass  # Allow it
                    else:
                        print(format_error(f"Command '{command_name}' is not available in the {session.current_module} module."))
                        if command_module == 'global':
                            print(format_info("This is a program command available from any module."))
                        else:
                            module_map = {
                                'tasks': 'tasks',
                                'folders': 'tasks',
                                'docs': 'docs',
                                'chat': 'chat',
                                'agent': 'agent',
                                'settings': 'settings'
                            }
                            suggested_module = module_map.get(command_module)
                            if suggested_module:
                                print(format_info(f"This command belongs to the '{suggested_module}' module."))
                                print(format_tip(f"Type: {suggested_module}"))
                        continue
                
                try:
                    # Execute command
                    command_function(*args)
                    session.increment_commands()
                    
                    # Show random tip every 10 commands
                    if session.commands_executed % 10 == 0 and session.commands_executed > 0:
                        print()
                        show_random_tip()
                        print()
                
                except TaskNotFoundError as e:
                    print(format_error(str(e)))
                
                except PDFNotFoundError as e:
                    print(format_error(str(e)))
                
                except InvalidInputError as e:
                    print(format_error(str(e)))
                
                except ValidationError as e:
                    print(format_error(str(e)))
                
                except APIError as e:
                    print(format_error(str(e)))
                
                except StorageError as e:
                    print(format_error(str(e)))
                    log_error_to_file(e, f"Command: {actual_command_name}")
                
                except PKMSError as e:
                    # Catch any other custom PKMS errors
                    print(format_error(str(e)))
                
                except KeyboardInterrupt:
                    # Ctrl+C during command execution - cancel operation
                    print("\n" + format_warning("Operation cancelled"))
                    continue
                
                except Exception as e:
                    # Unexpected error - log it and show generic message
                    print(format_error(f"An unexpected error occurred: {str(e)}"))
                    log_error_to_file(e, f"Command: {actual_command_name} {' '.join(args)}")
                    print(format_info("Error details have been logged to data/error.log"))
            
            else:
                # Command not found - suggest similar commands
                print(format_error(f"Unknown command: '{command_name}'"))
                
                similar = find_similar_commands(command_name, registry)
                if similar:
                    if len(similar) == 1:
                        print(format_tip(f"Did you mean '{similar[0]}'?"))
                    else:
                        suggestions = ', '.join([f"'{cmd}'" for cmd in similar])
                        print(format_tip(f"Did you mean: {suggestions}?"))
                else:
                    print(format_info("Type 'help' for available commands"))
        
        except KeyboardInterrupt:
            # Ctrl+C at prompt - ask to exit
            try:
                print()
                response = input("Exit program? (y/n): ").strip().lower()
                if response in ['y', 'yes']:
                    print("Goodbye!")
                    break
            except (KeyboardInterrupt, EOFError):
                # Double Ctrl+C or Ctrl+D - exit immediately
                print("\nGoodbye!")
                break
        
        except EOFError:
            # Ctrl+D - exit immediately
            print("\nGoodbye!")
            break
    
    # Save command history before exiting
    save_command_history(history_file)

if __name__ == '__main__':
    main()