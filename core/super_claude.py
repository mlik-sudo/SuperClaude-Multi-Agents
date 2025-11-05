#!/usr/bin/env python3
"""
🧠 Super Claude - Orchestrateur Central Multi-Agents

Chef d'orchestre coordonnant les équipes d'agents spécialisés :
- Équipe ADK (Google A2A)
- Équipe Anthropic (MCP)
- Équipe OpenAI (Agents)

Features:
- Hybrid MCP execution (simple CLI + code generation)
- Progressive tool disclosure
- Context-efficient orchestration
- Skills persistence
"""

import json
import subprocess
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Import centralized configuration
try:
    from config import settings
except ImportError:
    # Fallback if config module not available yet
    settings = None
    logging.warning("Config module not found, using fallback configuration")

# Import hybrid MCP components
try:
    from mcp.mcp_client import MCPClient
    from sandbox.executor import CodeExecutor
    from core.execution_modes import ExecutionRouter, ExecutionMode, CodeGenerator
    HYBRID_MCP_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Hybrid MCP components not available: {e}")
    HYBRID_MCP_AVAILABLE = False
    MCPClient = None
    CodeExecutor = None
    ExecutionRouter = None
    ExecutionMode = None
    CodeGenerator = None

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

    def __init__(self):
        self.session_id = 1
        self.logger = logging.getLogger(__name__)

        # Initialize hybrid MCP components
        if HYBRID_MCP_AVAILABLE:
            self.mcp_client = MCPClient()
            self.code_executor = CodeExecutor(
                timeout=settings.agent_timeout if settings else 300
            )
            self.hybrid_mode_enabled = True
            self.logger.info("✅ Hybrid MCP mode enabled (CLI + Code Execution)")
        else:
            self.mcp_client = None
            self.code_executor = None
            self.hybrid_mode_enabled = False
            self.logger.warning("⚠️  Hybrid MCP mode disabled (components not available)")

        # Get bridge path from configuration or fallback
        if settings:
            try:
                bridge_path = str(settings.get_adk_bridge_path())
            except ValueError as e:
                self.logger.warning(f"ADK bridge path not configured: {e}")
                bridge_path = str(Path.home() / ".gemini" / "bridge.py")
        else:
            # Fallback for backward compatibility
            bridge_path = str(Path.home() / ".gemini" / "bridge.py")

        self.agents = {
            AgentTeam.ADK: {
                "bridge_path": bridge_path,
                "available_agents": [
                    "watch_collect",
                    "analyse_watch_report",
                    "curate_digest",
                    "label_github_issue"
                ]
            },
            AgentTeam.ANTHROPIC: {
                "status": "planned",
                "available_agents": []
            },
            AgentTeam.OPENAI: {
                "status": "planned",
                "available_agents": []
            }
        }

        # Tools cache for progressive disclosure
        self.tools_cache: Dict[str, List[Dict[str, Any]]] = {}

        self.logger.info(f"SuperClaude initialized with ADK bridge at: {bridge_path}")
    
    async def delegate_to_adk(self, agent_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Délégation à l'équipe ADK (Google A2A)
        """
        bridge_path = self.agents[AgentTeam.ADK]["bridge_path"]

        # Get timeout from config or use default
        timeout = settings.agent_timeout if settings else 300

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

        self.logger.info(f"Delegating to ADK agent: {agent_name}")

        try:
            proc = await asyncio.create_subprocess_exec(
                "python3", "-u", bridge_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Add timeout to communicate
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=json.dumps(mcp_request).encode()),
                timeout=timeout
            )

            if proc.returncode == 0:
                response = json.loads(stdout.decode())
                if "result" in response:
                    content = response["result"].get("content", [{}])
                    if content:
                        self.logger.info(f"ADK agent {agent_name} completed successfully")
                        return json.loads(content[0].get("text", "{}"))

            self.logger.error(f"ADK agent {agent_name} failed: {stderr.decode()}")
            return {"status": "error", "output": stderr.decode()}

        except asyncio.TimeoutError:
            self.logger.error(f"ADK agent {agent_name} timed out after {timeout}s")
            return {"status": "timeout", "output": f"Agent execution timed out after {timeout}s"}
        except Exception as e:
            self.logger.exception(f"ADK agent {agent_name} raised exception")
            return {"status": "exception", "output": str(e)}
    
    async def delegate_to_anthropic(self, agent_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Délégation à l'équipe Anthropic (MCP) - Phase 3 ACTIVE

        Calls Anthropic Claude agents via JSON-RPC 2.0 STDIO bridge.
        Supported agents: research_agent, code_agent, writing_agent

        Args:
            agent_name: Name of the Anthropic agent (research_agent, code_agent, writing_agent)
            params: Agent-specific parameters

        Returns:
            Result dict with status, output, and usage tracking
        """
        try:
            # Get bridge path from configuration
            if settings:
                try:
                    bridge_path = str(settings.get_anthropic_bridge_path())
                except ValueError as e:
                    self.logger.error(f"Anthropic bridge not found: {e}")
                    return {
                        "status": "error",
                        "error": f"Bridge not found: {e}",
                        "output": "Anthropic bridge not configured"
                    }
            else:
                # Fallback to default location
                project_root = Path(__file__).parent.parent
                bridge_path = str(project_root / "agents" / "anthropic" / "bridge.py")

                if not Path(bridge_path).exists():
                    return {
                        "status": "error",
                        "error": "Bridge file not found",
                        "output": f"Anthropic bridge not found at {bridge_path}"
                    }

            # Construct JSON-RPC 2.0 request
            request = {
                "jsonrpc": "2.0",
                "id": f"sc-{self.session_id}",
                "method": f"tools/{agent_name}",
                "params": params
            }

            request_json = json.dumps(request)
            timeout = settings.agent_timeout if settings else 300

            self.logger.info(f"🟢 Calling Anthropic {agent_name} via MCP bridge")

            # Execute bridge via subprocess
            proc = await asyncio.create_subprocess_exec(
                "python", bridge_path,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Send request and get response
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=request_json.encode()),
                timeout=timeout
            )

            # Parse JSON-RPC response
            if proc.returncode == 0 and stdout:
                response = json.loads(stdout.decode())

                if "error" in response:
                    # JSON-RPC error response
                    error_obj = response["error"]
                    self.logger.error(f"Anthropic {agent_name} error: {error_obj.get('message')}")
                    return {
                        "status": "error",
                        "error": error_obj.get("message", "Unknown error"),
                        "code": error_obj.get("code", -1),
                        "output": json.dumps(error_obj)
                    }

                if "result" in response:
                    # Success response
                    result = response["result"]
                    self.logger.info(f"✅ Anthropic {agent_name} completed successfully")
                    self.session_id += 1
                    return result

            # Failed execution
            error_msg = stderr.decode() if stderr else "Unknown error"
            self.logger.error(f"Anthropic {agent_name} failed: {error_msg}")
            return {
                "status": "error",
                "error": "Execution failed",
                "output": error_msg,
                "returncode": proc.returncode
            }

        except asyncio.TimeoutError:
            self.logger.error(f"Anthropic {agent_name} timed out after {timeout}s")
            return {
                "status": "timeout",
                "error": f"Agent execution timed out after {timeout}s",
                "output": "Timeout exceeded"
            }
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON response from Anthropic {agent_name}: {e}")
            return {
                "status": "error",
                "error": f"Invalid JSON response: {e}",
                "output": stdout.decode() if stdout else ""
            }
        except Exception as e:
            self.logger.exception(f"Anthropic {agent_name} raised exception")
            return {
                "status": "exception",
                "error": str(e),
                "output": f"Exception: {type(e).__name__}: {e}"
            }
    
    async def delegate_to_openai(self, agent_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Délégation à l'équipe OpenAI - Phase 3
        """
        return {"status": "not_implemented", "output": "Phase 3 - Équipe OpenAI en développement"}

    # ========================================================================
    # HYBRID MCP METHODS (Phase 2.5)
    # ========================================================================

    async def discover_tools(self, mcp_name: str) -> List[Dict[str, Any]]:
        """
        Progressive tool discovery for an MCP server.

        Args:
            mcp_name: Name of the MCP server

        Returns:
            List of available tools with schemas
        """
        if not self.hybrid_mode_enabled or not self.mcp_client:
            self.logger.warning("Hybrid mode not enabled, cannot discover tools")
            return []

        # Check cache first
        if mcp_name in self.tools_cache:
            self.logger.debug(f"Using cached tools for {mcp_name}")
            return self.tools_cache[mcp_name]

        # Discover tools via MCP client
        tools = self.mcp_client.list_tools(mcp_name, use_cache=True)
        self.tools_cache[mcp_name] = tools

        self.logger.info(f"Discovered {len(tools)} tools for {mcp_name}")
        return tools

    async def execute_simple(
        self,
        mcp_name: str,
        tool_name: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simple execution mode: direct MCP CLI call.

        Args:
            mcp_name: Name of the MCP server
            tool_name: Name of the tool to call
            params: Tool parameters

        Returns:
            Tool execution result
        """
        if not self.hybrid_mode_enabled or not self.mcp_client:
            # Fallback to legacy delegate method
            self.logger.warning("Hybrid mode not enabled, falling back to legacy method")
            if mcp_name == "adk":
                return await self.delegate_to_adk(tool_name, params)
            return {"status": "error", "output": "Hybrid mode not available"}

        self.logger.info(f"[SIMPLE MODE] Calling {mcp_name}.{tool_name}")

        result = self.mcp_client.call_tool(mcp_name, tool_name, **params)

        return result

    async def execute_complex(
        self,
        tasks: List[AgentTask],
        task_description: str = ""
    ) -> Dict[str, Any]:
        """
        Complex execution mode: generate and execute code.

        Args:
            tasks: List of tasks to orchestrate
            task_description: Natural language description

        Returns:
            Execution result with aggregated outputs
        """
        if not self.hybrid_mode_enabled or not self.code_executor:
            self.logger.warning("Code execution not available, falling back to simple mode")
            return await self._orchestrate_simple(tasks)

        self.logger.info(f"[COMPLEX MODE] Generating code for {len(tasks)} tasks")

        # Generate Python code for orchestration
        code = CodeGenerator.generate_python_orchestration(tasks)

        self.logger.debug(f"Generated code:\n{code}")

        # Execute in sandbox
        result = await self.code_executor.execute_python(
            code, name=f"orchestration_{len(tasks)}_tasks"
        )

        if result.status == "success":
            # Parse the JSON output
            try:
                output = json.loads(result.stdout)
                return {
                    "status": "success",
                    "execution_mode": "complex",
                    "output": output,
                    "execution_time": result.execution_time
                }
            except json.JSONDecodeError:
                return {
                    "status": "success",
                    "execution_mode": "complex",
                    "output": result.stdout,
                    "execution_time": result.execution_time
                }
        else:
            return {
                "status": result.status,
                "execution_mode": "complex",
                "error": result.error or result.stderr,
                "execution_time": result.execution_time
            }

    async def orchestrate_hybrid(
        self,
        tasks: List[AgentTask],
        task_description: str = ""
    ) -> Dict[str, Any]:
        """
        Hybrid orchestration: intelligently route to simple or complex mode.

        Args:
            tasks: List of tasks to execute
            task_description: Natural language task description

        Returns:
            Orchestration results
        """
        if not self.hybrid_mode_enabled:
            self.logger.info("Hybrid mode disabled, using legacy orchestration")
            return await self.orchestrate(tasks)

        # Analyze task and determine execution mode
        mode = ExecutionRouter.analyze_task(task_description, tasks)
        explanation = ExecutionRouter.explain_decision(task_description, tasks, mode)

        self.logger.info(f"🔀 {explanation}")

        if mode == ExecutionMode.SIMPLE:
            return await self._orchestrate_simple(tasks)
        else:
            return await self.execute_complex(tasks, task_description)

    async def _orchestrate_simple(self, tasks: List[AgentTask]) -> Dict[str, Any]:
        """
        Simple sequential orchestration (original behavior).

        Args:
            tasks: List of tasks

        Returns:
            Results dict
        """
        results = {}
        tasks.sort(key=lambda x: x.priority, reverse=True)

        for task in tasks:
            self.logger.info(f"Executing {task.team.value}.{task.agent_name}")

            if self.hybrid_mode_enabled and self.mcp_client:
                # Use MCP client
                result = await self.execute_simple(
                    task.team.value,
                    task.agent_name,
                    task.params
                )
            else:
                # Use legacy delegation
                if task.team == AgentTeam.ADK:
                    result = await self.delegate_to_adk(task.agent_name, task.params)
                elif task.team == AgentTeam.ANTHROPIC:
                    result = await self.delegate_to_anthropic(task.agent_name, task.params)
                elif task.team == AgentTeam.OPENAI:
                    result = await self.delegate_to_openai(task.agent_name, task.params)
                else:
                    result = {"status": "unknown_team"}

            results[f"{task.team.value}_{task.agent_name}"] = result

        return {
            "status": "success",
            "execution_mode": "simple",
            "results": results
        }

    async def orchestrate(self, tasks: List[AgentTask]) -> Dict[str, Any]:
        """
        🎭 Orchestration multi-agents
        
        Coordonne l'exécution de tâches sur différentes équipes
        """
        results = {}
        
        # Tri par priorité
        tasks.sort(key=lambda x: x.priority, reverse=True)
        
        for task in tasks:
            print(f"🎯 Super Claude délègue : {task.agent_name} ({task.team.value})")
            
            if task.team == AgentTeam.ADK:
                result = await self.delegate_to_adk(task.agent_name, task.params)
            elif task.team == AgentTeam.ANTHROPIC:
                result = await self.delegate_to_anthropic(task.agent_name, task.params)  
            elif task.team == AgentTeam.OPENAI:
                result = await self.delegate_to_openai(task.agent_name, task.params)
            else:
                result = {"status": "unknown_team", "output": f"Équipe inconnue: {task.team}"}
            
            results[f"{task.team.value}_{task.agent_name}"] = result
            print(f"✅ Résultat : {result.get('status', 'unknown')}")
        
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
    print("🧠 Super Claude Multi-Agents - Démonstration")
    print("=" * 50)
    
    super_claude = SuperClaude()
    
    # Affichage des agents disponibles
    agents = super_claude.get_available_agents()
    print(f"📋 Agents disponibles : {agents}")
    
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
    print(f"\n🎉 Résultats orchestration : {len(results)} tâche(s) exécutée(s)")
    
    return results

if __name__ == "__main__":
    asyncio.run(demo_super_claude())