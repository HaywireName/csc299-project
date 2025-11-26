# Running Real API Cost Tracking Tests

## Overview

The `test_real_costs.py` file contains tests that make actual OpenAI API calls to verify cost tracking functionality. These tests are **skipped by default** to avoid incurring API costs during normal test runs.

## Test Status

- **Default**: 3 tests SKIPPED (no API calls made)
- **With API key**: 3 tests run (requires real OPENAI_API_KEY)

## Running Real API Tests

### Prerequisites

1. Valid OpenAI API key
2. Sufficient OpenAI credits (tests cost ~$0.01-0.05)
3. Python environment with all dependencies installed

### Method 1: Using Environment Variable (Recommended)

```bash
# Set the flag to enable real API tests
export RUN_REAL_API_TESTS=1
export OPENAI_API_KEY='your-actual-api-key'

# Run only the real API tests
pytest tests/test_real_costs.py -v

# Or run with all tests
python run_tests.py
```

### Method 2: Direct pytest command

```bash
# Run with your API key
OPENAI_API_KEY='your-key' RUN_REAL_API_TESTS=1 pytest tests/test_real_costs.py -v
```

### Viewing Results

```bash
# Verbose output to see costs
RUN_REAL_API_TESTS=1 pytest tests/test_real_costs.py -v -s
```

## What Gets Tested

### 1. Task Summary Cost Tracking
- Creates a task with long description
- Calls real OpenAI API to generate summary
- Verifies cost tracking records:
  - Total cost increased
  - Input/output tokens tracked
  - Operation count incremented

### 2. Document Summary Cost Tracking
- Creates a test text document
- Calls real OpenAI API to generate summary
- Verifies cost tracking records:
  - Total cost increased
  - Input/output tokens tracked
  - Operation count incremented

### 3. Cost Persistence
- Tracks API operations
- Saves cost history to JSON
- Verifies costs persist across sessions
- Tests previous session and all-time cost retrieval

## Expected Costs

| Test | Estimated Cost | Tokens |
|------|---------------|---------|
| Task Summary | $0.01 - $0.02 | ~500-1000 |
| Document Summary | $0.01 - $0.02 | ~1000-2000 |
| Cost Persistence | $0.00 | 0 (no API calls) |
| **Total** | **$0.02 - $0.05** | ~1500-3000 |

*Costs are approximate and depend on OpenAI pricing and content length*

## Safety Features

1. **Skip by Default**: Tests are skipped unless explicitly enabled
2. **API Key Check**: Tests verify real API key is present (not test key)
3. **Isolated Tests**: Uses temporary directories, no production data affected
4. **Cost Tracking**: All costs are tracked and reported

## Troubleshooting

### Tests Still Skipped

```bash
# Make sure environment variable is set
echo $RUN_REAL_API_TESTS  # Should output: 1

# Try with explicit export
export RUN_REAL_API_TESTS=1
pytest tests/test_real_costs.py -v
```

### API Key Issues

```bash
# Verify your API key is set
echo $OPENAI_API_KEY

# Should NOT start with 'sk-test' (that's the mock key)
# Should look like: sk-proj-... or sk-...
```

### Tests Fail

- **Check API credits**: Ensure you have available credits
- **Check network**: Verify internet connection
- **Check API key**: Ensure it's valid and not expired
- **Review errors**: Look at pytest output for specific error messages

## Integration with run_tests.py

The tests integrate seamlessly with the test runner:

```bash
# Normal run (tests skipped)
python run_tests.py
# Output: 214 passed, 3 skipped

# With real API tests
RUN_REAL_API_TESTS=1 python run_tests.py
# Output: 217 passed (if API key valid)
```

## Development Workflow

### During Development
```bash
# Run normal tests (skip API tests)
python run_tests.py
```

### Before Production Deploy
```bash
# Run all tests including API tests
export RUN_REAL_API_TESTS=1
export OPENAI_API_KEY='your-key'
python run_tests.py
```

### CI/CD Integration
```yaml
# In GitHub Actions or similar
- name: Run Tests
  run: python run_tests.py
  # Real API tests skipped automatically

- name: Run Real API Tests (optional)
  if: github.event_name == 'release'
  env:
    RUN_REAL_API_TESTS: 1
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: pytest tests/test_real_costs.py -v
```

## Notes

- Real API tests use the same fixtures as other tests (temp_data_dir, cost_tracker, etc.)
- Tests clean up after themselves (no persistent files)
- Costs are minimal but real - run responsibly
- Tests verify the cost tracking system works correctly with actual API responses

---

**Status**: ✅ Integrated with test suite
**Location**: `tests/test_real_costs.py`
**Skip Condition**: `RUN_REAL_API_TESTS != 1`
