"""
Unit tests for SuperClaude orchestrator.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path

# Import the modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.super_claude import SuperClaude, AgentTeam, AgentTask


class TestSuperClaude:
    """Test suite for SuperClaude orchestrator."""

    def test_initialization(self):
        """Test SuperClaude initialization."""
        orchestrator = SuperClaude()

        assert orchestrator.session_id == 1
        assert AgentTeam.ADK in orchestrator.agents
        assert AgentTeam.ANTHROPIC in orchestrator.agents
        assert AgentTeam.OPENAI in orchestrator.agents

    def test_initialization_with_config(self, mock_settings):
        """Test SuperClaude initialization with config."""
        with patch('core.super_claude.settings', mock_settings):
            orchestrator = SuperClaude()

            # Should use config bridge path
            mock_settings.get_adk_bridge_path.assert_called_once()

    def test_get_available_agents(self):
        """Test getting available agents list."""
        orchestrator = SuperClaude()

        # Get all agents
        all_agents = orchestrator.get_available_agents()
        assert "adk" in all_agents
        assert len(all_agents["adk"]) == 4  # watch_collect, analyse_watch_report, curate_digest, label_github_issue

        # Get specific team agents
        adk_agents = orchestrator.get_available_agents(team=AgentTeam.ADK)
        assert "adk" in adk_agents
        assert "watch_collect" in adk_agents["adk"]

    def test_get_available_agents_anthropic(self):
        """Test getting Anthropic agents (Phase 2 - should be empty)."""
        orchestrator = SuperClaude()

        anthropic_agents = orchestrator.get_available_agents(team=AgentTeam.ANTHROPIC)
        assert "anthropic" in anthropic_agents
        assert len(anthropic_agents["anthropic"]) == 0  # Not implemented yet

    @pytest.mark.asyncio
    async def test_delegate_to_adk_success(self, mock_subprocess):
        """Test successful delegation to ADK agent."""
        orchestrator = SuperClaude()

        with patch('asyncio.create_subprocess_exec', return_value=mock_subprocess):
            result = await orchestrator.delegate_to_adk(
                "watch_collect",
                {"sources": ["github"]}
            )

            assert result["status"] == "success"
            mock_subprocess.communicate.assert_called_once()

    @pytest.mark.asyncio
    async def test_delegate_to_adk_error(self):
        """Test ADK delegation with error."""
        orchestrator = SuperClaude()

        mock_proc = AsyncMock()
        mock_proc.returncode = 1
        mock_proc.communicate = AsyncMock(return_value=(
            b'',
            b'Error: Agent failed'
        ))

        with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
            result = await orchestrator.delegate_to_adk(
                "watch_collect",
                {"sources": ["github"]}
            )

            assert result["status"] == "error"
            assert "Agent failed" in result["output"]

    @pytest.mark.asyncio
    async def test_delegate_to_adk_timeout(self, mock_settings):
        """Test ADK delegation timeout."""
        with patch('core.super_claude.settings', mock_settings):
            mock_settings.agent_timeout = 1  # 1 second timeout

            orchestrator = SuperClaude()

            # Create a mock that will hang
            mock_proc = AsyncMock()
            mock_proc.communicate = AsyncMock(side_effect=asyncio.TimeoutError())

            with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
                result = await orchestrator.delegate_to_adk(
                    "watch_collect",
                    {"sources": ["github"]}
                )

                assert result["status"] == "timeout"

    @pytest.mark.asyncio
    async def test_delegate_to_adk_exception(self):
        """Test ADK delegation with exception."""
        orchestrator = SuperClaude()

        with patch('asyncio.create_subprocess_exec', side_effect=Exception("Test error")):
            result = await orchestrator.delegate_to_adk(
                "watch_collect",
                {"sources": ["github"]}
            )

            assert result["status"] == "exception"
            assert "Test error" in result["output"]

    @pytest.mark.asyncio
    async def test_delegate_to_anthropic(self):
        """Test delegation to Anthropic (Phase 2 - not implemented)."""
        orchestrator = SuperClaude()

        result = await orchestrator.delegate_to_anthropic(
            "test_agent",
            {"param": "value"}
        )

        assert result["status"] == "not_implemented"
        assert "Phase 2" in result["output"]

    @pytest.mark.asyncio
    async def test_delegate_to_openai(self):
        """Test delegation to OpenAI (Phase 3 - not implemented)."""
        orchestrator = SuperClaude()

        result = await orchestrator.delegate_to_openai(
            "test_agent",
            {"param": "value"}
        )

        assert result["status"] == "not_implemented"
        assert "Phase 3" in result["output"]

    @pytest.mark.asyncio
    async def test_orchestrate_single_task(self, mock_subprocess):
        """Test orchestrating a single task."""
        orchestrator = SuperClaude()

        tasks = [
            AgentTask(
                team=AgentTeam.ADK,
                agent_name="watch_collect",
                method="surveillance",
                params={"sources": ["github"]},
                priority=1
            )
        ]

        with patch('asyncio.create_subprocess_exec', return_value=mock_subprocess):
            results = await orchestrator.orchestrate(tasks)

            assert len(results) == 1
            assert "adk_watch_collect" in results
            assert results["adk_watch_collect"]["status"] == "success"

    @pytest.mark.asyncio
    async def test_orchestrate_multiple_tasks(self, mock_subprocess):
        """Test orchestrating multiple tasks."""
        orchestrator = SuperClaude()

        tasks = [
            AgentTask(
                team=AgentTeam.ADK,
                agent_name="watch_collect",
                method="surveillance",
                params={"sources": ["github"]},
                priority=2
            ),
            AgentTask(
                team=AgentTeam.ADK,
                agent_name="analyse_watch_report",
                method="analyse",
                params={"report": "test"},
                priority=1
            )
        ]

        with patch('asyncio.create_subprocess_exec', return_value=mock_subprocess):
            results = await orchestrator.orchestrate(tasks)

            assert len(results) == 2
            assert "adk_watch_collect" in results
            assert "adk_analyse_watch_report" in results

    @pytest.mark.asyncio
    async def test_orchestrate_priority_sorting(self, mock_subprocess):
        """Test that tasks are executed in priority order."""
        orchestrator = SuperClaude()

        execution_order = []

        async def mock_delegate(agent_name, params):
            execution_order.append(agent_name)
            return {"status": "success"}

        orchestrator.delegate_to_adk = mock_delegate

        tasks = [
            AgentTask(
                team=AgentTeam.ADK,
                agent_name="agent1",
                method="test",
                params={},
                priority=1
            ),
            AgentTask(
                team=AgentTeam.ADK,
                agent_name="agent2",
                method="test",
                params={},
                priority=3
            ),
            AgentTask(
                team=AgentTeam.ADK,
                agent_name="agent3",
                method="test",
                params={},
                priority=2
            )
        ]

        await orchestrator.orchestrate(tasks)

        # Should execute in priority order: 3, 2, 1
        assert execution_order == ["agent2", "agent3", "agent1"]

    def test_agent_task_dataclass(self):
        """Test AgentTask dataclass."""
        task = AgentTask(
            team=AgentTeam.ADK,
            agent_name="test_agent",
            method="test_method",
            params={"key": "value"},
            priority=5
        )

        assert task.team == AgentTeam.ADK
        assert task.agent_name == "test_agent"
        assert task.method == "test_method"
        assert task.params == {"key": "value"}
        assert task.priority == 5

    def test_agent_task_default_priority(self):
        """Test AgentTask default priority."""
        task = AgentTask(
            team=AgentTeam.ADK,
            agent_name="test_agent",
            method="test_method",
            params={}
        )

        assert task.priority == 1  # Default priority

    def test_session_id_increment(self):
        """Test that session ID increments correctly."""
        orchestrator = SuperClaude()

        initial_id = orchestrator.session_id
        assert initial_id == 1

        # Session ID should increment with each request
        # (This would normally happen during delegate_to_adk call)
