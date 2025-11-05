# 🟢 Agents Anthropic (MCP)

**Status:** ✅ Active (Phase 3)
**Protocol:** JSON-RPC 2.0 STDIO
**Communication:** SuperClaude ↔ Anthropic Bridge ↔ Claude API

---

## 📋 Available Agents

### 1. 🔬 research_agent
**Purpose:** Deep research and synthesis on any topic

**Parameters:**
- `query` (string, required): Research question or topic
- `depth` (string, optional): Research depth (quick/standard/deep)
- `sources` (array, optional): Specific sources to consider

**Example:**
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/research_agent","params":{"query":"Latest AI trends 2025","depth":"deep"}}' | python agents/anthropic/bridge.py
```

### 2. 💻 code_agent
**Purpose:** Code development and review

**Parameters:**
- `task` (string, required): Coding task description
- `language` (string, optional): Programming language (default: python)
- `context` (string, optional): Additional context or existing code

**Example:**
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/code_agent","params":{"task":"Write a function to calculate Fibonacci","language":"python"}}' | python agents/anthropic/bridge.py
```

### 3. ✍️ writing_agent
**Purpose:** Professional content and documentation

**Parameters:**
- `topic` (string, required): Topic or outline to write about
- `style` (string, optional): Writing style (professional/casual/technical)
- `length` (string, optional): Length (short/medium/long)

**Example:**
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/writing_agent","params":{"topic":"Benefits of async programming","style":"technical"}}' | python agents/anthropic/bridge.py
```

---

## ⚙️ Configuration

### Environment Variables

Required:
```bash
ANTHROPIC_API_KEY=your_api_key_here
```

Optional:
```bash
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022  # Model to use
ANTHROPIC_AGENT_TIMEOUT=300                  # Timeout in seconds
```

### Setup

1. Get API key from https://console.anthropic.com/
2. Add to `.env`:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-api03-...
   ```
3. Install dependency:
   ```bash
   pip install anthropic>=0.21.0
   ```

---

## 🔧 Usage from SuperClaude

```python
from core.super_claude import SuperClaude, AgentTask, AgentTeam

orchestrator = SuperClaude()

# Research task
task = AgentTask(
    team=AgentTeam.ANTHROPIC,
    agent_name="research_agent",
    method="call",
    params={"query": "Quantum computing breakthroughs", "depth": "deep"}
)

result = await orchestrator.delegate_to_anthropic("research_agent", task.params)
print(result["findings"])
```

---

## 📊 Token Usage

Each agent call returns token usage:

```json
{
  "status": "success",
  "findings": "...",
  "usage": {
    "input_tokens": 150,
    "output_tokens": 800
  }
}
```

---

## 🧪 Testing

```bash
# Test bridge initialization
echo '{"jsonrpc":"2.0","id":1,"method":"initialize"}' | python agents/anthropic/bridge.py

# List available tools
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python agents/anthropic/bridge.py

# Run integration tests
pytest tests/integration/test_anthropic_integration.py -v
```

---

## 🚀 Best Practices

1. **Token Efficiency:** Use appropriate depth/length to avoid over-processing
2. **Error Handling:** Always check status field in responses
3. **Rate Limiting:** Anthropic API has rate limits - implement backoff if needed
4. **Context Size:** Claude models have context limits - keep inputs reasonable

---

## 📚 Documentation

- [Anthropic API Docs](https://docs.anthropic.com/)
- [ANTHROPIC_SETUP.md](../../docs/ANTHROPIC_SETUP.md)
- [CODE_EXECUTION_MCP.md](../../docs/CODE_EXECUTION_MCP.md)

---

**Powered by Claude 3.5 Sonnet** 🎯
