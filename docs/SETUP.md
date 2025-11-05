# 🛠️ Setup Guide - SuperClaude Multi-Agents

Complete guide for setting up your development environment.

## Prerequisites

- **Python 3.8+** (3.11 recommended)
- **Git**
- **Virtual environment** (venv or conda)
- **Make** (optional, for automation)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/mlik-sudo/SuperClaude-Multi-Agents.git
cd SuperClaude-Multi-Agents
```

### 2. Set Up Development Environment (Automated)

```bash
make setup-dev
```

This will:
- Install all dependencies
- Create `.env` from template
- Install pre-commit hooks
- Set up the project for development

### 3. Configure Environment

Edit the `.env` file with your configuration:

```bash
# Copy template if not already done
cp .env.example .env

# Edit configuration
nano .env  # or use your preferred editor
```

**Required settings:**

```env
# ADK Configuration (Phase 1)
ADK_BRIDGE_PATH=/path/to/your/adk-workspace/bridge.py
ADK_WORKSPACE=/path/to/your/adk-workspace

# Optional: API Keys (for Phase 2+)
# ANTHROPIC_API_KEY=sk-ant-xxxxx
# OPENAI_API_KEY=sk-xxxxx
```

### 4. Verify Installation

```bash
# Run tests to verify everything works
make test

# Validate configuration
make validate-config

# Run demo
make run-demo
```

## Manual Setup

### Step 1: Create Virtual Environment

```bash
# Using venv
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or using conda
conda create -n super-claude python=3.11
conda activate super-claude
```

### Step 2: Install Dependencies

```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies (for testing, linting, etc.)
pip install -r requirements-dev.txt

# Install package in editable mode
pip install -e .
```

### Step 3: Install Pre-commit Hooks

```bash
pre-commit install
```

This will run code quality checks before each commit.

### Step 4: Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### Step 5: Verify Setup

```bash
# Run tests
pytest -v

# Check code quality
make lint

# Validate configuration
python config/settings.py
```

## Configuration Details

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ADK_BRIDGE_PATH` | Path to ADK bridge.py | `/home/user/adk/bridge.py` |
| `ADK_WORKSPACE` | ADK workspace directory | `/home/user/adk-workspace` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ENVIRONMENT` | Runtime environment | `development` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AGENT_TIMEOUT` | Agent execution timeout (seconds) | `300` |
| `MAX_CONCURRENT_AGENTS` | Max parallel agents | `5` |
| `LOG_FORMAT` | Log format (json/text) | `json` |
| `LOG_DIR` | Log directory | `./logs` |

## Development Workflow

### Running Tests

```bash
# All tests with coverage
make test

# Unit tests only
make test-unit

# Integration tests only
make test-integration

# Fast tests (no coverage)
make test-fast
```

### Code Quality

```bash
# Run all linters
make lint

# Auto-format code
make format

# Type checking
make type-check

# Security scan
make security
```

### Pre-commit Checks

Pre-commit hooks run automatically on `git commit`. To run manually:

```bash
# Run on all files
make pre-commit

# Run on staged files only
pre-commit run
```

## IDE Setup

### Visual Studio Code

1. Install recommended extensions:
   - Python
   - Pylance
   - Python Test Explorer
   - GitLens

2. Create `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### PyCharm

1. Set interpreter to your virtual environment
2. Enable pytest as test runner
3. Configure code style to use Black
4. Enable type checking with mypy

## Troubleshooting

### Import Errors

```bash
# Ensure package is installed in editable mode
pip install -e .

# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Pydantic Import Errors

```bash
# Update pydantic to v2
pip install --upgrade pydantic>=2.5.0
```

### Pre-commit Hook Failures

```bash
# Update hooks
pre-commit autoupdate

# Clear cache and reinstall
pre-commit clean
pre-commit install
```

### Test Failures

```bash
# Clean cache and rerun
make clean
make test

# Run with verbose output
pytest -vv -s
```

### Configuration Errors

```bash
# Validate configuration
python config/settings.py

# Check environment variables
python -c "from config import settings; print(settings.to_dict())"
```

## Next Steps

- ✅ Read [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
- ✅ Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- ✅ Review [ROADMAP.md](ROADMAP.md) for development phases
- ✅ Explore [examples/](../examples/) for usage examples

## Common Commands

```bash
# Development
make setup-dev          # Set up dev environment
make test               # Run tests
make lint               # Check code quality
make format             # Format code
make clean              # Clean build artifacts

# Running
make run-demo           # Run demo
make validate-config    # Validate configuration

# CI/CD
make ci                 # Run full CI pipeline locally
make check-all          # All checks (lint + test + security)

# Utilities
make help               # Show all available commands
make env-info           # Show environment info
make version            # Show version
```

## Support

- **Issues**: [GitHub Issues](https://github.com/mlik-sudo/SuperClaude-Multi-Agents/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mlik-sudo/SuperClaude-Multi-Agents/discussions)
- **Security**: See [SECURITY.md](../SECURITY.md)
