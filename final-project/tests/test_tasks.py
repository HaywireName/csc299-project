"""
Tests for modules.task_module (TaskManager).
"""
import pytest
from datetime import datetime
from core.errors import TaskNotFoundError, InvalidInputError, APIError


class TestTaskManagerBasics:
    """Test basic TaskManager functionality."""
    
    def test_add_task_basic(self, task_manager):
        """Test adding a basic task."""
        task = task_manager.add_task("Test Task")
        
        assert task['title'] == "Test Task"
        assert task['id'] is not None
        assert task['status'] == 'pending'
        assert task['priority'] == 'medium'
    
    def test_add_task_with_description(self, task_manager):
        """Test adding a task with description."""
        task = task_manager.add_task(
            "Test Task",
            description="This is a test description"
        )
        
        assert task['description'] == "This is a test description"
    
    def test_add_task_with_deadline(self, task_manager):
        """Test adding a task with deadline."""
        task = task_manager.add_task(
            "Test Task",
            deadline="31-12-2025"
        )
        
        assert task['deadline'] == "31-12-2025"
    
    def test_add_task_with_priority(self, task_manager):
        """Test adding a task with priority."""
        task = task_manager.add_task(
            "Test Task",
            priority="high"
        )
        
        assert task['priority'] == 'high'
    
    def test_add_task_empty_title_raises_error(self, task_manager):
        """Test that empty title raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            task_manager.add_task("")
    
    def test_add_task_invalid_priority_raises_error(self, task_manager):
        """Test that invalid priority raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            task_manager.add_task("Test Task", priority="invalid")
    
    def test_add_task_generates_unique_id(self, task_manager):
        """Test that each task gets a unique ID."""
        task1 = task_manager.add_task("Task 1")
        task2 = task_manager.add_task("Task 2")
        
        assert task1['id'] != task2['id']
    
    def test_list_tasks_empty(self, task_manager):
        """Test listing tasks when none exist."""
        tasks = task_manager.list_tasks()
        
        assert tasks == []
    
    def test_list_tasks_multiple(self, task_manager):
        """Test listing multiple tasks."""
        task_manager.add_task("Task 1")
        task_manager.add_task("Task 2")
        task_manager.add_task("Task 3")
        
        tasks = task_manager.list_tasks()
        
        assert len(tasks) == 3
    
    def test_list_tasks_sorts_completed_last(self, task_manager):
        """Test that completed tasks appear at the bottom."""
        task1 = task_manager.add_task("Task 1")
        task2 = task_manager.add_task("Task 2")
        task3 = task_manager.add_task("Task 3")
        
        # Complete task 2
        task_manager.complete_task(task2['id'])
        
        tasks = task_manager.list_tasks()
        
        # Completed task should be last
        assert tasks[-1]['id'] == task2['id']
        assert tasks[-1]['status'] == 'completed'


