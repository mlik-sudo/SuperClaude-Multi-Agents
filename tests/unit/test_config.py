"""
Unit tests for configuration module.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestSettings:
    """Test suite for Settings configuration."""

    def test_settings_default_values(self):
        """Test default configuration values."""
        from config.settings import Settings

        settings = Settings()

        assert settings.environment == "development"
        assert settings.log_level == "INFO"
        assert settings.log_format == "json"
        assert settings.agent_timeout == 300
        assert settings.max_concurrent_agents == 5

    def test_settings_from_env_vars(self, monkeypatch):
        """Test loading settings from environment variables."""
        from config.settings import Settings

        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        monkeypatch.setenv("AGENT_TIMEOUT", "600")

        settings = Settings()

        assert settings.environment == "production"
        assert settings.log_level == "WARNING"
        assert settings.agent_timeout == 600

    def test_settings_validation_timeout_min(self):
        """Test agent timeout minimum validation."""
        from config.settings import Settings
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Settings(agent_timeout=5)  # Less than minimum (10)

    def test_settings_validation_timeout_max(self):
        """Test agent timeout maximum validation."""
        from config.settings import Settings
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Settings(agent_timeout=5000)  # More than maximum (3600)

    def test_settings_validation_max_concurrent(self):
        """Test max concurrent agents validation."""
        from config.settings import Settings
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Settings(max_concurrent_agents=0)  # Less than minimum (1)

        with pytest.raises(ValidationError):
            Settings(max_concurrent_agents=100)  # More than maximum (50)

    def test_settings_is_production(self):
        """Test is_production() helper method."""
        from config.settings import Settings

        prod_settings = Settings(environment="production")
        assert prod_settings.is_production() is True

        dev_settings = Settings(environment="development")
        assert dev_settings.is_production() is False

    def test_settings_is_development(self):
        """Test is_development() helper method."""
        from config.settings import Settings

        dev_settings = Settings(environment="development")
        assert dev_settings.is_development() is True

        prod_settings = Settings(environment="production")
        assert prod_settings.is_development() is False

    def test_settings_get_adk_bridge_path_from_env(self, tmp_path, monkeypatch):
        """Test getting ADK bridge path from environment."""
        from config.settings import Settings

        bridge_path = tmp_path / "bridge.py"
        bridge_path.touch()

        monkeypatch.setenv("ADK_BRIDGE_PATH", str(bridge_path))

        settings = Settings()
        result = settings.get_adk_bridge_path()

        assert result == bridge_path

    def test_settings_get_adk_bridge_path_default(self, tmp_path):
        """Test getting ADK bridge path from default location."""
        from config.settings import Settings

        # Mock Path.home() to return tmp_path
        with patch("pathlib.Path.home", return_value=tmp_path):
            # Create default location
            default_dir = tmp_path / ".gemini"
            default_dir.mkdir()
            bridge_path = default_dir / "bridge.py"
            bridge_path.touch()

            settings = Settings()
            result = settings.get_adk_bridge_path()

            assert result == bridge_path

    def test_settings_get_adk_bridge_path_not_found(self):
        """Test error when bridge path not found."""
        from config.settings import Settings

        settings = Settings()

        with pytest.raises(ValueError, match="ADK_BRIDGE_PATH not configured"):
            settings.get_adk_bridge_path()

    def test_settings_get_adk_workspace(self, tmp_path, monkeypatch):
        """Test getting ADK workspace path."""
        from config.settings import Settings

        workspace = tmp_path / "workspace"
        workspace.mkdir()

        monkeypatch.setenv("ADK_WORKSPACE", str(workspace))

        settings = Settings()
        result = settings.get_adk_workspace()

        assert result == workspace

    def test_settings_get_adk_workspace_not_configured(self):
        """Test error when workspace not configured."""
        from config.settings import Settings

        settings = Settings()

        with pytest.raises(ValueError, match="ADK_WORKSPACE not configured"):
            settings.get_adk_workspace()

    def test_settings_get_adk_workspace_not_exists(self, monkeypatch):
        """Test error when workspace doesn't exist."""
        from config.settings import Settings

        monkeypatch.setenv("ADK_WORKSPACE", "/nonexistent/path")

        settings = Settings()

        with pytest.raises(ValueError, match="ADK workspace not found"):
            settings.get_adk_workspace()

    def test_settings_to_dict_redacts_secrets(self):
        """Test that to_dict() redacts sensitive fields."""
        from config.settings import Settings

        settings = Settings(
            anthropic_api_key="sk-ant-secret123",
            openai_api_key="sk-secret456",
            google_api_key="google-secret789"
        )

        result = settings.to_dict()

        assert result["anthropic_api_key"] == "***REDACTED***"
        assert result["openai_api_key"] == "***REDACTED***"
        assert result["google_api_key"] == "***REDACTED***"

    def test_settings_log_dir_creation(self, tmp_path, monkeypatch):
        """Test that log directory is created."""
        from config.settings import Settings

        log_dir = tmp_path / "logs"
        assert not log_dir.exists()

        settings = Settings(log_dir=str(log_dir))

        assert log_dir.exists()
        assert log_dir.is_dir()

    def test_api_key_validation_too_short(self):
        """Test API key validation rejects short keys."""
        from config.settings import Settings
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="too short"):
            Settings(anthropic_api_key="short")

    def test_settings_mcp_defaults(self):
        """Test MCP protocol default values."""
        from config.settings import Settings

        settings = Settings()

        assert settings.mcp_protocol_version == "2024-11-05"
        assert settings.mcp_server_name == "super-claude-orchestrator"

    def test_settings_retry_defaults(self):
        """Test retry configuration defaults."""
        from config.settings import Settings

        settings = Settings()

        assert settings.retry_max_attempts == 3
        assert settings.retry_backoff_factor == 2.0
        assert settings.retry_min_wait == 1.0
        assert settings.retry_max_wait == 30.0

    def test_settings_monitoring_defaults(self):
        """Test monitoring configuration defaults."""
        from config.settings import Settings

        settings = Settings()

        assert settings.enable_metrics is True
        assert settings.metrics_interval == 60
        assert settings.enable_profiling is False

    def test_initialize_settings(self, tmp_path, monkeypatch):
        """Test settings initialization."""
        from config.settings import initialize_settings

        # Set up valid environment
        log_dir = tmp_path / "logs"
        bridge_path = tmp_path / ".gemini" / "bridge.py"
        bridge_path.parent.mkdir(parents=True)
        bridge_path.touch()

        monkeypatch.setenv("LOG_DIR", str(log_dir))
        monkeypatch.setenv("ENVIRONMENT", "development")

        with patch("pathlib.Path.home", return_value=tmp_path):
            settings = initialize_settings()

            assert settings is not None
            assert log_dir.exists()
