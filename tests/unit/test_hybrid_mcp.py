"""
Unit tests for Hybrid MCP functionality.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.mcp_client import MCPClient
from sandbox.executor import CodeExecutor, ExecutionResult
from core.execution_modes import ExecutionRouter, ExecutionMode, CodeGenerator
from core.super_claude import AgentTask, AgentTeam


class TestMCPClient:
    """Test suite for MCP Client."""

    def test_initialization(self, tmp_path):
        """Test MCP client initialization."""
        config_file = tmp_path / "servers.json"
        config_file.write_text('[]')

        client = MCPClient(config_path=config_file)
        assert client.config_path == config_file
        assert client.servers == []

    def test_load_servers(self, tmp_path):
        """Test loading MCP server configurations."""
        config_file = tmp_path / "servers.json"
        config_file.write_text('''[
            {
                "name": "test-server",
                "command": "python test.py",
                "description": "Test MCP server"
            }
        ]''')

        client = MCPClient(config_path=config_file)
        assert len(client.servers) == 1
        assert client.servers[0]["name"] == "test-server"

    def test_get_server(self, tmp_path):
        """Test retrieving server by name."""
        config_file = tmp_path / "servers.json"
        config_file.write_text('''[
            {"name": "adk", "command": "python adk.py"}
        ]''')

        client = MCPClient(config_path=config_file)
        server = client.get_server("adk")
        assert server is not None
        assert server["name"] == "adk"

        missing = client.get_server("nonexistent")
        assert missing is None


class TestCodeExecutor:
    """Test suite for Code Executor."""

    @pytest.mark.asyncio
    async def test_execute_python_success(self):
        """Test successful Python code execution."""
        executor = CodeExecutor(keep_files=False)

        code = '''
import json
print(json.dumps({"status": "success", "result": 42}))
'''

        result = await executor.execute_python(code)

        assert result.status == "success"
        assert result.exit_code == 0
        assert "success" in result.stdout

    @pytest.mark.asyncio
    async def test_execute_python_error(self):
        """Test Python code with error."""
        executor = CodeExecutor(keep_files=False)

        code = '''
raise ValueError("Test error")
'''

        result = await executor.execute_python(code)

        assert result.status == "error"
        assert result.exit_code != 0
        assert "ValueError" in result.stderr

    @pytest.mark.asyncio
    async def test_execute_python_timeout(self):
        """Test Python code timeout."""
        executor = CodeExecutor(timeout=1, keep_files=False)

        code = '''
import time
time.sleep(10)
'''

        result = await executor.execute_python(code)

        assert result.status == "timeout"
        assert "timed out" in result.stderr.lower()

    @pytest.mark.asyncio
    async def test_keep_files(self, tmp_path):
        """Test code file persistence."""
        executor = CodeExecutor(workspace_dir=tmp_path, keep_files=True)

        code = 'print("test")'

        result = await executor.execute_python(code, name="test_script")

        assert result.code_file is not None
        assert result.code_file.exists()
        assert "test_script" in result.code_file.name


class TestExecutionRouter:
    """Test suite for Execution Router."""

    def test_single_task_simple_mode(self):
        """Test single task routes to SIMPLE mode."""
        tasks = [
            AgentTask(
                team=AgentTeam.ADK,
                agent_name="watch_collect",
                method="collect",
                params={},
                priority=1
            )
        ]

        mode = ExecutionRouter.analyze_task("collect github repos", tasks)
        assert mode == ExecutionMode.SIMPLE

    def test_multiple_tasks_complex_mode(self):
        """Test multiple coordinated tasks route to COMPLEX mode."""
        tasks = [
            AgentTask(
                team=AgentTeam.ADK,
                agent_name="watch_collect",
                method="collect",
                params={},
                priority=1
            ),
            AgentTask(
                team=AgentTeam.ADK,
                agent_name="analyse_watch_report",
                method="analyze",
                params={},
                priority=2
            )
        ]

        mode = ExecutionRouter.analyze_task(
            "collect repos then analyze the results",
            tasks
        )
        assert mode == ExecutionMode.COMPLEX

    def test_filter_keyword_complex_mode(self):
        """Test filtering keywords trigger COMPLEX mode."""
        tasks = [
            AgentTask(
                team=AgentTeam.ADK,
                agent_name="watch_collect",
                method="collect",
                params={},
                priority=1
            )
        ]

        mode = ExecutionRouter.analyze_task(
            "collect repos and filter only those with more than 1000 stars",
            tasks
        )
        assert mode == ExecutionMode.COMPLEX

    def test_loop_keyword_complex_mode(self):
        """Test loop/iteration keywords trigger COMPLEX mode."""
        tasks = [
            AgentTask(
                team=AgentTeam.ADK,
                agent_name="watch_collect",
                method="collect",
                params={},
                priority=1
            )
        ]

        mode = ExecutionRouter.analyze_task(
            "collect repos for each language in the list",
            tasks
        )
        assert mode == ExecutionMode.COMPLEX

    def test_explain_decision(self):
        """Test execution mode explanation."""
        tasks = [
            AgentTask(
                team=AgentTeam.ADK,
                agent_name="test",
                method="test",
                params={},
                priority=1
            )
        ]

        explanation = ExecutionRouter.explain_decision(
            "simple task",
            tasks,
            ExecutionMode.SIMPLE
        )

        assert "simple" in explanation.lower()
        assert "single task" in explanation.lower()


class TestCodeGenerator:
    """Test suite for Code Generator."""

    def test_generate_python_orchestration(self):
        """Test Python code generation for orchestration."""
        tasks = [
            AgentTask(
                team=AgentTeam.ADK,
                agent_name="watch_collect",
                method="collect",
                params={"sources": ["github"]},
                priority=1
            )
        ]

        code = CodeGenerator.generate_python_orchestration(tasks)

        assert "import subprocess" in code
        assert "import json" in code
        assert "call_mcp" in code
        assert "watch_collect" in code
        assert '"github"' in code

    def test_generate_multiple_tasks(self):
        """Test code generation for multiple tasks."""
        tasks = [
            AgentTask(
                team=AgentTeam.ADK,
                agent_name="watch_collect",
                method="collect",
                params={},
                priority=1
            ),
            AgentTask(
                team=AgentTeam.ADK,
                agent_name="analyse_watch_report",
                method="analyze",
                params={},
                priority=2
            )
        ]

        code = CodeGenerator.generate_python_orchestration(tasks)

        assert "result_0" in code
        assert "result_1" in code
        assert "watch_collect" in code
        assert "analyse_watch_report" in code


class TestHybridIntegration:
    """Integration tests for hybrid MCP system."""

    @pytest.mark.asyncio
    async def test_mcp_client_call_tool(self, tmp_path):
        """Test MCP client tool call (mock)."""
        config_file = tmp_path / "servers.json"
        config_file.write_text('''[
            {"name": "test", "command": "python test.py"}
        ]''')

        client = MCPClient(config_path=config_file)

        # Call will return mock result since actual MCP server isn't running
        result = client.call_tool("test", "test_tool", param1="value1")

        assert result is not None
        assert "status" in result

    @pytest.mark.asyncio
    async def test_code_executor_mcp_call(self):
        """Test code executor calling MCP via generated code."""
        executor = CodeExecutor(keep_files=False)

        # Generate code that would call MCP (but mock for testing)
        code = '''
import json

# Simulate MCP call result
result = {
    "status": "mock_success",
    "output": "Test output"
}

print(json.dumps(result))
'''

        result = await executor.execute_python(code)

        assert result.status == "success"
        assert "mock_success" in result.stdout
