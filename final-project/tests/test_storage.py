"""
Tests for core.storage module (JSONStorage and DataManager).
"""
import pytest
import json
import os
from pathlib import Path
from core.storage import JSONStorage, DataManager


class TestJSONStorage:
    """Test JSONStorage class."""
    
    def test_save_creates_file(self, temp_data_dir):
        """Test that save creates a new file."""
        filepath = temp_data_dir / "test.json"
        data = {"key": "value"}
        
        JSONStorage.save(filepath, data)
        
        assert filepath.exists()
        with open(filepath, 'r') as f:
            loaded = json.load(f)
        assert loaded == data
    
    def test_save_overwrites_file(self, temp_data_dir):
        """Test that save overwrites existing file."""
        filepath = temp_data_dir / "test.json"
        
        # Save initial data
        JSONStorage.save(filepath, {"key": "value1"})
        # Save new data
        JSONStorage.save(filepath, {"key": "value2"})
        
        with open(filepath, 'r') as f:
            loaded = json.load(f)
        assert loaded == {"key": "value2"}
    
    def test_load_existing_file(self, temp_data_dir):
        """Test loading an existing JSON file."""
        filepath = temp_data_dir / "test.json"
        data = {"tasks": [], "count": 0}
        
        with open(filepath, 'w') as f:
            json.dump(data, f)
        
        loaded = JSONStorage.load(filepath)
        assert loaded == data
    
    def test_load_missing_file(self, temp_data_dir):
        """Test loading a non-existent file returns empty dict."""
        filepath = temp_data_dir / "missing.json"
        
        loaded = JSONStorage.load(filepath)
        
        assert loaded == {}
    
    def test_load_corrupted_file(self, corrupted_json_file):
        """Test loading a corrupted JSON file returns empty dict."""
        loaded = JSONStorage.load(corrupted_json_file)
        
        assert loaded == {}
    
    def test_ensure_file_exists_creates_file(self, temp_data_dir):
        """Test ensure_file_exists creates file with default data."""
        filepath = temp_data_dir / "new_file.json"
        default_data = {"folders": {"default": []}}
        
        JSONStorage.ensure_file_exists(filepath, default_data)
        
        assert filepath.exists()
        loaded = JSONStorage.load(filepath)
        assert loaded == default_data
    
    def test_ensure_file_exists_preserves_existing(self, temp_data_dir):
        """Test ensure_file_exists doesn't overwrite existing file."""
        filepath = temp_data_dir / "existing.json"
        existing_data = {"folders": {"custom": ["task1"]}}
        default_data = {"folders": {"default": []}}
        
        # Create file with existing data
        JSONStorage.save(filepath, existing_data)
        
        # Ensure file exists
        JSONStorage.ensure_file_exists(filepath, default_data)
        
        # Verify original data is preserved
        loaded = JSONStorage.load(filepath)
        assert loaded == existing_data
    
    def test_ensure_file_creates_parent_directories(self, temp_data_dir):
        """Test ensure_file_exists creates parent directories."""
        filepath = temp_data_dir / "nested" / "dir" / "file.json"
        default_data = {"test": True}
        
        JSONStorage.ensure_file_exists(filepath, default_data)
        
        assert filepath.exists()
        assert filepath.parent.exists()


