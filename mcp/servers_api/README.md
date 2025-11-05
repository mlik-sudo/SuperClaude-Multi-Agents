# 🔌 MCP Servers API Reference

Complete API reference for all MCP servers and bridges in SuperClaude.

---

## 📋 Available MCP Servers

| Server | Status | Protocol | Description |
|--------|--------|----------|-------------|
| **adk** | ✅ Active | JSON-RPC 2.0 STDIO | Agent Development Kit agents |
| **anthropic** | ✅ Active | JSON-RPC 2.0 STDIO | Claude-powered agents (research, code, writing) |

---

## 🔧 ADK Server (Agent Development Kit)

**Bridge**: `agents/adk/bridge.py`
**Team**: ADK
**Protocol**: JSON-RPC 2.0 over STDIO

### Available Tools

#### 1. watch_collect

Collect data from various sources (GitHub, HuggingFace, Kaggle).

**Method**: `tools/watch_collect`

**Parameters**:
```typescript
{
  sources: string[]        // ["github", "huggingface", "kaggle"]
  days?: number           // Days to look back (default: 7)
  limit?: number          // Max items per source (default: 10)
  language?: string       // Filter by language (e.g., "Python")
  min_stars?: number      // Minimum stars (default: 0)
}
```

**Response**:
```typescript
{
  status: "success" | "error"
  repos?: Array<{
    name: string
    url: string
    stars: number
    language: string
    description: string
    created_at: string
  }>
  models?: Array<{
    name: string
    url: string
    downloads: number
    framework: string
  }>
  error?: string
}
```

**Example**:
```bash
echo '{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/watch_collect",
  "params": {
    "sources": ["github"],
    "days": 7,
    "language": "Python",
    "min_stars": 1000
  }
}' | python agents/adk/bridge.py
```

#### 2. watch_analyze

Analyze collected data and generate insights.

**Method**: `tools/watch_analyze`

**Parameters**:
```typescript
{
  data: Array<any>        // Data to analyze
  analysis_type?: string  // "trends" | "summary" | "deep"
  metrics?: string[]      // Metrics to focus on
}
```

**Response**:
```typescript
{
  status: "success" | "error"
  insights: {
    summary: string
    key_findings: string[]
    trends: Array<{
      metric: string
      value: number
      change: number
    }>
  }
  error?: string
}
```

---

## 🟢 Anthropic Server (Claude Agents)

**Bridge**: `agents/anthropic/bridge.py`
**Team**: Anthropic
**Protocol**: JSON-RPC 2.0 over STDIO
**API**: Anthropic Claude API

### Environment Variables

```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_AGENT_TIMEOUT=300
```

### Available Tools

#### 1. research_agent

Deep research and synthesis on any topic.

**Method**: `tools/research_agent`

**Parameters**:
```typescript
{
  query: string           // Research question or topic (required)
  depth?: string          // "quick" | "standard" | "deep" (default: "standard")
  sources?: string[]      // Sources to consider (optional)
}
```

**Response**:
```typescript
{
  status: "success" | "error"
  findings?: string       // Markdown-formatted research findings
  query: string           // Original query
  depth: string           // Research depth used
  usage: {
    input_tokens: number
    output_tokens: number
  }
  error?: string
}
```

**Example**:
```bash
echo '{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/research_agent",
  "params": {
    "query": "Latest developments in quantum computing",
    "depth": "deep",
    "sources": ["arxiv", "nature", "ieee"]
  }
}' | python agents/anthropic/bridge.py
```

**Token Usage**:
- Quick: ~500-1,000 output tokens
- Standard: ~1,000-2,000 output tokens
- Deep: ~2,000-4,000 output tokens

#### 2. code_agent

Code development, review, and generation.

**Method**: `tools/code_agent`

**Parameters**:
```typescript
{
  task: string            // Coding task description (required)
  language?: string       // Programming language (default: "python")
  context?: string        // Additional context or existing code (optional)
}
```

