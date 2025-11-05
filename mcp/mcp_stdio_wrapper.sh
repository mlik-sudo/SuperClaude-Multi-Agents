#!/usr/bin/env bash
# Generic wrapper for stdio MCP servers.
# Keeps repo-relative resolution for stdio commands while allowing optional output suppression.
set -euo pipefail

# Change to repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# Execute command with optional output suppression
if [[ "${MCP_STDIO_SILENT:-0}" == "1" ]]; then
  exec "$@" >/dev/null 2>&1
else
  exec "$@"
fi
