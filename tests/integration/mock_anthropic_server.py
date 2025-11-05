"""Mock Anthropic Server for Testing

This module provides a mock Anthropic API server that simulates Claude API responses
for integration testing without requiring actual API keys or making real API calls.
"""

import json
from typing import Any, Dict, List, Optional


class MockAnthropicMessage:
    """Mock Anthropic message response."""

    def __init__(self, content: str, role: str = "assistant"):
        self.content = [MockContentBlock(content)]
        self.role = role
        self.model = "claude-3-5-sonnet-20241022"
        self.stop_reason = "end_turn"
        self.usage = MockUsage(150, 800)


class MockContentBlock:
    """Mock content block in message."""

    def __init__(self, text: str):
        self.type = "text"
        self.text = text


class MockUsage:
    """Mock token usage."""

    def __init__(self, input_tokens: int, output_tokens: int):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


class MockAnthropicClient:
    """Mock Anthropic API client for testing."""

    def __init__(self, api_key: str = "mock-api-key"):
        self.api_key = api_key
        self.messages = MockMessagesAPI()


class MockMessagesAPI:
    """Mock messages API."""

    def create(
        self,
        model: str,
        max_tokens: int,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> MockAnthropicMessage:
        """Create a mock message response based on the prompt."""

        # Extract user message
        user_message = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        # Determine response based on keywords in the message
        response_text = self._generate_response(user_message, model)

        return MockAnthropicMessage(response_text)

    def _generate_response(self, prompt: str, model: str) -> str:
        """Generate appropriate mock response based on prompt."""

        prompt_lower = prompt.lower()

        # Research agent responses
        if "research" in prompt_lower or "query" in prompt_lower:
            return self._research_response(prompt)

        # Code agent responses
        elif "code" in prompt_lower or "function" in prompt_lower or "implement" in prompt_lower:
            return self._code_response(prompt)

        # Writing agent responses
        elif "write" in prompt_lower or "document" in prompt_lower or "article" in prompt_lower:
            return self._writing_response(prompt)

        # Default response
        else:
            return self._default_response(prompt)

    def _research_response(self, prompt: str) -> str:
        """Generate mock research response."""
        return """# Research Findings

## Key Findings
1. **Primary Discovery**: Advanced multi-agent systems are becoming increasingly sophisticated
2. **Current Trends**: Integration of MCP (Model Context Protocol) enables better agent coordination
3. **Best Practices**: Hybrid approaches combining simple and complex execution modes

## Analysis
The research reveals that modern AI agent architectures benefit from:
- Modular design with specialized agents
- Token-efficient communication protocols
- Real-time data processing capabilities

## Insights
- MCP provides standardized communication between agents
- Code generation approaches reduce manual workflow creation
- Anthropic's Claude models excel at complex reasoning tasks

## Next Steps
1. Implement prototype with core agents
2. Validate token efficiency metrics
3. Conduct integration testing
4. Deploy to production environment

**Confidence Level**: High (based on industry standards and documentation)
"""

    def _code_response(self, prompt: str) -> str:
        """Generate mock code response."""

        # Determine language from prompt
        if "python" in prompt.lower():
            return """```python
def fibonacci(n: int) -> int:
    \"\"\"Calculate the nth Fibonacci number.

    Args:
        n: The position in the Fibonacci sequence

    Returns:
        The Fibonacci number at position n

    Examples:
        >>> fibonacci(0)
        0
        >>> fibonacci(1)
        1
        >>> fibonacci(10)
        55
    \"\"\"
    if n <= 1:
        return n

    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b

    return b


# Usage example
if __name__ == "__main__":
    for i in range(11):
        print(f"fibonacci({i}) = {fibonacci(i)}")
```

**Code Review Notes:**
- Time complexity: O(n)
- Space complexity: O(1)
- Handles edge cases (n=0, n=1)
- Includes comprehensive docstring
- Type hints for better code clarity
"""

        elif "javascript" in prompt.lower() or "typescript" in prompt.lower():
            return """```typescript
function fibonacci(n: number): number {
  /**
   * Calculate the nth Fibonacci number
   * @param n - The position in the Fibonacci sequence
   * @returns The Fibonacci number at position n
   */
  if (n <= 1) return n;

  let [a, b] = [0, 1];
  for (let i = 2; i <= n; i++) {
    [a, b] = [b, a + b];
  }

  return b;
}

// Usage example
for (let i = 0; i <= 10; i++) {
  console.log(`fibonacci(${i}) = ${fibonacci(i)}`);
}

export { fibonacci };
```

**Code Review Notes:**
- Modern ES6+ syntax
- Type-safe with TypeScript
- Efficient iterative approach
- Exportable for module use
"""

        else:
            return """```python
# Generic implementation example
def process_data(data: list) -> dict:
    \"\"\"Process input data and return results.\"\"\"
    return {
        "status": "success",
        "items": data,
        "count": len(data)
    }
```
"""

    def _writing_response(self, prompt: str) -> str:
        """Generate mock writing response."""
        return """# Benefits of Asynchronous Programming

## Introduction

Asynchronous programming has become a cornerstone of modern software development, enabling applications to handle multiple operations concurrently without blocking execution. This paradigm shift offers significant advantages for scalability and performance.

## Key Benefits

### 1. Improved Performance
Asynchronous code allows programs to continue executing while waiting for I/O operations, network requests, or other time-consuming tasks to complete. This results in:
- Reduced idle CPU time
- Better resource utilization
- Faster overall application performance

### 2. Enhanced Scalability
By avoiding thread-per-request models, async systems can handle thousands of concurrent connections with minimal resource overhead:
- Lower memory footprint per connection
- Reduced context switching overhead
- Better handling of high-concurrency scenarios

### 3. Better User Experience
Non-blocking operations ensure applications remain responsive:
- UI doesn't freeze during long operations
- Real-time updates and streaming capabilities
- Smooth handling of multiple simultaneous requests

## Best Practices

1. **Use async/await syntax** for cleaner, more readable code
2. **Avoid blocking calls** in async functions
3. **Handle errors properly** with try/except blocks
4. **Use connection pooling** for database and API calls
5. **Monitor and profile** async operations for bottlenecks

## Conclusion

Asynchronous programming is essential for building modern, scalable applications. While it introduces complexity, the performance and scalability benefits make it indispensable for high-concurrency systems.
"""

    def _default_response(self, prompt: str) -> str:
        """Generate default mock response."""
        return f"""I understand you've asked about: {prompt[:100]}...

Here's a comprehensive response:

**Summary**: This is a mock response from the Anthropic test server.

**Details**:
- The mock server simulates real API behavior
- Responses are generated based on prompt keywords
- Token usage is tracked for testing purposes

**Recommendations**:
1. Review the mock implementation
2. Validate response structure
3. Test error handling scenarios

This mock response helps ensure integration tests work without real API calls.
"""


class MockAnthropicBridge:
    """Mock bridge for testing without real API calls."""

    def __init__(self, api_key: str = "mock-key", model: str = "claude-3-5-sonnet-20241022"):
        self.client = MockAnthropicClient(api_key)
        self.model = model

    def research_agent(
        self,
        query: str,
        depth: str = "standard",
        sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Mock research agent."""

        prompt = f"""You are a research specialist. Conduct {depth} research on:

Query: {query}
{f'Sources to consider: {", ".join(sources)}' if sources else ''}

Provide:
1. Key findings (3-5 bullet points)
2. Analysis of the topic
3. Insights and implications
4. Recommended next steps
"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        return {
            "status": "success",
            "findings": message.content[0].text,
            "query": query,
            "depth": depth,
            "usage": {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens
            }
        }

    def code_agent(
        self,
        task: str,
        language: str = "python",
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mock code agent."""

        prompt = f"""You are a coding specialist. Complete this task:

Task: {task}
Language: {language}
{f'Context: {context}' if context else ''}

Provide:
1. Complete, working code
2. Code review notes
3. Usage examples
4. Performance considerations
"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        return {
            "status": "success",
            "code": message.content[0].text,
            "language": language,
            "usage": {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens
            }
        }

    def writing_agent(
        self,
        topic: str,
        style: str = "professional",
        length: str = "medium"
    ) -> Dict[str, Any]:
        """Mock writing agent."""

        prompt = f"""You are a professional writer. Create content on:

Topic: {topic}
Style: {style}
Length: {length}

Provide:
1. Well-structured article or documentation
2. Clear sections with headers
3. Engaging and informative content
"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1800,
            messages=[{"role": "user", "content": prompt}]
        )

        return {
            "status": "success",
            "content": message.content[0].text,
            "topic": topic,
            "style": style,
            "usage": {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens
            }
        }


# Utility function for tests
def create_mock_bridge(api_key: str = "test-key") -> MockAnthropicBridge:
    """Create a mock Anthropic bridge for testing."""
    return MockAnthropicBridge(api_key=api_key)