class TestDataManager:
    """Test DataManager class."""
    
    def test_initialization_creates_files(self, temp_data_dir):
        """Test that DataManager initialization creates default files."""
        dm = DataManager(temp_data_dir)
        
        assert dm.tasks_file.exists()
        assert dm.docs_metadata_file.exists()
        assert dm.chat_history_file.exists()
    
    def test_initialization_creates_default_structure(self, temp_data_dir):
        """Test that default files have correct structure."""
        dm = DataManager(temp_data_dir)
        
        tasks_data = JSONStorage.load(dm.tasks_file)
        assert "folders" in tasks_data
        assert "default" in tasks_data["folders"]
        assert "current_folder" in tasks_data
        
        docs_data = JSONStorage.load(dm.docs_metadata_file)
        # Should be an empty array by default
        assert isinstance(docs_data, list)
        
        chat_data = JSONStorage.load(dm.chat_history_file)
        assert "conversations" in chat_data
    
    def test_get_tasks_default_folder(self, data_manager):
        """Test getting tasks from default folder."""
        # Add some tasks
        tasks = [
            {"id": "1", "title": "Task 1"},
            {"id": "2", "title": "Task 2"}
        ]
        data_manager.save_tasks(tasks, "default")
        
        loaded_tasks = data_manager.get_tasks("default")
        assert len(loaded_tasks) == 2
        assert loaded_tasks[0]["id"] == "1"
    
    def test_get_tasks_custom_folder(self, data_manager):
        """Test getting tasks from custom folder."""
        tasks = [{"id": "1", "title": "Task 1"}]
        data_manager.save_tasks(tasks, "work")
        
        loaded_tasks = data_manager.get_tasks("work")
        assert len(loaded_tasks) == 1
    
    def test_get_tasks_empty_folder(self, data_manager):
        """Test getting tasks from empty folder."""
        tasks = data_manager.get_tasks("nonexistent")
        assert tasks == []
    
    def test_save_tasks_creates_folder(self, data_manager):
        """Test that save_tasks creates folder if it doesn't exist."""
        tasks = [{"id": "1", "title": "Task 1"}]
        data_manager.save_tasks(tasks, "new_folder")
        
        all_data = JSONStorage.load(data_manager.tasks_file)
        assert "new_folder" in all_data["folders"]
        assert len(all_data["folders"]["new_folder"]) == 1
    
    def test_save_tasks_overwrites_folder(self, data_manager):
        """Test that save_tasks overwrites existing folder tasks."""
        # Save initial tasks
        data_manager.save_tasks([{"id": "1"}], "default")
        # Save new tasks
        data_manager.save_tasks([{"id": "2"}, {"id": "3"}], "default")
        
        tasks = data_manager.get_tasks("default")
        assert len(tasks) == 2
        assert tasks[0]["id"] == "2"
    
    def test_get_pdfs_empty(self, data_manager):
        """Test getting PDFs when none exist."""
        pdfs = data_manager.get_pdfs()
        assert pdfs == []
    
    def test_save_pdf_metadata(self, data_manager):
        """Test saving PDF metadata."""
        pdf_data = {
            "id": "1",
            "filename": "test.pdf",
            "page_count": 10
        }
        
        data_manager.save_pdf_metadata(pdf_data)
        
        pdfs = data_manager.get_pdfs()
        assert len(pdfs) == 1
        assert pdfs[0]["filename"] == "test.pdf"
    
    def test_save_multiple_pdfs(self, data_manager):
        """Test saving multiple PDF metadata entries."""
        data_manager.save_pdf_metadata({"id": "1", "filename": "test1.pdf"})
        data_manager.save_pdf_metadata({"id": "2", "filename": "test2.pdf"})
        
        pdfs = data_manager.get_pdfs()
        assert len(pdfs) == 2
    
    def test_get_chat_history_empty(self, data_manager):
        """Test getting chat history when empty."""
        history = data_manager.get_chat_history()
        assert history == []
    
    def test_save_chat_message(self, data_manager):
        """Test saving a chat message."""
        data_manager.save_chat_message(
            role="user",
            content="Hello",
            context_type="general",
            context_id=None
        )
        
        history = data_manager.get_chat_history()
        assert len(history) == 1
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
    
    def test_save_chat_message_with_context(self, data_manager):
        """Test saving a chat message with context."""
        data_manager.save_chat_message(
            role="user",
            content="Tell me about task 1",
            context_type="task",
            context_id="1"
        )
        
        history = data_manager.get_chat_history()
        assert history[0]["context_type"] == "task"
        assert history[0]["context_id"] == "1"
    
    def test_save_multiple_chat_messages(self, data_manager):
        """Test saving multiple chat messages."""
        data_manager.save_chat_message("user", "Hello")
        data_manager.save_chat_message("assistant", "Hi there!")
        data_manager.save_chat_message("user", "How are you?")
        
        history = data_manager.get_chat_history()
        assert len(history) == 3
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"