class TestTaskOperations:
    """Test task operations (complete, remove, edit)."""
    
    def test_complete_task(self, task_manager):
        """Test completing a task."""
        task = task_manager.add_task("Test Task")
        
        task_manager.complete_task(task['id'])
        
        completed_task = task_manager.get_task(task['id'])
        assert completed_task['status'] == 'completed'
    
    def test_complete_task_invalid_id(self, task_manager):
        """Test that invalid task ID raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_manager.complete_task("invalid_id")
    
    def test_remove_task(self, task_manager, monkeypatch):
        """Test removing a task."""
        task = task_manager.add_task("Test Task")
        
        # Mock user confirmation
        monkeypatch.setattr('builtins.input', lambda _: "yes")
        
        task_manager.remove_task(task['id'])
        
        with pytest.raises(TaskNotFoundError):
            task_manager.get_task(task['id'])
    
    def test_remove_task_invalid_id(self, task_manager):
        """Test that invalid task ID raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_manager.remove_task("invalid_id")
    
    def test_edit_task_description(self, task_manager):
        """Test editing task description."""
        task = task_manager.add_task("Test Task")
        
        updated = task_manager.edit_task(
            task['id'],
            description="Updated description"
        )
        
        assert updated['description'] == "Updated description"
    
    def test_edit_task_deadline(self, task_manager):
        """Test editing task deadline."""
        task = task_manager.add_task("Test Task")
        
        updated = task_manager.edit_task(
            task['id'],
            deadline="31-12-2025"
        )
        
        assert updated['deadline'] == "31-12-2025"
    
    def test_edit_task_priority(self, task_manager):
        """Test editing task priority."""
        task = task_manager.add_task("Test Task", priority="low")
        
        updated = task_manager.edit_task(
            task['id'],
            priority="high"
        )
        
        assert updated['priority'] == 'high'
    
    def test_get_task_by_full_id(self, task_manager):
        """Test getting task by full ID."""
        task = task_manager.add_task("Test Task")
        
        retrieved = task_manager.get_task(task['id'])
        
        assert retrieved['id'] == task['id']
    
    def test_get_task_by_partial_id(self, task_manager):
        """Test getting task by partial ID."""
        task = task_manager.add_task("Test Task")
        
        # Use first 4 characters of ID
        partial_id = task['id'][:4]
        retrieved = task_manager.get_task(partial_id)
        
        assert retrieved['id'] == task['id']
    
    def test_get_task_invalid_id(self, task_manager):
        """Test that invalid ID raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_manager.get_task("invalid_id")


class TestTaskFolders:
    """Test folder operations."""
    
    def test_default_folder(self, task_manager):
        """Test that tasks are added to default folder by default."""
        task = task_manager.add_task("Test Task")
        
        current_folder = task_manager.data['current_folder']
        assert current_folder == 'default'
        assert task in task_manager.tasks
    
    def test_create_folder(self, task_manager):
        """Test creating a new folder."""
        task_manager.create_folder("work")
        
        folders = task_manager.get_folders()
        assert "work" in folders
    
    def test_create_existing_folder_raises_error(self, task_manager):
        """Test that creating existing folder raises error."""
        task_manager.create_folder("work")
        
        with pytest.raises(ValueError):
            task_manager.create_folder("work")
    
    def test_switch_folder(self, task_manager):
        """Test switching to a different folder."""
        task_manager.switch_folder("work")
        
        assert task_manager.data['current_folder'] == "work"
    
    def test_switch_to_new_folder_creates_it(self, task_manager):
        """Test that switching to non-existent folder creates it."""
        task_manager.switch_folder("new_folder")
        
        assert "new_folder" in task_manager.data['folders']
    
    def test_delete_folder(self, task_manager):
        """Test deleting a folder."""
        task_manager.create_folder("temp")
        task_manager.delete_folder("temp")
        
        folders = task_manager.get_folders()
        assert "temp" not in folders
    
    def test_delete_default_folder_raises_error(self, task_manager):
        """Test that deleting default folder raises error."""
        with pytest.raises(ValueError):
            task_manager.delete_folder("default")
    
    def test_delete_nonexistent_folder_raises_error(self, task_manager):
        """Test that deleting non-existent folder raises error."""
        with pytest.raises(ValueError):
            task_manager.delete_folder("nonexistent")
    
    def test_get_folders(self, task_manager):
        """Test getting all folders with task counts."""
        task_manager.add_task("Task 1")
        task_manager.add_task("Task 2")
        task_manager.create_folder("work")
        task_manager.switch_folder("work")
        task_manager.add_task("Work Task")
        
        folders = task_manager.get_folders()
        
        assert folders['default'] == 2
        assert folders['work'] == 1


class TestTaskSearch:
    """Test task search functionality."""
    
    def test_search_tasks_by_title(self, task_manager):
        """Test searching tasks by title."""
        task_manager.add_task("Python Project")
        task_manager.add_task("Java Assignment")
        task_manager.add_task("Python Tutorial")
        
        results = task_manager.search_tasks("Python")
        
        assert len(results) == 2
        assert all("python" in r['title'].lower() for r in results)
    
    def test_search_tasks_by_description(self, task_manager):
        """Test searching tasks by description."""
        task_manager.add_task("Task 1", description="Learn machine learning")
        task_manager.add_task("Task 2", description="Study algorithms")
        task_manager.add_task("Task 3", description="Practice machine learning")
        
        results = task_manager.search_tasks("machine learning")
        
        assert len(results) == 2
    
    def test_search_tasks_case_insensitive(self, task_manager):
        """Test that search is case-insensitive."""
        task_manager.add_task("Python Project")
        
        results = task_manager.search_tasks("python")
        assert len(results) == 1
        
        results = task_manager.search_tasks("PYTHON")
        assert len(results) == 1
    
    def test_search_tasks_no_results(self, task_manager):
        """Test searching with no matches."""
        task_manager.add_task("Task 1")
        task_manager.add_task("Task 2")
        
        results = task_manager.search_tasks("nonexistent")
        
        assert len(results) == 0


class TestTaskDeadlines:
    """Test deadline parsing and handling."""
    
    def test_parse_deadline_dd_mm_yyyy(self, task_manager):
        """Test parsing DD-MM-YYYY format."""
        deadline = task_manager._parse_deadline("31-12-2025")
        assert deadline == "31-12-2025"
    
    def test_parse_deadline_mm_dd_yyyy(self, task_manager):
        """Test parsing MM-DD-YYYY format."""
        deadline = task_manager._parse_deadline("12-31-2025")
        assert deadline == "31-12-2025"
    
    def test_parse_deadline_tomorrow(self, task_manager):
        """Test parsing 'tomorrow' keyword."""
        deadline = task_manager._parse_deadline("tomorrow")
        # Should be tomorrow's date in DD-MM-YYYY format
        assert deadline is not None
        assert len(deadline.split('-')) == 3
    
    def test_parse_deadline_mm_dd(self, task_manager):
        """Test parsing MM-DD format (current year assumed)."""
        deadline = task_manager._parse_deadline("12-31")
        # Should include current year
        assert deadline is not None
        assert len(deadline.split('-')) == 3
    
    def test_parse_deadline_invalid_format(self, task_manager):
        """Test that invalid format raises ValueError."""
        with pytest.raises(ValueError):
            task_manager._parse_deadline("invalid-date")


class TestTaskSummarization:
    """Test task summarization with AI."""
    
    def test_summarize_task_short_description_raises_error(self, task_manager):
        """Test that short description raises InvalidInputError."""
        task = task_manager.add_task(
            "Test Task",
            description="Short description"
        )
        
        with pytest.raises(InvalidInputError):
            task_manager.summarize_task(task['id'])
    
    def test_summarize_task_no_description_raises_error(self, task_manager):
        """Test that missing description raises InvalidInputError."""
        task = task_manager.add_task("Test Task")
        
        with pytest.raises(InvalidInputError):
            task_manager.summarize_task(task['id'])
    
    def test_summarize_task_long_description(self, task_manager, long_description):
        """Test summarizing task with long description."""
        task = task_manager.add_task(
            "Test Task",
            description=long_description
        )
        
        summary = task_manager.summarize_task(task['id'])
        
        assert summary is not None
        assert len(summary) > 0
        # Verify summary is saved in task
        updated_task = task_manager.get_task(task['id'])
        assert updated_task['summary'] == summary
    
    def test_summarize_task_invalid_id(self, task_manager):
        """Test that invalid ID raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_manager.summarize_task("invalid_id")
    
    def test_summarize_tracks_cost(self, task_manager, long_description):
        """Test that summarization tracks API cost."""
        task = task_manager.add_task(
            "Test Task",
            description=long_description
        )
        
        initial_cost = task_manager.session_cost
        task_manager.summarize_task(task['id'])
        
        # Cost should increase
        assert task_manager.session_cost > initial_cost


