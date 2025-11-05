"""
🧪 Tests unitaires pour l'intégration Anthropic dans Super Claude

Tests de l'orchestrateur et de la délégation aux agents Anthropic
"""

import pytest
import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch, MagicMock

# Ajout du chemin pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.super_claude import SuperClaude, AgentTeam, AgentTask
from tests.fixtures.anthropic_responses import (
    RESEARCH_AGENT_SUCCESS,
    CODE_AGENT_SUCCESS,
    WRITING_AGENT_SUCCESS,
    ERROR_NO_API_KEY,
    TEST_SCENARIOS
)


class TestSuperClaudeAnthropicIntegration:
    """Tests de l'orchestrateur avec l'équipe Anthropic"""

    @pytest.fixture
    def super_claude(self):
        """Fixture SuperClaude"""
        return SuperClaude()

    def test_anthropic_team_configured(self, super_claude):
        """Vérifie que l'équipe Anthropic est correctement configurée"""
        assert AgentTeam.ANTHROPIC in super_claude.agents
        assert super_claude.agents[AgentTeam.ANTHROPIC]["status"] == "active"
        assert len(super_claude.agents[AgentTeam.ANTHROPIC]["available_agents"]) == 3

    def test_anthropic_agents_list(self, super_claude):
        """Vérifie la liste des agents Anthropic disponibles"""
        agents = super_claude.agents[AgentTeam.ANTHROPIC]["available_agents"]
        assert "research_agent" in agents
        assert "code_agent" in agents
        assert "writing_agent" in agents

    @pytest.mark.asyncio
    async def test_delegate_to_anthropic_research_success(self, super_claude):
        """Test délégation research_agent avec succès"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            # Mock du processus
            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(
                return_value=(
                    json.dumps(TEST_SCENARIOS["research_success"]).encode(),
                    b""
                )
            )
            mock_subprocess.return_value = mock_proc

            result = await super_claude.delegate_to_anthropic(
                "research_agent",
                {"query": "Tendances Python 2024", "depth": "standard"}
            )

            assert result["status"] == "success"
            assert "result" in result
            assert "tokens_used" in result

    @pytest.mark.asyncio
    async def test_delegate_to_anthropic_code_success(self, super_claude):
        """Test délégation code_agent avec succès"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(
                return_value=(
                    json.dumps(TEST_SCENARIOS["code_success"]).encode(),
                    b""
                )
            )
            mock_subprocess.return_value = mock_proc

            result = await super_claude.delegate_to_anthropic(
                "code_agent",
                {"task": "Implémenter Fibonacci", "language": "python"}
            )

            assert result["status"] == "success"
            assert "result" in result

    @pytest.mark.asyncio
    async def test_delegate_to_anthropic_writing_success(self, super_claude):
        """Test délégation writing_agent avec succès"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(
                return_value=(
                    json.dumps(TEST_SCENARIOS["writing_success"]).encode(),
                    b""
                )
            )
            mock_subprocess.return_value = mock_proc

            result = await super_claude.delegate_to_anthropic(
                "writing_agent",
                {"content": "Texte à améliorer", "style": "professional", "task": "improve"}
            )

            assert result["status"] == "success"
            assert "result" in result

    @pytest.mark.asyncio
    async def test_delegate_to_anthropic_bridge_not_found(self, super_claude):
        """Test erreur si bridge introuvable"""
        with patch('config.settings.get_anthropic_bridge_path') as mock_get_path:
            mock_get_path.side_effect = FileNotFoundError("Bridge introuvable")

            result = await super_claude.delegate_to_anthropic(
                "research_agent",
                {"query": "test"}
            )

            assert result["status"] == "error"
            assert "Bridge Anthropic introuvable" in result["output"]

    @pytest.mark.asyncio
    async def test_delegate_to_anthropic_timeout(self, super_claude):
        """Test gestion du timeout"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_proc = AsyncMock()
            mock_proc.communicate = AsyncMock(side_effect=asyncio.TimeoutError())
            mock_proc.kill = Mock()
            mock_subprocess.return_value = mock_proc

            with patch('asyncio.wait_for', side_effect=asyncio.TimeoutError()):
                result = await super_claude.delegate_to_anthropic(
                    "research_agent",
                    {"query": "test"}
                )

                assert result["status"] == "timeout"
                assert "timeout" in result["output"].lower()

    @pytest.mark.asyncio
    async def test_delegate_to_anthropic_process_error(self, super_claude):
        """Test erreur du processus bridge"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_proc = AsyncMock()
            mock_proc.returncode = 1
            mock_proc.communicate = AsyncMock(
                return_value=(b"", b"Error: API key invalid")
            )
            mock_subprocess.return_value = mock_proc

            result = await super_claude.delegate_to_anthropic(
                "research_agent",
                {"query": "test"}
            )

            assert result["status"] == "error"
            assert "erreur" in result["output"].lower()

    @pytest.mark.asyncio
    async def test_delegate_to_anthropic_invalid_json(self, super_claude):
        """Test réponse JSON invalide"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(
                return_value=(b"Not valid JSON", b"")
            )
            mock_subprocess.return_value = mock_proc

            result = await super_claude.delegate_to_anthropic(
                "research_agent",
                {"query": "test"}
            )

            assert result["status"] == "error"
            assert "JSON invalide" in result["output"]

    @pytest.mark.asyncio
    async def test_delegate_to_anthropic_jsonrpc_error(self, super_claude):
        """Test erreur JSON-RPC du bridge"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(
                return_value=(
                    json.dumps(TEST_SCENARIOS["error_invalid_tool"]).encode(),
                    b""
                )
            )
            mock_subprocess.return_value = mock_proc

            result = await super_claude.delegate_to_anthropic(
                "invalid_agent",
                {"query": "test"}
            )

            assert result["status"] == "error"
            assert "Erreur JSON-RPC" in result["output"]

    @pytest.mark.asyncio
    async def test_orchestrate_anthropic_task(self, super_claude):
        """Test orchestration d'une tâche Anthropic"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(
                return_value=(
                    json.dumps(TEST_SCENARIOS["research_success"]).encode(),
                    b""
                )
            )
            mock_subprocess.return_value = mock_proc

            tasks = [
                AgentTask(
                    team=AgentTeam.ANTHROPIC,
                    agent_name="research_agent",
                    method="research",
                    params={"query": "Python trends", "depth": "standard"},
                    priority=1
                )
            ]

            results = await super_claude.orchestrate(tasks)

            assert "anthropic_research_agent" in results
            assert results["anthropic_research_agent"]["status"] == "success"

    @pytest.mark.asyncio
    async def test_orchestrate_mixed_teams(self, super_claude):
        """Test orchestration multi-équipes (ADK + Anthropic)"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            # Mock pour Anthropic
            mock_proc_anthropic = AsyncMock()
            mock_proc_anthropic.returncode = 0
            mock_proc_anthropic.communicate = AsyncMock(
                return_value=(
                    json.dumps(TEST_SCENARIOS["writing_success"]).encode(),
                    b""
                )
            )

            # Mock pour ADK (simple success)
            mock_proc_adk = AsyncMock()
            mock_proc_adk.returncode = 0
            mock_proc_adk.communicate = AsyncMock(
                return_value=(
                    json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"content": [{"text": '{"status": "success"}'}]}}).encode(),
                    b""
                )
            )

            # Alternance des mocks selon l'appel
            mock_subprocess.side_effect = [mock_proc_anthropic, mock_proc_adk]

            tasks = [
                AgentTask(
                    team=AgentTeam.ANTHROPIC,
                    agent_name="writing_agent",
                    method="write",
                    params={"content": "test", "style": "professional"},
                    priority=2
                ),
                AgentTask(
                    team=AgentTeam.ADK,
                    agent_name="watch_collect",
                    method="collect",
                    params={"sources": ["github"]},
                    priority=1
                )
            ]

            results = await super_claude.orchestrate(tasks)

            # Vérifier que les deux tâches ont été exécutées
            assert len(results) == 2
            assert "anthropic_writing_agent" in results
            assert "adk_watch_collect" in results


class TestConfigurationSettings:
    """Tests des configurations et settings"""

    def test_get_anthropic_bridge_path_default(self):
        """Test résolution du chemin par défaut"""
        from config.settings import get_anthropic_bridge_path, PROJECT_ROOT

        path = get_anthropic_bridge_path()
        expected = PROJECT_ROOT / "agents" / "anthropic" / "bridge.py"

        assert path == str(expected)
        assert Path(path).exists()

    def test_get_anthropic_bridge_path_env_var(self, monkeypatch):
        """Test résolution via variable d'environnement"""
        custom_path = "/tmp/custom_bridge.py"

        # Créer un fichier temporaire
        Path(custom_path).touch()

        monkeypatch.setenv("ANTHROPIC_BRIDGE_PATH", custom_path)

        from config.settings import get_anthropic_bridge_path

        path = get_anthropic_bridge_path()
        assert path == custom_path

        # Cleanup
        Path(custom_path).unlink()

    def test_get_anthropic_bridge_path_not_found(self, monkeypatch):
        """Test erreur si bridge inexistant"""
        monkeypatch.setenv("ANTHROPIC_BRIDGE_PATH", "/nonexistent/bridge.py")

        from config.settings import get_anthropic_bridge_path

        with pytest.raises(FileNotFoundError):
            get_anthropic_bridge_path()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
