import json
from pathlib import Path

class JSONStorage:
    """Static utility class for JSON file operations.
    
    Provides low-level methods for loading, saving, and ensuring JSON files
    exist with proper error handling. All methods are static and can be called
    without instantiation.
    """
    
    @staticmethod
    def load(filepath):
        """Read JSON file and return its content as a dictionary.
        
        Safely loads a JSON file with error handling. Returns an empty
        dictionary if the file doesn't exist or contains invalid JSON.
        
        Args:
            filepath (str or Path): Path to the JSON file to load.
        
        Returns:
            dict: The parsed JSON content as a dictionary, or an empty
                dictionary if the file is not found or invalid.
        """
        try:
            with open(filepath, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def save(filepath, data):
        """Write dictionary data to a JSON file.
        
        Serializes and writes data to a JSON file with 2-space indentation
        for readability.
        
        Args:
            filepath (str or Path): Path where the JSON file will be saved.
            data (dict): Dictionary data to serialize and write.
        
        Raises:
            IOError: If the file cannot be written.
            TypeError: If the data is not JSON-serializable.
        """
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=2)

    @staticmethod
    def ensure_file_exists(filepath, default_data):
        """Ensure the JSON file exists, creating it with default data if necessary.
        
        Creates the file and all parent directories if they don't exist.
        If the file already exists, no action is taken.
        
        Args:
            filepath (str or Path): Path to the JSON file to ensure exists.
            default_data (dict): Default data to write if the file doesn't exist.
        
        Raises:
            IOError: If directories or file cannot be created.
        """
        path = Path(filepath)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            JSONStorage.save(filepath, default_data)

class DataManager:
    """High-level manager for all application data storage.
    
    Provides centralized access to tasks, documents, chat history, and other
    data files. Automatically initializes required files with default structures
    on first use.
    
    Attributes:
        data_dir (Path): Root directory for all data storage.
        tasks_file (Path): Path to tasks.json file.
        docs_metadata_file (Path): Path to docs_metadata.json file.
        chat_history_file (Path): Path to chat_history.json file.
    """
    
    def __init__(self, data_dir):
        """Initialize the DataManager with a data directory.
        
        Creates necessary data files with default structures if they don't exist.
        
        Args:
            data_dir (str or Path): Path to the root data directory.
        """
        self.data_dir = Path(data_dir)
        self.tasks_file = self.data_dir / 'tasks.json'
        self.docs_metadata_file = self.data_dir / 'docs_metadata.json'
        self.chat_history_file = self.data_dir / 'chat_history.json'

        # Ensure default files exist
        JSONStorage.ensure_file_exists(self.tasks_file, {"folders": {"default": []}, "current_folder": "default"})
        JSONStorage.ensure_file_exists(self.docs_metadata_file, [])
        JSONStorage.ensure_file_exists(self.chat_history_file, {"conversations": []})
    
    def load(self, filename):
        """Load a JSON file from the data directory.
        
        Args:
            filename (str): Name of the JSON file to load (relative to data_dir).
        
        Returns:
            dict: The parsed JSON content, or empty dict if file not found.
        """
        filepath = self.data_dir / filename
        return JSONStorage.load(filepath)
    
    def save(self, filename, data):
        """Save data to a JSON file in the data directory.
        
        Args:
            filename (str): Name of the JSON file to save (relative to data_dir).
            data (dict): Dictionary data to serialize and save.
        
        Raises:
            IOError: If the file cannot be written.
        """
        filepath = self.data_dir / filename
        JSONStorage.save(filepath, data)
    
    def get_current_folder(self):
        """Get the current task folder name.
        
        Returns:
            str: The name of the currently active task folder, defaults to 'default'.
        """
        data = JSONStorage.load(self.tasks_file)
        return data.get("current_folder", "default")
    
    def set_current_folder(self, folder_name):
        """Set the current task folder name.
        
        Args:
            folder_name (str): The name of the folder to set as current.
        
        Raises:
            IOError: If tasks file cannot be saved.
        """
        data = JSONStorage.load(self.tasks_file)
        data["current_folder"] = folder_name
        JSONStorage.save(self.tasks_file, data)

    def get_tasks(self, folder_name='default'):
        """Load tasks.json and return tasks for the specified folder.
        
        Args:
            folder_name (str): Name of the task folder. Defaults to 'default'.
        
        Returns:
            list[dict]: List of task dictionaries for the specified folder,
                or empty list if folder doesn't exist.
        """
        data = JSONStorage.load(self.tasks_file)
        return data.get("folders", {}).get(folder_name, [])

    def save_tasks(self, tasks, folder_name='default'):
        """Save tasks to tasks.json for the specified folder.
        
        Args:
            tasks (list[dict]): List of task dictionaries to save.
            folder_name (str): Name of the task folder. Defaults to 'default'.
        
        Raises:
            IOError: If tasks file cannot be saved.
        """
        data = JSONStorage.load(self.tasks_file)
        if "folders" not in data:
            data["folders"] = {}
        data["folders"][folder_name] = tasks
        JSONStorage.save(self.tasks_file, data)

    def get_pdfs(self):
        """Load and return docs_metadata.json.
        
        Handles both legacy (object) and current (array) formats for document
        metadata storage.
        
        Returns:
            list[dict]: List of document metadata dictionaries. Returns empty
                list if no documents exist.
        """
        docs_data = JSONStorage.load(self.docs_metadata_file)
        # Return as array if it's already an array, otherwise get documents key
        if isinstance(docs_data, list):
            return docs_data
        return docs_data.get("documents", [])

    def save_pdf_metadata(self, pdf_data):
        """Save document metadata to docs_metadata.json.
        
        Appends new document metadata to the existing metadata file.
        Handles both legacy (object) and current (array) formats.
        
        Args:
            pdf_data (dict): Document metadata dictionary to append.
        
        Raises:
            IOError: If metadata file cannot be saved.
        """
        data = JSONStorage.load(self.docs_metadata_file)
        # Handle both array format and object format
        if isinstance(data, list):
            data.append(pdf_data)
            JSONStorage.save(self.docs_metadata_file, data)
        else:
            if "documents" not in data:
                data["documents"] = []
            data["documents"].append(pdf_data)
            JSONStorage.save(self.docs_metadata_file, data)

    def get_chat_history(self):
        """Load and return chat_history.json.
        
        Returns:
            list[dict]: List of chat message dictionaries, or empty list
                if no history exists.
        """
        return JSONStorage.load(self.chat_history_file).get("conversations", [])

    def save_chat_message(self, role, content, context_type='general', context_id=None):
        """Append a chat message to chat_history.json.
        
        Args:
            role (str): The role of the message sender (e.g., 'user', 'assistant').
            content (str): The content/text of the message.
            context_type (str): Type of context for the message. Defaults to 'general'.
            context_id (str, optional): ID linking the message to a specific context
                (e.g., task ID, document ID). Defaults to None.
        
        Raises:
            IOError: If chat history file cannot be saved.
        """
        data = JSONStorage.load(self.chat_history_file)
        if "conversations" not in data:
            data["conversations"] = []
        message = {
            "role": role,
            "content": content,
            "context_type": context_type,
            "context_id": context_id
        }
        data["conversations"].append(message)
        JSONStorage.save(self.chat_history_file, data)
