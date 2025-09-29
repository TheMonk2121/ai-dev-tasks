from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional, Union

from scripts.utilities.memory.episodic_memory_mock import MockEpisodicReflectionStore

#!/usr/bin/env python3
"""
Episodic Workflow Integration

Integrates episodic memory with existing workflow systems.
Provides hooks for task completion and context retrieval.
"""

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after path modification

class EpisodicWorkflowIntegration:
    """Integrates episodic memory with existing workflows."""

    def __init__(self):
        """Initialize the integration."""
        self.store = MockEpisodicReflectionStore()
        print("🧠 Episodic Memory Integration initialized (mock mode)")

    def on_task_completion(
        self,
        task_description: str,
        input_text: str,
        output_text: str,
        agent: str = "cursor_ai",
        task_type: str = "general",
        outcome_metrics: dict[str, Any] | None = None,
        source_refs: dict[str, Any] | None = None,
    ) -> bool:
        """Hook called when a task is completed."""
        try:
            reflection = self.store.generate_reflection_from_task(
                task_description=task_description,
                input_text=input_text,
                output_text=output_text,
                agent=agent,
                task_type=task_type,
                outcome_metrics=outcome_metrics,
                source_refs=source_refs,
            )

            success = self.store.store_reflection(reflection)
            if success:
                print(f"✅ Stored episodic reflection for: {task_description[:50]}...")
            return success

        except Exception as e:
            print(f"❌ Failed to store task completion: {e}")
            return False

    def get_context_for_task(self, task_description: str, agent: str | None = None) -> dict[str, Any] | None:
        """Get episodic context for a new task."""
        try:
            context = self.store.get_episodic_context(task_description, agent)

            if context.similar_episodes:
                print(f"🧠 Found {len(context.similar_episodes)} similar episodes")
                print(f"   What worked: {len(context.what_worked_bullets)} items")
                print(f"   What to avoid: {len(context.what_to_avoid_bullets)} items")
                print(f"   Confidence: {context.confidence_score:.2f}")

                # Format for use in prompts
                formatted_context = {
                    "episodic_context": {
                        "similar_episodes": [
                            {
                                "summary": episode.summary,
                                "what_worked": episode.what_worked,
                                "what_to_avoid": episode.what_to_avoid,
                                "task_type": episode.task_type,
                            }
                            for episode in context.similar_episodes
                        ],
                        "what_worked_bullets": context.what_worked_bullets,
                        "what_to_avoid_bullets": context.what_to_avoid_bullets,
                        "confidence_score": context.confidence_score,
                    }
                }

                return formatted_context
            else:
                print("🧠 No similar episodes found")
                return None

        except Exception as e:
            print(f"❌ Failed to get episodic context: {e}")
            return None

    def format_for_prompt(self, context: dict[str, Any]) -> str:
        """Format episodic context for inclusion in prompts."""
        if not context or "episodic_context" not in context:
            return ""

        episodic = context["episodic_context"]

        prompt_section = "## 🧠 Episodic Memory Context\n\n"

        if episodic["what_worked_bullets"]:
            prompt_section += "**What worked in similar tasks:**\n"
            for item in episodic["what_worked_bullets"]:
                prompt_section += f"- {item}\n"
            prompt_section += "\n"

        if episodic["what_to_avoid_bullets"]:
            prompt_section += "**What to avoid in similar tasks:**\n"
            for item in episodic["what_to_avoid_bullets"]:
                prompt_section += f"- {item}\n"
            prompt_section += "\n"

        if episodic["similar_episodes"]:
            prompt_section += f"**Based on {len(episodic['similar_episodes'])} similar episodes** (confidence: {episodic['confidence_score']:.2f})\n\n"

        return prompt_section

def main():
    """Main CLI interface for episodic workflow integration."""
    parser = argparse.ArgumentParser(description="Episodic Workflow Integration")
    parser.add_argument("command", choices=["complete", "context", "test"], help="Command to execute")
    parser.add_argument("--task-description", help="Task description")
    parser.add_argument("--input-text", help="Input text for completion")
    parser.add_argument("--output-text", help="Output text for completion")
    parser.add_argument("--agent", default="cursor_ai", help="Agent name")
    parser.add_argument("--task-type", default="general", help="Task type")
    parser.add_argument("--format", choices=["json", "prompt"], default="prompt", help="Output format")

    args = parser.parse_args()

    integration = EpisodicWorkflowIntegration()

    if args.command == "complete":
        if not args.task_description or not args.input_text or not args.output_text:
            print("❌ --task-description, --input-text, and --output-text are required for complete command")
            sys.exit(1)

        success = integration.on_task_completion(
            task_description=args.task_description,
            input_text=args.input_text,
            output_text=args.output_text,
            agent=args.agent,
            task_type=args.task_type,
        )
        sys.exit(0 if success else 1)

    elif args.command == "context":
        if not args.task_description:
            print("❌ --task-description is required for context command")
            sys.exit(1)

        context = integration.get_context_for_task(args.task_description, args.agent)
        if context:
            if args.format == "json":
                print(json.dumps(context, indent=2))
            else:
                prompt_text = integration.format_for_prompt(context)
                print(prompt_text)
        else:
            print("No episodic context available")

    elif args.command == "test":
        print("🧪 Testing episodic workflow integration...")

        # Test task completion
        success = integration.on_task_completion(
            task_description="Test episodic memory integration",
            input_text="Test input for integration",
            output_text="Test output for integration",
            agent="test_agent",
            task_type="testing",
        )

        if success:
            print("✅ Task completion test passed")

            # Test context retrieval
            context = integration.get_context_for_task("test episodic memory", "test_agent")
            if context:
                print("✅ Context retrieval test passed")
                prompt_text = integration.format_for_prompt(context)
                print("📝 Formatted prompt:")
                print(prompt_text)
            else:
                print("⚠️  Context retrieval test - no context found")
        else:
            print("❌ Task completion test failed")
            sys.exit(1)

if __name__ == "__main__":
    main()
