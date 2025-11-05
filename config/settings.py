#!/usr/bin/env python3
"""
🔧 SuperClaude Configuration Management

Centralized configuration with environment variable support and validation.
Uses Pydantic for type-safe settings with automatic validation.
"""

import os
from pathlib import Path
from typing import Optional, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    All settings can be overridden via environment variables.
    Loads from .env file if present.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ========================================================================
    # GENERAL SETTINGS
    # ========================================================================

    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Runtime environment"
    )

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )

    log_format: Literal["json", "text"] = Field(
        default="json",
        description="Log output format"
    )

    log_dir: Path = Field(
        default=Path("./logs"),
        description="Directory for log files"
    )

    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )

    # ========================================================================
    # AGENT CONFIGURATION
    # ========================================================================

    adk_bridge_path: Optional[Path] = Field(
        default=None,
        description="Path to ADK bridge.py script"
    )

    adk_workspace: Optional[Path] = Field(
        default=None,
        description="Path to ADK workspace directory"
    )

    agent_timeout: int = Field(
        default=300,
        ge=10,
        le=3600,
        description="Agent execution timeout in seconds"
    )

    max_concurrent_agents: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum number of concurrent agents"
    )

    # ========================================================================
    # API KEYS (Optional, for Phase 2+)
    # ========================================================================

    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key for Claude"
    )

    anthropic_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Claude model version"
    )

    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )

    openai_model: str = Field(
        default="gpt-4-turbo-preview",
        description="GPT model version"
    )

    google_api_key: Optional[str] = Field(
        default=None,
        description="Google API key for Gemini"
    )

    gemini_model: str = Field(
        default="gemini-pro",
        description="Gemini model version"
    )

    # ========================================================================
    # MCP SETTINGS
    # ========================================================================

    mcp_protocol_version: str = Field(
        default="2024-11-05",
        description="MCP protocol version"
    )

    mcp_server_name: str = Field(
        default="super-claude-orchestrator",
        description="MCP server identifier"
    )

    # ========================================================================
    # PERFORMANCE & RELIABILITY
    # ========================================================================

    retry_max_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retry attempts"
    )

    retry_backoff_factor: float = Field(
        default=2.0,
        ge=1.0,
        le=10.0,
        description="Exponential backoff factor"
    )

    retry_min_wait: float = Field(
        default=1.0,
        ge=0.1,
        description="Minimum wait between retries (seconds)"
    )

    retry_max_wait: float = Field(
        default=30.0,
        ge=1.0,
        description="Maximum wait between retries (seconds)"
    )

    circuit_breaker_failure_threshold: int = Field(
        default=5,
        ge=1,
        description="Failures before circuit opens"
    )

    circuit_breaker_timeout: int = Field(
        default=60,
        ge=10,
        description="Circuit breaker timeout (seconds)"
    )

    # ========================================================================
    # MONITORING
    # ========================================================================

    enable_metrics: bool = Field(
        default=True,
        description="Enable performance metrics"
    )

    metrics_interval: int = Field(
        default=60,
        ge=10,
        description="Metrics collection interval (seconds)"
    )

    enable_profiling: bool = Field(
        default=False,
        description="Enable performance profiling"
    )

    # ========================================================================
    # SECURITY
    # ========================================================================

    enable_request_signing: bool = Field(
        default=False,
        description="Enable request signing/validation"
    )

    request_timeout: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Request timeout (seconds)"
    )

    rate_limit_rpm: int = Field(
        default=100,
        ge=1,
        description="Rate limit (requests per minute)"
    )

    # ========================================================================
    # DEVELOPMENT / TESTING
    # ========================================================================

    mock_agents: bool = Field(
        default=False,
        description="Use mock agents for testing"
    )

    # ========================================================================
    # VALIDATORS
    # ========================================================================

    @validator("log_dir", "adk_workspace", pre=True)
    def ensure_path(cls, v):
        """Convert string paths to Path objects."""
        if v is None:
            return v
        return Path(v) if not isinstance(v, Path) else v

    @validator("log_dir")
    def create_log_dir(cls, v):
        """Ensure log directory exists."""
        if v:
            v.mkdir(parents=True, exist_ok=True)
        return v

    @validator("anthropic_api_key", "openai_api_key", "google_api_key")
    def validate_api_key(cls, v, field):
        """Validate API key format (basic check)."""
        if v and len(v) < 10:
            raise ValueError(f"{field.name} appears to be invalid (too short)")
        return v

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"

    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    def get_adk_bridge_path(self) -> Path:
        """
        Get ADK bridge path with fallback logic.

        Priority:
        1. Environment variable ADK_BRIDGE_PATH
        2. Default location in user's home directory

        Raises:
            ValueError: If bridge path not configured and default doesn't exist
        """
        if self.adk_bridge_path:
            if not self.adk_bridge_path.exists():
                raise ValueError(f"ADK bridge not found at: {self.adk_bridge_path}")
            return self.adk_bridge_path

        # Try default location
        default_path = Path.home() / ".gemini" / "bridge.py"
        if default_path.exists():
            return default_path

        raise ValueError(
            "ADK_BRIDGE_PATH not configured and default location not found. "
            "Please set ADK_BRIDGE_PATH environment variable."
        )

    def get_adk_workspace(self) -> Path:
        """
        Get ADK workspace path with validation.

        Raises:
            ValueError: If workspace not configured or doesn't exist
        """
        if not self.adk_workspace:
            raise ValueError(
                "ADK_WORKSPACE not configured. "
                "Please set ADK_WORKSPACE environment variable."
            )

        if not self.adk_workspace.exists():
            raise ValueError(f"ADK workspace not found at: {self.adk_workspace}")

        return self.adk_workspace

    def get_anthropic_bridge_path(self) -> Path:
        """
        Get Anthropic bridge path with fallback logic.

        Priority:
        1. Environment variable ANTHROPIC_BRIDGE_PATH
        2. Default location: agents/anthropic/bridge.py in project root

        Returns:
            Path to the Anthropic bridge.py script

        Raises:
            ValueError: If bridge path not found
        """
        # Check for environment variable override
        env_path = os.getenv("ANTHROPIC_BRIDGE_PATH")
        if env_path:
            bridge_path = Path(env_path)
            if not bridge_path.exists():
                raise ValueError(f"Anthropic bridge not found at: {bridge_path}")
            return bridge_path

        # Try default location relative to project root
        # Assuming this file is in config/, project root is parent
        project_root = Path(__file__).parent.parent
        default_path = project_root / "agents" / "anthropic" / "bridge.py"

        if default_path.exists():
            return default_path

        raise ValueError(
            "Anthropic bridge not found. "
            f"Expected at: {default_path} "
            "or set ANTHROPIC_BRIDGE_PATH environment variable."
        )

    def to_dict(self) -> dict:
        """Export settings as dictionary (excluding sensitive data)."""
        data = self.model_dump()

        # Redact sensitive fields
        sensitive_fields = [
            "anthropic_api_key",
            "openai_api_key",
            "google_api_key"
        ]

        for field in sensitive_fields:
            if data.get(field):
                data[field] = "***REDACTED***"

        return data


# ============================================================================
# GLOBAL SETTINGS INSTANCE
# ============================================================================

# Singleton settings instance
# Import this in your modules: from config import settings
settings = Settings()


# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_settings() -> Settings:
    """
    Initialize and validate settings.

    Called on startup to ensure configuration is valid.
    Raises exceptions if critical settings are missing or invalid.
    """
    global settings

    # Validate critical paths if not in mock mode
    if not settings.mock_agents:
        try:
            settings.get_adk_bridge_path()
        except ValueError as e:
            if not settings.is_development():
                raise  # Strict in production
            # In development, just warn
            print(f"⚠️  Warning: {e}")

    # Create log directory
    settings.log_dir.mkdir(parents=True, exist_ok=True)

    return settings


if __name__ == "__main__":
    # Allow testing settings from command line
    import json

    try:
        settings = initialize_settings()
        print("✅ Configuration valid!")
        print("\nCurrent settings:")
        print(json.dumps(settings.to_dict(), indent=2, default=str))
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        exit(1)
