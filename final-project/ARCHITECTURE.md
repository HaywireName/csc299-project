  # ARCHITECTURE.md - Technical Documentation

Complete technical documentation for PKMS Task Manager.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Design](#architecture-design)
3. [Module Descriptions](#module-descriptions)
4. [Data Structures](#data-structures)
5. [API Integration](#api-integration)
6. [Cost Tracking System](#cost-tracking-system)
7. [Code Organization](#code-organization)
8. [Extension Points](#extension-points)

---

## System Overview

PKMS Task Manager is a modular, terminal-based application built with Python 3.9+. It follows a clean architecture pattern with clear separation of concerns.

### Key Components

- **Main Loop** (`main.py`): User interface and command routing
- **Modules** (`modules/`): Feature implementations (tasks, docs, chat, agent, settings)
- **Core** (`core/`): Shared utilities (commands, storage, errors, utils, backup, cost_tracker)
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

**Task ID System**:
- **Pending tasks**: Numeric IDs (1, 2, 3...) - automatically reindexed when tasks are removed
- **Completed tasks**: Letter IDs (a, b, c...) - allow distinguishing completed from pending tasks
- After 26 completed tasks, IDs continue as aa, ab, ac, etc.
- IDs are regenerated on each operation to maintain consistency
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

## Cost Tracking System

### Overview

The cost tracking system (`core/cost_tracker.py`) provides comprehensive monitoring of OpenAI API usage across all features with per-operation breakdown, session tracking, and persistent history.

### CostTracker Class

**Purpose**: Centralized API cost tracking and reporting

**Key Features**:
- Per-operation cost breakdown
- Session-level tracking
- Persistent cost history
- Multiple operation types support
- Accurate token-based pricing

### Architecture

```
┌──────────────────────────────────────────┐
│         main.py (Initialization)         │
│  cost_tracker = CostTracker(data_dir)    │
└────────────┬─────────────────────────────┘
             │
      ┌──────┴──────┐
      │             │
┌─────▼──────┐ ┌───▼──────┐
│  Modules   │ │  Core    │
│            │ │          │
│ - Tasks    │ │ - Tracker│
│ - Docs     │◄┤ - PRICING│
│ - Chat     │ │ - History│
│ - Agent    │ │          │
└────────────┘ └──────────┘
      │
      │
┌─────▼──────────────────┐
│  data/cost_history.json │
└────────────────────────┘
```

### Pricing Configuration

Defined in `CostTracker.PRICING` dictionary:

```python
PRICING = {
    "gpt-4o": {
        "input": 2.50,    # per 1M tokens
        "output": 10.00
    },
    "gpt-4o-mini": {
        "input": 0.150,   # per 1M tokens
        "output": 0.600
    }
}
```

### Operation Types

1. **task_summary**: AI-generated task summaries (gpt-4o-mini)
2. **doc_summary**: AI-generated document summaries (gpt-4o-mini)
3. **chat_message**: Interactive chat messages (gpt-4o)
4. **task_analysis**: Task prioritization and insights (gpt-4o)
5. **knowledge_synthesis**: Multi-document synthesis (gpt-4o)

### API Call Tracking

**Standard (Non-Streaming) Calls**:
```python
# In task_module.py, docs_module.py, agent_module.py
response = self.openai_client.chat.completions.create(...)

if self.cost_tracker and hasattr(response, 'usage') and response.usage:
    self.cost_tracker.track_api_call(
        operation_type='task_summary',
        model="gpt-4o-mini",
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens
    )
```

**Streaming Calls** (Chat):
```python
# In chat_module.py
stream = self.openai_client.chat.completions.create(..., stream=True)

for chunk in stream:
    # Process chunks...
    
    # Track from final chunk containing usage data
    if hasattr(chunk, 'usage') and chunk.usage:
        if self.cost_tracker:
            self.cost_tracker.track_api_call(
                operation_type='chat_message',
                model="gpt-4o",
                input_tokens=chunk.usage.prompt_tokens,
                output_tokens=chunk.usage.completion_tokens
            )
```

### Cost Calculation

```python
def track_api_call(self, operation_type, model, input_tokens, output_tokens):
    # Get pricing for model
    pricing = self.PRICING.get(model, self.PRICING["gpt-4o-mini"])
    
    # Calculate costs (pricing per 1M tokens)
    input_cost = (input_tokens / 1_000_000) * pricing['input']
    output_cost = (output_tokens / 1_000_000) * pricing['output']
    total_cost = input_cost + output_cost
    
    # Update session totals
    self.current_session['total_cost'] += total_cost
    self.current_session['total_input_tokens'] += input_tokens
    self.current_session['total_output_tokens'] += output_tokens
    
    # Update operation-specific tracking
    if operation_type not in self.current_session['by_operation']:
        self.current_session['by_operation'][operation_type] = {
            'count': 0, 'cost': 0, 'input_tokens': 0, 'output_tokens': 0
        }
    
    self.current_session['by_operation'][operation_type]['count'] += 1
    self.current_session['by_operation'][operation_type]['cost'] += total_cost
    self.current_session['by_operation'][operation_type]['input_tokens'] += input_tokens
    self.current_session['by_operation'][operation_type]['output_tokens'] += output_tokens
```

### Session Management

**Session Start** (automatic):
```python
def __init__(self, data_dir):
    self.cost_history_path = os.path.join(data_dir, 'cost_history.json')
    self.current_session = {
        'session_start': datetime.now().isoformat(),
        'total_cost': 0,
        'total_input_tokens': 0,
        'total_output_tokens': 0,
        'by_operation': {}
    }
```

**Session Save** (on exit):
```python
def save_session(self):
    if self.current_session['total_cost'] == 0:
        return  # Don't save empty sessions
    
    # Load history
    history = self._load_history()
    
    # Add current session with timestamp
    history['sessions'].append({
        'timestamp': self.current_session['session_start'],
        'total_cost': self.current_session['total_cost'],
        'total_input_tokens': self.current_session['total_input_tokens'],
        'total_output_tokens': self.current_session['total_output_tokens'],
        'by_operation': self.current_session['by_operation']
    })
    
    # Save to file
    with open(self.cost_history_path, 'w') as f:
        json.dump(history, f, indent=2)
```

### Data Structure

**cost_history.json**:
```json
{
  "sessions": [
    {
      "timestamp": "2025-11-24T10:30:45.123456",
      "total_cost": 0.0692,
      "total_input_tokens": 15234,
      "total_output_tokens": 8945,
      "by_operation": {
        "chat_message": {
          "count": 3,
          "cost": 0.0234,
          "input_tokens": 5000,
          "output_tokens": 2000
        },
        "task_summary": {
          "count": 5,
          "cost": 0.0012,
          "input_tokens": 1234,
          "output_tokens": 567
        },
        "doc_summary": {
          "count": 2,
          "cost": 0.0089,
          "input_tokens": 8000,
          "output_tokens": 5000
        }
      }
    }
  ]
}
```

### Integration Points

**Module Initialization** (main.py):
```python
from core.cost_tracker import CostTracker

# Initialize tracker
cost_tracker = CostTracker(data_manager.data_dir)

# Pass to all modules
task_manager = TaskManager(data_manager, registry, cost_tracker)
document_manager = DocumentManager(data_manager, registry, cost_tracker)
agent_manager = AgentManager(data_manager, task_manager, registry, document_manager, cost_tracker)
chat_manager = ChatManager(data_manager, registry, agent_manager, cost_tracker)
```

**Stats Command** (main.py):
```python
def cmd_stats():
    # ... existing stats ...
    
    # API Usage & Costs section
    print("\nAPI Usage & Costs:")
    
    # Current session
    summary = cost_tracker.get_session_summary()
    if summary['total_cost'] > 0:
        print("  Current Session:")
        for op_type, data in summary['by_operation'].items():
            print(f"    • {op_type.replace('_', ' ').title()}: ${data['cost']:.4f} ({data['count']} calls)")
        print(f"    {'─' * 37}")
        print(f"    Total: ${summary['total_cost']:.4f}")
    
    # Previous session
    prev_cost = cost_tracker.get_previous_session_cost()
    if prev_cost > 0:
        print(f"\n  Previous Session: ${prev_cost:.4f}")
    
    # All-time total
    all_time = cost_tracker.get_all_time_cost()
    if all_time > 0:
        print(f"  All-Time Total: ${all_time:.4f}")
```

**Exit Handler** (main.py):
```python
def exit_command(*args):
    # Display session summary
    summary = cost_tracker.get_session_summary()
    if summary['total_cost'] > 0:
        print("\n" + "=" * 60)
        print("💰 Session API Cost Summary")
        print("=" * 60)
        print(f"Total API calls: {sum(op['count'] for op in summary['by_operation'].values())}")
        print(f"Total cost: ${summary['total_cost']:.4f}")
        print("\nBreakdown by operation:")
        for op_type, data in summary['by_operation'].items():
            print(f"  • {op_type}: ${data['cost']:.4f} ({data['count']} calls)")
        print("=" * 60)
    
    # Save session
    cost_tracker.save_session()
    
    print("Goodbye!")
    sys.exit(0)
```

### Error Handling

**Missing Usage Data**:
```python
if self.cost_tracker and hasattr(response, 'usage') and response.usage:
    # Track only if usage data available
    self.cost_tracker.track_api_call(...)
```

**Graceful Degradation**:
- If `cost_tracker=None`, operations continue normally
- Missing models default to gpt-4o-mini pricing
- File errors during history save don't crash application

### Testing

**Unit Tests**:
```python
def test_cost_tracking():
    tracker = CostTracker(temp_dir)
    
    # Track operation
    tracker.track_api_call('test', 'gpt-4o-mini', 100, 50)
    
    # Verify calculation
    expected = (100 * 0.150 + 50 * 0.600) / 1_000_000
    summary = tracker.get_session_summary()
    assert abs(summary['total_cost'] - expected) < 1e-10
```

**Integration Testing**:
- Verify all API calls tracked
- Check session persistence
- Validate cost calculations
- Test exit handlers

### Performance Impact

- **Minimal overhead**: Simple arithmetic operations
- **No API calls**: Tracking is local only
- **Async-safe**: No blocking operations
- **Memory efficient**: Single session in memory

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
│   ├── backup.py          # Backup management
│   └── cost_tracker.py    # API cost tracking
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
    ├── cost_history.json  # API cost tracking
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
