from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Optional, Union

# FIXME: Update this import path after reorganization
# from scripts.enhanced_memory_orchestrator import EnhancedMemoryOrchestrator
# FIXME: Update this import path after reorganization
# from scripts.heuristics_pack_generator import HeuristicsPack, HeuristicsPackGenerator

#!/usr/bin/env python3
"""
Enhanced Memory Orchestrator with Heuristics Pack

Extends the enhanced memory orchestrator with automatic heuristics pack generation
and integration into system prompts as operational guidance.
"""

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after path modification

# Import heuristics components
try:

    HEURISTICS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Could not import heuristics components: {e}")
    HEURISTICS_AVAILABLE = False


class EnhancedMemoryOrchestratorWithHeuristics(EnhancedMemoryOrchestrator):
    """Enhanced memory orchestrator with heuristics pack integration."""

    def __init__(self: Any):
        """Initialize the orchestrator with heuristics."""
        super().__init__()

        if HEURISTICS_AVAILABLE:
            self.heuristics_generator: Any = HeuristicsPackGenerator()
            self.current_heuristics_pack: Any = None
            print("🧠 Heuristics pack integration enabled")
        else:
            self.heuristics_generator: Any = None
            self.current_heuristics_pack: Any = None
            print("⚠️  Heuristics pack integration disabled")

    def get_enhanced_context_with_heuristics(
        self,
        systems: list[str],
        role: str = "planner",
        query: str = "",
        include_episodic: bool = True,
        include_heuristics: bool = True,
        context_type: str = "guidance",
        regenerate_heuristics: bool = False,
    ) -> dict[str, Any]:
        """Get enhanced context with both episodic memory and heuristics pack."""
        start_time: Any = time.time()

        # Get base enhanced context
        enhanced_context = self.get_enhanced_context(
            systems=systems, role=role, query=query, include_episodic=include_episodic, context_type=context_type
        )

        if not include_heuristics or not self.heuristics_generator:
            return enhanced_context

        try:
            # Generate or update heuristics pack if needed
            if regenerate_heuristics or self.current_heuristics_pack is None:
                self.current_heuristics_pack: Any = self.heuristics_generator.generate_heuristics_pack("cursor_ai")
                print(f"🧠 Generated heuristics pack: {len(self.current_heuristics_pack.heuristics)} heuristics")

            # Add heuristics to the context
            heuristics_section = self.heuristics_generator.format_heuristics_pack(
                self.current_heuristics_pack, "system_prompt"
            )

            if heuristics_section:
                # Add to the main context bundle
                if "context_bundle" in enhanced_context:
                    enhanced_context["context_bundle"] += heuristics_section

                # Add heuristics metadata
                enhanced_context["heuristics_enhancement"] = {
                    "included": True,
                    "version": self.current_heuristics_pack.version,
                    "heuristics_count": len(self.current_heuristics_pack.heuristics),
                    "categories": self.current_heuristics_pack.categories,
                    "total_episodes": self.current_heuristics_pack.total_episodes,
                    "processing_time_ms": (time.time() - start_time) * 1000,
                }

                print(f"🧠 Enhanced context with heuristics pack v{self.current_heuristics_pack.version}")
            else:
                enhanced_context["heuristics_enhancement"] = {
                    "included": False,
                    "reason": "no_heuristics_available",
                    "processing_time_ms": (time.time() - start_time) * 1000,
                }

            return enhanced_context

        except Exception as e:
            print(f"❌ Failed to enhance context with heuristics: {e}")
            enhanced_context["heuristics_enhancement"] = {
                "included": False,
                "reason": "error",
                "error": str(e),
                "processing_time_ms": (time.time() - start_time) * 1000,
            }
            return enhanced_context

    def enhance_system_prompt_with_heuristics(
        self, base_prompt: str, current_task: str, agent: str = "cursor_ai", regenerate_heuristics: bool = False
    ) -> str:
        """Enhance a system prompt with both episodic context and heuristics pack."""
        # Start with episodic enhancement
        enhanced_prompt: Any = self.enhance_system_prompt_with_episodic(base_prompt, current_task, agent)

        if not self.heuristics_generator:
            return enhanced_prompt

        try:
            # Generate or update heuristics pack if needed
            if regenerate_heuristics or self.current_heuristics_pack is None:
                self.current_heuristics_pack: Any = self.heuristics_generator.generate_heuristics_pack(agent)

            # Add heuristics to the prompt
            heuristics_section = self.heuristics_generator.format_heuristics_pack(
                self.current_heuristics_pack, "system_prompt"
            )

            if heuristics_section:
                enhanced_prompt += heuristics_section
                print(f"🧠 Enhanced system prompt with heuristics pack v{self.current_heuristics_pack.version}")

            return enhanced_prompt

        except Exception as e:
            print(f"❌ Failed to enhance system prompt with heuristics: {e}")
            return enhanced_prompt

    def regenerate_heuristics_pack(self, agent: str = "cursor_ai") -> HeuristicsPack | None:
        """Regenerate the heuristics pack for an agent."""
        if not self.heuristics_generator:
            print("⚠️  Heuristics generator not available")
            return None

        try:
            self.current_heuristics_pack: Any = self.heuristics_generator.generate_heuristics_pack(agent)
            print(
                f"✅ Regenerated heuristics pack for {agent}: {len(self.current_heuristics_pack.heuristics)} heuristics"
            )
            return self.current_heuristics_pack

        except Exception as e:
            print(f"❌ Failed to regenerate heuristics pack: {e}")
            return None

    def save_heuristics_pack(self, output_path: str, agent: str = "cursor_ai") -> bool:
        """Save the current heuristics pack to file."""
        if not self.heuristics_generator or not self.current_heuristics_pack:
            print("⚠️  No heuristics pack available to save")
            return False

        return self.heuristics_generator.save_heuristics_pack(self.current_heuristics_pack, output_path)

    def load_heuristics_pack(self, input_path: str) -> bool:
        """Load a heuristics pack from file."""
        if not self.heuristics_generator:
            print("⚠️  Heuristics generator not available")
            return False

        try:
            self.current_heuristics_pack: Any = self.heuristics_generator.load_heuristics_pack(input_path)
            if self.current_heuristics_pack:
                print(f"✅ Loaded heuristics pack v{self.current_heuristics_pack.version}")
                return True
            return False

        except Exception as e:
            print(f"❌ Failed to load heuristics pack: {e}")
            return False

    def get_heuristics_stats(self) -> dict[str, Any]:
        """Get statistics about the current heuristics pack."""
        if not self.current_heuristics_pack:
            return {"error": "No heuristics pack loaded"}

        return {
            "agent": self.current_heuristics_pack.agent,
            "version": self.current_heuristics_pack.version,
            "created_at": self.current_heuristics_pack.created_at.isoformat(),
            "updated_at": self.current_heuristics_pack.updated_at.isoformat(),
            "total_episodes": self.current_heuristics_pack.total_episodes,
            "heuristics_count": len(self.current_heuristics_pack.heuristics),
            "categories": self.current_heuristics_pack.categories,
            "confidence_threshold": self.current_heuristics_pack.confidence_threshold,
        }


