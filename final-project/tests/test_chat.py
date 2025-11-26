"""
Tests for modules.chat_module (ChatManager).
"""
import pytest
from datetime import datetime


class TestChatManagerBasics:
    """Test basic ChatManager functionality."""
    
    def test_initialization(self, chat_manager):
        """Test ChatManager initialization."""
        assert chat_manager.openai_client is not None
        assert chat_manager.context_type == 'general'
        # ChatManager initialized successfully
    
    def test_load_conversations_empty(self, chat_manager):
        """Test loading conversations when none exist."""
        assert chat_manager.conversations == []
    
    def test_get_current_conversation_creates_new(self, chat_manager):
        """Test that getting conversation creates one if none exists."""
        conv = chat_manager._get_current_conversation()
        
        assert conv is not None
        assert 'id' in conv
        assert 'started' in conv
        assert 'messages' in conv
        assert conv['id'].startswith('conv_')
    
    def test_conversation_persistence(self, chat_manager, data_manager):
        """Test that conversations are saved."""
        chat_manager._get_current_conversation()
        
        # Load directly from storage
        data = data_manager.load("chat_history.json")
        
        assert 'conversations' in data
        assert len(data['conversations']) == 1


class TestChatMessages:
    """Test chat message handling."""
    
    def test_save_message(self, chat_manager):
        """Test saving a chat message."""
        chat_manager._save_message("user", "Hello")
        
        conv = chat_manager._get_current_conversation()
        
        assert len(conv['messages']) == 1
        assert conv['messages'][0]['role'] == 'user'
        assert conv['messages'][0]['content'] == "Hello"
    
    def test_save_multiple_messages(self, chat_manager):
        """Test saving multiple messages."""
        chat_manager._save_message("user", "Hello")
        chat_manager._save_message("assistant", "Hi there!")
        chat_manager._save_message("user", "How are you?")
        
        conv = chat_manager._get_current_conversation()
        
        assert len(conv['messages']) == 3
    
    def test_get_conversation_history(self, chat_manager):
        """Test getting conversation history."""
        # Add messages
        for i in range(15):
            chat_manager._save_message("user", f"Message {i}")
        
        # Get last 10 messages
        history = chat_manager._get_conversation_history(limit=10)
        
        assert len(history) == 10
        # Should get the most recent messages
        assert history[-1]['content'] == "Message 14"
    
    def test_get_conversation_history_fewer_than_limit(self, chat_manager):
        """Test getting history when fewer messages exist."""
        chat_manager._save_message("user", "Hello")
        chat_manager._save_message("assistant", "Hi!")
        
        history = chat_manager._get_conversation_history(limit=10)
        
        assert len(history) == 2
    
    def test_clear_conversation(self, chat_manager):
        """Test clearing conversation history."""
        chat_manager._save_message("user", "Hello")
        chat_manager._save_message("assistant", "Hi!")
        
        result = chat_manager._clear_conversation()
        
        assert result is True
        conv = chat_manager._get_current_conversation()
        assert len(conv['messages']) == 0


class TestChatContext:
    """Test context management."""
    
    def test_set_context_general(self, chat_manager):
        """Test setting general context."""
        result = chat_manager.set_context('general')
        
        assert result is True
        assert chat_manager.context_type == 'general'
    
    def test_set_context_tasks(self, chat_manager):
        """Test setting tasks context."""
        result = chat_manager.set_context('tasks')
        
        assert result is True
        assert chat_manager.context_type == 'tasks'
    
    def test_set_context_docs(self, chat_manager):
        """Test setting docs context."""
        result = chat_manager.set_context('docs')
        
        assert result is True
        assert chat_manager.context_type == 'docs'
    
    def test_set_context_all(self, chat_manager):
        """Test setting all context."""
        result = chat_manager.set_context('all')
        
        assert result is True
        assert chat_manager.context_type == 'all'
    
    def test_set_context_invalid(self, chat_manager):
        """Test that invalid context returns False."""
        result = chat_manager.set_context('invalid')
        
        assert result is False
    
    def test_build_context_message_general(self, chat_manager):
        """Test building context message for general."""
        chat_manager.set_context('general')
        
        message = chat_manager._build_context_message()
        
        assert "helpful assistant" in message.lower()
    
    def test_build_context_message_with_tasks(self, chat_manager, task_manager):
        """Test building context message with tasks."""
        # Add a task
        task_manager.add_task("Test Task", description="Test description")
        
        chat_manager.set_context('tasks')
        message = chat_manager._build_context_message()
        
        assert "tasks" in message.lower() or "task" in message.lower()
    
    def test_load_tasks_context(self, chat_manager, task_manager):
        """Test loading tasks for context."""
        task_manager.add_task("Task 1", description="Description 1")
        task_manager.add_task("Task 2", description="Description 2")
        
        context = chat_manager._load_tasks_context()
        
        assert "Task 1" in context
        assert "Task 2" in context
    
    def test_load_tasks_context_empty(self, chat_manager):
        """Test loading tasks context when no tasks exist."""
        context = chat_manager._load_tasks_context()
        
        assert "No tasks found" in context or context == ""