class TestTaskDetails:
    """Test task details and formatting."""
    
    def test_get_task_details(self, task_manager):
        """Test getting formatted task details."""
        task = task_manager.add_task(
            "Test Task",
            description="Test description",
            deadline="31-12-2025",
            priority="high"
        )
        
        details = task_manager.get_task_details(task['id'])
        
        assert "Test Task" in details
        assert "Test description" in details
        assert "31-12-2025" in details
        assert "high" in details
    
    def test_count_words(self, task_manager):
        """Test word counting."""
        text = "This is a test sentence with eight words"
        count = task_manager._count_words(text)
        assert count == 8
    
    def test_count_words_empty(self, task_manager):
        """Test word counting with empty string."""
        count = task_manager._count_words("")
        assert count == 0


class TestTaskPersistence:
    """Test that tasks are persisted correctly."""
    
    def test_tasks_persist_after_save(self, task_manager, data_manager):
        """Test that tasks are saved to storage."""
        task = task_manager.add_task("Test Task")
        
        # Load directly from storage
        tasks = data_manager.get_tasks("default")
        
        assert len(tasks) == 1
        assert tasks[0]['title'] == "Test Task"
    
    def test_multiple_folders_persist(self, task_manager, data_manager):
        """Test that multiple folders persist correctly."""
        task_manager.add_task("Default Task")
        task_manager.switch_folder("work")
        task_manager.add_task("Work Task")
        
        # Load directly from storage
        default_tasks = data_manager.get_tasks("default")
        work_tasks = data_manager.get_tasks("work")
        
        assert len(default_tasks) == 1
        assert len(work_tasks) == 1
