"""
Tests for real API cost tracking across all features.
These tests make actual API calls and require OPENAI_API_KEY.

Run with: pytest tests/test_real_costs.py -v --run-real-api

By default, these tests are skipped to avoid API costs during normal testing.
"""
import pytest
import os


@pytest.fixture
def real_task_manager(data_manager, command_registry, cost_tracker, monkeypatch):
    """Create a TaskManager with REAL OpenAI client for cost tracking tests."""
    from modules.task_module import TaskManager
    
    # Check for API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key or api_key.startswith('sk-test'):
        pytest.skip("Real OPENAI_API_KEY required for this test")
    
    monkeypatch.setenv("OPENAI_API_KEY", api_key)
    tm = TaskManager(data_manager, command_registry, cost_tracker)
    return tm


@pytest.fixture
def real_document_manager(data_manager, command_registry, cost_tracker, temp_data_dir, monkeypatch):
    """Create a DocumentManager with REAL OpenAI client for cost tracking tests."""
    from modules.docs_module import DocumentManager
    
    # Check for API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key or api_key.startswith('sk-test'):
        pytest.skip("Real OPENAI_API_KEY required for this test")
    
    # Create docs directories
    docs_dir = temp_data_dir / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "pdfs").mkdir(exist_ok=True)
    (docs_dir / "docx").mkdir(exist_ok=True)
    (docs_dir / "txt").mkdir(exist_ok=True)
    
    # Create doc_cache directory
    cache_dir = temp_data_dir / "doc_cache"
    cache_dir.mkdir(exist_ok=True)
    
    monkeypatch.setenv("OPENAI_API_KEY", api_key)
    dm = DocumentManager(data_manager, command_registry, cost_tracker)
    
    # Override directories
    dm.data_dir = str(docs_dir)
    dm.pdfs_dir = str(docs_dir / "pdfs")
    dm.docx_dir = str(docs_dir / "docx")
    dm.txt_dir = str(docs_dir / "txt")
    dm.cache_dir = str(cache_dir)
    
    return dm


@pytest.mark.skipif(
    os.environ.get('RUN_REAL_API_TESTS') != '1',
    reason="Real API tests skipped by default. Set RUN_REAL_API_TESTS=1 to run them."
)
class TestRealAPICostTracking:
    """Test real API cost tracking (requires OPENAI_API_KEY)."""
    
    def test_task_summary_cost_tracking(self, real_task_manager, cost_tracker, capsys):
        """Test that task summarization tracks costs correctly with real API."""
        # Add a task with a long description that triggers summarization
        task = real_task_manager.add_task(
            title="Cost Tracking Test Task",
            description="This is a very long description that will trigger AI summarization. " * 10,
            priority="high"
        )
        
        task_id = task['id']
        
        # Get cost before summarization
        summary_before = cost_tracker.get_session_summary()
        cost_before = summary_before['total_cost']
        
        # Summarize the task (makes real API call)
        real_task_manager.summarize_task(task_id)
        
        # Get cost after summarization
        summary_after = cost_tracker.get_session_summary()
        cost_after = summary_after['total_cost']
        
        # Verify cost increased
        assert cost_after > cost_before, "Cost should increase after API call"
        
        # Verify operation was tracked
        task_summary_ops = summary_after.get('by_operation', {}).get('task_summary', {})
        assert task_summary_ops.get('count', 0) > 0, "Task summary operation should be tracked"
        assert task_summary_ops.get('cost', 0) > 0, "Task summary should have cost"
        assert task_summary_ops.get('input_tokens', 0) > 0, "Should track input tokens"
        assert task_summary_ops.get('output_tokens', 0) > 0, "Should track output tokens"
    
    def test_document_summary_cost_tracking(self, real_document_manager, cost_tracker, temp_data_dir):
        """Test that document summarization tracks costs correctly with real API."""
        # Create a test text file
        test_file = temp_data_dir / "test_cost_tracking.txt"
        test_content = """This is a test document for cost tracking verification.
        
It contains multiple paragraphs of text to ensure the AI has enough
content to generate a meaningful summary. This will help us verify
that the cost tracking system is working correctly for document
summarization operations.

The document discusses various topics including artificial intelligence,
machine learning, and natural language processing. These are all important
fields in modern computer science and technology development.

By testing with real API calls, we can ensure that the token counting
and cost calculations are accurate and properly tracked across different
operation types in the PKMS Task Manager system.
""" * 3  # Make it longer
        
        test_file.write_text(test_content)
        
        # Add the document
        doc = real_document_manager.add_doc(str(test_file))
        doc_id = doc['id']
        
        # Get cost before summarization
        summary_before = cost_tracker.get_session_summary()
        cost_before = summary_before['total_cost']
        
        # Summarize the document (makes real API call)
        real_document_manager.summarize_doc(doc_id)
        
        # Get cost after summarization
        summary_after = cost_tracker.get_session_summary()
        cost_after = summary_after['total_cost']
        
        # Verify cost increased
        assert cost_after > cost_before, "Cost should increase after API call"
        
        # Verify operation was tracked
        doc_summary_ops = summary_after.get('by_operation', {}).get('doc_summary', {})
        assert doc_summary_ops.get('count', 0) > 0, "Doc summary operation should be tracked"
        assert doc_summary_ops.get('cost', 0) > 0, "Doc summary should have cost"
        assert doc_summary_ops.get('input_tokens', 0) > 0, "Should track input tokens"
        assert doc_summary_ops.get('output_tokens', 0) > 0, "Should track output tokens"
    
    def test_cost_persistence(self, cost_tracker, temp_data_dir):
        """Test that costs are properly saved and can be retrieved."""
        # Track some dummy cost
        cost_tracker.track_api_call(
            operation_type='test_operation',
            model='gpt-4o',
            input_tokens=100,
            output_tokens=50
        )
        
        # Get current session summary
        summary = cost_tracker.get_session_summary()
        current_cost = summary['total_cost']
        
        assert current_cost > 0, "Should have tracked some cost"
        
        # Save the session
        cost_tracker.save_session()
        
        # Check if file exists
        history_file = temp_data_dir / "cost_history.json"
        assert history_file.exists(), "Cost history file should be created"
        
        # Load and verify the saved data
        import json
        with open(history_file) as f:
            history = json.load(f)
        
        assert 'sessions' in history, "History should contain sessions"
        assert len(history['sessions']) > 0, "Should have at least one session"
        
        last_session = history['sessions'][-1]
        saved_cost = last_session['total_cost']
        
        # Verify saved cost matches current cost
        assert abs(saved_cost - current_cost) < 0.000001, "Saved cost should match current cost"
        
        # Create a new tracker instance and verify it can read history
        from core.cost_tracker import CostTracker
        new_tracker = CostTracker(str(temp_data_dir))
        
        previous_cost = new_tracker.get_previous_session_cost()
        all_time_cost = new_tracker.get_all_time_cost()
        
        assert previous_cost > 0, "Should retrieve previous session cost"
        assert all_time_cost >= previous_cost, "All-time cost should be >= previous session"