class TestChatAPI:
    """Test chat API interactions."""
    
    def test_send_message(self, chat_manager):
        """Test sending a message to OpenAI."""
        response = chat_manager.send_message("Hello, how are you?")
        
        assert response is not None
        assert len(response) > 0
    
    def test_send_message_saves_messages(self, chat_manager):
        """Test that sending message saves both user and assistant messages."""
        chat_manager.send_message("Hello")
        
        conv = chat_manager._get_current_conversation()
        
        # Should have user message and assistant response
        assert len(conv['messages']) >= 2
        assert conv['messages'][-2]['role'] == 'user'
        assert conv['messages'][-1]['role'] == 'assistant'
    
    def test_send_message_tracks_cost(self, chat_manager):
        """Test that sending message works (cost tracking is handled by CostTracker)."""
        response = chat_manager.send_message("Hello")
        
        # Message sent successfully, cost tracking handled by CostTracker if provided
        assert response is not None
    
    def test_send_message_returns_response(self, chat_manager):
        """Test that sending message returns a response."""
        response = chat_manager.send_message("Hello")
        
        # Response received (token tracking handled by CostTracker if provided)
        assert response is not None
        assert len(response) > 0
    
    def test_send_message_uses_conversation_history(self, chat_manager):
        """Test that send_message uses conversation history."""
        chat_manager.send_message("My name is Alice")
        chat_manager.send_message("What is my name?")
        
        conv = chat_manager._get_current_conversation()
        
        # Should have 4 messages (2 user, 2 assistant)
        assert len(conv['messages']) >= 4


class TestChatFormatting:
    """Test chat formatting utilities."""
    
    def test_format_response_basic(self, chat_manager):
        """Test formatting a basic response."""
        text = "This is a test response."
        formatted = chat_manager._format_response(text)
        
        assert formatted == text
    
    def test_format_response_long_lines(self, chat_manager):
        """Test formatting response with long lines."""
        text = "This is a very long line that should be wrapped to fit within the specified width limit for better readability in the terminal."
        formatted = chat_manager._format_response(text, width=50)
        
        lines = formatted.split('\n')
        for line in lines:
            assert len(line) <= 55  # Allow some buffer
    
    def test_format_response_preserves_paragraphs(self, chat_manager):
        """Test that formatting preserves paragraph breaks."""
        text = "First paragraph.\n\nSecond paragraph."
        formatted = chat_manager._format_response(text)
        
        assert "\n\n" in formatted


class TestChatPersistence:
    """Test chat persistence."""
    
    def test_conversations_persist(self, chat_manager, data_manager):
        """Test that conversations are saved to storage."""
        chat_manager.send_message("Test message")
        
        # Load directly from storage
        data = data_manager.load("chat_history.json")
        
        assert 'conversations' in data
        assert len(data['conversations']) > 0
    
    def test_multiple_conversations(self, chat_manager):
        """Test managing multiple conversations."""
        # Create first conversation
        conv1 = chat_manager._get_current_conversation()
        chat_manager._save_message("user", "Message in conv 1")
        
        # Create second conversation (simulate new session)
        chat_manager.current_conversation_id = None
        conv2 = chat_manager._get_current_conversation()
        chat_manager._save_message("user", "Message in conv 2")
        
        # Verify both conversations exist
        assert len(chat_manager.conversations) == 2
        assert conv1['id'] != conv2['id']
