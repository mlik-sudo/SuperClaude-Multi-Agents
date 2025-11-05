# 🏗️ Architecture - SuperClaude Multi-Agents

Detailed architecture documentation for the SuperClaude Multi-Agents orchestration system.

## System Overview

SuperClaude is a multi-agent orchestration framework that coordinates specialized AI agent teams across different platforms (Google ADK, Anthropic Claude, OpenAI GPT).

### Design Principles

1. **Modularity**: Each agent team is independent and pluggable
2. **Extensibility**: Easy to add new agent types and teams
3. **Async-First**: Built on asyncio for concurrent operations
4. **Type-Safe**: Comprehensive type hints and Pydantic validation
5. **Observable**: Structured logging and performance tracking
6. **Secure**: No hardcoded secrets, input validation, sandboxed execution

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Clients                              │
│           (Claude Code, Gemini CLI, Custom)                 │
└────────────────────────┬────────────────────────────────────┘
                         │ JSON-RPC 2.0 over STDIO
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              SuperClaude Orchestrator (core/)               │
├─────────────────────────────────────────────────────────────┤
│  • Task routing and delegation                              │
│  • Priority-based scheduling                                │
│  • Result aggregation                                       │
│  • Error handling and retries                               │
└────┬──────────────┬──────────────┬──────────────────────────┘
     │              │              │
     │ Phase 1      │ Phase 2      │ Phase 3
     │ (Active)     │ (Planned)    │ (Planned)
     ▼              ▼              ▼
┌─────────┐   ┌──────────┐   ┌─────────┐
│   ADK   │   │ Anthropic│   │ OpenAI  │
│  Team   │   │   Team   │   │  Team   │
└────┬────┘   └─────┬────┘   └────┬────┘
     │              │              │
     │ MCP Bridge   │ MCP Native   │ API Client
     ▼              ▼              ▼
