"""Unit tests for core/execution_modes.py"""
import json
from unittest.mock import MagicMock

import pytest

from core.execution_modes import CodeGenerator, ExecutionMode, ExecutionRouter


class TestExecutionMode:
    """Tests for ExecutionMode enum."""

    def test_execution_mode_values(self):
        """Test ExecutionMode enum values."""
        assert ExecutionMode.SIMPLE.value == "simple"
        assert ExecutionMode.COMPLEX.value == "complex"

    def test_execution_mode_string_representation(self):
        """Test that ExecutionMode can be used as a string."""
        assert str(ExecutionMode.SIMPLE) == "simple"
        assert str(ExecutionMode.COMPLEX) == "complex"


class TestExecutionRouter:
    """Tests for ExecutionRouter class."""

    def create_mock_task(self, team="adk", agent_name="test_agent", params=None):
        """Helper to create a mock AgentTask."""
        mock_task = MagicMock()
        mock_task.team.value = team
        mock_task.agent_name = agent_name
        mock_task.params = params or {}
        return mock_task

    def test_analyze_task_empty_list(self):
        """Test with zero tasks."""
        mode = ExecutionRouter.analyze_task("", [])
        assert mode == ExecutionMode.SIMPLE

    def test_analyze_task_single_simple(self):
        """Test single task without complex keywords."""
        task = self.create_mock_task()
        mode = ExecutionRouter.analyze_task("Collect repos", [task])
        assert mode == ExecutionMode.SIMPLE

    def test_analyze_task_single_with_filter_keyword(self):
        """Test single task with 'filter' keyword triggers complex."""
        task = self.create_mock_task()
        mode = ExecutionRouter.analyze_task("Collect and filter repos", [task])
        assert mode == ExecutionMode.COMPLEX

    def test_analyze_task_single_with_top_keyword(self):
        """Test single task with 'top' keyword triggers complex."""
        task = self.create_mock_task()
        mode = ExecutionRouter.analyze_task("Get top 10 repos", [task])
        assert mode == ExecutionMode.COMPLEX

    def test_analyze_task_single_with_large_params(self):
        """Test single task with large parameter values triggers complex."""
        task = self.create_mock_task(params={"limit": 500})
        mode = ExecutionRouter.analyze_task("Collect many repos", [task])
        assert mode == ExecutionMode.COMPLEX

    def test_analyze_task_multiple_no_keywords(self):
        """Test multiple tasks without keywords triggers complex."""
        task1 = self.create_mock_task(agent_name="collect")
        task2 = self.create_mock_task(agent_name="analyze")
        mode = ExecutionRouter.analyze_task("Do both tasks", [task1, task2])
        assert mode == ExecutionMode.COMPLEX

    def test_analyze_task_multiple_with_coordination(self):
        """Test multiple tasks with coordination keywords."""
        task1 = self.create_mock_task(agent_name="collect")
        task2 = self.create_mock_task(agent_name="analyze")
        mode = ExecutionRouter.analyze_task(
            "Collect repos then analyze results", [task1, task2]
        )
        assert mode == ExecutionMode.COMPLEX

    def test_analyze_task_keywords_case_insensitive(self):
        """Test that keyword matching is case-insensitive."""
        task = self.create_mock_task()
        mode1 = ExecutionRouter.analyze_task("FILTER repos", [task])
        mode2 = ExecutionRouter.analyze_task("Filter repos", [task])
        mode3 = ExecutionRouter.analyze_task("filter repos", [task])

        assert mode1 == ExecutionMode.COMPLEX
        assert mode2 == ExecutionMode.COMPLEX
        assert mode3 == ExecutionMode.COMPLEX

    def test_analyze_task_all_complex_keywords(self):
        """Test that all defined complex keywords work."""
        task = self.create_mock_task()

        for keyword in ExecutionRouter.COMPLEX_KEYWORDS[:5]:  # Test first 5
            mode = ExecutionRouter.analyze_task(
                f"Task with {keyword} operation", [task]
            )
            assert (
                mode == ExecutionMode.COMPLEX
            ), f"Keyword '{keyword}' should trigger COMPLEX mode"

    def test_analyze_task_coordination_keywords(self):
        """Test coordination keywords."""
        task1 = self.create_mock_task()
        task2 = self.create_mock_task()

        for keyword in ExecutionRouter.COORDINATION_KEYWORDS[:3]:  # Test first 3
            mode = ExecutionRouter.analyze_task(
                f"Task one {keyword} task two", [task1, task2]
            )
            assert (
                mode == ExecutionMode.COMPLEX
            ), f"Coordination keyword '{keyword}' should trigger COMPLEX mode"

    def test_explain_decision_simple_mode(self):
        """Test explanation for simple mode."""
        task = self.create_mock_task()
        mode = ExecutionMode.SIMPLE
        explanation = ExecutionRouter.explain_decision("Collect repos", [task], mode)

        assert "SIMPLE mode" in explanation
        assert "no complex patterns detected" in explanation

    def test_explain_decision_complex_with_keywords(self):
        """Test explanation for complex mode with keywords."""
        task = self.create_mock_task()
        mode = ExecutionMode.COMPLEX
        explanation = ExecutionRouter.explain_decision(
            "Filter top 10 repos with most stars", [task], mode
        )

        assert "COMPLEX mode" in explanation
        assert "keywords" in explanation

    def test_explain_decision_multiple_tasks(self):
        """Test explanation for multiple tasks."""
        task1 = self.create_mock_task()
        task2 = self.create_mock_task()
        mode = ExecutionMode.COMPLEX
        explanation = ExecutionRouter.explain_decision(
            "Do multiple things", [task1, task2], mode
        )

        assert "COMPLEX mode" in explanation
        assert "2 tasks" in explanation

    def test_task_params_suggest_complexity_large_value(self):
        """Test _task_params_suggest_complexity with large values."""
        task = self.create_mock_task(params={"limit": 300})
        result = ExecutionRouter._task_params_suggest_complexity(task)
        assert result is True

    def test_task_params_suggest_complexity_small_value(self):
        """Test _task_params_suggest_complexity with small values."""
        task = self.create_mock_task(params={"limit": 50})
        result = ExecutionRouter._task_params_suggest_complexity(task)
        assert result is False

    def test_task_params_suggest_complexity_no_params(self):
        """Test _task_params_suggest_complexity with no params."""
        task = self.create_mock_task(params={})
        result = ExecutionRouter._task_params_suggest_complexity(task)
        assert result is False

    def test_task_params_suggest_complexity_no_param_attribute(self):
        """Test _task_params_suggest_complexity when task has no params attribute."""
        mock_task = MagicMock()
        del mock_task.params  # Remove params attribute
        result = ExecutionRouter._task_params_suggest_complexity(mock_task)
        assert result is False


