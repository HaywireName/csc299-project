"""
Color management for PKMS application.

Provides ANSI color codes and theme management based on settings.
"""


class Colors:
    """ANSI color codes for terminal output."""
    
    # Reset
    RESET = '\033[0m'
    
    # Regular colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright/Light colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'


class ColorTheme:
    """Color theme manager for module-specific color schemes."""
    
    def __init__(self, settings_manager):
        """Initialize color theme with settings manager.
        
        Args:
            settings_manager: SettingsManager instance to check enable_colors setting.
        """
        self.settings_manager = settings_manager
    
    def is_enabled(self):
        """Check if colors are enabled in settings.
        
        Returns:
            bool: True if colors are enabled, False otherwise.
        """
        return self.settings_manager.get_setting('enable_colors')
    
    def apply(self, text, color_code):
        """Apply color code to text if colors are enabled.
        
        Args:
            text: Text to colorize.
            color_code: ANSI color code to apply.
        
        Returns:
            str: Colored text if enabled, plain text otherwise.
        """
        if self.is_enabled():
            return f"{color_code}{text}{Colors.RESET}"
        return text
    
    # Success/Error/Warning/Info formatters with colors
    def success(self, message):
        """Format success message with green color."""
        emoji = "✅"
        if self.is_enabled():
            return f"{Colors.BRIGHT_GREEN}{emoji} {message}{Colors.RESET}"
        return f"{emoji} {message}"
    
    def error(self, message):
        """Format error message with red color."""
        emoji = "❌"
        if self.is_enabled():
            return f"{Colors.BRIGHT_RED}{emoji} {message}{Colors.RESET}"
        return f"{emoji} {message}"
    
    def warning(self, message):
        """Format warning message with yellow color."""
        emoji = "⚠️"
        if self.is_enabled():
            return f"{Colors.BRIGHT_YELLOW}{emoji}  {message}{Colors.RESET}"
        return f"{emoji}  {message}"
    
    def info(self, message):
        """Format info message with blue color."""
        emoji = "ℹ️"
        if self.is_enabled():
            return f"{Colors.BRIGHT_BLUE}{emoji}  {message}{Colors.RESET}"
        return f"{emoji}  {message}"
    
    def tip(self, message):
        """Format tip message with cyan color."""
        emoji = "💡"
        if self.is_enabled():
            return f"{Colors.BRIGHT_CYAN}{emoji} {message}{Colors.RESET}"
        return f"{emoji} {message}"
    
    # Module-specific themes
    def tasks_header(self, text):
        """Format tasks module header with blue theme."""
        if self.is_enabled():
            return f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}"
        return text
    
    def tasks_prompt(self, folder):
        """Format tasks module prompt."""
        if self.is_enabled():
            return f"{Colors.BRIGHT_BLUE}tasks[{Colors.CYAN}{folder}{Colors.BRIGHT_BLUE}]>{Colors.RESET} "
        return f"tasks[{folder}]> "
    
    def tasks_text(self, text):
        """Format tasks module text with blue color."""
        if self.is_enabled():
            return f"{Colors.BLUE}{text}{Colors.RESET}"
        return text
    
    def docs_header(self, text):
        """Format docs module header with green theme."""
        if self.is_enabled():
            return f"{Colors.BOLD}{Colors.GREEN}{text}{Colors.RESET}"
        return text
    
    def docs_prompt(self):
        """Format docs module prompt."""
        if self.is_enabled():
            return f"{Colors.BRIGHT_GREEN}docs>{Colors.RESET} "
        return "docs> "
    
    def docs_text(self, text):
        """Format docs module text with light green color."""
        if self.is_enabled():
            return f"{Colors.BRIGHT_GREEN}{text}{Colors.RESET}"
        return text
    
    def chat_prompt(self, context_type="general"):
        """Format chat module prompt with rainbow/colorful theme.
        
        Args:
            context_type: Current context type (general, tasks, docs, all)
        """
        if self.is_enabled():
            return f"{Colors.BRIGHT_MAGENTA}chat[{context_type}]>{Colors.RESET} "
        return f"chat[{context_type}]> "
    
    def chat_header(self, text):
        """Format chat module header with rainbow theme."""
        if self.is_enabled():
            # Rainbow effect: alternate colors for visual interest
            return f"{Colors.BOLD}{Colors.MAGENTA}{text}{Colors.RESET}"
        return text
    
    def chat_separator(self):
        """Format chat module separator with rainbow colors."""
        if self.is_enabled():
            # Create a colorful separator
            colors = [Colors.RED, Colors.YELLOW, Colors.GREEN, Colors.CYAN, Colors.BLUE, Colors.MAGENTA]
            separator = ""
            segment_length = 10
            for i, color in enumerate(colors):
                separator += f"{color}{'=' * segment_length}"
            separator += Colors.RESET
            return separator
        return "=" * 60
    
    def settings_prompt(self):
        """Format settings module prompt."""
        if self.is_enabled():
            return f"{Colors.BRIGHT_CYAN}settings>{Colors.RESET} "
        return "settings> "
    
    def main_prompt(self):
        """Format main menu prompt."""
        if self.is_enabled():
            return f"{Colors.BRIGHT_WHITE}pkms>{Colors.RESET} "
        return "pkms> "
    
    def separator(self):
        """Format standard separator."""
        if self.is_enabled():
            return f"{Colors.DIM}{'=' * 60}{Colors.RESET}"
        return "=" * 60
    
    def highlight(self, text):
        """Highlight important text."""
        if self.is_enabled():
            return f"{Colors.BOLD}{Colors.YELLOW}{text}{Colors.RESET}"
        return text
    
    def dim(self, text):
        """Dim less important text."""
        if self.is_enabled():
            return f"{Colors.DIM}{text}{Colors.RESET}"
        return text
    
    def priority_high(self, text):
        """Format high priority with red."""
        if self.is_enabled():
            return f"{Colors.BRIGHT_RED}{text}{Colors.RESET}"
        return text
    
    def priority_medium(self, text):
        """Format medium priority with yellow."""
        if self.is_enabled():
            return f"{Colors.BRIGHT_YELLOW}{text}{Colors.RESET}"
        return text
    
    def priority_low(self, text):
        """Format low priority with green."""
        if self.is_enabled():
            return f"{Colors.BRIGHT_GREEN}{text}{Colors.RESET}"
        return text
    
    def status_completed(self, text):
        """Format completed status with green."""
        if self.is_enabled():
            return f"{Colors.GREEN}{text}{Colors.RESET}"
        return text
    
    def status_pending(self, text):
        """Format pending status with blue."""
        if self.is_enabled():
            return f"{Colors.BRIGHT_BLUE}{text}{Colors.RESET}"
        return text


def get_color_theme(settings_manager):
    """Factory function to create a ColorTheme instance.
    
    Args:
        settings_manager: SettingsManager instance.
    
    Returns:
        ColorTheme: Configured color theme instance.
    """
    return ColorTheme(settings_manager)
