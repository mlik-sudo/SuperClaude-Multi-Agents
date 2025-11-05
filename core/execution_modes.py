#!/usr/bin/env python3
"""
Execution Mode Router for SuperClaude.

Determines whether to use simple (direct CLI) or complex (code generation)
execution mode based on task characteristics.
"""

import json
from enum import Enum
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """Execution modes for agent orchestration."""

    SIMPLE = "simple"  # Direct MCP CLI calls
    COMPLEX = "complex"  # Code generation + sandbox execution


class ExecutionRouter:
    """
    Routes tasks to appropriate execution mode.

    Uses heuristics to determine if a task requires code execution
    or can be handled with direct CLI calls.
    """

    # Keywords that indicate complex orchestration needs
    COMPLEX_KEYWORDS = [
        "filter",
        "loop",
        "until",
        "while",
        "iterate",
        "aggregate",
        "combine",
        "merge",
        "batch",
        "parallel",
        "join",
        "transform",
        "map",
        "reduce",
        "collect all",
        "process each",
        "for each",
        "if",
        "when",
        "compare",
        "sort",
        "group",
    ]

    @staticmethod
    def analyze_task(
        task_description: str, tasks: List[Any], params: Dict[str, Any] = None
    ) -> ExecutionMode:
        """
        Determine optimal execution mode for given tasks.

        Args:
            task_description: Natural language description of the task
            tasks: List of AgentTask objects
            params: Additional parameters that might indicate complexity

        Returns:
            ExecutionMode (SIMPLE or COMPLEX)
        """
        params = params or {}

        # Rule 1: Single task with no complex operations → SIMPLE
        if len(tasks) == 1:
            task_desc_lower = task_description.lower()

            # Check for complex keywords in task description
            has_complex_keyword = any(
                kw in task_desc_lower for kw in ExecutionRouter.COMPLEX_KEYWORDS
            )

            if not has_complex_keyword:
                logger.info("Single task without complex keywords → SIMPLE mode")
                return ExecutionMode.SIMPLE

        # Rule 2: Multiple tasks (2+) → likely needs orchestration
        if len(tasks) >= 2:
            # Check if tasks are truly independent or need coordination
            task_desc_lower = task_description.lower()

            coordination_keywords = [
                "then",
                "after",
                "use result",
                "combine",
                "merge",
                "from the",
                "based on",
            ]

            needs_coordination = any(
                kw in task_desc_lower for kw in coordination_keywords
            )

            if needs_coordination:
                logger.info(
                    f"Multiple tasks ({len(tasks)}) with coordination → COMPLEX mode"
                )
                return ExecutionMode.COMPLEX

        # Rule 3: Check for data transformation/filtering needs
        task_desc_lower = task_description.lower()

        data_transformation_keywords = [
            "filter",
            "only",
            "where",
            "with more than",
            "greater than",
            "less than",
            "top",
            "first",
            "last",
            "limit",
            "exclude",
            "include",
            "matching",
        ]

        has_data_transformation = any(
            kw in task_desc_lower for kw in data_transformation_keywords
        )

        if has_data_transformation:
            logger.info("Data transformation detected → COMPLEX mode")
            return ExecutionMode.COMPLEX

        # Rule 4: Check for looping/iteration
        iteration_keywords = ["all", "each", "every", "for all", "repeatedly"]

        has_iteration = any(kw in task_desc_lower for kw in iteration_keywords)

        if has_iteration and len(tasks) >= 1:
            logger.info("Iteration pattern detected → COMPLEX mode")
            return ExecutionMode.COMPLEX

        # Rule 5: Explicit params indicating need for code execution
        if params.get("force_code_execution"):
            logger.info("Forced code execution mode → COMPLEX")
            return ExecutionMode.COMPLEX

        if params.get("force_simple"):
            logger.info("Forced simple mode → SIMPLE")
            return ExecutionMode.SIMPLE

        # Default: SIMPLE for straightforward cases
        logger.info(f"Default routing for {len(tasks)} task(s) → SIMPLE mode")
        return ExecutionMode.SIMPLE

    @staticmethod
    def explain_decision(
        task_description: str, tasks: List[Any], mode: ExecutionMode
    ) -> str:
        """
        Provide human-readable explanation of routing decision.

        Args:
            task_description: Task description
            tasks: List of tasks
            mode: Chosen execution mode

        Returns:
            Explanation string
        """
        task_desc_lower = task_description.lower()

        reasons = []

        # Analyze why this mode was chosen
        if mode == ExecutionMode.SIMPLE:
            if len(tasks) == 1:
                reasons.append("single task")

            no_complex_kw = not any(
                kw in task_desc_lower for kw in ExecutionRouter.COMPLEX_KEYWORDS
            )
            if no_complex_kw:
                reasons.append("no complex operations detected")

        else:  # COMPLEX
            if len(tasks) >= 2:
                reasons.append(f"{len(tasks)} tasks requiring coordination")

            complex_kw_found = [
                kw
                for kw in ExecutionRouter.COMPLEX_KEYWORDS
                if kw in task_desc_lower
            ]
            if complex_kw_found:
                reasons.append(f"complex keywords: {', '.join(complex_kw_found[:3])}")

        explanation = f"Execution mode: {mode.value} ({', '.join(reasons)})"
        return explanation


