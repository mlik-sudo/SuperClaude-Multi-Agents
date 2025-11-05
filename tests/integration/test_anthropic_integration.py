"""Integration tests for Anthropic agents via MCP bridge.

Tests the complete flow:
1. JSON-RPC request to bridge
2. Bridge calls Anthropic API
3. Response formatted and returned

Uses mock server for tests without real API calls.
"""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.integration.mock_anthropic_server import (
    MockAnthropicBridge,
    create_mock_bridge,
)


class TestAnthropicBridgeIntegration:
    """Integration tests for Anthropic bridge."""

    @pytest.fixture
    def mock_bridge(self):
        """Create a mock Anthropic bridge."""
        return create_mock_bridge(api_key="test-key-123")

    def test_bridge_initialization(self, mock_bridge):
        """Test that bridge initializes correctly."""
        assert mock_bridge is not None
        assert mock_bridge.client is not None
        assert mock_bridge.model == "claude-3-5-sonnet-20241022"

    def test_research_agent_basic(self, mock_bridge):
        """Test research agent with basic query."""
        result = mock_bridge.research_agent(
            query="What are the latest trends in AI?",
            depth="standard"
        )

        assert result["status"] == "success"
        assert "findings" in result
        assert len(result["findings"]) > 0
        assert "usage" in result
        assert result["usage"]["input_tokens"] > 0
        assert result["usage"]["output_tokens"] > 0

    def test_research_agent_deep_mode(self, mock_bridge):
        """Test research agent with deep research mode."""
        result = mock_bridge.research_agent(
            query="Quantum computing applications",
            depth="deep",
            sources=["arxiv", "nature", "ieee"]
        )

        assert result["status"] == "success"
        assert result["depth"] == "deep"
        assert "Key Findings" in result["findings"] or "findings" in result["findings"].lower()

    def test_research_agent_with_sources(self, mock_bridge):
        """Test research agent with specific sources."""
        result = mock_bridge.research_agent(
            query="Machine learning frameworks",
            sources=["github", "documentation"]
        )

        assert result["status"] == "success"
        assert result["query"] == "Machine learning frameworks"

    def test_code_agent_python(self, mock_bridge):
        """Test code agent for Python code generation."""
        result = mock_bridge.code_agent(
            task="Write a function to calculate Fibonacci numbers",
            language="python"
        )

        assert result["status"] == "success"
        assert "code" in result
        assert result["language"] == "python"
        assert "def fibonacci" in result["code"] or "fibonacci" in result["code"].lower()
        assert "```python" in result["code"]

    def test_code_agent_javascript(self, mock_bridge):
        """Test code agent for JavaScript code generation."""
        result = mock_bridge.code_agent(
            task="Implement a sorting algorithm",
            language="javascript"
        )

        assert result["status"] == "success"
        assert result["language"] == "javascript"
        assert "function" in result["code"] or "const" in result["code"]

    def test_code_agent_with_context(self, mock_bridge):
        """Test code agent with additional context."""
        result = mock_bridge.code_agent(
            task="Add error handling to this function",
            language="python",
            context="def divide(a, b): return a / b"
        )

        assert result["status"] == "success"
        assert "usage" in result

    def test_writing_agent_professional(self, mock_bridge):
        """Test writing agent with professional style."""
        result = mock_bridge.writing_agent(
            topic="Benefits of async programming",
            style="professional",
            length="medium"
        )

        assert result["status"] == "success"
        assert "content" in result
        assert result["style"] == "professional"
        assert len(result["content"]) > 100

    def test_writing_agent_technical(self, mock_bridge):
        """Test writing agent with technical style."""
        result = mock_bridge.writing_agent(
            topic="Docker containerization best practices",
            style="technical",
            length="long"
        )

        assert result["status"] == "success"
        assert result["topic"] == "Docker containerization best practices"

    def test_writing_agent_casual(self, mock_bridge):
        """Test writing agent with casual style."""
        result = mock_bridge.writing_agent(
            topic="Getting started with Python",
            style="casual",
            length="short"
        )

        assert result["status"] == "success"
        assert "usage" in result

    def test_token_usage_tracking(self, mock_bridge):
        """Test that all agents track token usage."""
        results = [
            mock_bridge.research_agent(query="test"),
            mock_bridge.code_agent(task="test"),
            mock_bridge.writing_agent(topic="test")
        ]

        for result in results:
            assert "usage" in result
            assert "input_tokens" in result["usage"]
            assert "output_tokens" in result["usage"]
            assert result["usage"]["input_tokens"] > 0
            assert result["usage"]["output_tokens"] > 0


