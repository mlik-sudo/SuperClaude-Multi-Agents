#!/usr/bin/env python3
"""
Anthropic Claude MCP Bridge

JSON-RPC 2.0 STDIO Bridge for Anthropic Claude agents.
Implements research_agent, code_agent, and writing_agent using Claude API.

Usage:
    echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python agents/anthropic/bridge.py
    echo '{"jsonrpc":"2.0","id":1,"method":"tools/research_agent","params":{"query":"AI trends"}}' | python agents/anthropic/bridge.py
"""

import json
import os
import sys
from typing import Any, Dict, Optional

# Try to import anthropic
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class AnthropicBridge:
    """Bridge between MCP JSON-RPC and Anthropic Claude API."""

    def __init__(self):
        """Initialize Anthropic bridge."""
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.model = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

        if ANTHROPIC_AVAILABLE and self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.available = True
        else:
            self.client = None
            self.available = False

    def research_agent(self, query: str, depth: str = "standard", sources: list = None) -> Dict[str, Any]:
        """
        Research agent - Deep research and synthesis.

        Args:
            query: Research question or topic
            depth: Research depth (quick/standard/deep)
            sources: Specific sources to consider

        Returns:
            Research results with synthesis
        """
        if not self.available:
            return {
                "status": "error",
                "error": "Anthropic API not available. Set ANTHROPIC_API_KEY environment variable."
            }

        try:
            # Construct research prompt
            prompt = f"""You are a research specialist. Conduct {depth} research on the following query:

Query: {query}

Provide:
1. Key findings (3-5 bullet points)
2. Analysis and synthesis
3. Relevant insights
4. Suggested next steps

Be thorough but concise."""

            if sources:
                prompt += f"\n\nConsider these sources: {', '.join(sources)}"

            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract response
            response_text = message.content[0].text

            return {
                "status": "success",
                "query": query,
                "depth": depth,
                "findings": response_text,
                "model": self.model,
                "usage": {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Research failed: {str(e)}"
            }

    def code_agent(self, task: str, language: str = "python", context: str = None) -> Dict[str, Any]:
        """
        Code agent - Development and code review.

        Args:
            task: Coding task description
            language: Programming language
            context: Additional context or existing code

        Returns:
            Code solution with explanation
        """
        if not self.available:
            return {
                "status": "error",
                "error": "Anthropic API not available. Set ANTHROPIC_API_KEY environment variable."
            }

        try:
            # Construct coding prompt
            prompt = f"""You are an expert {language} developer.

Task: {task}

Provide:
1. Complete, working code
2. Brief explanation of the approach
3. Key considerations
4. Example usage if applicable

Code should be production-ready and follow best practices."""

            if context:
                prompt += f"\n\nContext:\n{context}"

            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract response
            response_text = message.content[0].text

            return {
                "status": "success",
                "task": task,
                "language": language,
                "solution": response_text,
                "model": self.model,
                "usage": {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Code generation failed: {str(e)}"
            }

    def writing_agent(self, topic: str, style: str = "professional", length: str = "medium") -> Dict[str, Any]:
        """
        Writing agent - Documentation and content creation.

        Args:
            topic: Topic or outline to write about
            style: Writing style (professional/casual/technical)
            length: Length (short/medium/long)

        Returns:
            Written content
        """
        if not self.available:
            return {
                "status": "error",
                "error": "Anthropic API not available. Set ANTHROPIC_API_KEY environment variable."
            }

        try:
            # Construct writing prompt
            length_guide = {
                "short": "1-2 paragraphs",
                "medium": "3-5 paragraphs",
                "long": "6-10 paragraphs"
            }

            prompt = f"""You are a professional writer. Create {style} content on the following topic:

Topic: {topic}

Length: {length_guide.get(length, 'medium')}
Style: {style}

Provide well-structured, engaging content that:
1. Clearly addresses the topic
2. Is appropriate for the specified style
3. Includes relevant examples or insights
4. Has a clear conclusion"""

            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract response
            response_text = message.content[0].text

            return {
                "status": "success",
                "topic": topic,
                "style": style,
                "length": length,
                "content": response_text,
                "model": self.model,
                "usage": {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Writing failed: {str(e)}"
            }

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON-RPC 2.0 request."""
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")

        # Handle initialize
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "1.0",
                    "serverInfo": {
                        "name": "anthropic-bridge",
                        "version": "1.0.0"
                    },
                    "capabilities": {
                        "tools": ["research_agent", "code_agent", "writing_agent"]
                    }
                }
            }

        # Handle tools/list
        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "research_agent",
                            "description": "Deep research and synthesis on any topic",
                            "parameters": {
                                "query": {"type": "string", "required": True},
                                "depth": {"type": "string", "enum": ["quick", "standard", "deep"]},
                                "sources": {"type": "array"}
                            }
                        },
                        {
                            "name": "code_agent",
                            "description": "Code development and review",
                            "parameters": {
                                "task": {"type": "string", "required": True},
                                "language": {"type": "string", "default": "python"},
                                "context": {"type": "string"}
                            }
                        },
                        {
                            "name": "writing_agent",
                            "description": "Professional content and documentation",
                            "parameters": {
                                "topic": {"type": "string", "required": True},
                                "style": {"type": "string", "enum": ["professional", "casual", "technical"]},
                                "length": {"type": "string", "enum": ["short", "medium", "long"]}
                            }
                        }
                    ]
                }
            }

        # Handle tool calls
        if method.startswith("tools/"):
            tool_name = method.replace("tools/", "")

            if tool_name == "research_agent":
                result = self.research_agent(**params)
            elif tool_name == "code_agent":
                result = self.code_agent(**params)
            elif tool_name == "writing_agent":
                result = self.writing_agent(**params)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }

            if result.get("status") == "error":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32000,
                        "message": result.get("error", "Unknown error")
                    }
                }

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }

        # Unknown method
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }


def main():
    """Main STDIO loop for JSON-RPC communication."""
    bridge = AnthropicBridge()

    # Read from stdin line by line
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
            response = bridge.handle_request(request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }
            print(json.dumps(error_response), flush=True)
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()