def main() -> Any:
    """Main CLI interface for enhanced memory orchestrator with heuristics."""
    parser: Any = argparse.ArgumentParser(description="Enhanced Memory Orchestrator with Heuristics Pack")

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
    parser.add_argument("--query", default="", help="Query or task description for enhancement")

    # Enhancement arguments
    parser.add_argument(
        "--include-episodic", action="store_true", default=True, help="Include episodic context enhancement"
    )
    parser.add_argument(
        "--include-heuristics", action="store_true", default=True, help="Include heuristics pack enhancement"
    )
    parser.add_argument(
        "--context-type",
        choices=["few_shot", "guidance", "compact"],
        default="guidance",
        help="Episodic context injection method",
    )
    parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")

    # Heuristics-specific arguments
    parser.add_argument("--regenerate-heuristics", action="store_true", help="Regenerate heuristics pack")
    parser.add_argument("--save-heuristics", help="Save heuristics pack to file")
    parser.add_argument("--load-heuristics", help="Load heuristics pack from file")
    parser.add_argument("--heuristics-stats", action="store_true", help="Show heuristics pack statistics")

    # Task completion arguments
    parser.add_argument("--store-completion", action="store_true", help="Store current task as completed for learning")
    parser.add_argument("--task-description", help="Task description for storage")
    parser.add_argument("--input-text", help="Input text for storage")
    parser.add_argument("--output-text", help="Output text for storage")
    parser.add_argument("--task-type", default="general", help="Task type for storage")
    parser.add_argument("--agent", default="cursor_ai", help="Agent name")

    # Testing
    parser.add_argument("--test", action="store_true", help="Test the orchestrator with heuristics")

    args: Any = parser.parse_args()

    # Initialize orchestrator
    orchestrator = EnhancedMemoryOrchestratorWithHeuristics()

    # Handle heuristics-specific commands
    if args.save_heuristics:
        success: Any = orchestrator.save_heuristics_pack(args.save_heuristics, args.agent)
        sys.exit(0 if success else 1)

    if args.load_heuristics:
        success: Any = orchestrator.load_heuristics_pack(args.load_heuristics)
        sys.exit(0 if success else 1)

    if args.heuristics_stats:
        stats: Any = orchestrator.get_heuristics_stats()
        if args.format == "json":
            print(json.dumps(stats, indent=2, default=str))
        else:
            print("📊 Heuristics Pack Statistics:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
        return

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

    # Handle testing
    if args.test:
        print("🧪 Testing Enhanced Memory Orchestrator with Heuristics...")

        # Test heuristics generation
        pack: Any = orchestrator.regenerate_heuristics_pack(args.agent)
        if pack and pack.heuristics:
            print(f"✅ Heuristics generation test passed: {len(pack.heuristics)} heuristics")
        else:
            print("⚠️  No heuristics generated")

        # Test context enhancement with heuristics
        test_query = "implement error handling for database connections"
        enhanced_context = orchestrator.get_enhanced_context_with_heuristics(
            systems=args.systems,
            role=args.role,
            query=test_query,
            include_episodic=True,
            include_heuristics=True,
            context_type=args.context_type,
            regenerate_heuristics=True,
        )

        if enhanced_context.get("heuristics_enhancement", {}).get("included"):
            print("✅ Context enhancement with heuristics test passed")
            enhancement = enhanced_context["heuristics_enhancement"]
            print(f"   Version: {enhancement['version']}")
            print(f"   Heuristics: {enhancement['heuristics_count']}")
            print(f"   Categories: {enhancement['categories']}")
        else:
            print("⚠️  No heuristics enhancement applied")

        # Test system prompt enhancement
        base_prompt = "You are a helpful AI assistant."
        enhanced_prompt = orchestrator.enhance_system_prompt_with_heuristics(
            base_prompt, test_query, args.agent, regenerate_heuristics=True
        )

        if enhanced_prompt != base_prompt:
            print("✅ System prompt enhancement with heuristics test passed")
        else:
            print("⚠️  No system prompt enhancement applied")

        print("✅ All tests completed")
        return

    # Get enhanced context with heuristics
    enhanced_context = orchestrator.get_enhanced_context_with_heuristics(
        systems=args.systems,
        role=args.role,
        query=args.query,
        include_episodic=args.include_episodic,
        include_heuristics=args.include_heuristics,
        context_type=args.context_type,
        regenerate_heuristics=args.regenerate_heuristics,
    )

    # Output results
    if args.format == "json":
        print(json.dumps(enhanced_context, indent=2, default=str))
    else:
        # Format for easy copying into Cursor chat
        print("🧠 Enhanced Memory Context Bundle with Heuristics")
        print("=" * 60)

        if "context_bundle" in enhanced_context:
            print(enhanced_context["context_bundle"])

        # Show episodic enhancement info
        if enhanced_context.get("episodic_enhancement"):
            enhancement = enhanced_context["episodic_enhancement"]
            print(f"\n🧠 Episodic Enhancement: {enhancement['method']} method")
            print(f"   Confidence: {enhancement['confidence']:.2f}")
            print(f"   Tokens: {enhancement['token_estimate']}")
            print(f"   Processing time: {enhancement['processing_time_ms']:.1f}ms")

        # Show heuristics enhancement info
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
            for system, info in status.items():
                status_icon = "✅" if info.get("active", False) else "❌"
                print(f"   {status_icon} {system}: {info.get('status', 'unknown')}")


if __name__ == "__main__":
    main()
