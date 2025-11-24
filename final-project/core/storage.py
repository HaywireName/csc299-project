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
        self.pdfs_dir = self.data_dir / 'pdfs'
        self.docx_dir = self.data_dir / 'docx'
        self.txts_dir = self.data_dir / 'txt'

        # Ensure default files and directories exist
        JSONStorage.ensure_file_exists(self.tasks_file, {"folders": {"default": []}, "current_folder": "default"})
        JSONStorage.ensure_file_exists(self.docs_metadata_file, {"documents": []})
        JSONStorage.ensure_file_exists(self.chat_history_file, {"conversations": []})
        self.pdfs_dir.mkdir(parents=True, exist_ok=True)
        self.docx_dir.mkdir(parents=True, exist_ok=True)
        self.txts_dir.mkdir(parents=True, exist_ok=True)

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

    def get_docs(self):
        """Load and return docs_metadata.json."""
        return JSONStorage.load(self.docs_metadata_file).get("documents", [])

    def save_doc_metadata(self, doc_data):
        """Save document metadata to docs_metadata.json."""
        data = JSONStorage.load(self.docs_metadata_file)
        if "documents" not in data:
            data["documents"] = []
        data["documents"].append(doc_data)
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

    def supported_doc_types(self):
        """Return a list of supported document file types."""
        return ["pdf", "docx", "txt"]

    def get_docs_folder(self, file_type):
        """Return the appropriate folder for the given file type."""
        if file_type == 'pdf':
            return self.pdfs_dir
        elif file_type == 'docx':
            return self.docx_dir
        elif file_type == 'txt':
            return self.txts_dir
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def save_doc(self, file_name, file_type, content):
        """Save a document to the appropriate folder based on its type."""
        folder = self.get_docs_folder(file_type)
        file_path = folder / file_name
        with open(file_path, 'w') as file:
            file.write(content)

    def list_docs(self, file_type):
        """List all documents of a specific type."""
        folder = self.get_docs_folder(file_type)
        return [file.name for file in folder.iterdir() if file.is_file()]
