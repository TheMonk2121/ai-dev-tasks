from __future__ import annotations
import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any
from scripts.unified_memory_orchestrator import UnifiedMemoryOrchestrator  # noqa: E402
    from scripts.dynamic_few_shot_injector import DynamicFewShotInjector
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Enhanced Memory Orchestrator with Episodic Context

Extends the unified memory orchestrator with dynamic episodic context injection.
Provides intelligent context enhancement for improved task performance.
"""

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the base orchestrator after path setup

# Import episodic components
try:

    EPISODIC_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Could not import episodic components: {e}")
    EPISODIC_AVAILABLE = False

class EnhancedMemoryOrchestrator(UnifiedMemoryOrchestrator):
    """Enhanced memory orchestrator with episodic context injection."""

    def __init__(self):
        """Initialize the enhanced orchestrator."""
        super().__init__()

        if EPISODIC_AVAILABLE:
            self.episodic_injector = DynamicFewShotInjector()
            print("🧠 Episodic context injection enabled")
        else:
            self.episodic_injector = None
            print("⚠️  Episodic context injection disabled")

    def get_enhanced_context(
        self,
        systems: list[str],
        role: str = "planner",
        query: str = "",
        include_episodic: bool = True,
        context_type: str = "guidance",
    ) -> dict[str, Any]:
        """Get enhanced context with episodic memory injection."""
        start_time = time.time()

        # Get base context from parent orchestrator
        base_context = self.orchestrate_memory(
            query=query,
            role=role,
            include_ltst="ltst" in systems,
            include_cursor="cursor" in systems,
            include_go="go_cli" in systems,
            include_prime="prime" in systems,
        )

        if not include_episodic or not self.episodic_injector:
            return base_context

        try:
            # Enhance with episodic context
            enhanced_result = self.episodic_injector.inject_episodic_context(
                query=query or f"{role} task", agent="cursor_ai", context_type=context_type
            )

            # Add episodic enhancement to results
            base_context["episodic_enhancement"] = {
                "injected": enhanced_result["episodic_context"] is not None,
                "method": enhanced_result["injection_method"],
                "confidence": enhanced_result.get("confidence_score", 0.0),
                "token_estimate": enhanced_result.get("token_estimate", 0),
                "processing_time_ms": enhanced_result.get("processing_time_ms", 0),
            }

            # If we have episodic context, enhance the main context
            if enhanced_result["episodic_context"]:
                episodic = enhanced_result["episodic_context"]

                # Add episodic section to the main context
                episodic_section = "\n\n## 🧠 Episodic Memory Context\n"
                episodic_section += f"*Based on {len(episodic['similar_episodes'])} similar episodes "
                episodic_section += f"(confidence: {episodic['confidence_score']:.2f})*\n\n"

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

                # Add to the main context bundle
                if "context_bundle" in base_context:
                    base_context["context_bundle"] += episodic_section

                # Update timing
                base_context["total_time_ms"] = (time.time() - start_time) * 1000

                print(f"🧠 Enhanced context with episodic memory (confidence: {episodic['confidence_score']:.2f})")

            return base_context

        except Exception as e:
            print(f"❌ Failed to enhance context with episodic memory: {e}")
            return base_context

    def enhance_system_prompt_with_episodic(self, base_prompt: str, current_task: str, agent: str = "cursor_ai") -> str:
        """Enhance a system prompt with episodic context."""
        if not self.episodic_injector:
            return base_prompt

        return self.episodic_injector.enhance_system_prompt(base_prompt, current_task, agent)

    def store_task_completion(
        self,
        task_description: str,
        input_text: str,
        output_text: str,
        agent: str = "cursor_ai",
        task_type: str = "general",
        outcome_metrics: dict[str, Any] | None = None,
        source_refs: dict[str, Any] | None = None,
    ) -> bool:
        """Store a task completion for future episodic learning."""
        if not self.episodic_injector:
            print("⚠️  Episodic storage not available")
            return False

        try:
            # Use the episodic integration to store the completion
            success = self.episodic_injector.episodic_integration.on_task_completion(
                task_description=task_description,
                input_text=input_text,
                output_text=output_text,
                agent=agent,
                task_type=task_type,
                outcome_metrics=outcome_metrics,
                source_refs=source_refs,
            )

            if success:
                print(f"✅ Stored episodic reflection for: {task_description[:50]}...")

            return success

        except Exception as e:
            print(f"❌ Failed to store task completion: {e}")
            return False

    def get_episodic_stats(self) -> dict[str, Any]:
        """Get statistics about episodic memory usage."""
        if not self.episodic_injector:
            return {"error": "Episodic injector not available"}

        return self.episodic_injector.get_injection_stats()

def main():
    """Main CLI interface for enhanced memory orchestrator."""
    parser = argparse.ArgumentParser(description="Enhanced Memory Orchestrator with Episodic Context")

    # Base orchestrator arguments
    parser.add_argument(
        "--systems",
        nargs="+",
        choices=["ltst", "cursor", "go_cli", "prime"],
        default=["ltst", "cursor"],
        help="Memory systems to activate",
    )
    parser.add_argument(
        "--role",
        default="planner",
        choices=["planner", "implementer", "researcher", "coder"],
        help="Role for context enhancement",
    )
    parser.add_argument("--query", default="", help="Query or task description for episodic enhancement")

    # Episodic enhancement arguments
    parser.add_argument(
        "--include-episodic", action="store_true", default=True, help="Include episodic context enhancement"
    )
    parser.add_argument(
        "--context-type",
        choices=["few_shot", "guidance", "compact"],
        default="guidance",
        help="Episodic context injection method",
    )
    parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")

    # Task completion arguments
    parser.add_argument(
        "--store-completion", action="store_true", help="Store current task as completed for episodic learning"
    )
    parser.add_argument("--task-description", help="Task description for storage")
    parser.add_argument("--input-text", help="Input text for storage")
    parser.add_argument("--output-text", help="Output text for storage")
    parser.add_argument("--task-type", default="general", help="Task type for storage")
    parser.add_argument("--agent", default="cursor_ai", help="Agent name")

    # Stats and testing
    parser.add_argument("--stats", action="store_true", help="Show episodic memory statistics")
    parser.add_argument("--test", action="store_true", help="Test episodic enhancement")

    args = parser.parse_args()

    # Initialize enhanced orchestrator
    orchestrator = EnhancedMemoryOrchestrator()

    # Handle task completion storage
    if args.store_completion:
        if not args.task_description or not args.input_text or not args.output_text:
            print("❌ --task-description, --input-text, and --output-text are required for --store-completion")
            sys.exit(1)

        success = orchestrator.store_task_completion(
            task_description=args.task_description,
            input_text=args.input_text,
            output_text=args.output_text,
            agent=args.agent,
            task_type=args.task_type,
        )
        sys.exit(0 if success else 1)

    # Handle stats
    if args.stats:
        stats = orchestrator.get_episodic_stats()
        if args.format == "json":
            print(json.dumps(stats, indent=2))
        else:
            print("📊 Episodic Memory Statistics:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
        return

    # Handle testing
    if args.test:
        print("🧪 Testing Enhanced Memory Orchestrator...")

        # Test episodic enhancement
        test_query = "implement error handling for database connections"
        enhanced_context = orchestrator.get_enhanced_context(
            systems=args.systems,
            role=args.role,
            query=test_query,
            include_episodic=True,
            context_type=args.context_type,
        )

        if enhanced_context.get("episodic_enhancement", {}).get("injected"):
            print("✅ Episodic enhancement test passed")
            enhancement = enhanced_context["episodic_enhancement"]
            print(f"   Method: {enhancement['method']}")
            print(f"   Confidence: {enhancement['confidence']:.2f}")
            print(f"   Tokens: {enhancement['token_estimate']}")
        else:
            print("⚠️  No episodic enhancement applied")

        # Test system prompt enhancement
        base_prompt = "You are a helpful AI assistant."
        enhanced_prompt = orchestrator.enhance_system_prompt_with_episodic(base_prompt, test_query)

        if enhanced_prompt != base_prompt:
            print("✅ System prompt enhancement test passed")
        else:
            print("⚠️  No system prompt enhancement applied")

        print("✅ All tests completed")
        return

    # Get enhanced context
    enhanced_context = orchestrator.get_enhanced_context(
        systems=args.systems,
        role=args.role,
        query=args.query,
        include_episodic=args.include_episodic,
        context_type=args.context_type,
    )

    # Output results
    if args.format == "json":
        print(json.dumps(enhanced_context, indent=2, default=str))
    else:
        # Format for easy copying into Cursor chat
        print("🧠 Enhanced Memory Context Bundle")
        print("=" * 50)

        if "context_bundle" in enhanced_context:
            print(enhanced_context["context_bundle"])

        # Show episodic enhancement info
        if enhanced_context.get("episodic_enhancement"):
            enhancement = enhanced_context["episodic_enhancement"]
            print(f"\n🧠 Episodic Enhancement: {enhancement['method']} method")
            print(f"   Confidence: {enhancement['confidence']:.2f}")
            print(f"   Tokens: {enhancement['token_estimate']}")
            print(f"   Processing time: {enhancement['processing_time_ms']:.1f}ms")

        # Show system status
        if enhanced_context.get("system_status"):
            status = enhanced_context["system_status"]
            print("\n📊 System Status:")
            for system, info in status.items():
                status_icon = "✅" if info.get("active", False) else "❌"
                print(f"   {status_icon} {system}: {info.get('status', 'unknown')}")

if __name__ == "__main__":
    main()