┌─────────┐   ┌──────────┐   ┌─────────┐
│  Agent  │   │  Agent   │   │ Agent   │
│Processes│   │ Services │   │Services │
└─────────┘   └──────────┘   └─────────┘
```

## Component Architecture

### 1. Core Orchestrator (`core/super_claude.py`)

**Responsibilities:**
- Receive and validate task requests
- Route tasks to appropriate agent teams
- Manage task priorities and scheduling
- Aggregate results from multiple agents
- Handle errors and implement retry logic

**Key Classes:**

#### `SuperClaude`
```python
class SuperClaude:
    """Central orchestrator coordinating all agent teams."""

    def __init__(self):
        self.session_id: int
        self.logger: logging.Logger
        self.agents: Dict[AgentTeam, Dict[str, Any]]

    async def orchestrate(
        self, tasks: List[AgentTask]
    ) -> Dict[str, Any]:
        """Execute multiple tasks with priority sorting."""

    async def delegate_to_adk(
        self, agent_name: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Delegate task to ADK team."""
```

#### `AgentTask`
```python
@dataclass
class AgentTask:
    """Task specification for agent execution."""
    team: AgentTeam          # Target team
    agent_name: str          # Specific agent
    method: str              # Method/operation
    params: Dict[str, Any]   # Parameters
    priority: int = 1        # Execution priority
```

### 2. Configuration Management (`config/`)

**Responsibilities:**
- Load and validate environment variables
- Provide type-safe settings
- Manage secrets securely
- Support multiple environments (dev, staging, prod)

**Architecture:**
```python
# Singleton pattern for global settings
from config import settings

# Type-safe with Pydantic validation
class Settings(BaseSettings):
    agent_timeout: int = Field(ge=10, le=3600)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]

    def get_adk_bridge_path(self) -> Path:
        """Get bridge path with fallback logic."""
```

### 3. Agent Bridge (`agents/adk/bridge.py`)

**Responsibilities:**
- Translate MCP requests to ADK agent calls
- Manage agent subprocess execution
- Handle STDIO communication
- Implement timeout and error handling

**Communication Flow:**
```
MCP Request → JSON-RPC Parser → Agent Dispatcher → Subprocess Exec
                                                         ↓
MCP Response ← JSON Formatter ← Result Handler ← Stdout/Stderr
```

### 4. Logging System (`utils/logging.py`)

**Features:**
- Structured logging (JSON/text formats)
- Log rotation (size and time-based)
- Performance tracking
- Context injection
- Error-only log files

**Architecture:**
```python
# Setup logging on application start
setup_logging(
    log_level="INFO",
    log_format="json",
    log_dir=Path("./logs")
)

# Use performance tracking
with PerformanceLogger("agent_execution", agent="watch_collect"):
    result = await execute_agent()
```

### 5. Validation (`utils/validation.py`)

**Responsibilities:**
- Validate JSON-RPC requests/responses
- Validate agent parameters
- Prevent injection attacks
- Type safety enforcement

**Schema Validation:**
```python
# Validate MCP request
request = validate_mcp_request({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {...}
})

# Validate agent-specific params
params = validate_agent_params("watch_collect", {
    "sources": ["github"],
    "output_format": "markdown"
})
```

## Data Flow

### Request Processing Flow

```
1. MCP Client sends JSON-RPC request via STDIO
   ↓
2. SuperClaude receives and validates request
   ↓
3. Request parsed into AgentTask objects
   ↓
4. Tasks sorted by priority
   ↓
5. For each task:
   a. Route to appropriate team (ADK/Anthropic/OpenAI)
   b. Execute delegation method
   c. Agent bridge translates to subprocess call
   d. Subprocess executes agent code
   e. Results captured and parsed
   ↓
6. Results aggregated into response
   ↓
7. Response formatted as JSON-RPC
   ↓
8. Sent back to client via STDIO
```

### Error Handling Flow

```
Exception Raised
   ↓
Caught by delegation method
   ↓
Logged with context
   ↓
Retry logic (if applicable)
   ↓
  Success? ──Yes──> Return result
     │
    No
     ↓
Format error response
   ↓
Return to orchestrator
   ↓
Include in aggregated results
```

## Security Architecture

### Defense in Depth

**Layer 1: Input Validation**
- JSON-RPC schema validation
- Agent parameter validation
- Path traversal prevention
- Size limits on inputs

**Layer 2: Process Isolation**
- Subprocess execution (not eval/exec)
- Environment isolation
- Resource limits (timeout, memory)

**Layer 3: Secrets Management**
- Environment variables only
- No hardcoded credentials
- Gitignore comprehensive
- Secrets scanning in CI

**Layer 4: Logging & Monitoring**
- Audit logging
- Error tracking
- Performance metrics
- Anomaly detection (future)

### Threat Model

| Threat | Mitigation |
|--------|-----------|
| **Code Injection** | Subprocess with args list, no shell=True |
| **Path Traversal** | Path validation, ".." detection |
| **DoS via Timeout** | Configurable timeouts, resource limits |
| **Secret Leakage** | .gitignore, pre-commit hooks, secret scanning |
| **Dependency Vuln** | Safety checks, automated updates |

## Performance Considerations

### Async Execution

**Current State (Phase 1):**
- Sequential task execution
- Async subprocess communication
- Non-blocking I/O

**Planned (Phase 2):**
```python
# Parallel execution of independent tasks
async def orchestrate_parallel(tasks: List[AgentTask]):
    # Group tasks by dependencies
    task_groups = group_by_dependencies(tasks)

    for group in task_groups:
        # Execute group in parallel
        results = await asyncio.gather(*[
            execute_task(task) for task in group
        ])
```

### Caching Strategy (Future)

```python
# Cache agent results
@lru_cache(maxsize=100)
def get_agent_result(agent_name: str, params_hash: str):
    """Cache frequently used results."""

# Time-based cache invalidation
cache = TTLCache(maxsize=100, ttl=300)  # 5 minutes
```

### Resource Management

- **Timeout**: Default 300s, configurable per agent
- **Concurrency**: Max 5 agents (configurable)
- **Memory**: No explicit limits (future: cgroups)
- **Log Rotation**: 10MB files, 5 backups

## Extensibility Patterns

### Adding New Agent Team

1. **Define Team Enum**
```python
class AgentTeam(Enum):
    ADK = "adk"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    NEW_TEAM = "new_team"  # Add here
```

2. **Implement Delegation Method**
```python
async def delegate_to_new_team(
    self, agent_name: str, params: Dict[str, Any]
) -> Dict[str, Any]:
    """Delegate to new team."""
    # Implementation
```

3. **Update Orchestrator Routing**
```python
if task.team == AgentTeam.NEW_TEAM:
    result = await self.delegate_to_new_team(...)
```

4. **Add Configuration**
```python
# In __init__
self.agents[AgentTeam.NEW_TEAM] = {
    "endpoint": settings.new_team_endpoint,
    "available_agents": [...]
}
```

### Adding New Agent to Existing Team

1. **Update agent list** in team config
2. **Add parameter schema** in `validation.py`
3. **Update agent dispatch** in bridge
4. **Add tests** for new agent

## Testing Architecture

### Test Pyramid

```
         /\
        /  \  E2E Tests (10%)
       /────\
      /      \  Integration Tests (30%)
     /────────\
    /          \  Unit Tests (60%)
   /────────────\
```

**Unit Tests** (`tests/unit/`)
- Test individual functions/classes
- Mock external dependencies
- Fast execution (<1s)
- High coverage (>80%)

**Integration Tests** (`tests/integration/`)
- Test component interactions
- Real subprocess execution (or mock)
- Medium speed (<10s)

**End-to-End Tests** (Future)
- Full workflow testing
- Real agent execution
- Slow (<60s)

### Test Fixtures

```python
# conftest.py
@pytest.fixture
def mock_settings():
    """Provide test configuration."""

@pytest.fixture
def mock_subprocess():
    """Mock agent subprocess execution."""

@pytest.fixture
async def orchestrator():
    """Provide configured orchestrator instance."""
```

## Deployment Architecture (Future)

### Container Deployment
```
┌─────────────────────────────────┐
│     Load Balancer (nginx)       │
└────────────┬────────────────────┘
             │
        ┌────┴────┐
        │         │
   ┌────▼───┐ ┌──▼──────┐
   │ Super  │ │ Super   │  (Horizontal scaling)
   │Claude 1│ │ Claude 2│
   └────┬───┘ └──┬──────┘
        │        │
   ┌────▼────────▼────┐
   │   Redis Cache    │  (Shared state)
   └──────────────────┘
```

### Kubernetes Manifest (Example)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: super-claude
spec:
  replicas: 3
  selector:
    matchLabels:
      app: super-claude
  template:
    spec:
      containers:
      - name: super-claude
        image: super-claude:latest
        env:
        - name: ENVIRONMENT
          value: "production"
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## Monitoring & Observability (Planned)

### Metrics to Track

**Performance:**
- Agent execution time (p50, p95, p99)
- Request throughput (req/s)
- Error rate (%)
- Queue depth

**Resources:**
- CPU usage
- Memory usage
- Disk I/O
- Network I/O

**Business:**
- Agent invocations by type
- Success/failure rates
- User/session counts

### Instrumentation

```python
# OpenTelemetry integration (future)
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("agent_execution"):
    result = await execute_agent()
```

## Future Architecture Enhancements

### Phase 2: Anthropic Integration
- Native MCP client for Claude
- Streaming responses
- Function calling support

### Phase 3: OpenAI Integration
- GPT Assistants API
- Thread management
- File uploads

### Phase 4: Memory & RAG
- Vector database (ChromaDB/Pinecone)
- Conversation history
- Context retrieval
- Long-term memory

## References

- [Model Context Protocol Spec](https://spec.modelcontextprotocol.io/)
- [Google ADK Documentation](https://cloud.google.com/agent-development-kit)
- [Anthropic MCP](https://www.anthropic.com/mcp)
- [Pydantic Documentation](https://docs.pydantic.dev/)
