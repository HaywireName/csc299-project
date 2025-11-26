# PKMS Task Manager - Testing Suite

Comprehensive testing suite for the PKMS (Personal Knowledge Management System) Task Manager.

## Overview

This testing suite provides complete coverage of the PKMS Task Manager functionality including:
- **Storage operations** (JSON read/write, data persistence)
- **Task management** (CRUD operations, folders, search, AI summarization)
- **Document management** (PDF/DOCX/TXT handling, text extraction, summarization)
- **Chat functionality** (conversation management, context switching)
- **AI agents** (task analysis, knowledge synthesis)
- **Command system** (command registry, parsing)

## Test Structure

```
tests/
├── __init__.py                  # Package initialization
├── conftest.py                  # Pytest fixtures and configuration
├── mock_openai.py               # Mock OpenAI client (no API calls needed)
├── test_agents.py               # 26 tests - AI agents (task analysis, synthesis)
├── test_chat.py                 # 28 tests - Chat functionality (messages, context)
├── test_commands.py             # 39 tests - Command system (registry, parsing)
├── test_docs.py                 # 47 tests - Document management (including title extraction)
├── test_intelligent_chat.py     # 13 tests - Intelligent task suggestions
├── test_storage.py              # 22 tests - Storage operations (JSON, persistence)
└── test_tasks.py                # 48 tests - Task management (CRUD, folders, search)

Total: 214 tests
```

## Installation

### 1. Install Testing Dependencies

```bash
pip install -r requirements.txt
```

Or install just the testing packages:

```bash
pip install pytest pytest-cov pytest-mock reportlab
```

### 2. Verify Installation

```bash
python -m pytest --version
```

## Running Tests

### Quick Start

Run all tests with coverage:

```bash
python run_tests.py
```

### Basic Commands

```bash
# Run all tests with coverage
python run_tests.py

# Run without coverage (faster)
python run_tests.py --no-coverage

# Run with verbose output
python run_tests.py --verbose

# List all test files
python run_tests.py --list

# Run a specific test file
python run_tests.py --file test_tasks.py
```

### Using Pytest Directly

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_tasks.py

# Run specific test class
pytest tests/test_tasks.py::TestTaskManagerBasics

# Run specific test
pytest tests/test_tasks.py::TestTaskManagerBasics::test_add_task_basic

# Run tests matching a pattern
pytest -k "test_add"

# Run with coverage
pytest --cov=core --cov=modules --cov-report=html

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l
```

## Test Coverage

### Coverage Report

After running tests with coverage, view the HTML report:

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Expected Coverage

- **core.storage**: ~95% coverage
- **core.commands**: ~100% coverage
- **modules.task_module**: ~90% coverage
- **modules.docs_module**: ~85% coverage
- **modules.chat_module**: ~85% coverage
- **modules.agent_module**: ~80% coverage

## Test Categories

### test_storage.py (22 tests)
Tests for JSON storage and data management:
- JSON read/write operations
- File creation and updates
- Error handling (corrupted files, missing files)
- Data persistence across sessions
- Chat history storage
- Document metadata storage

### test_tasks.py (48 tests)
Tests for task management:
- Adding tasks (with/without options)
- Listing and sorting tasks
- Completing and removing tasks
- Task editing and updates
- Folder operations (create, switch, delete)
- Search functionality
- Deadline parsing (multiple formats)
- AI summarization (mocked)
- Task persistence

### test_docs.py (47 tests)
Tests for document management:
- Adding documents (PDF, DOCX, TXT)
- Listing and sorting documents
- Removing documents
- Text extraction and caching
- Document search
- AI summarization (mocked)
- Metadata extraction
- Chunking for large documents
- Title extraction from content and metadata (PDF, DOCX, TXT)

### test_chat.py (28 tests)
Tests for chat functionality:
- Message storage and retrieval
- Conversation management
- Context switching (general, tasks, docs, all)
- Chat history limits
- API interaction (mocked)
- Response formatting

### test_agents.py (26 tests)
Tests for AI agent functionality:
- Task categorization (overdue, due soon, etc.)
- Task analysis with AI insights (mocked)
- Knowledge synthesis
- Finding relevant tasks and documents
- Connection discovery
- Report formatting

### test_commands.py (39 tests)
Tests for command system:
- Command registration
- Command retrieval
- Command parsing
- Module organization
- Command execution
- Integration with managers

### test_intelligent_chat.py (13 tests)
Tests for intelligent task suggestions:
- Task suggestion parsing (complete, minimal, multi-line)
- Case insensitive parsing
- Default values and edge cases
- Handler integration with ChatManager
- Safety checks for missing managers

## Mocking Strategy

### OpenAI API Mocking

The test suite uses `tests/mock_openai.py` to mock OpenAI API calls:

- **No real API calls** - Tests run without requiring API keys
- **Realistic responses** - Mock responses match actual API behavior
- **Call tracking** - Track number and content of API calls
- **Cost simulation** - Simulate token usage and costs

Example mock responses:
- Task summarization: Returns concise summary
- Document summarization: Returns structured summary
- Task analysis: Returns JSON with complexity, priorities, insights
- Knowledge synthesis: Returns formatted synthesis with citations

### Benefits

1. **Fast**: No network calls, tests run in seconds
2. **Reliable**: No API rate limits or network issues
3. **Free**: No API costs during testing
4. **Deterministic**: Consistent results every run

## Fixtures

### Core Fixtures (conftest.py)

- `temp_data_dir`: Temporary directory for test data
- `data_manager`: DataManager with temp directory
- `command_registry`: Fresh command registry
- `mock_openai_client`: Mocked OpenAI client

### Manager Fixtures

- `task_manager`: TaskManager with mocked OpenAI
- `document_manager`: DocumentManager with mocked OpenAI
- `chat_manager`: ChatManager with mocked OpenAI
- `agent_manager`: AgentManager with mocked OpenAI

### Sample Data Fixtures

- `sample_task`: Single task dictionary
- `sample_tasks`: List of multiple tasks
- `sample_txt_file`: Generated TXT file
- `sample_pdf_file`: Generated PDF file (requires reportlab)
- `sample_docx_file`: Generated DOCX file
- `long_description`: 100+ word description for testing summarization

## Writing New Tests

### Example Test

```python
def test_add_task(task_manager):
    """Test adding a new task."""
    task = task_manager.add_task(
        title="Test Task",
        description="Test Description",
        deadline="2025-12-31",
        priority="high"
    )
    
    assert task['title'] == "Test Task"
    assert task['priority'] == "high"
    assert 'id' in task
