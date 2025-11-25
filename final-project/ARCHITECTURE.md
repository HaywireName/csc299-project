# ARCHITECTURE.md - Technical Documentation

Complete technical documentation for PKMS Task Manager.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Design](#architecture-design)
3. [Module Descriptions](#module-descriptions)
4. [Data Structures](#data-structures)
5. [API Integration](#api-integration)
6. [Code Organization](#code-organization)
7. [Extension Points](#extension-points)

---

## System Overview

PKMS Task Manager is a modular, terminal-based application built with Python 3.9+. It follows a clean architecture pattern with clear separation of concerns.

### Key Components

- **Main Loop** (`main.py`): User interface and command routing
- **Modules** (`modules/`): Feature implementations (tasks, docs, chat, agent, settings)
- **Core** (`core/`): Shared utilities (commands, storage, errors, utils, backup)
- **Data** (`data/`): JSON-based persistent storage

### Technology Stack

- **Python**: 3.9+
- **OpenAI API**: GPT-4o and GPT-4o-mini
- **Libraries**:
  - `pypdf`: PDF text extraction
  - `python-docx`: DOCX processing
  - `openai`: API client
  - `tabulate`: Table formatting
  - `python-dateutil`: Date parsing
  - `tqdm`: Progress bars

---

## Architecture Design

### Modular Architecture

```
┌─────────────────────────────────────────┐
│           main.py (Entry Point)          │
│  - Session Management                    │
│  - Command Router                        │
│  - Error Handler                         │
└─────────────────┬───────────────────────┘
                  │
      ┌───────────┴───────────┐
      │                        │
┌─────▼──────┐       ┌────────▼────────┐
│   Modules  │       │   Core Services  │
│            │       │                  │
│ - Tasks    │       │ - Commands       │
│ - Docs     │◄──────┤ - Storage        │
│ - Chat     │       │ - Errors         │
│ - Agent    │       │ - Utils          │
│ - Settings │       │ - Backup         │
└────────────┘       └──────────────────┘
      │
      │
┌─────▼──────┐
│    Data    │
│            │
│ JSON Files │
└────────────┘
```

### Design Patterns

1. **Registry Pattern**: Command registration and lookup
2. **Strategy Pattern**: Module-specific command handling
3. **Singleton Pattern**: DataManager instance
4. **Factory Pattern**: Document and task creation
5. **Observer Pattern**: Event-based updates (implicit)

### Session Management

The `SessionState` class tracks:
- Current module
- Session start time
- Command count
- First-run status

This enables context-aware command routing and statistics.

---

## Module Descriptions

### Task Module (`modules/task_module.py`)

**Purpose**: Comprehensive task management

**Features**:
- CRUD operations for tasks
- Folder-based organization
- Priority and deadline management
- AI summarization
- Search functionality

**Key Classes**:
- `TaskManager`: Main controller

**Dependencies**:
- `DataManager`: Persistence
- `CommandRegistry`: Command registration
- `OpenAI`: AI summaries

**Data Flow**:
1. User command → TaskManager method
2. Method validates input
3. Updates in-memory data structure
4. Saves to tasks.json
5. Returns feedback

### Document Module (`modules/docs_module.py`)

**Purpose**: Document library management

**Features**:
- Multi-format support (PDF, DOCX, TXT)
- Metadata extraction
- Text extraction with caching
- Full-text search
- AI summarization

**Key Classes**:
- `DocumentManager`: Main controller

**Key Methods**:
- `add_doc()`: Import and process documents
- `extract_text()`: Text extraction with caching
- `search_docs()`: Full-text search
- `summarize_doc()`: AI summarization

**Caching Strategy**:
- Extracted text cached in `data/doc_cache/`
- Format: `{doc_id}_full.txt` or `{doc_id}_page{N}.txt`
- Significantly improves performance

### Chat Module (`modules/chat_module.py`)

**Purpose**: AI conversational interface

**Features**:
- Context-aware chat
- Streaming responses
- Conversation history
- Cost tracking

**Context Types**:
- `general`: No specific context
- `tasks`: Load all task data
- `pdfs`: Load document summaries
- `all`: Combined context

**Implementation**:
- Uses GPT-4o for responses
- Maintains last 10 messages for context
- Streaming via OpenAI API
- Real-time cost calculation

### Agent Module (`modules/agent_module.py`)

**Purpose**: AI-powered analysis and synthesis

**Features**:
- Task analysis with recommendations
- Document synthesis
- Cross-module intelligence

**Key Methods**:
- `analyze_tasks()`: Comprehensive task analysis
- `synthesize_documents()`: Multi-document synthesis

### Settings Module (`modules/settings_module.py`)

**Purpose**: Application configuration

**Features**:
- View and modify settings
- Persistent storage
- Validation

---

## Data Structures

### tasks.json

```json
{
  "folders": {
    "default": [
      {
        "id": "1",
        "title": "Task Title",
        "description": "Detailed description",
        "deadline": "DD-MM-YYYY",
        "priority": "low|medium|high",
        "status": "pending|completed",
        "summary": "AI-generated summary or null",
        "created": "DD-MM-YYYYTHH:MM:SS"
      }
    ],
    "work": [],
    "personal": []
  },
  "current_folder": "default"
}
```

### docs_metadata.json

```json
[
  {
    "id": "1",
    "filename": "original_name.pdf",
    "filepath": "/full/path/to/stored/file.pdf",
    "extension": ".pdf",
    "title": "Extracted or filename",
    "page_count": 42,
    "added_date": "MM-DD-YYYYTHH:MM:SS.ffffff",
    "last_accessed": "MM-DD-YYYYTHH:MM:SS.ffffff",
    "summary": "AI summary or null",
    "summary_word_count": 150,
    "preview": "First 500 chars of text"
  }
]
```

### chat_history.json

```json
{
  "conversations": [
    {
      "id": "conv_12345678",
      "started": "YYYY-MM-DDTHH:MM:SS",
      "messages": [
        {
          "role": "user|assistant",
          "content": "Message text",
          "timestamp": "YYYY-MM-DDTHH:MM:SS"
        }
      ]
    }
  ]
}
```

### settings.json

```json
{
  "theme": "default",
  "auto_backup": true,
  "backup_retention_days": 30,
  "default_priority": "medium"
}
```

---

## API Integration

### OpenAI Integration

**Models Used**:
- **GPT-4o**: Chat conversations (`chat_module.py`)
  - Input: $2.50 per 1M tokens
  - Output: $10.00 per 1M tokens
  
- **GPT-4o-mini**: Summaries and analysis (`task_module.py`, `docs_module.py`)
  - Input: $0.15 per 1M tokens
  - Output: $0.60 per 1M tokens

**Rate Limiting**:
- Exponential backoff on rate limit errors
- Max 3 retries with delays: 1s, 2s, 4s

**Error Handling**:
```python
try:
    response = client.chat.completions.create(...)
except RateLimitError:
    # Exponential backoff
except AuthenticationError:
    # Invalid API key
except APIError:
    # General API error
```

**Cost Tracking**:
- Session-level tracking via `session_cost` attribute
- Per-request calculation from token usage
- User-facing cost commands in modules

### API Client Initialization

```python
def _init_openai_client(self):
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if api_key:
            self.openai_client = OpenAI(api_key=api_key)
    except Exception as e:
        print(f"Warning: {e}")
```

---

## Code Organization

### Project Structure

```
final-project/
├── main.py                 # Entry point, main loop
├── config.py              # Configuration, API key handling
├── requirements.txt       # Dependencies
├── run_tests.py          # Test runner
│
├── core/                  # Core utilities
│   ├── __init__.py
│   ├── commands.py        # Command registry
│   ├── storage.py         # Data persistence
│   ├── errors.py          # Custom exceptions
│   ├── utils.py           # Helper functions
│   └── backup.py          # Backup management
│
├── modules/               # Feature modules
│   ├── __init__.py
│   ├── task_module.py     # Task management
│   ├── docs_module.py     # Document library
│   ├── chat_module.py     # AI chat
│   ├── agent_module.py    # AI agents
│   └── settings_module.py # Settings
│
├── tests/                 # Test suite
│   ├── conftest.py        # Pytest configuration
│   ├── test_tasks.py
│   ├── test_docs.py
│   ├── test_chat.py
│   └── ...
│
└── data/                  # User data (gitignored)
    ├── tasks.json
    ├── docs_metadata.json
    ├── chat_history.json
    ├── settings.json
    ├── docs/
    ├── doc_cache/
    └── backups/
```

### Code Conventions

**Naming**:
- Classes: PascalCase (`TaskManager`)
- Functions/Methods: snake_case (`add_task()`)
- Constants: UPPER_SNAKE_CASE (`MAX_RETRIES`)
- Private methods: Leading underscore (`_save_data()`)

**Documentation**:
- Google-style docstrings
- Type hints for parameters
- Comprehensive error documentation

**Error Handling**:
- Custom exceptions in `core/errors.py`
- Centralized error handling in main loop
- User-friendly error messages

---

## Extension Points

### Adding New Modules

1. Create module file in `modules/`:
```python
class MyModule:
    def __init__(self, data_manager, registry):
        self.data_manager = data_manager
        self.registry = registry
        self._register_commands()
    
    def _register_commands(self):
        self.registry.register_command(
            'mycommand',
            self.cmd_mycommand,
            'Description',
            'mymodule'
        )
    
    def cmd_mycommand(self, *args):
        # Implementation
        pass
```

2. Initialize in `main.py`:
```python
my_module = MyModule(data_manager, registry)
```

3. Add module entry command:
```python
def cmd_mymodule(*args):
    enter_module('mymodule')

registry.register_command('mymodule', cmd_mymodule, 'Enter my module', 'global')
```

### Adding New Commands

In existing module:
```python
def _register_commands(self):
    self.registry.register_command(
        'newcmd',
        self.cmd_newcmd,
        'Command description',
        'modulename'
    )

def cmd_newcmd(self, *args):
    # Validate input
    if not args:
        print("Usage: newcmd <arg>")
        return
    
    # Process
    result = self.do_something(args[0])
    
    # Save if needed
    self._save_data()
    
    # Feedback
    print(f"✓ Success: {result}")
```

### Custom Error Types

Add to `core/errors.py`:
```python
class MyCustomError(PKMSError):
    def __init__(self, message, **kwargs):
        super().__init__(message, **kwargs)
        # Custom initialization
```

Handle in main loop:
```python
except MyCustomError as e:
    print(format_error(str(e)))
```

### Storage Extensions

Extend `DataManager` in `core/storage.py`:
```python
def get_my_data(self):
    """Load my custom data."""
    return self.load("my_data.json")

def save_my_data(self, data):
    """Save my custom data."""
    self.save("my_data.json", data)
```

### Custom Utilities

Add to `core/utils.py`:
```python
def my_helper_function(arg):
    """Helper function description."""
    # Implementation
    return result
```

---

## Testing

### Test Structure

```python
# tests/test_mymodule.py
import pytest
from modules.mymodule import MyModule

@pytest.fixture
def my_module(data_manager, registry):
    return MyModule(data_manager, registry)

def test_my_feature(my_module):
    result = my_module.do_something()
    assert result == expected
```

### Running Tests

```bash
# All tests
python run_tests.py

# Specific module
python -m pytest tests/test_mymodule.py -v

# With coverage
python run_tests.py --coverage
```

---

## Performance Considerations

### Caching Strategy

- **Document Text**: Cached after first extraction
- **Search Results**: Not cached (dynamic)
- **Summaries**: Saved to metadata

### Memory Management

- JSON loaded on demand
- Large documents processed in chunks
- Streaming for API responses

### Optimization Opportunities

1. Database migration (SQLite) for better performance
2. Async API calls for parallel processing
3. Local LLM integration for offline operation
4. Full-text search indexing

---

## Security Considerations

### API Key Management

- Environment variables only
- Never stored in files
- Stripped of quotes automatically
- Validated on startup

### Data Security

- Local storage only
- No cloud sync
- User controls backups
- JSON format (readable, auditable)

### Input Validation

- All user inputs validated
- File paths sanitized
- JSON parsing with error handling
- Command injection prevention

---

## Future Enhancements

### Planned Features

1. **Database Backend**: SQLite for better performance
2. **Plugin System**: External module loading
3. **Cloud Sync**: Optional cloud backup
4. **Web Interface**: Browser-based access
5. **Mobile App**: iOS/Android clients
6. **Collaboration**: Multi-user support
7. **Advanced Search**: Full-text indexing
8. **Custom Themes**: UI customization
9. **Voice Input**: Speech-to-text
10. **Local LLM**: Privacy-focused AI

### Contributing

See repository issues for planned enhancements. Pull requests welcome!

---

For user documentation, see:
- [README.md](README.md)
- [USER_GUIDE.md](USER_GUIDE.md)
- [COMMANDS.md](COMMANDS.md)