**Response**:
```typescript
{
  status: "success" | "error"
  code?: string           // Generated code (markdown with syntax highlighting)
  language: string        // Language used
  usage: {
    input_tokens: number
    output_tokens: number
  }
  error?: string
}
```

**Example**:
```bash
echo '{
  "jsonrpc": "2.0",
  "id": "2",
  "method": "tools/code_agent",
  "params": {
    "task": "Create a binary search tree implementation with insert, search, and delete operations",
    "language": "python"
  }
}' | python agents/anthropic/bridge.py
```

**Supported Languages**:
- Python
- JavaScript/TypeScript
- Go
- Rust
- Java
- C++
- And more...

**Token Usage**:
- Simple function: ~300-600 output tokens
- Class implementation: ~600-1,200 output tokens
- Full module: ~1,200-2,500 output tokens

#### 3. writing_agent

Professional content and documentation creation.

**Method**: `tools/writing_agent`

**Parameters**:
```typescript
{
  topic: string           // Topic or outline to write about (required)
  style?: string          // "professional" | "casual" | "technical" (default: "professional")
  length?: string         // "short" | "medium" | "long" (default: "medium")
}
```

**Response**:
```typescript
{
  status: "success" | "error"
  content?: string        // Markdown-formatted content
  topic: string           // Original topic
  style: string           // Style used
  usage: {
    input_tokens: number
    output_tokens: number
  }
  error?: string
}
```

**Example**:
```bash
echo '{
  "jsonrpc": "2.0",
  "id": "3",
  "method": "tools/writing_agent",
  "params": {
    "topic": "Best practices for API design and implementation",
    "style": "technical",
    "length": "long"
  }
}' | python agents/anthropic/bridge.py
```

**Style Guidelines**:
- **Professional**: Formal, business-appropriate language
- **Casual**: Conversational, friendly tone
- **Technical**: Precise, documentation-style writing

**Length Guidelines**:
- **Short**: ~300 words (~400-700 tokens)
- **Medium**: ~800 words (~800-1,200 tokens)
- **Long**: ~1,500+ words (~1,500-2,500 tokens)

---

## 🔄 JSON-RPC 2.0 Protocol

All MCP servers follow the JSON-RPC 2.0 specification.

### Standard Methods

#### initialize

Initialize the MCP server.

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": "init-1",
  "method": "initialize",
  "params": {}
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": "init-1",
  "result": {
    "protocolVersion": "2024-11-05",
    "serverInfo": {
      "name": "anthropic-bridge",
      "version": "1.0.0"
    },
    "capabilities": {
      "tools": {}
    }
  }
}
```

#### tools/list

List all available tools.

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": "list-1",
  "method": "tools/list",
  "params": {}
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": "list-1",
  "result": {
    "tools": [
      {
        "name": "research_agent",
        "description": "Deep research and synthesis",
        "inputSchema": { ... }
      },
      {
        "name": "code_agent",
        "description": "Code development and review",
        "inputSchema": { ... }
      },
      {
        "name": "writing_agent",
        "description": "Content and documentation",
        "inputSchema": { ... }
      }
    ]
  }
}
```

### Error Codes

| Code | Message | Description |
|------|---------|-------------|
| -32700 | Parse error | Invalid JSON |
| -32600 | Invalid request | Invalid JSON-RPC |
| -32601 | Method not found | Unknown method |
| -32602 | Invalid params | Invalid parameters |
| -32603 | Internal error | Server error |
| -32000 | Server error | Custom server error |

**Error Response**:
```json
{
  "jsonrpc": "2.0",
  "id": "req-1",
  "error": {
    "code": -32601,
    "message": "Method not found",
    "data": {
      "method": "unknown_method"
    }
  }
}
```

---

## 🚀 Usage Patterns

### Pattern 1: Direct CLI Call

```bash
# Using mcp_call.py
python -m mcp.mcp_call call anthropic research_agent \
  --params '{"query": "AI trends", "depth": "standard"}'
```

