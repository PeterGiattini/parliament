# Parliament Backend Tests

This directory contains a lean guardrail suite for the Parliament backend.
The goal is fast, deterministic feedback while APIs are evolving.

## What we test (now)

- DebateSpec loads/validates from the default YAML
- Router reaches END across the current spec (no content-level assertions)
- Transcript shape is stable at a coarse level (roles/order/counts only)
- Budget guardrails: small recursion_limit raises a clear error

Files:
- `test_debate_spec_and_flow.py`
- `test_budget_guard.py`

## Running Tests

### Run all tests
```bash
uv run pytest -q
```

### Run specific test file
```bash
uv run pytest tests/test_debate_spec_and_flow.py -q
```

### Run tests with coverage
```bash
uv run pytest tests/ --cov=. --cov-report=html
```

### Run tests quietly
```bash
./run_tests.py --quiet
```

## Categories

- Unit tests (current): isolated, fast, no external services; fake LLM injected
- Integration/slow tests (future): to be added once APIs stabilize

## Configuration

Configured in `pyproject.toml`:
- discover `tests/` with `test_*.py`
- handy markers for future slow/integration tests

## Writing tests

- Prefer fakes over networked services; use the `llm` constructor arg to inject a fake
- Assert structure/shape over wording while features are in flux
- Keep tests <5 seconds total runtime

## Test Dependencies

- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting (optional)

## Notes

- Tests avoid real LLM calls via a deterministic fake LLM
- All tests pass without external service configuration
