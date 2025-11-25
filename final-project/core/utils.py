"""
Utility functions for PKMS application.

Provides validation helpers, formatting utilities, and user interaction functions.
"""

from datetime import datetime
from dateutil import parser as date_parser
import sys


def validate_date(date_string):
    """
    Validate and parse a date string.
    
    Args:
        date_string: String to parse as a date
        
    Returns:
        datetime object if valid, None if invalid
    """
    if not date_string:
        return None
    
    try:
        # Try dateutil parser first (handles many formats)
        return date_parser.parse(date_string, fuzzy=True)
    except (ValueError, OverflowError):
        return None


def validate_priority(priority):
    """
    Validate and normalize priority value.
    
    Args:
        priority: Priority string to validate
        
    Returns:
        Normalized priority ('low', 'medium', 'high') or None if invalid
    """
    if not priority:
        return None
    
    priority_lower = priority.lower().strip()
    
    # Map shortcuts and variations
    priority_map = {
        'l': 'low',
        'low': 'low',
        'm': 'medium',
        'med': 'medium',
        'medium': 'medium',
        'h': 'high',
        'high': 'high',
        '1': 'low',
        '2': 'medium',
        '3': 'high'
    }
    
    return priority_map.get(priority_lower)


def validate_task_id(task_id, tasks):
    """
    Validate task ID and retrieve the task.
    
    Args:
        task_id: Task ID to validate
        tasks: List of tasks to search
        
    Returns:
        Task dict if found, None if not found
    """
    if not tasks:
        return None
    
    for task in tasks:
        if task.get('id') == task_id:
            return task
    
    return None


def confirm_action(prompt, require_yes=False):
    """
    Ask user for confirmation.
    
    Args:
        prompt: Confirmation prompt to display
        require_yes: If True, require explicit "yes". Otherwise accept "y".
        
    Returns:
        True if confirmed, False if cancelled
    """
    while True:
        try:
            response = input(f"⚠️  {prompt} ").strip().lower()
            
            if require_yes:
                if response in ['yes']:
                    return True
                elif response in ['no', 'n']:
                    return False
                else:
                    print("Please type 'yes' or 'no'")
            else:
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no']:
                    return False
                else:
                    print("Please type 'y' or 'n'")
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.")
            return False


def format_success(message):
    """Format a success message with emoji."""
    return f"✅ {message}"


def format_error(message):
    """Format an error message with emoji."""
    return f"❌ {message}"


def format_warning(message):
    """Format a warning message with emoji."""
    return f"⚠️  {message}"


def format_info(message):
    """Format an info message with emoji."""
    return f"ℹ️  {message}"


def format_tip(message):
    """Format a tip message with emoji."""
    return f"💡 {message}"


def truncate_text(text, max_length=100, suffix="..."):
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def safe_input(prompt, default=None):
    """
    Get user input with handling for interrupts.
    
    Args:
        prompt: Input prompt to display
        default: Default value if user provides no input
        
    Returns:
        User input string or default
    """
    try:
        response = input(prompt).strip()
        return response if response else default
    except (KeyboardInterrupt, EOFError):
        print()
        return default


def pluralize(count, singular, plural=None):
    """
    Return singular or plural form based on count.
    
    Args:
        count: Number to check
        singular: Singular form of word
        plural: Plural form (defaults to singular + 's')
        
    Returns:
        Formatted string with count and word
    """
    if plural is None:
        plural = singular + 's'
    
    word = singular if count == 1 else plural
    return f"{count} {word}"


def parse_yes_no(response):
    """
    Parse yes/no response.
    
    Args:
        response: User response string
        
    Returns:
        True for yes, False for no, None for invalid
    """
    response_lower = response.lower().strip()
    
    if response_lower in ['y', 'yes', 'yeah', 'yep', 'true', '1']:
        return True
    elif response_lower in ['n', 'no', 'nope', 'false', '0']:
        return False
    else:
        return None


def get_tips():
    """
    Get list of helpful tips for users.
    
    Returns:
        List of tip strings
    """
    return [
        "Use Tab completion to autocomplete commands (if your terminal supports it)",
        "Type 'help' in any module to see available commands",
        "Use Ctrl+C to cancel an operation without exiting the program",
        "The 'search' command works across tasks, documents, and chat history",
        "You can use shortcuts: 'h' for high priority, 'm' for medium, 'l' for low",
        "Date shortcuts: 'tomorrow', 'today', or formats like '12/25', '2025-12-25'",
        "Use 'folders' to organize your tasks into categories",
        "Chat mode has AI analysis features: /analyze, /synthesize, /connections",
        "Chatbot context modes: 'general', 'tasks', 'docs', or 'all' for everything",
        "Export your settings with 'settings > export backup.json'",
        "Documents are cached after first extraction for faster access",
        "Use 'cost' to track your OpenAI API usage in any module",
        "Type module names directly: 'tasks', 'docs', 'chat', 'settings'",
        "Use /synthesize in chat mode to create insights from tasks and documents",
        "Use 'edit' to modify tasks without recreating them",
        "Progress bars show during long operations like PDF extraction",
        "Type 'back' or 'exit' to return to the main menu"
    ]


def print_progress_bar(current, total, prefix='', suffix='', length=40, fill='█'):
    """
    Print a progress bar.
    
    Args:
        current: Current progress value
        total: Total value for 100%
        prefix: Prefix string before bar
        suffix: Suffix string after bar
        length: Character length of bar
        fill: Fill character for completed portion
    """
    if total == 0:
        percent = 100
    else:
        percent = int(100 * (current / float(total)))
    
    filled_length = int(length * current // total) if total > 0 else length
    bar = fill * filled_length + '░' * (length - filled_length)
    
    # Use \r to overwrite the same line
    sys.stdout.write(f'\r{prefix} {bar} {percent}% {suffix}')
    sys.stdout.flush()
    
    # Print newline when complete
    if current >= total:
        print()
