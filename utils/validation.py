#!/usr/bin/env python3
"""
✅ Schema Validation for SuperClaude

Provides JSON-RPC and agent parameter validation using Pydantic.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator


class MCPRequest(BaseModel):
    """JSON-RPC 2.0 MCP Request schema."""

    jsonrpc: str = Field(default="2.0", const=True)
    id: Union[int, str]
    method: str
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator("jsonrpc")
    def validate_jsonrpc_version(cls, v):
        """Ensure JSON-RPC version is 2.0."""
        if v != "2.0":
            raise ValueError("Only JSON-RPC 2.0 is supported")
        return v

    @validator("method")
    def validate_method(cls, v):
        """Validate method name."""
        valid_methods = [
            "initialize",
            "tools/list",
            "tools/call",
            "resources/list",
            "prompts/list"
        ]
        if v not in valid_methods:
            raise ValueError(f"Invalid method: {v}. Must be one of {valid_methods}")
        return v


class MCPResponse(BaseModel):
    """JSON-RPC 2.0 MCP Response schema."""

    jsonrpc: str = Field(default="2.0", const=True)
    id: Union[int, str]
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

    @validator("error")
    def validate_error_format(cls, v, values):
        """Ensure error has proper format if present."""
        if v is not None:
            if "code" not in v or "message" not in v:
                raise ValueError("Error must contain 'code' and 'message'")
            if values.get("result") is not None:
                raise ValueError("Response cannot have both result and error")
        return v


class ToolCallParams(BaseModel):
    """Parameters for tools/call method."""

    name: str = Field(..., description="Tool/agent name to invoke")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")

    @validator("name")
    def validate_agent_name(cls, v):
        """Validate agent name format."""
        if not v or not isinstance(v, str):
            raise ValueError("Agent name must be a non-empty string")
        if len(v) > 100:
            raise ValueError("Agent name too long (max 100 characters)")
        return v


class WatchCollectParams(BaseModel):
    """Parameters for watch_collect agent."""

    sources: List[str] = Field(..., description="Data sources to watch")
    output_format: str = Field(default="markdown", description="Output format")

    @validator("sources")
    def validate_sources(cls, v):
        """Validate sources list."""
        if not v:
            raise ValueError("At least one source is required")

        valid_sources = ["github", "pypi", "npm", "hackernews", "reddit"]
        for source in v:
            if source not in valid_sources:
                raise ValueError(f"Invalid source: {source}. Must be one of {valid_sources}")
        return v

    @validator("output_format")
    def validate_output_format(cls, v):
        """Validate output format."""
        valid_formats = ["markdown", "json", "html"]
        if v not in valid_formats:
            raise ValueError(f"Invalid format: {v}. Must be one of {valid_formats}")
        return v


class AnalyseWatchReportParams(BaseModel):
    """Parameters for analyse_watch_report agent."""

    report_path: str = Field(..., description="Path to watch report")
    analysis_type: str = Field(default="full", description="Type of analysis")

    @validator("report_path")
    def validate_report_path(cls, v):
        """Validate report path."""
        if not v or not isinstance(v, str):
            raise ValueError("Report path must be a non-empty string")
        if ".." in v:
            raise ValueError("Report path cannot contain '..' (path traversal)")
        return v

    @validator("analysis_type")
    def validate_analysis_type(cls, v):
        """Validate analysis type."""
        valid_types = ["full", "quick", "trends", "security"]
        if v not in valid_types:
            raise ValueError(f"Invalid analysis type: {v}. Must be one of {valid_types}")
        return v


class CurateDigestParams(BaseModel):
    """Parameters for curate_digest agent."""

    content_type: str = Field(..., description="Type of content to curate")
    max_items: int = Field(default=10, ge=1, le=100, description="Maximum items to include")
    format: str = Field(default="newsletter", description="Output format")

    @validator("content_type")
    def validate_content_type(cls, v):
        """Validate content type."""
        valid_types = ["newsletter", "social", "blog", "report"]
        if v not in valid_types:
            raise ValueError(f"Invalid content type: {v}. Must be one of {valid_types}")
        return v


class LabelGithubIssueParams(BaseModel):
    """Parameters for label_github_issue agent."""

    issue_url: str = Field(..., description="GitHub issue URL")
    suggested_labels: Optional[List[str]] = Field(default=None, description="Suggested labels")

    @validator("issue_url")
    def validate_issue_url(cls, v):
        """Validate GitHub issue URL."""
        if not v.startswith("https://github.com/"):
            raise ValueError("Must be a valid GitHub issue URL")
        if "/issues/" not in v and "/pull/" not in v:
            raise ValueError("URL must point to an issue or pull request")
        return v


# Registry mapping agent names to their parameter schemas
AGENT_PARAMS_SCHEMA = {
    "watch_collect": WatchCollectParams,
    "analyse_watch_report": AnalyseWatchReportParams,
    "curate_digest": CurateDigestParams,
    "label_github_issue": LabelGithubIssueParams,
}


def validate_mcp_request(data: Dict[str, Any]) -> MCPRequest:
    """
    Validate MCP JSON-RPC request.

    Args:
        data: Raw request data

    Returns:
        Validated MCPRequest object

    Raises:
        ValidationError: If request is invalid
    """
    return MCPRequest(**data)


def validate_mcp_response(data: Dict[str, Any]) -> MCPResponse:
    """
    Validate MCP JSON-RPC response.

    Args:
        data: Raw response data

    Returns:
        Validated MCPResponse object

    Raises:
        ValidationError: If response is invalid
    """
    return MCPResponse(**data)


def validate_agent_params(agent_name: str, params: Dict[str, Any]) -> BaseModel:
    """
    Validate agent-specific parameters.

    Args:
        agent_name: Name of the agent
        params: Parameters to validate

    Returns:
        Validated parameters object

    Raises:
        ValueError: If agent not found
        ValidationError: If parameters are invalid
    """
    schema_class = AGENT_PARAMS_SCHEMA.get(agent_name)

    if schema_class is None:
        raise ValueError(f"Unknown agent: {agent_name}")

    return schema_class(**params)


def validate_tool_call(params: Dict[str, Any]) -> ToolCallParams:
    """
    Validate tools/call parameters.

    Args:
        params: Raw tool call parameters

    Returns:
        Validated ToolCallParams object

    Raises:
        ValidationError: If parameters are invalid
    """
    return ToolCallParams(**params)
