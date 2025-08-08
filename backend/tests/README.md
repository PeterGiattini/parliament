# Parliament Backend Tests

This directory contains unit tests for the Parliament backend system.

## Test Structure

- `test_langgraph_structure.py` - Tests for LangGraph orchestrator structure and state management
- `test_debate_orchestrators.py` - Tests for debate orchestrator methods and utilities

## Running Tests

### Run all tests
```bash
# Using the test runner script
./run_tests.py

# Using pytest directly
uv run pytest tests/ -v
```

### Run specific test file
```bash
uv run pytest tests/test_langgraph_structure.py -v
```

### Run tests with coverage
```bash
# Using the test runner script
./run_tests.py --coverage

# Using pytest directly
uv run pytest tests/ --cov=. --cov-report=html
```

### Run tests quietly
```bash
./run_tests.py --quiet
```

## Test Categories

### Unit Tests
- Test individual functions and methods
- Mock external dependencies (LLM, APIs)
- Fast execution
- No external service requirements

### Integration Tests (Future)
- Test complete workflows
- May require external services
- Slower execution
- Marked with `@pytest.mark.integration`

### Slow Tests (Future)
- Tests that take longer to run
- Marked with `@pytest.mark.slow`
- Can be excluded with `-m "not slow"`

## Test Configuration

Tests are configured in `pyproject.toml`:
- Test discovery: `tests/` directory
- File pattern: `test_*.py`
- Class pattern: `Test*`
- Function pattern: `test_*`

## Writing Tests

### Guidelines
1. Use descriptive test names that explain what is being tested
2. Test both success and failure cases
3. Mock external dependencies to avoid credential requirements
4. Use setup/teardown methods for test fixtures
5. Group related tests in test classes

### Example
```python
class TestMyFeature:
    def setup_method(self):
        """Set up test fixtures."""
        self.test_data = {...}

    def test_success_case(self):
        """Test successful operation."""
        result = my_function(self.test_data)
        assert result == expected_value

    def test_failure_case(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            my_function(invalid_data)
```

## Test Dependencies

- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting (optional)

## Notes

- Tests avoid making actual LLM calls to avoid credential requirements.
- **Orchestrator Feature Flag**: The system can switch between the legacy and LangGraph orchestrators via the `USE_LANGGRAPH_ORCHESTRATOR` environment variable. Tests should account for both configurations where applicable.
- All tests should pass without external service configuration.