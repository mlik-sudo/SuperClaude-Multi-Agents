#!/usr/bin/env python3
"""
🧠 Super Claude - Orchestrateur Central Multi-Agents

Chef d'orchestre coordonnant les équipes d'agents spécialisés :
- Équipe ADK (Google A2A)
- Équipe Anthropic (MCP)
- Équipe OpenAI (Agents)
"""

import json
import subprocess
import asyncio
import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Ajout du chemin config pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import get_anthropic_bridge_path, BRIDGE_TIMEOUT

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s [%(name)s]: %(message)s'
)
logger = logging.getLogger(__name__)

class AgentTeam(Enum):
    ADK = "adk"
    ANTHROPIC = "anthropic" 
    OPENAI = "openai"

@dataclass
class AgentTask:
    team: AgentTeam
    agent_name: str
    method: str
    params: Dict[str, Any]
    priority: int = 1

class SuperClaude:
    """
    🧠 Super Claude - Orchestrateur Central
    
    Coordonne et délègue aux équipes d'agents spécialisés
    """
    
    def __init__(self) -> None:
        self.session_id = 1
        self.agents = {
            AgentTeam.ADK: {
                "bridge_path": os.environ.get("ADK_BRIDGE_PATH"),
                "available_agents": [
                    "watch_collect",
                    "analyse_watch_report",
                    "curate_digest",
                    "label_github_issue"
                ]
            },
            AgentTeam.ANTHROPIC: {
                "status": "active",
                "available_agents": [
                    "research_agent",
                    "code_agent",
                    "writing_agent"
                ]
            },
            AgentTeam.OPENAI: {
                "status": "planned",
                "available_agents": []
            }
        }
    
    async def delegate_to_adk(self, agent_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Délégation à l'équipe ADK (Google A2A)
        """
        bridge_path = self.agents[AgentTeam.ADK]["bridge_path"]
        if not bridge_path:
            return {
                "status": "error",
                "output": "ADK_BRIDGE_PATH environment variable not set."
            }
        
        mcp_request = {
            "jsonrpc": "2.0",
            "id": self.session_id,
            "method": "tools/call",
            "params": {
                "name": agent_name,
                "arguments": params
            }
        }
        self.session_id += 1
        
        try:
            proc = await asyncio.create_subprocess_exec(
                "python3", "-u", bridge_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate(
                input=json.dumps(mcp_request).encode()
            )
            
            if proc.returncode == 0:
                response = json.loads(stdout.decode())
                if "result" in response:
                    content = response["result"].get("content", [{}])
                    if content:
                        return json.loads(content[0].get("text", "{}"))
                    
            return {"status": "error", "output": stderr.decode()}
            
        except Exception as e:
            return {"status": "exception", "output": str(e)}
    
    async def delegate_to_anthropic(self, agent_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Délégation à l'équipe Anthropic (MCP) - Phase 2

        Exécute le bridge JSON-RPC Anthropic pour accéder aux agents spécialisés.

        Args:
            agent_name: Nom de l'agent ("research_agent", "code_agent", "writing_agent")
            params: Paramètres spécifiques à l'agent

        Returns:
            Résultat de l'exécution de l'agent avec métadonnées
        """
        try:
            # Résolution du chemin du bridge
            bridge_path = get_anthropic_bridge_path()
        except FileNotFoundError as e:
            return {
                "status": "error",
                "output": f"Bridge Anthropic introuvable: {str(e)}"
            }

        # Construction de la requête JSON-RPC
        mcp_request = {
            "jsonrpc": "2.0",
            "id": self.session_id,
            "method": "tools/call",
            "params": {
                "name": agent_name,
                "arguments": params
            }
        }
        self.session_id += 1

        try:
            # Exécution du bridge
            proc = await asyncio.create_subprocess_exec(
                "python3", "-u", bridge_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Communication avec timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(input=json.dumps(mcp_request).encode()),
                    timeout=BRIDGE_TIMEOUT
                )
            except asyncio.TimeoutError:
                proc.kill()
                return {
                    "status": "timeout",
                    "output": f"Bridge Anthropic timeout après {BRIDGE_TIMEOUT}s"
                }

            # Vérification du code de retour
            if proc.returncode != 0:
                return {
                    "status": "error",
                    "output": f"Bridge Anthropic erreur (code {proc.returncode}): {stderr.decode()}"
                }

            # Parsing de la réponse JSON-RPC
            try:
                response = json.loads(stdout.decode())
            except json.JSONDecodeError as e:
                return {
                    "status": "error",
                    "output": f"Réponse JSON invalide du bridge: {str(e)}\nStdout: {stdout.decode()}"
                }

            # Gestion des erreurs JSON-RPC
            if "error" in response:
                return {
                    "status": "error",
                    "output": f"Erreur JSON-RPC: {response['error'].get('message', 'Unknown error')}"
                }

            # Extraction du résultat MCP
            if "result" not in response:
                return {
                    "status": "error",
                    "output": "Réponse JSON-RPC sans champ 'result'"
                }

            result_content = response["result"].get("content", [])
            if not result_content:
                return {
                    "status": "error",
                    "output": "Réponse MCP sans contenu"
                }

            # Extraction du texte (premier bloc de contenu)
            text_content = result_content[0].get("text", "{}")

            # Parsing du résultat de l'agent
            try:
                agent_result = json.loads(text_content)
                return agent_result
            except json.JSONDecodeError:
                # Si ce n'est pas du JSON, retourner le texte brut
                return {
                    "status": "success",
                    "result": text_content
                }

        except Exception as e:
            return {
                "status": "exception",
                "output": f"Exception lors de l'appel au bridge Anthropic: {str(e)}"
            }
    
    async def delegate_to_openai(self, agent_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Délégation à l'équipe OpenAI - Phase 3  
        """
        return {"status": "not_implemented", "output": "Phase 3 - Équipe OpenAI en développement"}
    
    async def orchestrate(self, tasks: List[AgentTask]) -> Dict[str, Any]:
        """
        🎭 Orchestration multi-agents
        
        Coordonne l'exécution de tâches sur différentes équipes
        """
        results = {}
        
        # Tri par priorité
        tasks.sort(key=lambda x: x.priority, reverse=True)
        
        for task in tasks:
            logger.info(f"Super Claude délègue: {task.agent_name} ({task.team.value})")

            if task.team == AgentTeam.ADK:
                result = await self.delegate_to_adk(task.agent_name, task.params)
            elif task.team == AgentTeam.ANTHROPIC:
                result = await self.delegate_to_anthropic(task.agent_name, task.params)
            elif task.team == AgentTeam.OPENAI:
                result = await self.delegate_to_openai(task.agent_name, task.params)
            else:
                result = {"status": "unknown_team", "output": f"Équipe inconnue: {task.team}"}

            results[f"{task.team.value}_{task.agent_name}"] = result
            logger.info(f"Résultat: {result.get('status', 'unknown')} pour {task.agent_name}")
        
        return results
    
    def get_available_agents(self, team: Optional[AgentTeam] = None) -> Dict[str, List[str]]:
        """
        📋 Liste des agents disponibles par équipe
        """
        if team:
            return {team.value: self.agents[team]["available_agents"]}
        
        return {
            team.value: config["available_agents"] 
            for team, config in self.agents.items()
        }

# 🧪 Tests de démonstration
async def demo_super_claude():
    """
    🎭 Démonstration Super Claude Multi-Agents
    """
    logger.info("Super Claude Multi-Agents - Démonstration")
    logger.info("=" * 50)

    super_claude = SuperClaude()

    # Affichage des agents disponibles
    agents = super_claude.get_available_agents()
    logger.info(f"Agents disponibles: {agents}")

    # Orchestration de tâches
    tasks = [
        AgentTask(
            team=AgentTeam.ADK,
            agent_name="watch_collect",
            method="surveillance",
            params={"sources": ["github"], "output_format": "markdown"},
            priority=1
        )
    ]

    results = await super_claude.orchestrate(tasks)
    logger.info(f"Résultats orchestration: {len(results)} tâche(s) exécutée(s)")

    return results

if __name__ == "__main__":
    asyncio.run(demo_super_claude())