# Simple Skills

Simple skills use direct MCP CLI calls without code generation.

## Usage

Skills in this directory can be invoked directly via the CLI:

```bash
python skills/simple/check-github-trending.py
```

## Creating Simple Skills

1. Create a Python script
2. Use `subprocess` to call `mcp/mcp_call.py`
3. Handle the JSON output
4. Return results

## Example

See `check-github-trending.py` for a basic example.
