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
        self.pdf_metadata_file = self.data_dir / 'pdf_metadata.json'
        self.chat_history_file = self.data_dir / 'chat_history.json'

        # Ensure default files exist
        JSONStorage.ensure_file_exists(self.tasks_file, {"folders": {"default": []}, "current_folder": "default"})
        JSONStorage.ensure_file_exists(self.pdf_metadata_file, {"documents": []})
        JSONStorage.ensure_file_exists(self.chat_history_file, {"conversations": []})

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
        """Load and return pdf_metadata.json."""
        return JSONStorage.load(self.pdf_metadata_file).get("documents", [])

    def save_pdf_metadata(self, pdf_data):
        """Save PDF metadata to pdf_metadata.json."""
        data = JSONStorage.load(self.pdf_metadata_file)
        if "documents" not in data:
            data["documents"] = []
        data["documents"].append(pdf_data)
        JSONStorage.save(self.pdf_metadata_file, data)

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
