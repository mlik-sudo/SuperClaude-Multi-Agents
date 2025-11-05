# Makefile for SuperClaude Multi-Agents
# Automates common development tasks

.PHONY: help install install-dev test lint format clean docs run

# Default target
.DEFAULT_GOAL := help

# Python executable
PYTHON := python3
PIP := $(PYTHON) -m pip

# Directories
SRC_DIRS := core config agents utils
TEST_DIR := tests
DOCS_DIR := docs

help:  ## Show this help message
	@echo "SuperClaude Multi-Agents - Development Commands"
	@echo "================================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install-dev:  ## Install development dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .
	pre-commit install

test:  ## Run tests with coverage
	pytest -v --cov --cov-report=term --cov-report=html

test-unit:  ## Run unit tests only
	pytest tests/unit -v

test-integration:  ## Run integration tests only
	pytest tests/integration -v

test-fast:  ## Run tests without coverage (faster)
	pytest -v

test-verbose:  ## Run tests with verbose output
	pytest -vv -s

lint:  ## Run all linters
	@echo "Running Black..."
	black --check $(SRC_DIRS) $(TEST_DIR)
	@echo "\nRunning isort..."
	isort --check-only $(SRC_DIRS) $(TEST_DIR)
	@echo "\nRunning flake8..."
	flake8 $(SRC_DIRS) $(TEST_DIR)
	@echo "\nRunning mypy..."
	mypy $(SRC_DIRS) --ignore-missing-imports

format:  ## Auto-format code with Black and isort
	black $(SRC_DIRS) $(TEST_DIR)
	isort $(SRC_DIRS) $(TEST_DIR)

type-check:  ## Run type checking with mypy
	mypy $(SRC_DIRS) --strict --ignore-missing-imports

security:  ## Run security checks
	@echo "Running Bandit security scan..."
	bandit -r $(SRC_DIRS) -f screen
	@echo "\nChecking dependencies for vulnerabilities..."
	safety check --json || true

clean:  ## Clean build artifacts and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .eggs/
	rm -rf .pytest_cache/ .mypy_cache/ .coverage htmlcov/
	rm -rf logs/*.log

clean-logs:  ## Clean log files
	rm -rf logs/*.log

validate-config:  ## Validate configuration
	$(PYTHON) config/settings.py

run-demo:  ## Run SuperClaude demo
	$(PYTHON) core/super_claude.py

pre-commit:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

build:  ## Build distribution packages
	$(PYTHON) setup.py sdist bdist_wheel

install-local:  ## Install package locally in editable mode
	$(PIP) install -e .

init-secrets-baseline:  ## Initialize secrets detection baseline
	detect-secrets scan > .secrets.baseline

update-deps:  ## Update dependencies to latest versions
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements.txt
	$(PIP) install --upgrade -r requirements-dev.txt

freeze-deps:  ## Freeze current dependency versions
	$(PIP) freeze > requirements-frozen.txt

check-all:  ## Run all checks (lint, type-check, test, security)
	@echo "Running all checks..."
	@$(MAKE) lint
	@$(MAKE) type-check
	@$(MAKE) test
	@$(MAKE) security

ci:  ## Run CI pipeline locally
	@echo "Running CI pipeline locally..."
	@$(MAKE) clean
	@$(MAKE) install-dev
	@$(MAKE) check-all

setup-dev:  ## Set up development environment
	@echo "Setting up development environment..."
	@$(MAKE) install-dev
	@echo "\nCreating .env file from template..."
	@cp -n .env.example .env || true
	@echo "\nInitializing git hooks..."
	@pre-commit install
	@echo "\n✅ Development environment ready!"
	@echo "Next steps:"
	@echo "  1. Edit .env with your configuration"
	@echo "  2. Run 'make test' to verify setup"
	@echo "  3. Run 'make run-demo' to test SuperClaude"

watch-tests:  ## Watch for changes and run tests automatically
	pytest-watch -v

coverage-html:  ## Generate HTML coverage report
	pytest --cov --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

coverage-xml:  ## Generate XML coverage report (for CI)
	pytest --cov --cov-report=xml

benchmark:  ## Run performance benchmarks
	pytest tests/ -v --benchmark-only

profile:  ## Profile code performance
	$(PYTHON) -m cProfile -o profile.stats core/super_claude.py
	$(PYTHON) -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative'); p.print_stats(20)"

version:  ## Show version information
	@echo "SuperClaude Multi-Agents v0.1.0"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Pip: $$($(PIP) --version)"

env-info:  ## Show environment information
	@echo "Environment Information"
	@echo "======================="
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Pip: $$($(PIP) --version)"
	@echo "Virtual Env: $$VIRTUAL_ENV"
	@echo "\nInstalled packages:"
	@$(PIP) list

.PHONY: all
all: clean install-dev test lint  ## Clean, install, test, and lint