```

### Best Practices

1. **Use descriptive names**: `test_add_task_with_deadline` not `test1`
2. **One assertion per concept**: Test one thing at a time
3. **Use fixtures**: Avoid setup code in tests
4. **Clean up**: Fixtures handle cleanup automatically
5. **Test edge cases**: Empty inputs, invalid data, etc.
6. **Mock external calls**: Use mock_openai_client for API calls

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python run_tests.py
```

## Troubleshooting

### Import Errors

If you see import errors:
```bash
# Ensure you're in the project root
cd /path/to/final-project

# Run tests from project root
python run_tests.py
```

### Missing Dependencies

```bash
# Install all dependencies including test packages
pip install -r requirements.txt

# Or install just what's missing
pip install pytest pytest-cov pytest-mock
```

### PDF Generation Errors

If `sample_pdf_file` fixture fails:
```bash
pip install reportlab
```

Or tests will be skipped automatically.

### Fixture Not Found

Make sure `conftest.py` is in the tests directory:
```bash
ls tests/conftest.py
```

## Performance

### Expected Run Times

- All tests: ~5-10 seconds
- With coverage: ~10-15 seconds
- Single test file: ~1-2 seconds

### Optimization Tips

```bash
# Run without coverage for faster execution
python run_tests.py --no-coverage

# Run specific test file
python run_tests.py --file test_commands.py

# Run in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest -n auto
```

## Test Output Example

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PKMS Task Manager - Test Suite
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

────────────────────────────────────────────────────────────
  Running Tests
────────────────────────────────────────────────────────────

tests/test_storage.py ...................... [ 14%]
tests/test_tasks.py ..................................... [ 45%]
tests/test_docs.py .............................. [ 70%]
tests/test_chat.py ...................... [ 84%]
tests/test_agents.py ..................... [ 93%]
tests/test_commands.py ............. [100%]

---------- coverage: platform darwin, python 3.9.13 ----------
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
core/__init__.py                   0      0   100%
core/commands.py                  45      2    96%   78-79
core/storage.py                   56      3    95%   34, 45, 62
modules/__init__.py                0      0   100%
modules/task_module.py           312     28    91%   145-152, 289-296
modules/docs_module.py           287     42    85%   178-185, 345-352
modules/chat_module.py           198     31    84%   234-241, 298-305
modules/agent_module.py          245     48    80%   312-319, 456-463
------------------------------------------------------------
TOTAL                           1143    154    87%

────────────────────────────────────────────────────────────
  Results
────────────────────────────────────────────────────────────

✓ All tests passed!

📊 Coverage report generated in: htmlcov/index.html
   Open it in your browser to see detailed coverage
```

## Contributing

When adding new features:

1. Write tests first (TDD)
2. Ensure tests pass: `python run_tests.py`
3. Check coverage: Aim for >80%
4. Update this README if needed

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

---

**Last Updated**: November 25, 2025
**Test Suite Version**: 1.1
**Total Tests**: 214 tests across 8 test files
**Pass Rate**: 100%
