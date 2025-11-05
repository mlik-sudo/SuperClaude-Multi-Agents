#!/usr/bin/env python3
"""
MCP helper CLI using definitions from mcp/servers.json.

This script provides command-line access to MCP servers with progressive disclosure.
Typical invocations:
    python mcp/mcp_call.py list
    python mcp/mcp_call.py list adk --schema
    python mcp/mcp_call.py call adk.watch_collect sources='["github"]'
    python mcp/mcp_call.py call adk.analyse_watch_report report_path=report.json

Argument syntax:
    • Selector accepts `mcp.tool`, `mcp:tool`, or `mcp/tool`
    • Structured payloads: `--args '{"key":"value"}'`
    • Additional `key=value` tokens auto-coerce booleans, numbers, null, or nested JSON
    • Later keys override earlier ones
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path
from textwrap import indent
from typing import Any, Iterable

# Suppress common warnings
warnings.filterwarnings("ignore", message="coroutine.*was never awaited")

# Remove extra "--" that might be forwarded by package managers
if "--" in sys.argv:
    sys.argv = [arg for arg in sys.argv if arg != "--"]

CONFIG_PATH = Path(__file__).resolve().parent / "servers.json"


def load_servers() -> list[dict[str, Any]]:
    """Load and validate MCP server definitions from servers.json."""
    if not CONFIG_PATH.exists():
        print(f"Config file not found: {CONFIG_PATH}", file=sys.stderr)
        return []

    try:
        data = json.loads(CONFIG_PATH.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Failed to read {CONFIG_PATH}: {exc}", file=sys.stderr)
        sys.exit(1)

    servers: list[dict[str, Any]] = []
    for item in data:
        if isinstance(item, dict) and item.get("name") and item.get("command"):
            servers.append(item)
    return servers


def resolve_target(
    *,
    servers: list[dict[str, Any]],
    mcp_name: str | None,
    override_command: str | None,
) -> tuple[str, dict[str, Any] | None]:
    """Return the command + entry for the requested MCP name or explicit override."""
    if override_command:
        return override_command, None

    if mcp_name:
        for entry in servers:
            if entry.get("name") == mcp_name:
                return entry["command"], entry
        print(
            f"Unknown MCP '{mcp_name}'. Run 'python mcp/mcp_call.py list' to see available names.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(
        "MCP name missing. Use '<name>.<tool>' or supply --mcp/--server.",
        file=sys.stderr,
    )
    sys.exit(1)


def maybe_parse_json(value: str) -> Any:
    """Attempt to parse a JSON literal, falling back to the raw string."""
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def coerce_call_value(raw: str) -> Any:
    """Convert stringy key=value tokens into loosely typed values."""
    value = raw.strip()
    if value == "":
        return ""

    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none"}:
        return None

    # Try integer
    try:
        if value.startswith("0") and value != "0" and not value.startswith("0."):
            raise ValueError("Leading zero")
        return int(value)
    except ValueError:
        pass

    # Try float
    try:
        return float(value)
    except ValueError:
        pass

    # Try JSON object/array
    if value.startswith("{") or value.startswith("["):
        decoded = maybe_parse_json(value)
        if isinstance(decoded, (dict, list)):
            return decoded

    return value


def parse_call_style_args(tokens: Iterable[str]) -> dict[str, Any]:
    """Parse key=value arguments passed after the selector."""
    results: dict[str, Any] = {}
    for token in tokens:
        if "=" not in token:
            raise ValueError(f"Argument '{token}' must be in key=value format.")
        key, raw = token.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError("Argument names cannot be empty.")
        results[key] = coerce_call_value(raw)
    return results


def command_list(args: argparse.Namespace, servers: list[dict[str, Any]]) -> int:
    """Handle the 'list' command."""
    targets: Iterable[dict[str, Any]]

    if args.mcp:
        targets = [entry for entry in servers if entry.get("name") == args.mcp]
        if not targets:
            print(f"Unknown MCP '{args.mcp}'.", file=sys.stderr)
            return 1
    else:
        targets = servers

    targets = list(targets)
    if not targets:
        print("No MCP servers configured. Add entries to mcp/servers.json.")
        return 0

    for entry in targets:
        name = entry.get("name", "<unknown>")
        description = entry.get("description", "")
        command = entry.get("command", "")
        tools = entry.get("tools", [])

        line = f"- {name}"
        if description:
            line += f" — {description}"
        print(line)

        if command:
            print(f"  Command: {command}")

        if tools:
            print(f"  Tools ({len(tools)}):")
            for tool in tools:
                print(f"    - {tool}")
        else:
            print("  Tools: <not configured>")

        if args.schema:
            # In a real implementation, you'd introspect the MCP server
            print("  Schema: <introspection not implemented>")

    return 0


def command_call(args: argparse.Namespace, servers: list[dict[str, Any]]) -> int:
    """Handle the 'call' command."""
    selector = args.selector
    mcp_name = args.mcp
    tool_name = args.tool

    # Parse selector
    if selector:
        normalized = selector.replace("/", ".").replace(":", ".")
        parts = normalized.split(".", 1)
        if len(parts) == 2:
            if not mcp_name:
                mcp_name = parts[0]
            if not tool_name:
                tool_name = parts[1]
        else:
            value = parts[0]
            if mcp_name and not tool_name:
                tool_name = value
            elif tool_name and not mcp_name:
                mcp_name = value
            elif args.server:
                tool_name = value
            else:
                tool_name = value

    if not mcp_name and not args.server:
        print(
            "MCP name missing. Use '<name>.<tool>' or supply --mcp/--server.",
            file=sys.stderr,
        )
        return 1

    if not tool_name:
        print("Tool name missing. Provide one via selector or --tool.", file=sys.stderr)
        return 1

    command, entry = resolve_target(
        servers=servers, mcp_name=mcp_name, override_command=args.server
    )

    # Build kwargs
    kwargs: dict[str, Any] = {}
    if args.args:
        parsed = maybe_parse_json(args.args)
        if not isinstance(parsed, dict):
            print("--args must decode to a JSON object", file=sys.stderr)
            return 1
        kwargs = dict(parsed)

    if args.call_args:
        try:
            call_kwargs = parse_call_style_args(args.call_args)
        except ValueError as exc:
            print(f"Invalid call argument: {exc}", file=sys.stderr)
            return 1
        kwargs.update(call_kwargs)

    # For now, simulate the call
    # In a real implementation, you would:
    # 1. Load the MCP server using the command
    # 2. Call the tool with kwargs
    # 3. Return the result

    print(
        f"[MOCK] Would call {mcp_name}.{tool_name} with args: {json.dumps(kwargs, indent=2)}"
    )
    print(f"[MOCK] Command: {command}")

    # Mock result
    result = {
        "status": "mock_success",
        "mcp": mcp_name,
        "tool": tool_name,
        "args": kwargs,
        "note": "This is a mock response. Real MCP integration pending.",
    }

    print(json.dumps(result, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI parser with subcommands."""
    parser = argparse.ArgumentParser(
        description="Interact with MCP servers for SuperClaude"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # List command
    list_parser = sub.add_parser("list", help="List configured MCP servers")
    list_parser.add_argument(
        "mcp", nargs="?", help="Name of a specific MCP to display"
    )
    list_parser.add_argument(
        "--schema", action="store_true", help="Print raw JSON schema for each tool"
    )
    list_parser.set_defaults(func=command_list)

    # Call command
    call_parser = sub.add_parser("call", help="Invoke a tool on an MCP server")
    call_parser.add_argument(
        "selector",
        nargs="?",
        help="Optional shorthand '<mcp>.<tool>' (dot/colon/slash) or tool name",
    )
    call_parser.add_argument("--mcp", help="MCP name from servers.json")
    call_parser.add_argument("--tool", help="Tool name when selector omits it")
    call_parser.add_argument("--server", help="Override MCP command/URL")
    call_parser.add_argument("--args", help="JSON object with tool arguments")
    call_parser.add_argument(
        "--tail-log",
        action="store_true",
        help="Tail log files returned by tools",
    )
    call_parser.add_argument(
        "call_args",
        nargs="*",
        help="Optional key=value arguments (function-style) appended after the selector",
    )
    call_parser.set_defaults(func=command_call)

    return parser


def main() -> int:
    """Entry point for the CLI."""
    parser = build_parser()
    args = parser.parse_args()
    servers = load_servers()
    return args.func(args, servers)


if __name__ == "__main__":
    sys.exit(main())
