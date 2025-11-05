#!/usr/bin/env python3
"""
Tech Digest with Analysis - Hybrid Skill

This skill demonstrates the power of combining multiple Anthropic agents
in a coordinated workflow to create comprehensive technical digests.

Workflow:
1. Research Agent: Gathers information on a technical topic
2. Code Agent: Creates example implementations
3. Writing Agent: Produces polished documentation

Usage:
    python skills/complex/tech-digest-with-analysis.py --topic "async programming"
    python skills/complex/tech-digest-with-analysis.py --topic "docker containers" --depth deep
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.super_claude import SuperClaude, AgentTask, AgentTeam


class TechDigestSkill:
    """Hybrid skill for creating comprehensive technical digests."""

    def __init__(self):
        """Initialize the skill with SuperClaude orchestrator."""
        self.orchestrator = SuperClaude()
        self.results = {
            "research": None,
            "code": None,
            "documentation": None
        }

    async def execute(
        self,
        topic: str,
        depth: str = "standard",
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Execute the complete tech digest workflow.

        Args:
            topic: Technical topic to research and document
            depth: Research depth (quick/standard/deep)
            language: Programming language for examples

        Returns:
            Complete digest with research, code, and documentation
        """

        print(f"\n🚀 Starting Tech Digest: {topic}")
        print(f"📊 Depth: {depth} | Language: {language}\n")

        # Step 1: Research the topic
        print("📚 Step 1/3: Researching topic...")
        research_result = await self._research_topic(topic, depth)
        self.results["research"] = research_result
        print(f"✅ Research complete ({research_result['usage']['output_tokens']} tokens)")

        # Step 2: Generate code examples
        print("\n💻 Step 2/3: Generating code examples...")
        code_result = await self._generate_code_examples(topic, language, research_result)
        self.results["code"] = code_result
        print(f"✅ Code generation complete ({code_result['usage']['output_tokens']} tokens)")

        # Step 3: Create documentation
        print("\n✍️  Step 3/3: Creating documentation...")
        doc_result = await self._create_documentation(topic, research_result, code_result)
        self.results["documentation"] = doc_result
        print(f"✅ Documentation complete ({doc_result['usage']['output_tokens']} tokens)")

        # Compile final digest
        digest = self._compile_digest(topic)

        # Print summary
        self._print_summary()

        return digest

    async def _research_topic(self, topic: str, depth: str) -> Dict[str, Any]:
        """Use research agent to gather information."""

        task = AgentTask(
            team=AgentTeam.ANTHROPIC,
            agent_name="research_agent",
            method="call",
            params={
                "query": f"Latest developments, best practices, and key concepts in {topic}",
                "depth": depth,
                "sources": ["documentation", "github", "technical blogs"]
            }
        )

        result = await self.orchestrator.delegate_to_anthropic("research_agent", task.params)
        return result

    async def _generate_code_examples(
        self,
        topic: str,
        language: str,
        research_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use code agent to create practical examples."""

        # Extract key concepts from research
        research_findings = research_result.get("findings", "")

        task = AgentTask(
            team=AgentTeam.ANTHROPIC,
            agent_name="code_agent",
            method="call",
            params={
                "task": f"Create a practical, production-ready example demonstrating {topic}",
                "language": language,
                "context": f"Based on research: {research_findings[:500]}..."
            }
        )

        result = await self.orchestrator.delegate_to_anthropic("code_agent", task.params)
        return result

    async def _create_documentation(
        self,
        topic: str,
        research_result: Dict[str, Any],
        code_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use writing agent to create polished documentation."""

        task = AgentTask(
            team=AgentTeam.ANTHROPIC,
            agent_name="writing_agent",
            method="call",
            params={
                "topic": f"Complete guide to {topic} with examples",
                "style": "technical",
                "length": "long"
            }
        )

        result = await self.orchestrator.delegate_to_anthropic("writing_agent", task.params)
        return result

    def _compile_digest(self, topic: str) -> Dict[str, Any]:
        """Compile all results into final digest."""

        return {
            "title": f"Tech Digest: {topic}",
            "sections": {
                "research": {
                    "title": "Research Findings",
                    "content": self.results["research"]["findings"],
                    "tokens": self.results["research"]["usage"]["output_tokens"]
                },
                "code": {
                    "title": "Code Examples",
                    "content": self.results["code"]["code"],
                    "language": self.results["code"]["language"],
                    "tokens": self.results["code"]["usage"]["output_tokens"]
                },
                "documentation": {
                    "title": "Complete Documentation",
                    "content": self.results["documentation"]["content"],
                    "tokens": self.results["documentation"]["usage"]["output_tokens"]
                }
            },
            "metadata": {
                "total_tokens": sum([
                    self.results["research"]["usage"]["output_tokens"],
                    self.results["code"]["usage"]["output_tokens"],
                    self.results["documentation"]["usage"]["output_tokens"]
                ]),
                "agents_used": ["research_agent", "code_agent", "writing_agent"],
                "status": "success"
            }
        }

    def _print_summary(self):
        """Print execution summary."""

        total_input = sum([
            self.results["research"]["usage"]["input_tokens"],
            self.results["code"]["usage"]["input_tokens"],
            self.results["documentation"]["usage"]["input_tokens"]
        ])

        total_output = sum([
            self.results["research"]["usage"]["output_tokens"],
            self.results["code"]["usage"]["output_tokens"],
            self.results["documentation"]["usage"]["output_tokens"]
        ])

        print("\n" + "="*60)
        print("📊 TECH DIGEST SUMMARY")
        print("="*60)
        print(f"✅ All agents completed successfully")
        print(f"🔬 Research Agent: {self.results['research']['usage']['output_tokens']} tokens")
        print(f"💻 Code Agent: {self.results['code']['usage']['output_tokens']} tokens")
        print(f"✍️  Writing Agent: {self.results['documentation']['usage']['output_tokens']} tokens")
        print(f"\n📈 Total Usage:")
        print(f"   Input tokens:  {total_input:,}")
        print(f"   Output tokens: {total_output:,}")
        print(f"   Total tokens:  {total_input + total_output:,}")
        print("="*60 + "\n")


async def main():
    """Main entry point for the skill."""

    parser = argparse.ArgumentParser(
        description="Create comprehensive technical digests using Anthropic agents"
    )
    parser.add_argument(
        "--topic",
        type=str,
        required=True,
        help="Technical topic to research and document"
    )
    parser.add_argument(
        "--depth",
        type=str,
        choices=["quick", "standard", "deep"],
        default="standard",
        help="Research depth (default: standard)"
    )
    parser.add_argument(
        "--language",
        type=str,
        default="python",
        help="Programming language for code examples (default: python)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (JSON format)"
    )

    args = parser.parse_args()

    # Execute the skill
    skill = TechDigestSkill()

    try:
        digest = await skill.execute(
            topic=args.topic,
            depth=args.depth,
            language=args.language
        )

        # Save to file if requested
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                json.dump(digest, f, indent=2)
            print(f"💾 Digest saved to: {output_path}")

        # Print digest
        print("\n" + "="*60)
        print(f"📄 {digest['title']}")
        print("="*60)

        for section_key, section in digest["sections"].items():
            print(f"\n## {section['title']}")
            print("-" * 60)
            print(section['content'][:500])
            if len(section['content']) > 500:
                print(f"\n... ({len(section['content']) - 500} more characters)")
            print()

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
