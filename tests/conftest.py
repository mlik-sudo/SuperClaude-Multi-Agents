"""
Pytest configuration and shared fixtures.
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_settings():
    """Mock settings object for testing."""
    from unittest.mock import MagicMock

    settings = MagicMock()
    settings.agent_timeout = 300
    settings.log_level = "INFO"
    settings.log_format = "json"
    settings.log_dir = Path("./logs")
    settings.max_concurrent_agents = 5
    settings.mock_agents = True
    settings.get_adk_bridge_path.return_value = Path("/mock/bridge.py")
    settings.get_adk_workspace.return_value = Path("/mock/workspace")

    return settings


@pytest.fixture
def mock_agent_response():
    """Mock successful agent response."""
    return {
        "status": "success",
        "output": {
            "result": "Test agent executed successfully",
            "data": {"test": "data"}
        }
    }


@pytest.fixture
def mock_mcp_request():
    """Mock MCP JSON-RPC request."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "test_agent",
            "arguments": {"param1": "value1"}
        }
    }


@pytest.fixture
def mock_mcp_response():
    """Mock MCP JSON-RPC response."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "content": [
                {
                    "type": "text",
                    "text": '{"status": "success", "data": "test"}'
                }
            ]
        }
    }


@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file."""
    config_file = tmp_path / ".env"
    config_file.write_text("""
ENVIRONMENT=development
LOG_LEVEL=DEBUG
ADK_BRIDGE_PATH=/tmp/test/bridge.py
ADK_WORKSPACE=/tmp/test/workspace
AGENT_TIMEOUT=60
    """.strip())
    return config_file


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for agent execution."""
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate = AsyncMock(return_value=(
        b'{"jsonrpc": "2.0", "id": 1, "result": {"content": [{"text": "{\\"status\\": \\"success\\"}"}]}}',
        b''
    ))
    return mock_proc
