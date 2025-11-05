# 🤝 Contributing to SuperClaude Multi-Agents

Thank you for your interest in contributing! This guide will help you get started.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/SuperClaude-Multi-Agents.git
cd SuperClaude-Multi-Agents

# Add upstream remote
git remote add upstream https://github.com/mlik-sudo/SuperClaude-Multi-Agents.git
```

### 2. Set Up Development Environment

```bash
make setup-dev
```

See [SETUP.md](SETUP.md) for detailed setup instructions.

### 3. Create a Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/improvements
- `chore/` - Maintenance tasks

## Development Workflow

### 1. Make Changes

```bash
# Edit files
# ...

# Run tests frequently
make test

# Format code
make format

# Check code quality
make lint
```

### 2. Write Tests

All new code should include tests:

```python
# tests/unit/test_your_feature.py
import pytest

def test_your_feature():
    """Test description."""
    # Arrange
    input_data = ...

    # Act
    result = your_function(input_data)

    # Assert
    assert result == expected_output
```

**Test coverage requirements:**
- New features: ≥80% coverage
- Bug fixes: Add regression test
- Refactoring: Maintain existing coverage

### 3. Commit Changes

```bash
# Stage changes
git add .

# Commit with conventional commit message
git commit -m "feat: add new agent orchestration feature"
```

**Commit message format:**

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting (no code change)
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```
feat(orchestrator): add parallel task execution
fix(config): handle missing env variables gracefully
docs(readme): update installation instructions
test(bridge): add integration tests for ADK agents
```

### 4. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## Pull Request Guidelines

### PR Checklist

- [ ] Code follows project style (Black, isort, flake8)
- [ ] All tests pass (`make test`)
- [ ] New code has tests (≥80% coverage)
- [ ] Documentation updated (if needed)
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main
- [ ] Pre-commit hooks pass

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Tests pass
- [ ] Code formatted
- [ ] Documentation updated
```

### Review Process

1. **Automated Checks**: CI runs tests, linting, security scans
2. **Code Review**: Maintainer reviews code
3. **Feedback**: Address review comments
4. **Approval**: Once approved, PR is merged

## Code Style

### Python Style Guide

Follow [PEP 8](https://peps.python.org/pep-0008/) with these tools:

- **Black**: Code formatting (line length 100)
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

```bash
# Auto-format
make format

# Check style
make lint
```

### Type Hints

All functions should have type hints:

```python
def process_agent_task(
    agent_name: str,
    params: Dict[str, Any],
    timeout: int = 300
) -> Dict[str, Any]:
    """
    Process agent task with given parameters.

    Args:
        agent_name: Name of the agent
        params: Task parameters
        timeout: Execution timeout in seconds

    Returns:
        Task execution result

    Raises:
        ValueError: If agent_name is invalid
        TimeoutError: If execution exceeds timeout
    """
    ...
```

### Documentation

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of function.

    Longer description if needed, explaining the function's
    purpose and behavior in detail.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is not an integer

    Example:
        >>> example_function("test", 42)
        True
    """
    ...
```

## Testing Guidelines

### Test Structure

```
tests/
├── unit/                # Unit tests (fast, isolated)
│   ├── test_super_claude.py
│   └── test_config.py
├── integration/         # Integration tests
│   └── test_orchestration.py
├── fixtures/            # Test fixtures and mocks
│   └── mock_agents.py
└── conftest.py         # Shared fixtures
```

### Writing Tests

```python
# tests/unit/test_example.py
import pytest
from unittest.mock import Mock, patch

class TestExample:
    """Test suite for Example class."""

    def test_basic_functionality(self):
        """Test basic functionality."""
        result = example_function("input")
        assert result == "expected"

    @pytest.mark.asyncio
    async def test_async_function(self):
        """Test async function."""
        result = await async_function()
        assert result is not None

    def test_error_handling(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            example_function(None)

    @patch('module.external_call')
    def test_with_mock(self, mock_call):
        """Test with mocked dependency."""
        mock_call.return_value = "mocked"
        result = function_using_external_call()
        assert result == "mocked"
        mock_call.assert_called_once()
```

### Running Tests

```bash
# All tests
make test

# Specific test file
pytest tests/unit/test_super_claude.py -v

# Specific test
pytest tests/unit/test_super_claude.py::TestSuperClaude::test_initialization -v

# With coverage
pytest --cov=core --cov-report=html

# Watch mode (auto-rerun on changes)
make watch-tests
```

## Security

### Reporting Vulnerabilities

**DO NOT** create public issues for security vulnerabilities.

Instead:
1. Email security@example.com (or use GitHub Security Advisories)
2. Provide detailed description
3. Wait for response before disclosure

### Security Checklist

- [ ] No hardcoded secrets or credentials
- [ ] Input validation for all user input
- [ ] Path traversal prevention
- [ ] No SQL injection vectors
- [ ] Dependencies have no known vulnerabilities
- [ ] Secrets excluded in `.gitignore`

### Security Tools

```bash
# Security scan
make security

# Pre-commit secret detection
detect-secrets scan
```

## Documentation

### Documentation Updates

Update docs when:
- Adding new features
- Changing APIs
- Adding configuration options
- Fixing bugs (if affects usage)

### Documentation Files

- `README.md` - Project overview
- `docs/SETUP.md` - Setup instructions
- `docs/ARCHITECTURE.md` - System design
- `docs/ROADMAP.md` - Development roadmap
- `SECURITY.md` - Security policies
- Docstrings in code

## Release Process

Releases are managed by maintainers:

1. Version bump in `setup.py` and `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release tag
4. GitHub Actions builds and publishes

## Getting Help

- **Questions**: [GitHub Discussions](https://github.com/mlik-sudo/SuperClaude-Multi-Agents/discussions)
- **Bugs**: [GitHub Issues](https://github.com/mlik-sudo/SuperClaude-Multi-Agents/issues)
- **Chat**: (TBD - Discord/Slack)

## Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Project README

Thank you for contributing! 🎉
