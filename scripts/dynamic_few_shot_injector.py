#!/usr/bin/env python3
"""
Dynamic Few-Shot Injector

Automatically injects relevant episodic context into system prompts and workflows.
Provides intelligent context selection and compression for optimal token usage.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after path modification
from scripts.episodic_workflow_integration import EpisodicWorkflowIntegration


class DynamicFewShotInjector:
    """Dynamically injects episodic context as few-shot examples."""

    def __init__(self):
        """Initialize the injector."""
        self.episodic_integration = EpisodicWorkflowIntegration()
        self.max_tokens = 900  # Target token limit for episodic context
        self.min_confidence = 0.3  # Minimum confidence for inclusion
        print("🧠 Dynamic Few-Shot Injector initialized")

    def inject_episodic_context(
        self, query: str, agent: str = "cursor_ai", context_type: str = "few_shot"
    ) -> dict[str, Any]:
        """Inject episodic context into a query or system prompt."""
        start_time = time.time()

        try:
            # Get episodic context
            context = self.episodic_integration.get_context_for_task(query, agent)

            if not context or "episodic_context" not in context:
                return {
                    "original_query": query,
                    "enhanced_query": query,
                    "episodic_context": None,
                    "injection_method": "none",
                    "token_estimate": 0,
                    "processing_time_ms": (time.time() - start_time) * 1000,
                }

            episodic = context["episodic_context"]

            # Filter by confidence
            if episodic["confidence_score"] < self.min_confidence:
                return {
                    "original_query": query,
                    "enhanced_query": query,
                    "episodic_context": None,
                    "injection_method": "confidence_filtered",
                    "token_estimate": 0,
                    "processing_time_ms": (time.time() - start_time) * 1000,
                }

            # Choose injection method based on context type
            if context_type == "few_shot":
                enhanced_query, token_estimate = self._inject_as_few_shot(query, episodic)
            elif context_type == "guidance":
                enhanced_query, token_estimate = self._inject_as_guidance(query, episodic)
            elif context_type == "compact":
                enhanced_query, token_estimate = self._inject_as_compact(query, episodic)
            else:
                enhanced_query, token_estimate = self._inject_as_guidance(query, episodic)

            # Compress if over token limit
            if token_estimate > self.max_tokens:
                enhanced_query, token_estimate = self._compress_context(enhanced_query, episodic)

            processing_time_ms = (time.time() - start_time) * 1000

            return {
                "original_query": query,
                "enhanced_query": enhanced_query,
                "episodic_context": episodic,
                "injection_method": context_type,
                "token_estimate": token_estimate,
                "confidence_score": episodic["confidence_score"],
                "processing_time_ms": processing_time_ms,
            }

        except Exception as e:
            print(f"❌ Failed to inject episodic context: {e}")
            return {
                "original_query": query,
                "enhanced_query": query,
                "episodic_context": None,
                "injection_method": "error",
                "token_estimate": 0,
                "processing_time_ms": (time.time() - start_time) * 1000,
            }

    def _inject_as_few_shot(self, query: str, episodic: dict[str, Any]) -> tuple[str, int]:
        """Inject episodic context as few-shot examples."""
        enhanced_parts = [query]
        token_count = len(query.split())  # Rough token estimate

        if episodic["similar_episodes"]:
            enhanced_parts.append("\n\n## 🧠 Similar Successful Episodes:")

            for i, episode in enumerate(episodic["similar_episodes"][:2]):  # Limit to 2 examples
                example = f"\n**Example {i+1}:** {episode['summary']}"
                if episode["what_worked"]:
                    example += f"\n✅ What worked: {', '.join(episode['what_worked'][:2])}"
                if episode["what_to_avoid"]:
                    example += f"\n❌ What to avoid: {', '.join(episode['what_to_avoid'][:2])}"

                enhanced_parts.append(example)
                token_count += len(example.split())

        if episodic["what_worked_bullets"]:
            enhanced_parts.append("\n\n**Apply these patterns:**")
            for item in episodic["what_worked_bullets"][:3]:  # Limit to 3 bullets
                enhanced_parts.append(f"- {item}")
                token_count += len(item.split()) + 2

        if episodic["what_to_avoid_bullets"]:
            enhanced_parts.append("\n\n**Avoid these patterns:**")
            for item in episodic["what_to_avoid_bullets"][:3]:  # Limit to 3 bullets
                enhanced_parts.append(f"- {item}")
                token_count += len(item.split()) + 2

        return "\n".join(enhanced_parts), token_count

    def _inject_as_guidance(self, query: str, episodic: dict[str, Any]) -> tuple[str, int]:
        """Inject episodic context as guidance bullets."""
        enhanced_parts = [query]
        token_count = len(query.split())

        if episodic["what_worked_bullets"] or episodic["what_to_avoid_bullets"]:
            enhanced_parts.append("\n\n## 🧠 Episodic Guidance:")

            if episodic["what_worked_bullets"]:
                enhanced_parts.append("**Successful patterns from similar tasks:**")
                for item in episodic["what_worked_bullets"][:4]:  # Limit to 4 bullets
                    enhanced_parts.append(f"✅ {item}")
                    token_count += len(item.split()) + 2

            if episodic["what_to_avoid_bullets"]:
                enhanced_parts.append("**Patterns to avoid from similar tasks:**")
                for item in episodic["what_to_avoid_bullets"][:4]:  # Limit to 4 bullets
                    enhanced_parts.append(f"❌ {item}")
                    token_count += len(item.split()) + 2

        return "\n".join(enhanced_parts), token_count

    def _inject_as_compact(self, query: str, episodic: dict[str, Any]) -> tuple[str, int]:
        """Inject episodic context in compact format."""
        enhanced_parts = [query]
        token_count = len(query.split())

        if episodic["what_worked_bullets"] or episodic["what_to_avoid_bullets"]:
            enhanced_parts.append("\n🧠 **Context:**")

            if episodic["what_worked_bullets"]:
                worked_compact = " | ".join(episodic["what_worked_bullets"][:2])
                enhanced_parts.append(f"✅ {worked_compact}")
                token_count += len(worked_compact.split()) + 2

            if episodic["what_to_avoid_bullets"]:
                avoid_compact = " | ".join(episodic["what_to_avoid_bullets"][:2])
                enhanced_parts.append(f"❌ {avoid_compact}")
                token_count += len(avoid_compact.split()) + 2

        return "\n".join(enhanced_parts), token_count

    def _compress_context(self, enhanced_query: str, episodic: dict[str, Any]) -> tuple[str, int]:
        """Compress context to fit within token limits."""
        # Take only the most important bullets
        compressed_parts = [enhanced_query.split("\n")[0]]  # Keep original query

        if episodic["what_worked_bullets"]:
            compressed_parts.append("\n🧠 **Key patterns:**")
            for item in episodic["what_worked_bullets"][:2]:  # Only top 2
                compressed_parts.append(f"✅ {item}")

        if episodic["what_to_avoid_bullets"]:
            for item in episodic["what_to_avoid_bullets"][:2]:  # Only top 2
                compressed_parts.append(f"❌ {item}")

        compressed_query = "\n".join(compressed_parts)
        token_count = len(compressed_query.split())

        return compressed_query, token_count

    def enhance_system_prompt(self, base_prompt: str, current_task: str, agent: str = "cursor_ai") -> str:
        """Enhance a system prompt with episodic context."""
        try:
            # Get episodic context for the current task
            context = self.episodic_integration.get_context_for_task(current_task, agent)

            if not context or "episodic_context" not in context:
                return base_prompt

            episodic = context["episodic_context"]

            # Only add if confidence is high enough
            if episodic["confidence_score"] < self.min_confidence:
                return base_prompt

            # Add episodic section to system prompt
            episodic_section = "\n\n## 🧠 Episodic Memory Context\n"
            episodic_section += f"*Based on {len(episodic['similar_episodes'])} similar episodes (confidence: {episodic['confidence_score']:.2f})*\n\n"

            if episodic["what_worked_bullets"]:
                episodic_section += "**Successful patterns from similar tasks:**\n"
                for item in episodic["what_worked_bullets"][:3]:
                    episodic_section += f"- {item}\n"
                episodic_section += "\n"

            if episodic["what_to_avoid_bullets"]:
                episodic_section += "**Patterns to avoid from similar tasks:**\n"
                for item in episodic["what_to_avoid_bullets"][:3]:
                    episodic_section += f"- {item}\n"
                episodic_section += "\n"

            return base_prompt + episodic_section

        except Exception as e:
            print(f"❌ Failed to enhance system prompt: {e}")
            return base_prompt

    def get_injection_stats(self) -> dict[str, Any]:
        """Get statistics about injection performance."""
        try:
            stats = self.episodic_integration.store.get_stats()
            return {
                "total_episodes": stats.get("total_reflections", 0),
                "unique_agents": stats.get("unique_agents", 0),
                "unique_task_types": stats.get("unique_task_types", 0),
                "avg_what_worked_items": stats.get("avg_what_worked_items", 0),
                "avg_what_to_avoid_items": stats.get("avg_what_to_avoid_items", 0),
                "injection_config": {"max_tokens": self.max_tokens, "min_confidence": self.min_confidence},
            }
        except Exception as e:
            print(f"❌ Failed to get injection stats: {e}")
            return {}


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Dynamic Few-Shot Injector")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Inject command
    inject_parser = subparsers.add_parser("inject", help="Inject episodic context into query")
    inject_parser.add_argument("--query", required=True, help="Query to enhance")
    inject_parser.add_argument("--agent", default="cursor_ai", help="Agent name")
    inject_parser.add_argument(
        "--context-type", choices=["few_shot", "guidance", "compact"], default="guidance", help="Injection method"
    )
    inject_parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")

    # Enhance system prompt command
    prompt_parser = subparsers.add_parser("enhance-prompt", help="Enhance system prompt with episodic context")
    prompt_parser.add_argument("--prompt", required=True, help="Base system prompt")
    prompt_parser.add_argument("--task", required=True, help="Current task description")
    prompt_parser.add_argument("--agent", default="cursor_ai", help="Agent name")
    prompt_parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")

    # Stats command
    subparsers.add_parser("stats", help="Get injection statistics")

    # Test command
    subparsers.add_parser("test", help="Test the injector")

    args = parser.parse_args()

    injector = DynamicFewShotInjector()

    if args.command == "inject":
        result = injector.inject_episodic_context(query=args.query, agent=args.agent, context_type=args.context_type)

        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            print("🧠 Enhanced Query:")
            print(result["enhanced_query"])
            if result["episodic_context"]:
                print(
                    f"\n📊 Context: {result['injection_method']} method, "
                    f"{result['token_estimate']} tokens, "
                    f"{result['confidence_score']:.2f} confidence"
                )

    elif args.command == "enhance-prompt":
        enhanced_prompt = injector.enhance_system_prompt(
            base_prompt=args.prompt, current_task=args.task, agent=args.agent
        )

        if args.format == "json":
            print(json.dumps({"enhanced_prompt": enhanced_prompt}, indent=2))
        else:
            print("🧠 Enhanced System Prompt:")
            print(enhanced_prompt)

    elif args.command == "stats":
        stats = injector.get_injection_stats()
        if stats:
            print("📊 Injection Statistics:")
            print(f"   Total episodes: {stats.get('total_episodes', 0)}")
            print(f"   Unique agents: {stats.get('unique_agents', 0)}")
            print(f"   Unique task types: {stats.get('unique_task_types', 0)}")
            print(f"   Max tokens: {stats.get('injection_config', {}).get('max_tokens', 0)}")
            print(f"   Min confidence: {stats.get('injection_config', {}).get('min_confidence', 0)}")

    elif args.command == "test":
        print("🧪 Testing Dynamic Few-Shot Injector...")

        # Test different injection methods
        test_query = "implement error handling for database connections"

        for method in ["few_shot", "guidance", "compact"]:
            print(f"\n🔍 Testing {method} method:")
            result = injector.inject_episodic_context(test_query, context_type=method)

            if result["episodic_context"]:
                print(f"   ✅ Enhanced with {result['token_estimate']} tokens")
                print(f"   📊 Confidence: {result['confidence_score']:.2f}")
                print(f"   ⏱️  Time: {result['processing_time_ms']:.1f}ms")
            else:
                print("   ⚠️  No episodic context available")

        # Test system prompt enhancement
        print("\n🔍 Testing system prompt enhancement:")
        base_prompt = "You are a helpful AI assistant."
        enhanced = injector.enhance_system_prompt(base_prompt, test_query)

        if enhanced != base_prompt:
            print("   ✅ System prompt enhanced with episodic context")
        else:
            print("   ⚠️  No enhancement applied")

        print("\n✅ All tests completed")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
