# AGENTS.md

- Language: python 3.13

## Code Standards

- Use modern python features and types
- Use `uv` for dependency management
- Use `pytest` for testing
- Use `ruff` for linting and formatting
- Use `pre-commit` for linting

## Documentation

- Write concise docstrings for all functions, classes and modules. Do not mention unrelated concepts from spec/task/plan/chat.

## Testing

- Always run tests
- Always run lint
- Use fixtures for common logic and mocks in tests
- Put common fixtures needed in multiple tests files in `conftest.py`
- Write concise docstrings for all test functions, classes and fixtures
- Put empty line before first assert call in tests
- Do not use `unittest.mock` or `monkeypatch` where `mocker` fixture from `pytest-mock` can be used
- Do not use `import` inside functions in tests
