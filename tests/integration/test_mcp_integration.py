"""Integration tests for MCP system components."""
import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.execution_modes import CodeGenerator, ExecutionRouter
from mcp.mcp_call import invoke_mcp_request, load_servers


class TestMCPCallIntegration:
    """Integration tests for mcp_call.py functionality."""

    def test_load_servers_from_config(self):
        """Test loading servers from servers.json."""
        servers = load_servers()

        # Should return a list (even if empty)
        assert isinstance(servers, list)

        # Each server should have required keys
        for server in servers:
            assert "name" in server
            assert "command" in server

    def test_invoke_mcp_request_structure(self):
        """Test that invoke_mcp_request returns expected structure."""
        # Mock subprocess to avoid actual MCP calls
        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_process.stdin = MagicMock()
            mock_process.stdout = MagicMock()
            mock_process.stdout.readline.side_effect = [
                json.dumps({"jsonrpc": "2.0", "id": "test", "result": {}}).encode(),
                b"",
            ]
            mock_process.stderr = MagicMock()
            mock_process.stderr.read.return_value = b""
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            result = invoke_mcp_request("echo test", "tools/list", {}, timeout=5)

            # Should have expected keys
            assert "initialize" in result
            assert "call" in result
            assert "logs" in result
            assert "stderr" in result
            assert "returncode" in result

    @pytest.mark.integration
    def test_mcp_call_list_command_real(self):
        """Test real mcp_call.py list command (if servers configured)."""
        try:
            result = subprocess.run(
                ["python", "-m", "mcp.mcp_call", "list"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=Path(__file__).parent.parent.parent,
            )

            # Should execute without crashing
            assert result.returncode in [0, 1]  # 0 = success, 1 = no servers

            # Should not have critical errors
            assert "Traceback" not in result.stderr
            assert "ModuleNotFoundError" not in result.stderr

        except subprocess.TimeoutExpired:
            pytest.skip("MCP call timed out (servers may not be configured)")
        except FileNotFoundError:
            pytest.skip("mcp_call.py not found in expected location")


class TestCodeGeneratorIntegration:
    """Integration tests for CodeGenerator with real workflows."""

    def create_mock_task(self, team="adk", agent_name="test", params=None):
        """Helper to create mock task."""
        mock_task = MagicMock()
        mock_task.team.value = team
        mock_task.agent_name = agent_name
        mock_task.params = params or {}
        return mock_task

    def test_generated_code_is_executable(self):
        """Test that generated code can be executed."""
        task = self.create_mock_task(
            team="adk", agent_name="watch_collect", params={"sources": ["github"]}
        )

        code = CodeGenerator.generate_workflow_code([task], "Collect repos", [])

        # Should compile without syntax errors
        compile(code, "<string>", "exec")

    def test_generated_code_structure(self):
        """Test that generated code has expected structure."""
        task = self.create_mock_task()
        code = CodeGenerator.generate_workflow_code([task], "Simple task", [])

        # Should have all required components
        assert "import json" in code
        assert "import subprocess" in code
        assert "def call_mcp" in code
        assert "def main()" in code
        assert "if __name__ == '__main__':" in code
        assert "outputs = []" in code
        assert "print(json.dumps(payload" in code

    def test_generated_code_with_complex_workflow(self):
        """Test code generation for complex multi-step workflow."""
        task1 = self.create_mock_task(agent_name="collect", params={"limit": 100})
        task2 = self.create_mock_task(agent_name="analyze", params={})
        task3 = self.create_mock_task(agent_name="report", params={"format": "json"})

        code = CodeGenerator.generate_workflow_code(
            [task1, task2, task3],
            "Collect, analyze, and report",
            [],
        )

        # Should have all three tasks
        assert "Task 1:" in code
        assert "Task 2:" in code
        assert "Task 3:" in code
        assert "result_0" in code
        assert "result_1" in code
        assert "result_2" in code

        # Should compile
        compile(code, "<string>", "exec")


class TestHybridMCPWorkflow:
    """Integration tests for complete hybrid MCP workflows."""

    def create_mock_task(self, team="adk", agent_name="test", params=None):
        """Helper to create mock task."""
        mock_task = MagicMock()
        mock_task.team.value = team
        mock_task.agent_name = agent_name
        mock_task.params = params or {}
        return mock_task

    def test_simple_workflow_routing(self):
        """Test that simple workflows are routed correctly."""
        task = self.create_mock_task(agent_name="watch_collect")

        mode = ExecutionRouter.analyze_task("Collect GitHub repos", [task])
        assert mode.value == "simple"

    def test_complex_workflow_routing(self):
        """Test that complex workflows are routed correctly."""
        task = self.create_mock_task(agent_name="watch_collect")

        mode = ExecutionRouter.analyze_task(
            "Collect repos, filter top 10 with most stars", [task]
        )
        assert mode.value == "complex"

    def test_multi_task_workflow_routing(self):
        """Test routing for multi-task workflows."""
        task1 = self.create_mock_task(agent_name="collect")
        task2 = self.create_mock_task(agent_name="analyze")

        mode = ExecutionRouter.analyze_task(
            "Collect then analyze", [task1, task2]
        )
        assert mode.value == "complex"

    def test_end_to_end_complex_workflow(self):
        """Test complete workflow from routing to code generation."""
        # Step 1: Define tasks
        tasks = [
            self.create_mock_task(
                agent_name="watch_collect",
                params={"sources": ["github"], "days": 7},
            )
        ]

        # Step 2: Route
        description = "Collect Python repos with more than 1000 stars, top 10"
        mode = ExecutionRouter.analyze_task(description, tasks)

        # Should choose complex mode
        assert mode.value == "complex"

        # Step 3: Generate code
        code = CodeGenerator.generate_workflow_code(tasks, description, [])

        # Code should contain filter logic
        assert "Python" in code
        assert "1000" in code or "stars" in code
        assert "filtered" in code or "sorted" in code

        # Should compile
        compile(code, "<string>", "exec")

    def test_routing_explanation_integration(self):
        """Test that routing provides clear explanations."""
        task = self.create_mock_task()

        mode = ExecutionRouter.analyze_task(
            "Filter top 10 Python repos", [task]
        )
        explanation = ExecutionRouter.explain_decision(
            "Filter top 10 Python repos", [task], mode
        )

        # Explanation should be informative
        assert "COMPLEX mode" in explanation
        assert "keywords" in explanation or "filter" in explanation.lower()


class TestMCPClientIntegration:
    """Integration tests for MCP client behavior."""

    @pytest.mark.integration
    def test_servers_json_exists(self):
        """Test that servers.json exists and is valid."""
        servers_path = Path(__file__).parent.parent.parent / "mcp" / "servers.json"

        assert servers_path.exists(), "servers.json should exist"

        # Should be valid JSON
        with open(servers_path) as f:
            data = json.load(f)

        assert isinstance(data, list), "servers.json should contain a list"

    @pytest.mark.integration
    def test_mcp_call_help(self):
        """Test that mcp_call.py --help works."""
        try:
            result = subprocess.run(
                ["python", "-m", "mcp.mcp_call", "list", "--help"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=Path(__file__).parent.parent.parent,
            )

            # Should show help
            assert result.returncode == 0
            assert "usage:" in result.stdout.lower() or "list" in result.stdout.lower()

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Could not run mcp_call.py help")


@pytest.mark.integration
class TestFullWorkflowSimulation:
    """Simulate full workflows with mocked MCP responses."""

    def test_simulated_hybrid_workflow(self):
        """Simulate a complete hybrid workflow."""
        from core.execution_modes import CodeGenerator, ExecutionRouter

        # Mock task
        mock_task = MagicMock()
        mock_task.team.value = "adk"
        mock_task.agent_name = "watch_collect"
        mock_task.params = {"sources": ["github"]}

        # Step 1: Routing
        description = "Collect top 10 Python repos with >1000 stars"
        mode = ExecutionRouter.analyze_task(description, [mock_task])
        assert mode.value == "complex"

        # Step 2: Code generation
        code = CodeGenerator.generate_workflow_code([mock_task], description, [])

        # Verify code structure
        assert "def call_mcp" in code
        assert "watch_collect" in code
        assert "Python" in code
        assert "1000" in code

        # Step 3: Code should be executable (compilation test)
        compile(code, "<string>", "exec")

        # In a real scenario, this code would be executed by CodeExecutor
        # and would make actual MCP calls
