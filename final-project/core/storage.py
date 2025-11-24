import json
from pathlib import Path

class JSONStorage:
    @staticmethod
    def load(filepath):
        """Read JSON file and return its content as a dictionary."""
        try:
            with open(filepath, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def save(filepath, data):
        """Write dictionary data to a JSON file."""
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=2)

    @staticmethod
    def ensure_file_exists(filepath, default_data):
        """Ensure the JSON file exists, creating it with default data if necessary."""
        path = Path(filepath)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            JSONStorage.save(filepath, default_data)

class DataManager:
    def __init__(self, data_dir):
        """Initialize the DataManager with a data directory."""
        self.data_dir = Path(data_dir)
        self.tasks_file = self.data_dir / 'tasks.json'
        self.docs_metadata_file = self.data_dir / 'docs_metadata.json'
        self.chat_history_file = self.data_dir / 'chat_history.json'

        # Ensure default files exist
        JSONStorage.ensure_file_exists(self.tasks_file, {"folders": {"default": []}, "current_folder": "default"})
        JSONStorage.ensure_file_exists(self.docs_metadata_file, [])
        JSONStorage.ensure_file_exists(self.chat_history_file, {"conversations": []})
    
    def load(self, filename):
        """Load a JSON file from the data directory."""
        filepath = self.data_dir / filename
        return JSONStorage.load(filepath)
    
    def save(self, filename, data):
        """Save data to a JSON file in the data directory."""
        filepath = self.data_dir / filename
        JSONStorage.save(filepath, data)
    
    def get_current_folder(self):
        """Get the current task folder name."""
        data = JSONStorage.load(self.tasks_file)
        return data.get("current_folder", "default")
    
    def set_current_folder(self, folder_name):
        """Set the current task folder name."""
        data = JSONStorage.load(self.tasks_file)
        data["current_folder"] = folder_name
        JSONStorage.save(self.tasks_file, data)

    def get_tasks(self, folder_name='default'):
        """Load tasks.json and return tasks for the specified folder."""
        data = JSONStorage.load(self.tasks_file)
        return data.get("folders", {}).get(folder_name, [])

    def save_tasks(self, tasks, folder_name='default'):
        """Save tasks to tasks.json for the specified folder."""
        data = JSONStorage.load(self.tasks_file)
        if "folders" not in data:
            data["folders"] = {}
        data["folders"][folder_name] = tasks
        JSONStorage.save(self.tasks_file, data)

    def get_pdfs(self):
        """Load and return docs_metadata.json."""
        docs_data = JSONStorage.load(self.docs_metadata_file)
        # Return as array if it's already an array, otherwise get documents key
        if isinstance(docs_data, list):
            return docs_data
        return docs_data.get("documents", [])

    def save_pdf_metadata(self, pdf_data):
        """Save document metadata to docs_metadata.json."""
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
        """Load and return chat_history.json."""
        return JSONStorage.load(self.chat_history_file).get("conversations", [])

    def save_chat_message(self, role, content, context_type='general', context_id=None):
        """Append a chat message to chat_history.json."""
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