class TestCodeGenerator:
    """Tests for CodeGenerator class."""

    def create_mock_task(self, team="adk", agent_name="test_agent", params=None):
        """Helper to create a mock AgentTask."""
        mock_task = MagicMock()
        mock_task.team.value = team
        mock_task.agent_name = agent_name
        mock_task.params = params or {}
        return mock_task

    def test_generate_workflow_code_single_task(self):
        """Test code generation for a single task."""
        task = self.create_mock_task(
            team="adk", agent_name="watch_collect", params={"sources": ["github"]}
        )
        code = CodeGenerator.generate_workflow_code([task], "Collect repos", [])

        assert "import json" in code
        assert "import subprocess" in code
        assert "def call_mcp" in code
        assert "def main()" in code
        assert "watch_collect" in code
        assert "'adk'" in code
        assert "if __name__ == '__main__':" in code

    def test_generate_workflow_code_multiple_tasks(self):
        """Test code generation for multiple tasks."""
        task1 = self.create_mock_task(agent_name="collect", params={})
        task2 = self.create_mock_task(agent_name="analyze", params={})

        code = CodeGenerator.generate_workflow_code(
            [task1, task2], "Collect and analyze", []
        )

        assert "result_0" in code
        assert "result_1" in code
        assert "Task 1:" in code
        assert "Task 2:" in code

    def test_generate_workflow_code_with_filter(self):
        """Test code generation with filter block."""
        task = self.create_mock_task(params={"language": "Python"})

        code = CodeGenerator.generate_workflow_code(
            [task], "Filter Python repos with more than 1000 stars", []
        )

        assert "items = " in code
        assert "filtered_items" in code
        assert "'filtered': filtered_items" in code

    def test_generate_workflow_code_executable(self):
        """Test that generated code is valid Python syntax."""
        task = self.create_mock_task()
        code = CodeGenerator.generate_workflow_code([task], "Simple task", [])

        # Should compile without errors
        compile(code, "<string>", "exec")

    def test_build_filter_block_no_filters(self):
        """Test _build_filter_block with no filter keywords."""
        result = CodeGenerator._build_filter_block("simple task", "result_0")
        assert result is None

    def test_build_filter_block_python_only(self):
        """Test _build_filter_block with 'python only' filter."""
        result = CodeGenerator._build_filter_block("python only repos", "result_0")

        assert result is not None
        code = "\n".join(result)
        assert "language" in code
        assert "Python" in code

    def test_build_filter_block_star_threshold(self):
        """Test _build_filter_block with star threshold."""
        result = CodeGenerator._build_filter_block(
            "repos with more than 500 stars", "result_0"
        )

        assert result is not None
        code = "\n".join(result)
        assert "stars" in code
        assert "500" in code

    def test_build_filter_block_top_n(self):
        """Test _build_filter_block with 'top N' filter."""
        result = CodeGenerator._build_filter_block("top 10 repos", "result_0")

        assert result is not None
        code = "\n".join(result)
        assert "sorted" in code
        assert "[:10]" in code
        assert "reverse=True" in code

    def test_build_filter_block_combined_filters(self):
        """Test _build_filter_block with multiple filters."""
        result = CodeGenerator._build_filter_block(
            "top 20 python only repos with more than 1000 stars", "result_0"
        )

        assert result is not None
        code = "\n".join(result)
        assert "Python" in code
        assert "1000" in code
        assert "[:20]" in code

    def test_extract_number_with_number(self):
        """Test _extract_number extracts numbers correctly."""
        assert CodeGenerator._extract_number("top 10 repos") == 10
        assert CodeGenerator._extract_number("more than 500 stars") == 500
        assert CodeGenerator._extract_number("1000 items") == 1000

    def test_extract_number_no_number(self):
        """Test _extract_number returns None when no number."""
        assert CodeGenerator._extract_number("top repos") is None
        assert CodeGenerator._extract_number("many stars") is None

    def test_extract_number_multiple_numbers(self):
        """Test _extract_number returns first number."""
        assert CodeGenerator._extract_number("10 repos with 20 stars") == 10

    def test_generate_workflow_code_params_serialization(self):
        """Test that task params are properly serialized."""
        task = self.create_mock_task(
            params={"sources": ["github"], "days": 7, "enabled": True}
        )

        code = CodeGenerator.generate_workflow_code([task], "Task", [])

        # Should contain serialized JSON
        assert '"sources": ["github"]' in code or '"sources":["github"]' in code
        assert '"days": 7' in code or '"days":7' in code
        assert '"enabled": true' in code or '"enabled":true' in code
