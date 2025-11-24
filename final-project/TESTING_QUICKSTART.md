# Quick Start - Testing Guide

## Installation

1. **Install test dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify installation**:
   ```bash
   python -m pytest --version
   ```

## Running Tests

### Option 1: Using run_tests.py (Recommended)

```bash
# Run all tests with coverage
python run_tests.py

# Run without coverage (faster)
python run_tests.py --no-coverage

# Run with verbose output  
python run_tests.py --verbose

# Run a specific test file
python run_tests.py --file test_tasks.py

# List all available tests
python run_tests.py --list
```

### Option 2: Using pytest directly

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_tasks.py

# Run with coverage
pytest --cov=core --cov=modules --cov-report=html

# Run verbose
pytest -v
```

## Test Files

- **test_storage.py** - Storage and data persistence (24 tests)
- **test_tasks.py** - Task management operations (41 tests)
- **test_docs.py** - Document management (30 tests)
- **test_chat.py** - Chat functionality (25 tests)
- **test_agents.py** - AI agent operations (25 tests)
- **test_commands.py** - Command system (25 tests)

**Total: ~170 tests**

## Expected Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PKMS Task Manager - Test Suite
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

────────────────────────────────────────────────────────────
  Running Tests
────────────────────────────────────────────────────────────

tests/test_storage.py ......................  ✓
tests/test_tasks.py .....................................  ✓
tests/test_docs.py ..............................  ✓
tests/test_chat.py ......................  ✓
tests/test_agents.py .....................  ✓
tests/test_commands.py .............  ✓

Coverage: 87%

────────────────────────────────────────────────────────────
  Results
────────────────────────────────────────────────────────────

✓ All tests passed!

📊 Coverage report: htmlcov/index.html
```

## Key Features

✅ **No API Keys Required** - All OpenAI calls are mocked
✅ **Fast Execution** - Complete test suite runs in ~10 seconds
✅ **Comprehensive Coverage** - ~87% code coverage
✅ **Isolated Tests** - Each test uses temporary directories
✅ **Automatic Cleanup** - No leftover test data

## Troubleshooting

**Import errors?**
```bash
# Make sure you're in the project root
cd /path/to/final-project
python run_tests.py
```

**Missing pytest?**
```bash
pip install pytest pytest-cov pytest-mock
```

**Coverage report not found?**
```bash
# Run with coverage first
python run_tests.py
# Then open the report
open htmlcov/index.html
```

## Next Steps

- View detailed README: `tests/README.md`
- Check coverage: Open `htmlcov/index.html` in browser
- Run specific tests: `python run_tests.py --file test_tasks.py`
- Add new tests: See `tests/README.md` for examples

---

For more details, see the full documentation in `tests/README.md`
