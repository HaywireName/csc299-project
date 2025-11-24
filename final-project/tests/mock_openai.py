"""
Mock OpenAI client for testing without making real API calls.
"""
from unittest.mock import Mock
from datetime import datetime


class MockMessage:
    """Mock message response from OpenAI."""
    def __init__(self, content):
        self.content = content


class MockChoice:
    """Mock choice from OpenAI response."""
    def __init__(self, content):
        self.message = MockMessage(content)
        self.delta = MockMessage(content)


class MockUsage:
    """Mock usage statistics from OpenAI."""
    def __init__(self, prompt_tokens=10, completion_tokens=20):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class MockCompletion:
    """Mock completion response from OpenAI."""
    def __init__(self, content, prompt_tokens=10, completion_tokens=20):
        self.choices = [MockChoice(content)]
        self.usage = MockUsage(prompt_tokens, completion_tokens)
    
    def __iter__(self):
        """Support streaming mode."""
        # Yield chunk by chunk
        words = self.choices[0].message.content.split()
        for i, word in enumerate(words):
            chunk = Mock()
            chunk.choices = [Mock()]
            chunk.choices[0].delta = Mock()
            chunk.choices[0].delta.content = word + (" " if i < len(words) - 1 else "")
            chunk.usage = None
            yield chunk
        
        # Last chunk with usage
        final_chunk = Mock()
        final_chunk.choices = [Mock()]
        final_chunk.choices[0].delta = Mock()
        final_chunk.choices[0].delta.content = None
        final_chunk.usage = self.usage
        yield final_chunk


class MockChatCompletions:
    """Mock chat completions API."""
    def __init__(self):
        self.call_history = []
    
    def create(self, model, messages, **kwargs):
        """Mock create method."""
        # Store call info
        self.call_history.append({
            'model': model,
            'messages': messages,
            'kwargs': kwargs,
            'timestamp': datetime.now()
        })
        
        # Determine response based on system message
        user_message = messages[-1]['content'].lower() if messages else ""
        
        # Task summarization
        if 'summarize' in user_message or 'summary' in messages[0]['content'].lower():
            content = "Complete project report and prepare presentation slides"
            return MockCompletion(content, 50, 15)
        
        # Document summarization
        elif 'document' in user_message or len(user_message) > 500:
            content = "This document discusses key concepts in machine learning including supervised and unsupervised learning approaches."
            return MockCompletion(content, 200, 100)
        
        # Task analysis
        elif 'analyze' in messages[0]['content'].lower() or 'complexity' in user_message:
            import json
            content = json.dumps({
                "complexity_estimates": [
                    {
                        "task_id": "1",
                        "task_title": "Test Task",
                        "complexity": "medium",
                        "estimated_hours": "2-4",
                        "reason": "Moderate scope with clear requirements"
                    }
                ],
                "priority_suggestions": [
                    {
                        "task_id": "1",
                        "current_priority": "low",
                        "suggested_priority": "medium",
                        "reason": "Approaching deadline"
                    }
                ],
                "related_tasks": [
                    {
                        "task_ids": ["1", "2"],
                        "relationship": "Sequential dependency",
                        "suggestion": "Complete task 1 before starting task 2"
                    }
                ],
                "deadline_suggestions": [
                    {
                        "task_id": "1",
                        "suggested_deadline": "2025-12-31",
                        "reason": "Based on project timeline"
                    }
                ],
                "insights": [
                    "High workload detected in default folder",
                    "Consider prioritizing overdue tasks"
                ]
            })
            return MockCompletion(content, 300, 200)
        
        # Knowledge synthesis
        elif 'synthesize' in messages[0]['content'].lower():
            content = """Overview: Machine learning encompasses various techniques for pattern recognition and prediction.

Key Points:
• Supervised learning uses labeled data for training
• Unsupervised learning discovers patterns in unlabeled data
• Deep learning uses neural networks for complex problems

Actionable Insights:
• Start with simple algorithms before moving to complex ones [doc_1]
• Ensure sufficient data for training models [task_1]
• Consider computational resources required [doc_2]"""
            return MockCompletion(content, 400, 250)
        
        # Chat responses
        elif kwargs.get('stream', False):
            content = "I'm here to help you with your tasks and documents. What would you like to know?"
            return MockCompletion(content, 50, 30)
        
        # Default response
        else:
            content = "This is a mock response from the OpenAI API."
            return MockCompletion(content, 20, 15)


class MockChat:
    """Mock chat API."""
    def __init__(self):
        self.completions = MockChatCompletions()


class MockOpenAIClient:
    """Mock OpenAI client for testing."""
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.chat = MockChat()
    
    def get_call_count(self):
        """Get total number of API calls made."""
        return len(self.chat.completions.call_history)
    
    def get_last_call(self):
        """Get the last API call made."""
        if self.chat.completions.call_history:
            return self.chat.completions.call_history[-1]
        return None
    
    def clear_history(self):
        """Clear call history."""
        self.chat.completions.call_history = []


def create_mock_openai_client():
    """Factory function to create a mock OpenAI client."""
    return MockOpenAIClient(api_key="sk-test-key-123")
