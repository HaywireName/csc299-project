# Testing Checklist for PKMS Task Manager

Use this checklist when running or developing tests.

## Pre-Testing Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment activated (if using one)
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] In project root directory: `/path/to/final-project`

## Running Tests Checklist

### Quick Test Run
- [ ] Run: `python run_tests.py`
- [ ] Verify all tests pass (look for ✓)
- [ ] Check coverage percentage (~87% expected)
- [ ] No errors in output

### Detailed Test Run
- [ ] Run with verbose: `python run_tests.py --verbose`
- [ ] Review each test result
- [ ] Check for any warnings
- [ ] Open coverage report: `htmlcov/index.html`

### Specific Module Testing
- [ ] Storage tests: `python run_tests.py --file test_storage.py`
- [ ] Task tests: `python run_tests.py --file test_tasks.py`
- [ ] Docs tests: `python run_tests.py --file test_docs.py`
- [ ] Chat tests: `python run_tests.py --file test_chat.py`
- [ ] Agent tests: `python run_tests.py --file test_agents.py`
- [ ] Command tests: `python run_tests.py --file test_commands.py`

## Test Coverage Checklist

### Expected Coverage by Module
- [ ] core.storage: ~95%
- [ ] core.commands: ~100%
- [ ] modules.task_module: ~90%
- [ ] modules.docs_module: ~85%
- [ ] modules.chat_module: ~85%
- [ ] modules.agent_module: ~80%

### Overall
- [ ] Total coverage: ~87%
- [ ] No critical paths uncovered
- [ ] Edge cases tested

## Test Quality Checklist

### Code Quality
- [ ] All tests have docstrings
- [ ] Test names are descriptive
- [ ] No hardcoded paths
- [ ] Using fixtures properly
- [ ] Tests are isolated

### Coverage Quality
- [ ] Success cases tested
- [ ] Failure cases tested
- [ ] Edge cases tested
- [ ] Invalid input tested
- [ ] Error handling tested

## Adding New Tests Checklist

When adding new features, ensure:

- [ ] New test file created (if new module)
- [ ] Tests for new functionality added
- [ ] Fixtures updated if needed
- [ ] Mock OpenAI responses added if needed
- [ ] Tests pass: `pytest tests/test_newfile.py`
- [ ] Coverage maintained or improved
- [ ] Documentation updated

## Test File Verification

Verify each test file exists and runs:

- [ ] `tests/__init__.py` - Package init
- [ ] `tests/conftest.py` - Fixtures (250+ lines)
- [ ] `tests/mock_openai.py` - Mock client (200+ lines)
- [ ] `tests/test_storage.py` - 24 tests
- [ ] `tests/test_tasks.py` - 41 tests
- [ ] `tests/test_docs.py` - 30 tests
- [ ] `tests/test_chat.py` - 25 tests
- [ ] `tests/test_agents.py` - 25 tests
- [ ] `tests/test_commands.py` - 25 tests

**Total: ~170 tests**

## Documentation Checklist

- [ ] `tests/README.md` - Comprehensive guide
- [ ] `TESTING_QUICKSTART.md` - Quick reference
- [ ] `TESTING_SUMMARY.md` - Overview
- [ ] `TESTING_CHECKLIST.md` - This file
- [ ] All documentation is up to date

## Performance Checklist

Expected performance:

- [ ] All tests complete in < 15 seconds
- [ ] Single test file in < 3 seconds
- [ ] No hanging tests
- [ ] No memory leaks
- [ ] Cleanup working properly

## CI/CD Checklist

For continuous integration:

- [ ] Tests run on push
- [ ] Tests run on pull request
- [ ] Coverage reports generated
- [ ] Failure notifications working
- [ ] No flaky tests

## Troubleshooting Checklist

If tests fail:

- [ ] Check Python version (3.8+ required)
- [ ] Verify all dependencies installed
- [ ] Check working directory (must be project root)
- [ ] Look for import errors
- [ ] Check for corrupted test data
- [ ] Review error messages
- [ ] Run with `-v` for details
- [ ] Check `pytest --tb=short` for traceback

## Mock OpenAI Checklist

Verify mocking is working:

- [ ] No real API calls made
- [ ] Mock responses returned
- [ ] Call history tracked
- [ ] Cost simulation working
- [ ] No API key needed for tests

## Test Results Verification

After running tests:

- [ ] All tests passed
- [ ] No skipped tests (unless intended)
- [ ] No warnings
- [ ] Coverage report generated
- [ ] HTML report accessible: `htmlcov/index.html`
- [ ] No failed assertions
- [ ] No unhandled exceptions

## Maintenance Checklist

Regular maintenance:

- [ ] Run tests weekly
- [ ] Update dependencies monthly
- [ ] Review and update fixtures
- [ ] Add tests for new features
- [ ] Remove deprecated tests
- [ ] Keep documentation current

## Integration Checklist

Integration with main application:

- [ ] Tests don't interfere with main app
- [ ] Test data isolated
- [ ] No test files in production
- [ ] Mock data clearly marked
- [ ] Tests can run offline

## Security Checklist

Security considerations:

- [ ] No real API keys in tests
- [ ] No sensitive data in test files
- [ ] Temporary files cleaned up
- [ ] No production data accessed
- [ ] Mock credentials used

## Final Verification

Before considering testing complete:

- [ ] All checklists above completed
- [ ] Coverage meets requirements (>85%)
- [ ] All tests pass consistently
- [ ] Documentation reviewed
- [ ] Team members can run tests
- [ ] CI/CD pipeline working

## Quick Commands Reference

```bash
# Run all tests
python run_tests.py

# Run without coverage
python run_tests.py --no-coverage

# Run specific file
python run_tests.py --file test_tasks.py

# Run with verbose output
python run_tests.py --verbose

# List all tests
python run_tests.py --list

# Using pytest directly
pytest                                    # All tests
pytest tests/test_tasks.py               # Specific file
pytest -v                                 # Verbose
pytest -k "test_add"                     # Pattern match
pytest --cov=core --cov=modules          # Coverage
```

## Success Criteria

Tests are considered successful when:

✅ All 170 tests pass
✅ Coverage is ≥87%
✅ No warnings or errors
✅ Tests complete in <15 seconds
✅ HTML coverage report generated
✅ All critical paths tested
✅ Edge cases covered
✅ Error handling verified

---

**Last Updated**: December 2025
**Version**: 1.0