class CodeGenerator:
    """
    Generates executable code for complex orchestration tasks.

    Produces Python code that:
    - Calls MCP tools via mcp_call.py
    - Filters and transforms data
    - Implements control flow
    - Returns only necessary results to the model
    """

    @staticmethod
    def generate_python_orchestration(tasks: List[Any]) -> str:
        """
        Generate Python code to orchestrate multiple MCP tool calls.

        Args:
            tasks: List of AgentTask objects

        Returns:
            Executable Python code as string
        """
        code_parts = [
            "#!/usr/bin/env python3",
            '"""Generated orchestration code by SuperClaude."""',
            "",
            "import subprocess",
            "import json",
            "import sys",
            "",
            "def call_mcp(mcp_name, tool_name, **kwargs):",
            '    """Call MCP tool via CLI."""',
            "    args_json = json.dumps(kwargs)",
            "    result = subprocess.run(",
            "        ['python', 'mcp/mcp_call.py', 'call', f'{mcp_name}.{tool_name}', '--args', args_json],",
            "        capture_output=True,",
            "        text=True,",
            "        timeout=300",
            "    )",
            "    if result.returncode != 0:",
            "        return {'status': 'error', 'stderr': result.stderr}",
            "    try:",
            "        return json.loads(result.stdout)",
            "    except json.JSONDecodeError:",
            "        return {'status': 'success', 'output': result.stdout}",
            "",
            "# Generated task execution",
            "",
        ]

        # Generate calls for each task
        for i, task in enumerate(tasks):
            mcp = task.team.value
            tool = task.agent_name
            params = task.params

            # Convert params dict to Python literal
            params_str = json.dumps(params, indent=4)

            code_parts.append(f"# Task {i + 1}: {tool}")
            code_parts.append(f"print('Executing task {i + 1}: {mcp}.{tool}', file=sys.stderr)")
            code_parts.append(f"result_{i} = call_mcp(")
            code_parts.append(f"    '{mcp}',")
            code_parts.append(f"    '{tool}',")

            # Add parameters as keyword arguments
            if params:
                params_obj = json.loads(params_str)
                for key, value in params_obj.items():
                    value_repr = json.dumps(value)
                    code_parts.append(f"    {key}={value_repr},")

            code_parts.append(")")
            code_parts.append("")

        # Collect and output results
        code_parts.extend(
            [
                "# Collect results",
                "all_results = [",
            ]
        )

        for i in range(len(tasks)):
            code_parts.append(f"    result_{i},")

        code_parts.extend(
            [
                "]",
                "",
                "# Filter successful results",
                "successful_results = [r for r in all_results if r.get('status') != 'error']",
                "",
                "# Output final results",
                "output = {",
                "    'status': 'success',",
                f"    'task_count': {len(tasks)},",
                "    'successful': len(successful_results),",
                "    'results': successful_results",
                "}",
                "",
                "print(json.dumps(output, indent=2))",
            ]
        )

        return "\n".join(code_parts)

    @staticmethod
    def generate_typescript_orchestration(tasks: List[Any]) -> str:
        """
        Generate TypeScript code for orchestration (future).

        Args:
            tasks: List of AgentTask objects

        Returns:
            Executable TypeScript code as string
        """
        # Placeholder for TypeScript generation
        return "// TypeScript generation not yet implemented"
