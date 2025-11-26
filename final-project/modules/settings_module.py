import os
import json
from tabulate import tabulate


class SettingsManager:
    """Manages application settings and configuration.
    
    The SettingsManager handles all application settings including OpenAI API
    configuration, default preferences, and feature toggles. Provides validation,
    import/export functionality, and an interactive settings mode.
    
    Attributes:
        data_manager: Data persistence manager for settings.
        registry: Command registry for registering settings commands.
        settings_file: Filename for settings storage.
        defaults: Dictionary of default setting values.
        descriptions: Dictionary mapping setting keys to descriptions.
        valid_models: List of valid OpenAI model names.
        settings: Current settings dictionary.
    """
    
    def __init__(self, data_manager, registry):
        """Initialize SettingsManager with dependencies.
        
        Loads settings from storage (or uses defaults), defines setting
        metadata, and registers settings commands.
        
        Args:
            data_manager: Data persistence manager instance.
            registry: Command registry instance for registering commands.
        """
        self.data_manager = data_manager
        self.registry = registry
        self.settings_file = "settings.json"
        
        # Default settings
        self.defaults = {
            "openai_api_key": os.environ.get('OPENAI_API_KEY', ''),
            "default_model": "gpt-4o-mini",
            "default_folder": "default",
            "auto_summarize_threshold": 40,
            "max_summary_words": 600,
            "chat_history_limit": 10,
            "enable_colors": True
        }
        
        # Setting descriptions
        self.descriptions = {
            "openai_api_key": "OpenAI API key for AI features",
            "default_model": "Default OpenAI model to use",
            "default_folder": "Default task folder on startup",
            "auto_summarize_threshold": "Auto-summarize tasks longer than N words",
            "max_summary_words": "Maximum words in AI-generated summaries",
            "chat_history_limit": "Number of chat messages to keep in context",
            "enable_colors": "Enable colored terminal output"
        }
        
        # Valid models
        self.valid_models = [
            "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4",
            "gpt-3.5-turbo", "gpt-3.5-turbo-16k"
        ]
        
        self.settings = {}
        self._load_settings()
        self._register_commands()

    def _load_settings(self):
        """Load settings from file or use defaults.
        
        Loads settings from storage and merges with defaults to ensure all
        expected keys exist. Creates new settings file with defaults if none exists.
        """
        data = self.data_manager.load(self.settings_file)
        if data:
            # Merge with defaults to ensure all keys exist
            self.settings = {**self.defaults, **data}
        else:
            self.settings = self.defaults.copy()
            self._save_settings()

    def _save_settings(self):
        """Save settings to file.
        
        Persists current settings to the settings.json file.
        """
        self.data_manager.save(self.settings_file, self.settings)

    def get_setting(self, key):
        """Get a setting value.
        
        Args:
            key: Setting key to retrieve.
        
        Returns:
            Setting value, or None if key doesn't exist.
        """
        return self.settings.get(key)

    def set_setting(self, key, value):
        """Set a setting value with validation.
        
        Validates the new value before updating the setting. Persists
        changes immediately to storage.
        
        Args:
            key: Setting key to update.
            value: New value for the setting.
        
        Returns:
            tuple: (success (bool), message (str)) indicating result and
                description of the operation.
        """
        if key not in self.defaults:
            return False, f"Unknown setting: {key}"
        
        # Validate value
        valid, message = self._validate_setting(key, value)
        if not valid:
            return False, message
        
        # Update setting
        self.settings[key] = value
        self._save_settings()
        return True, f"Updated: {key} = {value}"

    def _validate_setting(self, key, value):
        """Validate a setting value.
        
        Checks if the provided value is valid for the given setting key.
        Different validation rules apply to different setting types (API keys,
        model names, numeric thresholds, boolean flags, etc.).
        
        Args:
            key: Setting key being validated.
            value: Value to validate.
        
        Returns:
            tuple: (valid (bool), message (str)) where valid indicates if
                validation passed and message describes the result.
        """
        if key == "openai_api_key":
            if not isinstance(value, str):
                return False, "API key must be a string"
            if value and not value.startswith("sk-"):
                return False, "API key must start with 'sk-'"
            return True, "Valid"
        
        elif key == "default_model":
            if value not in self.valid_models:
                return False, f"Invalid model. Valid options: {', '.join(self.valid_models)}"
            return True, "Valid"
        
        elif key == "default_folder":
            if not isinstance(value, str) or not value:
                return False, "Folder name must be a non-empty string"
            return True, "Valid"
        
        elif key == "auto_summarize_threshold":
            try:
                val = int(value)
                if val <= 0:
                    return False, "Threshold must be greater than 0"
                return True, "Valid"
            except ValueError:
                return False, "Threshold must be an integer"
        
        elif key == "max_summary_words":
            try:
                val = int(value)
                if val <= 0:
                    return False, "Max words must be greater than 0"
                return True, "Valid"
            except ValueError:
                return False, "Max words must be an integer"
        
        elif key == "chat_history_limit":
            try:
                val = int(value)
                if val <= 0:
                    return False, "Limit must be greater than 0"
                return True, "Valid"
            except ValueError:
                return False, "Limit must be an integer"
        
        elif key == "enable_colors":
            if isinstance(value, bool):
                return True, "Valid"
            if isinstance(value, str):
                if value.lower() in ['true', '1', 'yes', 'on']:
                    return True, "Valid"
                elif value.lower() in ['false', '0', 'no', 'off']:
                    return True, "Valid"
                else:
                    return False, "Value must be true/false, yes/no, on/off, or 1/0"
            return False, "Value must be boolean or boolean string"
        
        return True, "Valid"

    def reset_settings(self):
        """Reset all settings to defaults.
        
        Restores all settings to their default values and saves to storage.
        """
        self.settings = self.defaults.copy()
        self._save_settings()

    def export_settings(self, filepath):
        """Export settings to a file.
        
        Saves current settings to a JSON file for backup or transfer.
        
        Args:
            filepath: Path where settings should be exported.
        
        Returns:
            tuple: (success (bool), message (str)) indicating result and
                path or error details.
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True, f"Settings exported to: {filepath}"
        except Exception as e:
            return False, f"Failed to export settings: {e}"

    def import_settings(self, filepath):
        """Import settings from a file.
        
        Loads settings from a JSON file after validating all values.
        Merges imported settings with defaults to ensure completeness.
        
        Args:
            filepath: Path to settings file to import.
        
        Returns:
            tuple: (success (bool), message (str)) indicating result and
                path or error details.
        """
        try:
            with open(filepath, 'r') as f:
                imported = json.load(f)
            
            # Validate all settings before importing
            for key, value in imported.items():
                if key not in self.defaults:
                    return False, f"Unknown setting in file: {key}"
                valid, message = self._validate_setting(key, value)
                if not valid:
                    return False, f"Invalid value for {key}: {message}"
            
            # Import settings
            self.settings = {**self.defaults, **imported}
            self._save_settings()
            return True, f"Settings imported from: {filepath}"
        except FileNotFoundError:
            return False, f"File not found: {filepath}"
        except json.JSONDecodeError:
            return False, f"Invalid JSON file: {filepath}"
        except Exception as e:
            return False, f"Failed to import settings: {e}"

    def _mask_api_key(self, key):
        """Mask API key for display (show first 3 and last 3 chars).
        
        Args:
            key: API key to mask.
        
        Returns:
            str: Masked API key showing only first and last 3 characters,
                or '(not set)' if key is too short or empty.
        """
        if not key or len(key) < 10:
            return "(not set)"
        return f"{key[:3]}...{key[-3:]}"

    def _format_value(self, key, value):
        """Format a setting value for display.
        
        Formats values based on their type and purpose for user-friendly
        display (e.g., masks API keys, adds units to numeric values).
        
        Args:
            key: Setting key.
            value: Setting value to format.
        
        Returns:
            str: Formatted value string suitable for display.
        """
        if key == "openai_api_key":
            return f"{self._mask_api_key(value)} {'✓' if value else '✗'}"
        elif key == "enable_colors":
            return "enabled" if value else "disabled"
        elif key == "auto_summarize_threshold":
            return f"{value} words"
        elif key == "max_summary_words":
            return f"{value} words"
        elif key == "chat_history_limit":
            return f"{value} messages"
        else:
            return str(value)

    def show_settings(self):
        """Display all settings in formatted output.
        
        Shows current settings values, available commands, and setting
        descriptions in a formatted table.
        """
        print("\n" + "=" * 60)
        print("Current Settings")
        print("=" * 60)
        
        # Prepare data for display
        data = []
        labels = {
            "openai_api_key": "API Key:",
            "default_model": "Model:",
            "default_folder": "Default Folder:",
            "auto_summarize_threshold": "Auto-summarize:",
            "max_summary_words": "Max Summary:",
            "chat_history_limit": "Chat History:",
            "enable_colors": "Colors:"
        }
        
        for key in self.defaults.keys():
            label = labels.get(key, key + ":")
            value = self._format_value(key, self.settings.get(key))
            data.append([label, value])
        
        # Print in nice format
        for label, value in data:
            print(f"{label:<20} {value}")
        
        print("=" * 60)
        print("\nCommands:")
        print("  set <setting> <value>  - Change a setting")
        print("  reset                  - Reset all to defaults")
        print("  save <file>            - Save settings to file")
        print("  load <file>            - Load settings from file")
        print("  help                   - Show this help")
        print("  home                   - Return to main menu")
        print("\nAvailable settings:")
        
        # Define accepted arguments for each setting
        setting_args = {
            "openai_api_key": "<api-key starting with sk->",
            "default_model": "gpt-4o | gpt-4o-mini | gpt-4-turbo | gpt-4 | gpt-3.5-turbo",
            "default_folder": "<folder-name>",
            "auto_summarize_threshold": "<number> (words)",
            "max_summary_words": "<number> (words)",
            "chat_history_limit": "<number> (messages)",
            "enable_colors": "true | false | yes | no | on | off | 1 | 0"
        }
        
        for key in self.defaults.keys():
            desc = self.descriptions.get(key, "")
            args = setting_args.get(key, "<value>")
            print(f"  {key:<30} - {desc}")
            print(f"    {'':30}   Args: {args}")
        print("=" * 60 + "\n")

    def _settings_loop(self):
        """Settings mode interactive loop.
        
        Main loop for interactive settings mode. Handles user commands:
        set, reset, save, load, help, and home.
        """
        while True:
            try:
                user_input = input("settings> ").strip()
                
                if not user_input:
                    continue
                
                parts = user_input.split(maxsplit=2)
                command = parts[0].lower()
                
                if command in ['exit', 'quit', 'home']:
                    break
                
                elif command == 'set':
                    if len(parts) < 3:
                        print("Usage: set <setting> <value>")
                        continue
                    
                    key = parts[1]
                    value = parts[2]
                    
                    # Convert string values to appropriate types
                    if key == "enable_colors":
                        if value.lower() in ['true', '1', 'yes', 'on']:
                            value = True
                        elif value.lower() in ['false', '0', 'no', 'off']:
                            value = False
                    elif key in ["auto_summarize_threshold", "max_summary_words", "chat_history_limit"]:
                        try:
                            value = int(value)
                        except ValueError:
                            print(f"❌ Error: {key} must be an integer")
                            continue
                    
                    success, message = self.set_setting(key, value)
                    if success:
                        print(f"✓ {message}")
                    else:
                        print(f"❌ Error: {message}")
                        print(f"Available settings: {', '.join(self.defaults.keys())}")
                
                elif command == 'reset':
                    confirm = input("Reset all settings to defaults? (yes/no): ").strip().lower()
                    if confirm in ['yes', 'y']:
                        self.reset_settings()
                        print("✓ All settings reset to defaults")
                    else:
                        print("Reset cancelled")
                
                elif command == 'save':
                    if len(parts) < 2:
                        print("Usage: save <filepath>")
                        continue
                    
                    filepath = parts[1]
                    success, message = self.export_settings(filepath)
                    if success:
                        print(f"✓ {message}")
                    else:
                        print(f"❌ Error: {message}")
                
                elif command == 'load':
                    if len(parts) < 2:
                        print("Usage: load <filepath>")
                        continue
                    
                    filepath = parts[1]
                    success, message = self.import_settings(filepath)
                    if success:
                        print(f"✓ {message}")
                    else:
                        print(f"❌ Error: {message}")
                
                elif command == 'help':
                    self.show_settings()
                
                else:
                    print(f"Unknown command: {command}")
                    print("Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                print()
                break
            except EOFError:
                print()
                break

    def start_settings_mode(self):
        """Enter settings mode.
        
        Starts an interactive settings session where users can view and
        modify application settings.
        """
        print("\nEntering settings mode...\n")
        self.show_settings()
        self._settings_loop()
        print("Exiting settings mode.\n")

    def _register_commands(self):
        """Register settings-related commands.
        
        Registers the settings command with the command registry.
        """
        self.registry.register_command('settings', self.cmd_settings, 
                                      'Manage application settings', 'global')

    def cmd_settings(self, *args):
        """Command to enter settings mode.
        
        Launches the interactive settings management interface.
        
        Args:
            *args: Unused command arguments.
        """
        self.start_settings_mode()
