from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional, Union

# FIXME: Update this import path after reorganization
# from scripts.enhanced_memory_orchestrator_with_heuristics import EnhancedMemoryOrchestratorWithHeuristics

#!/usr/bin/env python3
"""
Episodic Memory System - Complete Integration

Complete episodic memory system with all three phases:
1. Episodic Reflection Store
2. Dynamic Few-Shot from Episodes
3. Procedural Heuristics Pack

This is the main entry point for the complete episodic memory system.
"""

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after path modification

class EpisodicMemorySystem:
    """Complete episodic memory system with all three phases."""

    def __init__(self):
        """Initialize the complete episodic memory system."""
        self.orchestrator = EnhancedMemoryOrchestratorWithHeuristics()
        print("🧠 Episodic Memory System initialized (all phases)")

    def get_enhanced_context(
        self,
        systems: list[str] | None = None,
        role: str = "planner",
        query: str = "",
        include_episodic: bool = True,
        include_heuristics: bool = True,
        context_type: str = "guidance",
    ) -> dict[str, Any]:
        """Get fully enhanced context with episodic memory and heuristics."""
        if systems is None:
            systems = ["ltst", "cursor"]

        return self.orchestrator.get_enhanced_context_with_heuristics(
            systems=systems,
            role=role,
            query=query,
            include_episodic=include_episodic,
            include_heuristics=include_heuristics,
            context_type=context_type,
            regenerate_heuristics=False,
        )

    def enhance_system_prompt(self, base_prompt: str, current_task: str, agent: str = "cursor_ai") -> str:
        """Enhance a system prompt with episodic context and heuristics."""
        return self.orchestrator.enhance_system_prompt_with_heuristics(
            base_prompt=base_prompt, current_task=current_task, agent=agent, regenerate_heuristics=False
        )

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
        return self.orchestrator.store_task_completion(
            task_description=task_description,
            input_text=input_text,
            output_text=output_text,
            agent=agent,
            task_type=task_type,
            outcome_metrics=outcome_metrics,
            source_refs=source_refs,
        )

    def regenerate_heuristics(self, agent: str = "cursor_ai") -> bool:
        """Regenerate heuristics pack from current episodic data."""
        pack = self.orchestrator.regenerate_heuristics_pack(agent)
        return pack is not None

    def get_system_stats(self) -> dict[str, Any]:
        """Get comprehensive system statistics."""
        stats = {
            "episodic_stats": self.orchestrator.get_episodic_stats(),
            "heuristics_stats": self.orchestrator.get_heuristics_stats(),
        }
        return stats

    def save_heuristics_pack(self, output_path: str, agent: str = "cursor_ai") -> bool:
        """Save current heuristics pack to file."""
        return self.orchestrator.save_heuristics_pack(output_path, agent)

    def load_heuristics_pack(self, input_path: str) -> bool:
        """Load heuristics pack from file."""
        return self.orchestrator.load_heuristics_pack(input_path)

