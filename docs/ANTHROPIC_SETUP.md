# 🟢 Anthropic Agents Setup Guide

Complete guide to setting up and using Anthropic Claude agents via Model Context Protocol (MCP).

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Available Agents](#available-agents)
6. [Usage Examples](#usage-examples)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Anthropic integration provides three specialized agents powered by Claude 3.5 Sonnet:

- **🔬 Research Agent**: Deep research and synthesis on any topic
- **💻 Code Agent**: Code development, review, and generation
- **✍️ Writing Agent**: Professional content and documentation

These agents communicate via JSON-RPC 2.0 STDIO protocol through a Python bridge that interfaces with the Anthropic API.

### Architecture

```
SuperClaude → MCP Client → Bridge (STDIO) → Anthropic API → Claude 3.5 Sonnet
```

**Token Efficiency**: Anthropic agents use real-time API calls for complex reasoning that benefits from Claude's advanced capabilities.

---

## Prerequisites

### 1. Anthropic API Key

Get your API key from the Anthropic Console:

1. Visit https://console.anthropic.com/
2. Sign up or log in
3. Navigate to "API Keys"
4. Click "Create Key"
5. Copy your key (starts with `sk-ant-api03-...`)

⚠️ **Important**: Keep your API key secure. Never commit it to version control.

### 2. System Requirements

- Python 3.9 or higher
- pip (Python package manager)
- Internet connection (for API calls)

### 3. Dependencies

The following Python packages are required:

```txt
anthropic>=0.21.0    # Official Anthropic Python SDK
pydantic>=2.0.0      # Data validation
python-dotenv>=1.0.0 # Environment variable management
```

---

## Installation

### Step 1: Install SuperClaude

If you haven't already:

```bash
git clone https://github.com/mlik-sudo/SuperClaude-Multi-Agents.git
cd SuperClaude-Multi-Agents
```

### Step 2: Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Or install development dependencies (includes testing tools)
make setup-dev
```

### Step 3: Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```bash
# Anthropic Configuration
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_AGENT_TIMEOUT=300
```

### Step 4: Verify Installation

Test that the bridge works:

```bash
# Initialize the bridge
echo '{"jsonrpc":"2.0","id":"test","method":"initialize"}' | python agents/anthropic/bridge.py

# List available tools
echo '{"jsonrpc":"2.0","id":"test","method":"tools/list"}' | python agents/anthropic/bridge.py
```

You should see JSON responses with no errors.

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | ✅ Yes | - | Your Anthropic API key |
| `ANTHROPIC_MODEL` | ❌ No | `claude-3-5-sonnet-20241022` | Model to use |
| `ANTHROPIC_AGENT_TIMEOUT` | ❌ No | `300` | Timeout in seconds |

### MCP Server Configuration

The Anthropic bridge is automatically configured in `mcp/servers.json`:

```json
{
  "name": "anthropic",
  "command": "python agents/anthropic/bridge.py",
  "description": "Anthropic Claude agents via JSON-RPC STDIO",
  "team": "anthropic",
  "status": "active"
}
```

---

## Available Agents

### 🔬 Research Agent

**Purpose**: Deep research and synthesis on any topic

**Method**: `tools/research_agent`

**Parameters**:
- `query` (string, required): Research question or topic
- `depth` (string, optional): Research depth
  - `"quick"`: Fast overview (fewer tokens)
  - `"standard"`: Balanced research (default)
  - `"deep"`: Comprehensive analysis (more tokens)
- `sources` (array, optional): Specific sources to consider

**Example Request**:
```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/research_agent",
  "params": {
    "query": "Latest AI trends 2025",
    "depth": "deep",
    "sources": ["arxiv", "github", "technical blogs"]
  }
}
```

**Example Response**:
```json
{
  "status": "success",
  "findings": "# Research Findings\n\n## Key Findings...",
  "query": "Latest AI trends 2025",
  "depth": "deep",
  "usage": {
    "input_tokens": 150,
    "output_tokens": 1200
  }
}
```

### 💻 Code Agent

**Purpose**: Code development, review, and generation

**Method**: `tools/code_agent`

**Parameters**:
- `task` (string, required): Coding task description
- `language` (string, optional): Programming language (default: `"python"`)
- `context` (string, optional): Additional context or existing code

**Example Request**:
```json
{
  "jsonrpc": "2.0",
  "id": "2",
  "method": "tools/code_agent",
  "params": {
    "task": "Write a function to calculate Fibonacci numbers",
    "language": "python"
  }
}
```

**Example Response**:
```json
{
  "status": "success",
  "code": "```python\ndef fibonacci(n: int) -> int:\n    ...\n```",
  "language": "python",
  "usage": {
    "input_tokens": 80,
    "output_tokens": 450
  }
}
```

### ✍️ Writing Agent

**Purpose**: Professional content and documentation

**Method**: `tools/writing_agent`

**Parameters**:
- `topic` (string, required): Topic or outline to write about
- `style` (string, optional): Writing style
  - `"professional"`: Formal business style (default)
  - `"casual"`: Conversational tone
  - `"technical"`: Technical documentation style
- `length` (string, optional): Content length
  - `"short"`: Brief summary (~300 words)
  - `"medium"`: Standard article (~800 words, default)
  - `"long"`: Comprehensive guide (~1500+ words)

**Example Request**:
```json
{
  "jsonrpc": "2.0",
  "id": "3",
  "method": "tools/writing_agent",
  "params": {
    "topic": "Benefits of async programming",
    "style": "technical",
    "length": "medium"
  }
}
```

**Example Response**:
```json
{
  "status": "success",
  "content": "# Benefits of Async Programming\n\n## Introduction...",
  "topic": "Benefits of async programming",
  "style": "technical",
  "usage": {
    "input_tokens": 100,
    "output_tokens": 900
  }
}
```

---

## Usage Examples

### Example 1: Direct MCP Call

Call agents directly via the MCP interface:

```bash
# Research agent
python -m mcp.mcp_call call anthropic research_agent \
  --params '{"query": "Quantum computing", "depth": "standard"}'

# Code agent
python -m mcp.mcp_call call anthropic code_agent \
  --params '{"task": "Binary search in Python", "language": "python"}'

# Writing agent
python -m mcp.mcp_call call anthropic writing_agent \
  --params '{"topic": "Docker best practices", "style": "technical"}'
```

### Example 2: Python API

Use agents programmatically:

```python
import asyncio
from core.super_claude import SuperClaude, AgentTask, AgentTeam

async def research_example():
    orchestrator = SuperClaude()

    # Research task
    task = AgentTask(
        team=AgentTeam.ANTHROPIC,
        agent_name="research_agent",
        method="call",
        params={
            "query": "Machine learning breakthroughs 2025",
            "depth": "deep"
        }
    )

    result = await orchestrator.delegate_to_anthropic(
        "research_agent",
        task.params
    )

    print(f"Findings: {result['findings']}")
    print(f"Tokens: {result['usage']['output_tokens']}")

asyncio.run(research_example())
```

### Example 3: Hybrid Skill

Use multiple agents together:

```bash
python skills/complex/tech-digest-with-analysis.py \
  --topic "async programming" \
  --depth deep \
  --language python \
  --output digest.json
```

This skill:
1. Uses **research agent** to gather information
2. Uses **code agent** to create examples
3. Uses **writing agent** to produce documentation

---

## Testing

### Unit Tests

Test individual components:

```bash
# Test mock server
pytest tests/integration/test_anthropic_integration.py::TestAnthropicBridgeIntegration -v

# Test response structures
pytest tests/integration/test_anthropic_integration.py::TestAnthropicResponseStructure -v
```

### Integration Tests

Test end-to-end workflows:

```bash
# Full integration test suite
pytest tests/integration/test_anthropic_integration.py -v -m integration

# Test specific agent
pytest tests/integration/test_anthropic_integration.py::TestAnthropicBridgeIntegration::test_research_agent_basic -v
```

### Manual Testing

Test the bridge manually:

```bash
# 1. Initialize
echo '{"jsonrpc":"2.0","id":"1","method":"initialize"}' | \
  python agents/anthropic/bridge.py

# 2. List tools
echo '{"jsonrpc":"2.0","id":"2","method":"tools/list"}' | \
  python agents/anthropic/bridge.py

# 3. Call research agent
echo '{"jsonrpc":"2.0","id":"3","method":"tools/research_agent","params":{"query":"AI trends"}}' | \
  python agents/anthropic/bridge.py
```

---

## Troubleshooting

### Issue: "ANTHROPIC_API_KEY not found"

**Solution**: Ensure your `.env` file contains the API key:

```bash
# Check .env file
cat .env | grep ANTHROPIC_API_KEY

# If missing, add it
echo "ANTHROPIC_API_KEY=sk-ant-api03-your-key" >> .env
```

### Issue: "anthropic module not found"

**Solution**: Install the Anthropic SDK:

```bash
pip install anthropic>=0.21.0
```

### Issue: API Rate Limit Errors

**Solution**: Anthropic has rate limits. If you hit them:

1. Wait a few seconds between requests
2. Reduce request frequency
3. Upgrade your Anthropic plan for higher limits
4. Implement exponential backoff in your code

### Issue: Timeout Errors

**Solution**: Increase the timeout:

```bash
# In .env
ANTHROPIC_AGENT_TIMEOUT=600  # 10 minutes
```

Or for specific calls:

```python
# Increase timeout for long-running tasks
result = await orchestrator.delegate_to_anthropic(
    "research_agent",
    {"query": "complex topic", "depth": "deep"},
    timeout=600
)
```

### Issue: Invalid JSON Responses

**Solution**: Verify the bridge is working:

```bash
# Test JSON-RPC format
echo '{"jsonrpc":"2.0","id":"test","method":"initialize"}' | \
  python agents/anthropic/bridge.py | jq '.'
```

If `jq` shows errors, check:
1. Python version (≥3.9)
2. All dependencies installed
3. No syntax errors in bridge.py

### Issue: High Token Usage

**Solution**: Optimize your requests:

1. Use `"depth": "quick"` for research (fewer tokens)
2. Use `"length": "short"` for writing (fewer tokens)
3. Provide clear, specific prompts
4. Monitor usage with the returned `usage` field

---

## Best Practices

### 1. Token Efficiency

- Start with `depth: "quick"` and `length: "short"`
- Increase only when needed
- Monitor token usage in responses
- Cache results for repeated queries

### 2. Error Handling

Always check response status:

```python
result = await orchestrator.delegate_to_anthropic("research_agent", params)

if result.get("status") != "success":
    print(f"Error: {result.get('error', 'Unknown error')}")
    return

# Process result
findings = result["findings"]
```

### 3. Timeout Management

Set appropriate timeouts based on task complexity:

```python
# Quick tasks: 60s
# Standard tasks: 300s (default)
# Complex tasks: 600s
```

### 4. API Key Security

- Never commit `.env` to git
- Use environment variables in production
- Rotate keys periodically
- Monitor usage in Anthropic Console

---

## Additional Resources

- [Anthropic API Documentation](https://docs.anthropic.com/)
- [CODE_EXECUTION_MCP.md](./CODE_EXECUTION_MCP.md) - MCP protocol details
- [agents/anthropic/README.md](../agents/anthropic/README.md) - Agent reference
- [Anthropic Console](https://console.anthropic.com/) - Manage API keys and usage

---

## Support

For issues or questions:

1. Check this guide's troubleshooting section
2. Review the [Anthropic API docs](https://docs.anthropic.com/)
3. Open an issue on the [GitHub repository](https://github.com/mlik-sudo/SuperClaude-Multi-Agents/issues)

---

**Last Updated**: 2025-11-05
**Version**: Phase 3.0