### Pattern 2: Python API

```python
from mcp.mcp_call import invoke_mcp_request

result = invoke_mcp_request(
    command="python agents/anthropic/bridge.py",
    method="tools/research_agent",
    params={"query": "AI trends", "depth": "standard"},
    timeout=300
)

findings = result["call"]["result"]["findings"]
```

### Pattern 3: SuperClaude Orchestration

```python
from core.super_claude import SuperClaude, AgentTask, AgentTeam

orchestrator = SuperClaude()

result = await orchestrator.delegate_to_anthropic(
    "research_agent",
    {"query": "AI trends", "depth": "standard"}
)

print(result["findings"])
```

### Pattern 4: Multi-Agent Workflow

```python
# Step 1: Research
research = await orchestrator.delegate_to_anthropic(
    "research_agent",
    {"query": "Async programming", "depth": "deep"}
)

# Step 2: Generate code based on research
code = await orchestrator.delegate_to_anthropic(
    "code_agent",
    {
        "task": "Create async example",
        "language": "python",
        "context": research["findings"][:500]
    }
)

# Step 3: Write documentation
docs = await orchestrator.delegate_to_anthropic(
    "writing_agent",
    {"topic": "Async programming guide", "style": "technical"}
)
```

---

## 📊 Rate Limits & Quotas

### Anthropic API Limits

| Tier | RPM | TPM | Daily Limit |
|------|-----|-----|-------------|
| Free | 5 | 20,000 | 100,000 |
| Pro | 50 | 100,000 | 1,000,000 |
| Team | 1,000 | 400,000 | 5,000,000 |

**RPM**: Requests per minute
**TPM**: Tokens per minute

### Best Practices

1. **Implement backoff**: Retry failed requests with exponential backoff
2. **Batch requests**: Combine multiple tasks when possible
3. **Cache results**: Store frequently used responses
4. **Monitor usage**: Track token consumption

---

## 🧪 Testing

### Test MCP Server

```bash
# Test initialize
echo '{"jsonrpc":"2.0","id":"1","method":"initialize"}' | \
  python agents/anthropic/bridge.py

# Test tools/list
echo '{"jsonrpc":"2.0","id":"2","method":"tools/list"}' | \
  python agents/anthropic/bridge.py

# Test research agent
echo '{"jsonrpc":"2.0","id":"3","method":"tools/research_agent","params":{"query":"test"}}' | \
  python agents/anthropic/bridge.py
```

### Integration Tests

```bash
# Run all Anthropic integration tests
pytest tests/integration/test_anthropic_integration.py -v

# Test specific agent
pytest tests/integration/test_anthropic_integration.py::TestAnthropicBridgeIntegration::test_research_agent_basic -v
```

---

## 🔐 Security

### API Key Management

```bash
# ❌ Bad: Hardcoded API key
ANTHROPIC_API_KEY="sk-ant-api03-..."

# ✅ Good: Environment variable
export ANTHROPIC_API_KEY=$(cat ~/.anthropic_key)

# ✅ Better: Use .env file (not committed)
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

### Input Validation

All bridges validate inputs:

```python
# Parameters are validated
result = research_agent(
    query="",  # ❌ Will fail: empty query
    depth="invalid"  # ❌ Will fail: invalid depth
)

# Proper usage
result = research_agent(
    query="Valid query",
    depth="standard"  # ✅ Valid
)
```

---

## 📚 Additional Resources

- [ANTHROPIC_SETUP.md](../../docs/ANTHROPIC_SETUP.md) - Setup guide
- [CODE_EXECUTION_MCP.md](../../docs/CODE_EXECUTION_MCP.md) - Execution patterns
- [Anthropic API Docs](https://docs.anthropic.com/)
- [JSON-RPC 2.0 Spec](https://www.jsonrpc.org/specification)

---

**Last Updated**: 2025-11-05
**Version**: Phase 3.0
