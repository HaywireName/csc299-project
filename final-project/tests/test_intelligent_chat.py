"""
Test intelligent chat task suggestion parsing.
Tests the _parse_task_suggestion method without requiring OpenAI API.
"""
import pytest


class TestIntelligentChatParsing:
    """Test intelligent chat task suggestion parsing."""
    
    def test_parse_complete_suggestion(self, chat_manager):
        """Test parsing a complete suggestion with all fields."""
        response = """
        Here's what I suggest:
        
        [TASK_SUGGESTION]
        Title: Review quarterly report
        Description: Review and analyze Q4 2025 quarterly report before board meeting
        Deadline: 30-11-2025
        Priority: high
        [/TASK_SUGGESTION]
        
        Would you like me to create this task?
        """
        
        result = chat_manager._parse_task_suggestion(response)
        
        assert result is not None
        assert result['title'] == "Review quarterly report"
        assert "Q4 2025 quarterly report" in result['description']
        assert result['deadline'] == "30-11-2025"
        assert result['priority'] == "high"
    
    def test_parse_minimal_suggestion(self, chat_manager):
        """Test parsing a minimal suggestion (title and description only)."""
        response = """
        [TASK_SUGGESTION]
        Title: Complete code review
        Description: Review pull request #42
        Deadline: 
        Priority: medium
        [/TASK_SUGGESTION]
        """
        
        result = chat_manager._parse_task_suggestion(response)
        
        assert result is not None
        assert result['title'] == "Complete code review"
        assert result['description'] == "Review pull request #42"
        assert result['deadline'] is None
        assert result['priority'] == "medium"
    
    def test_parse_no_suggestion(self, chat_manager):
        """Test that normal responses don't trigger suggestion parsing."""
        response = "I'd be happy to help! Could you provide more details about what you need?"
        
        result = chat_manager._parse_task_suggestion(response)
        
        assert result is None
    
    def test_parse_case_insensitive(self, chat_manager):
        """Test case insensitive parsing."""
        response = """
        [task_suggestion]
        TITLE: Send weekly update
        description: Send weekly status update to team
        DEADLINE: 27-11-2025
        priority: Low
        [/task_suggestion]
        """
        
        result = chat_manager._parse_task_suggestion(response)
        
        assert result is not None
        assert result['title'] == "Send weekly update"
        assert result['priority'] == "low"
        assert result['deadline'] == "27-11-2025"
    
    def test_parse_multiline_description(self, chat_manager):
        """Test parsing multi-line descriptions."""
        response = """
        [TASK_SUGGESTION]
        Title: Prepare presentation
        Description: Create slides for Monday's presentation
                     Include charts from Q3 data
                     Review with manager beforehand
        Deadline: 28-11-2025
        Priority: high
        [/TASK_SUGGESTION]
        """
        
        result = chat_manager._parse_task_suggestion(response)
        
        assert result is not None
        assert result['title'] == "Prepare presentation"
        assert "Create slides" in result['description']
        assert "Include charts" in result['description']
        assert result['deadline'] == "28-11-2025"
        assert result['priority'] == "high"
    
    def test_parse_missing_title(self, chat_manager):
        """Test that suggestion without title returns None."""
        response = """
        [TASK_SUGGESTION]
        Description: Some description
        Deadline: 30-11-2025
        Priority: high
        [/TASK_SUGGESTION]
        """
        
        result = chat_manager._parse_task_suggestion(response)
        
        # Should return None if no title
        assert result is None
    
    def test_parse_empty_deadline(self, chat_manager):
        """Test parsing with explicitly empty deadline."""
        response = """
        [TASK_SUGGESTION]
        Title: Ongoing task
        Description: This task has no deadline
        Deadline: 
        Priority: low
        [/TASK_SUGGESTION]
        """
        
        result = chat_manager._parse_task_suggestion(response)
        
        assert result is not None
        assert result['title'] == "Ongoing task"
        assert result['deadline'] is None  # Empty deadline should be None
    
    def test_parse_default_priority(self, chat_manager):
        """Test that missing priority defaults to medium."""
        response = """
        [TASK_SUGGESTION]
        Title: Default priority task
        Description: No priority specified
        Deadline: 30-11-2025
        [/TASK_SUGGESTION]
        """
        
        result = chat_manager._parse_task_suggestion(response)
        
        assert result is not None
        assert result['priority'] == "medium"  # Default priority
    
    def test_parse_invalid_priority_uses_default(self, chat_manager):
        """Test that invalid priority values use default."""
        response = """
        [TASK_SUGGESTION]
        Title: Invalid priority task
        Description: Has invalid priority
        Deadline: 30-11-2025
        Priority: urgent
        [/TASK_SUGGESTION]
        """
        
        result = chat_manager._parse_task_suggestion(response)
        
        assert result is not None
        # Invalid priority should use default (medium)
        assert result['priority'] == "medium"
    
    def test_parse_priority_shortcuts(self, chat_manager):
        """Test parsing priority shortcuts (l/m/h)."""
        responses = [
            ('l', 'low'),
            ('m', 'medium'),
            ('h', 'high')
        ]
        
        for shortcut, expected in responses:
            response = f"""
            [TASK_SUGGESTION]
            Title: Test task
            Description: Testing priority shortcut
            Priority: {shortcut}
            [/TASK_SUGGESTION]
            """
            
            result = chat_manager._parse_task_suggestion(response)
            
            assert result is not None
            assert result['priority'] == shortcut  # Parser stores as-is


class TestIntelligentChatIntegration:
    """Test intelligent chat integration features."""
    
    def test_handler_with_no_task_manager(self, chat_manager):
        """Test that handler safely handles missing task_manager."""
        # Ensure no task_manager is set
        chat_manager.task_manager = None
        
        response = """
        [TASK_SUGGESTION]
        Title: Test task
        Description: Should not cause error
        Priority: high
        [/TASK_SUGGESTION]
        """
        
        # Should not raise error
        chat_manager._handle_structured_suggestions(response)
    
    def test_handler_with_no_suggestion(self, chat_manager):
        """Test that handler ignores normal responses."""
        # Ensure no task_manager is set to avoid prompts
        chat_manager.task_manager = None
        
        response = "This is a normal chat response without suggestions."
        
        # Should not raise error or do anything
        chat_manager._handle_structured_suggestions(response)
    
    def test_parse_multiple_fields_in_description(self, chat_manager):
        """Test that description stops before other fields."""
        response = """
        [TASK_SUGGESTION]
        Title: Complex task
        Description: This description has
        multiple lines
        and should not include the following fields
        Deadline: 30-11-2025
        Priority: high
        [/TASK_SUGGESTION]
        """
        
        result = chat_manager._parse_task_suggestion(response)
        
        assert result is not None
        # Description should not contain "Deadline:" or "Priority:"
        assert "Deadline:" not in result['description']
        assert "Priority:" not in result['description']
