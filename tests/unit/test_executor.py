"""Unit tests for sandbox/executor.py"""
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sandbox.executor import CodeExecutor, ExecutionResult


class TestExecutionResult:
    """Tests for ExecutionResult dataclass."""

    def test_execution_result_success(self):
        """Test successful execution result."""
        result = ExecutionResult(
            success=True,
            stdout="Hello, World!",
            stderr="",
            exit_code=0,
            duration_seconds=0.5,
        )
        assert result.success is True
        assert result.stdout == "Hello, World!"
        assert result.exit_code == 0
        assert result.error_message is None

    def test_execution_result_failure(self):
        """Test failed execution result."""
        result = ExecutionResult(
            success=False,
            stdout="",
            stderr="Error occurred",
            exit_code=1,
            duration_seconds=0.3,
            error_message="Error occurred",
        )
        assert result.success is False
        assert result.exit_code == 1
        assert result.error_message == "Error occurred"


class TestCodeExecutor:
    """Tests for CodeExecutor class."""

    @pytest.fixture
    def tmp_workspace(self, tmp_path):
        """Create a temporary workspace directory."""
        workspace = tmp_path / "sandbox"
        workspace.mkdir()
        return workspace

    @pytest.fixture
    def executor(self, tmp_workspace):
        """Create a CodeExecutor with temporary workspace."""
        return CodeExecutor(timeout=10, workspace_dir=tmp_workspace, keep_files=False)

    @pytest.mark.asyncio
    async def test_execute_python_success(self, executor):
        """Test successful Python code execution."""
        code = 'print("Hello from sandbox")'
        result = await executor.execute_python(code)

        assert result.success is True
        assert "Hello from sandbox" in result.stdout
        assert result.exit_code == 0
        assert result.stderr == ""
        assert result.duration_seconds > 0

    @pytest.mark.asyncio
    async def test_execute_python_with_error(self, executor):
        """Test Python code execution with syntax error."""
        code = "print('Hello')\nraise ValueError('Test error')"
        result = await executor.execute_python(code)

        assert result.success is False
        assert result.exit_code != 0
        assert "ValueError" in result.stderr
        assert result.error_message is not None

    @pytest.mark.asyncio
    async def test_execute_python_timeout(self, tmp_workspace):
        """Test Python execution with timeout."""
        executor = CodeExecutor(timeout=1, workspace_dir=tmp_workspace)
        code = """
import time
time.sleep(10)
print("Should not reach here")
"""
        result = await executor.execute_python(code)

        assert result.success is False
        assert "timed out" in result.stderr.lower()
        assert result.exit_code == -1
        assert "Timeout" in result.error_message

    @pytest.mark.asyncio
    async def test_execute_python_with_name(self, executor):
        """Test execution with custom script name."""
        code = 'print("Named script")'
        result = await executor.execute_python(code, name="custom_script")

        assert result.success is True
        assert "Named script" in result.stdout

    @pytest.mark.asyncio
    async def test_execute_python_keep_files(self, tmp_workspace):
        """Test that files are kept when keep_files=True."""
        executor = CodeExecutor(
            timeout=10, workspace_dir=tmp_workspace, keep_files=True
        )
        code = 'print("Keep this file")'
        result = await executor.execute_python(code)

        assert result.success is True
        assert result.code_path is not None
        assert result.code_path.exists()

        # Cleanup manually
        result.code_path.unlink()

    @pytest.mark.asyncio
    async def test_execute_python_cleanup(self, executor, tmp_workspace):
        """Test that files are cleaned up by default."""
        code = 'print("Temporary file")'

        # Execute code
        result = await executor.execute_python(code)
        assert result.success is True

        # Verify cleanup - only .gitkeep or empty directory
        files = list(tmp_workspace.glob("*.py"))
        assert len(files) == 0

    @pytest.mark.asyncio
    async def test_execute_python_unicode_output(self, executor):
        """Test Python execution with unicode characters."""
        code = 'print("Unicode: 你好世界 🌍")'
        result = await executor.execute_python(code)

        assert result.success is True
        assert "Unicode:" in result.stdout

    @pytest.mark.asyncio
    async def test_execute_python_empty_code(self, executor):
        """Test execution with empty code."""
        code = ""
        result = await executor.execute_python(code)

        assert result.success is True
        assert result.stdout == ""

    @pytest.mark.asyncio
    async def test_execute_deno_not_available(self, executor):
        """Test Deno execution when Deno is not installed."""
        with patch("shutil.which", return_value=None):
            code = 'console.log("Hello from Deno");'
            result = await executor.execute_deno(code)

            assert result.success is False
            assert "Deno binary not found" in result.stderr
            assert result.exit_code == -1
            assert "Deno runtime unavailable" in result.error_message

    @pytest.mark.asyncio
    async def test_execute_deno_success(self, executor):
        """Test successful Deno execution (if Deno is available)."""
        import shutil

        if shutil.which("deno") is None:
            pytest.skip("Deno not available")

        code = 'console.log("Hello from Deno");'
        result = await executor.execute_deno(code)

        assert result.success is True
        assert "Hello from Deno" in result.stdout
        assert result.exit_code == 0

    @pytest.mark.asyncio
    async def test_execute_deno_timeout(self, tmp_workspace):
        """Test Deno execution timeout (if Deno is available)."""
        import shutil

        if shutil.which("deno") is None:
            pytest.skip("Deno not available")

        executor = CodeExecutor(timeout=1, workspace_dir=tmp_workspace)
        code = """
await new Promise((resolve) => setTimeout(resolve, 10000));
console.log("Should not reach here");
"""
        result = await executor.execute_deno(code)

        assert result.success is False
        assert "timed out" in result.stderr.lower()

    def test_cleanup_workspace(self, executor, tmp_workspace):
        """Test cleanup method."""
        # Create some test files
        (tmp_workspace / "test1.py").write_text("print('test')")
        (tmp_workspace / "test2.py").write_text("print('test2')")

        executor.cleanup()

        # Files should be removed
        assert len(list(tmp_workspace.glob("*.py"))) == 0

    def test_cleanup_workspace_keep_files(self, tmp_workspace):
        """Test that cleanup doesn't remove files when keep_files=True."""
        executor = CodeExecutor(
            timeout=10, workspace_dir=tmp_workspace, keep_files=True
        )

        # Create test file
        test_file = tmp_workspace / "test.py"
        test_file.write_text("print('test')")

        executor.cleanup()

        # File should still exist
        assert test_file.exists()

        # Cleanup manually
        test_file.unlink()

    def test_workspace_creation(self, tmp_path):
        """Test that workspace is created if it doesn't exist."""
        workspace = tmp_path / "new_workspace"
        assert not workspace.exists()

        executor = CodeExecutor(workspace_dir=workspace)
        assert workspace.exists()
        assert workspace.is_dir()

    def test_default_workspace(self):
        """Test default workspace path."""
        executor = CodeExecutor()
        expected_path = Path(__file__).parent.parent.parent / "sandbox" / "generated"
        assert executor.workspace.name == "generated"
        assert executor.workspace.parent.name == "sandbox"

    @pytest.mark.asyncio
    async def test_execute_python_multiline(self, executor):
        """Test execution with multiline Python code."""
        code = """
def greet(name):
    return f"Hello, {name}!"

print(greet("SuperClaude"))
"""
        result = await executor.execute_python(code)

        assert result.success is True
        assert "Hello, SuperClaude!" in result.stdout