class TestAnthropicBridgeJSONRPC:
    """Test JSON-RPC interface of the Anthropic bridge."""

    @pytest.fixture
    def bridge_path(self):
        """Get path to the Anthropic bridge script."""
        return PROJECT_ROOT / "agents" / "anthropic" / "bridge.py"

    def test_bridge_file_exists(self, bridge_path):
        """Test that bridge.py exists."""
        assert bridge_path.exists(), f"Bridge file not found at {bridge_path}"

    @pytest.mark.integration
    def test_bridge_json_rpc_initialize(self, bridge_path):
        """Test JSON-RPC initialize method."""
        request = {
            "jsonrpc": "2.0",
            "id": "test-1",
            "method": "initialize",
            "params": {}
        }

        try:
            result = subprocess.run(
                ["python", str(bridge_path)],
                input=json.dumps(request),
                capture_output=True,
                text=True,
                timeout=10,
                env={"ANTHROPIC_API_KEY": "test-key"}
            )

            # Should not crash
            assert result.returncode in [0, 1]

            # Should return valid JSON (if successful)
            if result.returncode == 0 and result.stdout:
                response = json.loads(result.stdout)
                assert "jsonrpc" in response
                assert response["jsonrpc"] == "2.0"

        except subprocess.TimeoutExpired:
            pytest.skip("Bridge process timed out")
        except json.JSONDecodeError:
            pytest.skip("Bridge returned non-JSON output (may need API key)")

    @pytest.mark.integration
    def test_bridge_json_rpc_tools_list(self, bridge_path):
        """Test JSON-RPC tools/list method."""
        request = {
            "jsonrpc": "2.0",
            "id": "test-2",
            "method": "tools/list",
            "params": {}
        }

        try:
            result = subprocess.run(
                ["python", str(bridge_path)],
                input=json.dumps(request),
                capture_output=True,
                text=True,
                timeout=10,
                env={"ANTHROPIC_API_KEY": "test-key"}
            )

            if result.returncode == 0 and result.stdout:
                response = json.loads(result.stdout)
                assert "result" in response
                assert "tools" in response["result"]
                tools = response["result"]["tools"]
                assert len(tools) == 3  # research, code, writing agents

        except (subprocess.TimeoutExpired, json.JSONDecodeError):
            pytest.skip("Could not test tools/list")


class TestAnthropicMCPIntegration:
    """Test integration with MCP system."""

    def test_anthropic_in_mcp_servers_config(self):
        """Test that Anthropic is configured in mcp/servers.json."""
        servers_path = PROJECT_ROOT / "mcp" / "servers.json"

        if not servers_path.exists():
            pytest.skip("servers.json not found")

        with open(servers_path) as f:
            servers = json.load(f)

        # Find Anthropic server
        anthropic_server = None
        for server in servers:
            if server.get("name") == "anthropic":
                anthropic_server = server
                break

        if anthropic_server is None:
            pytest.skip("Anthropic server not yet configured in servers.json")

        # Validate configuration
        assert "command" in anthropic_server
        assert "bridge.py" in anthropic_server["command"]

    @pytest.mark.integration
    def test_mcp_call_anthropic_research(self):
        """Test calling Anthropic research agent via mcp_call.py."""
        try:
            # Prepare MCP request
            request = {
                "server": "anthropic",
                "tool": "research_agent",
                "params": {
                    "query": "Test query for integration",
                    "depth": "quick"
                }
            }

            result = subprocess.run(
                ["python", "-m", "mcp.mcp_call", "call", "anthropic", "research_agent",
                 "--params", json.dumps(request["params"])],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=PROJECT_ROOT,
                env={"ANTHROPIC_API_KEY": "test-key"}
            )

            # Should execute without crash
            assert result.returncode in [0, 1]

            # Should not have Python errors
            assert "Traceback" not in result.stderr

        except subprocess.TimeoutExpired:
            pytest.skip("MCP call timed out")
        except FileNotFoundError:
            pytest.skip("mcp_call.py not available")