def main():
    """Main CLI interface for the complete episodic memory system."""
    parser = argparse.ArgumentParser(description="Episodic Memory System - Complete Integration")

    # Context enhancement
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
    parser.add_argument("--query", default="", help="Query or task description for enhancement")
    parser.add_argument(
        "--context-type",
        choices=["few_shot", "guidance", "compact"],
        default="guidance",
        help="Episodic context injection method",
    )
    parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")

    # Task completion
    parser.add_argument("--store-completion", action="store_true", help="Store current task as completed for learning")
    parser.add_argument("--task-description", help="Task description for storage")
    parser.add_argument("--input-text", help="Input text for storage")
    parser.add_argument("--output-text", help="Output text for storage")
    parser.add_argument("--task-type", default="general", help="Task type for storage")
    parser.add_argument("--agent", default="cursor_ai", help="Agent name")

    # Heuristics management
    parser.add_argument(
        "--regenerate-heuristics", action="store_true", help="Regenerate heuristics pack from current data"
    )
    parser.add_argument("--save-heuristics", help="Save heuristics pack to file")
    parser.add_argument("--load-heuristics", help="Load heuristics pack from file")

    # System information
    parser.add_argument("--stats", action="store_true", help="Show system statistics")
    parser.add_argument("--test", action="store_true", help="Test the complete system")

    args = parser.parse_args()

    # Initialize system
    system = EpisodicMemorySystem()

    # Handle heuristics management
    if args.save_heuristics:
        success = system.save_heuristics_pack(args.save_heuristics, args.agent)
        sys.exit(0 if success else 1)

    if args.load_heuristics:
        success = system.load_heuristics_pack(args.load_heuristics)
        sys.exit(0 if success else 1)

    if args.regenerate_heuristics:
        success = system.regenerate_heuristics(args.agent)
        sys.exit(0 if success else 1)

    # Handle task completion storage
    if args.store_completion:
        if not args.task_description or not args.input_text or not args.output_text:
            print("❌ --task-description, --input-text, and --output-text are required for --store-completion")
            sys.exit(1)

        success = system.store_task_completion(
            task_description=args.task_description,
            input_text=args.input_text,
            output_text=args.output_text,
            agent=args.agent,
            task_type=args.task_type,
        )
        sys.exit(0 if success else 1)

    # Handle system statistics
    if args.stats:
        stats = system.get_system_stats()
        if args.format == "json":
            print(json.dumps(stats, indent=2, default=str))
        else:
            print("📊 Episodic Memory System Statistics:")
            print("\n🧠 Episodic Memory:")
            for key, value in stats["episodic_stats"].items():
                print(f"   {key}: {value}")
            print("\n🧠 Heuristics Pack:")
            for key, value in stats["heuristics_stats"].items():
                print(f"   {key}: {value}")
        return

    # Handle testing
    if args.test:
        print("🧪 Testing Complete Episodic Memory System...")

        # Test context enhancement
        test_query = "implement error handling for database connections"
        enhanced_context = system.get_enhanced_context(
            systems=args.systems,
            role=args.role,
            query=test_query,
            include_episodic=True,
            include_heuristics=True,
            context_type=args.context_type,
        )

        if enhanced_context.get("episodic_enhancement", {}).get("injected"):
            print("✅ Episodic enhancement test passed")
        else:
            print("⚠️  No episodic enhancement applied")

        if enhanced_context.get("heuristics_enhancement", {}).get("included"):
            print("✅ Heuristics enhancement test passed")
        else:
            print("⚠️  No heuristics enhancement applied")

        # Test system prompt enhancement
        base_prompt = "You are a helpful AI assistant."
        enhanced_prompt = system.enhance_system_prompt(base_prompt, test_query)

        if enhanced_prompt != base_prompt:
            print("✅ System prompt enhancement test passed")
        else:
            print("⚠️  No system prompt enhancement applied")

        # Test task completion storage
        success = system.store_task_completion(
            task_description="Test task completion",
            input_text="Test input",
            output_text="Test output",
            agent="test_agent",
            task_type="testing",
        )

        if success:
            print("✅ Task completion storage test passed")
        else:
            print("❌ Task completion storage test failed")

        # Test heuristics regeneration
        success = system.regenerate_heuristics("test_agent")
        if success:
            print("✅ Heuristics regeneration test passed")
        else:
            print("❌ Heuristics regeneration test failed")

        print("✅ All tests completed")
        return

    # Get enhanced context
    enhanced_context = system.get_enhanced_context(
        systems=args.systems,
        role=args.role,
        query=args.query,
        include_episodic=True,
        include_heuristics=True,
        context_type=args.context_type,
    )

    # Output results
    if args.format == "json":
        print(json.dumps(enhanced_context, indent=2, default=str))
    else:
        # Format for easy copying into Cursor chat
        print("🧠 Complete Episodic Memory System Context")
        print("=" * 50)

        if "context_bundle" in enhanced_context:
            print(enhanced_context["context_bundle"])

        # Show enhancement info
        if enhanced_context.get("episodic_enhancement"):
            enhancement = enhanced_context["episodic_enhancement"]
            print(f"\n🧠 Episodic Enhancement: {enhancement['method']} method")
            print(f"   Confidence: {enhancement['confidence']:.2f}")
            print(f"   Tokens: {enhancement['token_estimate']}")
            print(f"   Processing time: {enhancement['processing_time_ms']:.1f}ms")

        if enhanced_context.get("heuristics_enhancement"):
            enhancement = enhanced_context["heuristics_enhancement"]
            if enhancement.get("included"):
                print(f"\n🧠 Heuristics Enhancement: v{enhancement['version']}")
                print(f"   Heuristics: {enhancement['heuristics_count']}")
                print(f"   Categories: {enhancement['categories']}")
                print(f"   Episodes: {enhancement['total_episodes']}")
                print(f"   Processing time: {enhancement['processing_time_ms']:.1f}ms")
            else:
                print(f"\n🧠 Heuristics Enhancement: {enhancement.get('reason', 'not included')}")

        # Show system status
        if enhanced_context.get("system_status"):
            status = enhanced_context["system_status"]
            print("\n📊 System Status:")
            for system_name, info in status.items():
                status_icon = "✅" if info.get("active", False) else "❌"
                print(f"   {status_icon} {system_name}: {info.get('status', 'unknown')}")

if __name__ == "__main__":
    main()
