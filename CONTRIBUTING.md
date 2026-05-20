# Contributing to ReconForge

Thank you for your interest in contributing to ReconForge! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful and constructive. We're building a tool for authorized security testing and expect all contributors to follow ethical guidelines.

## Getting Started

### Development Setup

```bash
git clone https://github.com/ferasbusiness666/ReconForge.git
cd ReconForge
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
pip install -e .
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=reconforge

# Run specific test file
pytest tests/test_subdomains.py

# Run with verbose output
pytest -v
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code with black
black reconforge tests

# Sort imports with isort
isort reconforge tests

# Lint with flake8
flake8 reconforge tests

# Type check with mypy
mypy reconforge
```

### Pre-commit Hooks

To automatically run checks before committing:

```bash
pre-commit install
pre-commit run --all-files
```

## Making Changes

### Before You Start

1. Check existing issues to avoid duplicate work
2. Open an issue to discuss major changes
3. Fork the repository and create a feature branch

### Commit Guidelines

- Write clear, descriptive commit messages
- Reference related issues (e.g., "Fixes #123")
- Keep commits focused and atomic
- Use present tense ("Add feature" not "Added feature")

### Pull Request Process

1. Update README.md if needed
2. Add tests for new functionality
3. Ensure all tests pass: `pytest`
4. Ensure code is formatted: `black reconforge tests`
5. Write a clear PR description explaining your changes
6. Link related issues

## Adding Features

### New Modules

If adding a new module:

1. Create `reconforge/new_module.py`
2. Add corresponding tests in `tests/test_new_module.py`
3. Update `reconforge/cli.py` if adding CLI commands
4. Update README.md with usage examples
5. Add docstrings following existing style

### New CLI Commands

1. Add function to `reconforge/cli.py` with `@cli.command()` decorator
2. Add appropriate `@click.option()` decorators
3. Add help text and examples
4. Create tests in `tests/test_cli.py`
5. Update README.md with usage

## Testing Requirements

- All new code must have tests
- Tests should cover both success and error cases
- Aim for >80% code coverage
- Use descriptive test names
- Add docstrings to test functions

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all functions
- Include type hints in function signatures
- Update CHANGELOG.md with significant changes

## Reporting Bugs

When reporting bugs, include:

- Python version
- Operating system
- ReconForge version
- Steps to reproduce
- Expected vs actual behavior
- Error messages or tracebacks

## Requesting Features

When requesting features:

- Describe the use case
- Explain why it would be useful
- Provide examples if possible
- Consider backwards compatibility

## Questions?

- Check existing documentation
- Review closed issues for similar questions
- Open a discussion issue

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to ReconForge!
