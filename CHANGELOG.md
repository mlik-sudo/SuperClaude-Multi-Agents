# Changelog

All notable changes to SuperClaude Multi-Agents will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive configuration management system with Pydantic validation
- Environment variable support via .env files
- Structured logging system with rotation and JSON format
- JSON-RPC and agent parameter validation
- Complete test suite (unit and integration tests)
- CI/CD pipeline with GitHub Actions
  - Automated testing across Python 3.8-3.12
  - Code quality checks (Black, isort, flake8, mypy)
  - Security scanning (Bandit, Safety, CodeQL)
- Pre-commit hooks for code quality
- Development automation with Makefile
- Comprehensive documentation
  - SETUP.md - Development setup guide
  - CONTRIBUTING.md - Contribution guidelines
  - ARCHITECTURE.md - Detailed system architecture
- Package setup (setup.py, pyproject.toml)

### Changed
- Replaced hardcoded bridge path with configurable environment variable
- Enhanced error handling with proper timeout support
- Improved logging with context and performance tracking
- Updated core orchestrator to use centralized configuration

### Fixed
- Path compatibility issues (now uses Path objects)
- Missing timeout handling in agent execution
- Configuration portability across different environments

### Security
- Added comprehensive .gitignore for secrets
- Implemented input validation and schema checking
- Added security scanning in CI/CD pipeline
- Path traversal prevention in file operations

## [0.1.0] - 2025-01-XX

### Added
- Initial Phase 1 implementation
- SuperClaude central orchestrator
- ADK agent team integration via MCP bridge
- Basic agent delegation system
- Support for 4 ADK agents:
  - watch_collect
  - analyse_watch_report
  - curate_digest
  - label_github_issue
- Priority-based task orchestration
- JSON-RPC 2.0 MCP protocol support
- Basic documentation (README, ROADMAP, SECURITY)
- Git repository initialization

[Unreleased]: https://github.com/mlik-sudo/SuperClaude-Multi-Agents/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/mlik-sudo/SuperClaude-Multi-Agents/releases/tag/v0.1.0
