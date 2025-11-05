#!/usr/bin/env python3
"""
MCP Client for SuperClaude.

Provides progressive disclosure and on-demand tool loading for MCP servers.
This is the Python API wrapper around mcp_call.py CLI.
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for interacting with MCP servers via CLI."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize MCP client.

        Args:
            config_path: Path to servers.json config file
        """
        self.config_path = config_path or Path(__file__).parent / "servers.json"
        self.servers = self._load_servers()
        self.tools_cache: Dict[str, List[Dict[str, Any]]] = {}

    def _load_servers(self) -> List[Dict[str, Any]]:
        """Load MCP server configurations from JSON file."""
        if not self.config_path.exists():
            logger.warning(f"MCP config not found at {self.config_path}")
            return []

        try:
            data = json.loads(self.config_path.read_text())
            if not isinstance(data, list):
                logger.error("MCP config must be a JSON array")
                return []
            return data
        except (OSError, json.JSONDecodeError) as exc:
            logger.error(f"Failed to load MCP config: {exc}")
            return []

    def list_servers(self) -> List[Dict[str, Any]]:
        """
        List all configured MCP servers.

        Returns:
            List of server configurations
        """
        return self.servers

    def get_server(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get server configuration by name.

        Args:
            name: Server name

        Returns:
            Server config dict or None if not found
        """
        for server in self.servers:
            if server.get("name") == name:
                return server
        return None

    def list_tools(
        self, mcp_name: str, use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        List tools available on an MCP server (progressive disclosure).

        Args:
            mcp_name: Name of the MCP server
            use_cache: Whether to use cached tool list

        Returns:
            List of tool definitions with signatures and schemas
        """
        # Check cache first
        if use_cache and mcp_name in self.tools_cache:
            logger.debug(f"Using cached tools for {mcp_name}")
            return self.tools_cache[mcp_name]

        logger.info(f"Discovering tools for MCP server: {mcp_name}")

        try:
            result = subprocess.run(
                ["python", "mcp/mcp_call.py", "list", mcp_name, "--schema"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=Path.cwd(),
            )

            if result.returncode != 0:
                logger.error(f"Failed to list tools: {result.stderr}")
                return []

            # Parse the output to extract tools
            tools = self._parse_tool_list(result.stdout)
            self.tools_cache[mcp_name] = tools

            logger.info(f"Discovered {len(tools)} tools for {mcp_name}")
            return tools

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout listing tools for {mcp_name}")
            return []
        except Exception as exc:
            logger.error(f"Error listing tools: {exc}")
            return []

    def _parse_tool_list(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse mcp_call.py list output into structured tool definitions.

        Args:
            output: Raw stdout from mcp_call.py list

        Returns:
            List of tool definitions
        """
        # For now, return simple structure
        # TODO: Implement proper parsing of mcp_call.py output format
        tools = []
        lines = output.strip().split("\n")

        current_tool = None
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("- ") and "(" in stripped:
                # Tool signature line
                if current_tool:
                    tools.append(current_tool)

                # Extract tool name
                signature = stripped[2:]  # Remove "- "
                name = signature.split("(")[0]

                current_tool = {
                    "name": name,
                    "signature": signature,
                    "description": "",
                    "schema": None,
                }

        if current_tool:
            tools.append(current_tool)

        return tools

    def call_tool(
        self,
        mcp_name: str,
        tool_name: str,
        timeout: int = 300,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Call a tool on an MCP server.

        Args:
            mcp_name: Name of the MCP server
            tool_name: Name of the tool to call
            timeout: Execution timeout in seconds
            **kwargs: Tool arguments

        Returns:
            Tool execution result
        """
        logger.info(f"Calling {mcp_name}.{tool_name} with args: {kwargs}")

        args_json = json.dumps(kwargs)

        try:
            result = subprocess.run(
                [
                    "python",
                    "mcp/mcp_call.py",
                    "call",
                    f"{mcp_name}.{tool_name}",
                    "--args",
                    args_json,
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path.cwd(),
            )

            if result.returncode != 0:
                logger.error(f"Tool call failed: {result.stderr}")
                return {"status": "error", "stderr": result.stderr, "stdout": ""}

            # Try to parse as JSON
            try:
                output = json.loads(result.stdout)
            except json.JSONDecodeError:
                output = result.stdout

            return {"status": "success", "output": output, "stderr": result.stderr}

        except subprocess.TimeoutExpired:
            logger.error(f"Tool call timeout after {timeout}s")
            return {
                "status": "timeout",
                "error": f"Tool execution timed out after {timeout}s",
            }
        except Exception as exc:
            logger.error(f"Tool call exception: {exc}")
            return {"status": "exception", "error": str(exc)}

    def validate_tool_params(
        self, mcp_name: str, tool_name: str, params: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate tool parameters against schema.

        Args:
            mcp_name: MCP server name
            tool_name: Tool name
            params: Parameters to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        tools = self.list_tools(mcp_name)

        # Find tool schema
        tool_schema = None
        for tool in tools:
            if tool["name"] == tool_name:
                tool_schema = tool.get("schema")
                break

        if not tool_schema:
            return True, None  # No schema to validate against

        # TODO: Implement JSON schema validation
        # For now, just return valid
        return True, None


# Standalone CLI interface
if __name__ == "__main__":
    import sys

    client = MCPClient()

    if len(sys.argv) < 2:
        print("Usage: python mcp_client.py <command> [args...]")
        print("Commands: list, call")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        servers = client.list_servers()
        print(f"Available MCP servers ({len(servers)}):")
        for server in servers:
            print(f"  - {server['name']}: {server.get('description', '')}")

    elif command == "call":
        if len(sys.argv) < 4:
            print("Usage: python mcp_client.py call <mcp.tool> <args_json>")
            sys.exit(1)

        selector = sys.argv[2]
        mcp_name, tool_name = selector.split(".")
        args_json = sys.argv[3] if len(sys.argv) > 3 else "{}"
        args = json.loads(args_json)

        result = client.call_tool(mcp_name, tool_name, **args)
        print(json.dumps(result, indent=2))