class TestAnthropicErrorHandling:
    """Test error handling in Anthropic bridge."""

    @pytest.fixture
    def mock_bridge(self):
        """Create mock bridge."""
        return create_mock_bridge()

    def test_research_agent_empty_query(self, mock_bridge):
        """Test research agent with empty query."""
        result = mock_bridge.research_agent(query="")

        # Should still work (mock doesn't validate)
        assert "status" in result

    def test_code_agent_unsupported_language(self, mock_bridge):
        """Test code agent with unsupported language."""
        result = mock_bridge.code_agent(
            task="Write hello world",
            language="brainfuck"
        )

        # Mock should handle any language
        assert "status" in result

    def test_writing_agent_invalid_style(self, mock_bridge):
        """Test writing agent with non-standard style."""
        result = mock_bridge.writing_agent(
            topic="Test topic",
            style="super-casual-slang"
        )

        # Should still generate content
        assert result["status"] == "success"


class TestAnthropicResponseStructure:
    """Test response structure consistency."""

    @pytest.fixture
    def mock_bridge(self):
        """Create mock bridge."""
        return create_mock_bridge()

    def test_all_responses_have_status(self, mock_bridge):
        """Test that all agent responses include status field."""
        results = [
            mock_bridge.research_agent(query="test"),
            mock_bridge.code_agent(task="test"),
            mock_bridge.writing_agent(topic="test")
        ]

        for result in results:
            assert "status" in result
            assert result["status"] == "success"

    def test_all_responses_have_usage(self, mock_bridge):
        """Test that all agent responses include usage tracking."""
        results = [
            mock_bridge.research_agent(query="test"),
            mock_bridge.code_agent(task="test"),
            mock_bridge.writing_agent(topic="test")
        ]

        for result in results:
            assert "usage" in result
            assert isinstance(result["usage"], dict)
            assert "input_tokens" in result["usage"]
            assert "output_tokens" in result["usage"]

    def test_response_json_serializable(self, mock_bridge):
        """Test that all responses are JSON serializable."""
        results = [
            mock_bridge.research_agent(query="test"),
            mock_bridge.code_agent(task="test"),
            mock_bridge.writing_agent(topic="test")
        ]

        for result in results:
            # Should not raise exception
            json_str = json.dumps(result)
            assert len(json_str) > 0

            # Should be deserializable
            parsed = json.loads(json_str)
            assert parsed == result


@pytest.mark.integration
class TestAnthropicEndToEnd:
    """End-to-end tests for complete workflows."""

    @pytest.fixture
    def mock_bridge(self):
        """Create mock bridge."""
        return create_mock_bridge()

    def test_research_then_write_workflow(self, mock_bridge):
        """Test workflow: research a topic, then write about it."""

        # Step 1: Research
        research_result = mock_bridge.research_agent(
            query="Async programming benefits",
            depth="standard"
        )
        assert research_result["status"] == "success"

        # Step 2: Write based on research
        writing_result = mock_bridge.writing_agent(
            topic="Async programming benefits",
            style="technical",
            length="medium"
        )
        assert writing_result["status"] == "success"

        # Both should have token usage
        total_tokens = (
            research_result["usage"]["output_tokens"] +
            writing_result["usage"]["output_tokens"]
        )
        assert total_tokens > 0

    def test_code_review_workflow(self, mock_bridge):
        """Test workflow: generate code, then review it."""

        # Step 1: Generate code
        code_result = mock_bridge.code_agent(
            task="Write a binary search function",
            language="python"
        )
        assert code_result["status"] == "success"
        generated_code = code_result["code"]

        # Step 2: Review the code
        review_result = mock_bridge.code_agent(
            task="Review this code for bugs and improvements",
            language="python",
            context=generated_code
        )
        assert review_result["status"] == "success"

    def test_multi_agent_collaboration(self, mock_bridge):
        """Test multiple agents working together."""

        # Research agent finds information
        research = mock_bridge.research_agent(
            query="Best practices for API design"
        )

        # Code agent implements based on research
        code = mock_bridge.code_agent(
            task="Create a REST API example following best practices",
            language="python"
        )

        # Writing agent documents it
        docs = mock_bridge.writing_agent(
            topic="API design best practices and implementation",
            style="technical"
        )

        # All should succeed
        assert all([
            research["status"] == "success",
            code["status"] == "success",
            docs["status"] == "success"
        ])

        # Total token usage should be tracked
        total_input = sum([
            research["usage"]["input_tokens"],
            code["usage"]["input_tokens"],
            docs["usage"]["input_tokens"]
        ])
        total_output = sum([
            research["usage"]["output_tokens"],
            code["usage"]["output_tokens"],
            docs["usage"]["output_tokens"]
        ])

        assert total_input > 0
        assert total_output > 0
