#!/usr/bin/env python3
"""
Episodic Memory Integration

Integrates episodic memory capabilities with existing workflows.
Provides hooks for task completion and context retrieval.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add dspy-rag-system to path
dspy_rag_path = project_root / "dspy-rag-system"
if str(dspy_rag_path) not in sys.path:
    sys.path.insert(0, str(dspy_rag_path))

try:
    from src.utils.episodic_reflection_store import EpisodicReflectionStore, create_episodic_reflections_table

    EPISODIC_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Could not import episodic reflection store: {e}")
    EPISODIC_AVAILABLE = False


class EpisodicMemoryIntegration:
    """Integrates episodic memory with existing workflows."""

    def __init__(self):
        """Initialize the integration."""
        self.store = None
        if EPISODIC_AVAILABLE:
            try:
                self.store = EpisodicReflectionStore()
            except Exception as e:
                print(f"⚠️  Could not initialize episodic store: {e}")

    def setup_database(self) -> bool:
        """Set up the episodic reflections table."""
        if not EPISODIC_AVAILABLE:
            print("❌ Episodic memory not available")
            return False

        try:
            success = create_episodic_reflections_table()
            if success:
                print("✅ Episodic reflections table created successfully")
            else:
                print("❌ Failed to create episodic reflections table")
            return success
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            return False

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
        """Store a reflection for a completed task."""
        if not self.store:
            print("❌ Episodic store not available")
            return False

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
                print(f"✅ Stored reflection for task: {task_description[:50]}...")
            else:
                print(f"❌ Failed to store reflection for task: {task_description[:50]}...")
            return success

        except Exception as e:
            print(f"❌ Task completion storage failed: {e}")
            return False

    def get_episodic_context(self, query: str, agent: str | None = None) -> dict[str, Any] | None:
        """Get episodic context for a query."""
        if not self.store:
            print("❌ Episodic store not available")
            return None

        try:
            context = self.store.get_episodic_context(query, agent)

            # Format for easy use in prompts
            formatted_context = {
                "similar_episodes": [
                    {
                        "summary": episode.summary,
                        "what_worked": episode.what_worked,
                        "what_to_avoid": episode.what_to_avoid,
                        "task_type": episode.task_type,
                        "created_at": episode.created_at.isoformat() if episode.created_at else None,
                    }
                    for episode in context.similar_episodes
                ],
                "what_worked_bullets": context.what_worked_bullets,
                "what_to_avoid_bullets": context.what_to_avoid_bullets,
                "confidence_score": context.confidence_score,
                "retrieval_time_ms": context.retrieval_time_ms,
            }

            print(f"✅ Retrieved episodic context with {len(context.similar_episodes)} episodes")
            print(f"   Confidence: {context.confidence_score:.2f}")
            print(f"   What worked: {len(context.what_worked_bullets)} items")
            print(f"   What to avoid: {len(context.what_to_avoid_bullets)} items")

            return formatted_context

        except Exception as e:
            print(f"❌ Episodic context retrieval failed: {e}")
            return None

    def get_stats(self) -> dict[str, Any] | None:
        """Get statistics about stored reflections."""
        if not self.store:
            print("❌ Episodic store not available")
            return None

        try:
            stats = self.store.get_stats()
            print("📊 Episodic Memory Statistics:")
            print(f"   Total reflections: {stats.get('total_reflections', 0)}")
            print(f"   Unique agents: {stats.get('unique_agents', 0)}")
            print(f"   Unique task types: {stats.get('unique_task_types', 0)}")
            print(f"   Avg what_worked items: {stats.get('avg_what_worked_items', 0):.1f}")
            print(f"   Avg what_to_avoid items: {stats.get('avg_what_to_avoid_items', 0):.1f}")
            return stats

        except Exception as e:
            print(f"❌ Stats retrieval failed: {e}")
            return None


def main():
    """Main CLI interface for episodic memory integration."""
    parser = argparse.ArgumentParser(description="Episodic Memory Integration")
    parser.add_argument("command", choices=["setup", "store", "retrieve", "stats"], help="Command to execute")
    parser.add_argument("--query", help="Query for retrieval")
    parser.add_argument("--agent", help="Agent name for filtering")
    parser.add_argument("--task-description", help="Task description for storage")
    parser.add_argument("--input-text", help="Input text for storage")
    parser.add_argument("--output-text", help="Output text for storage")
    parser.add_argument("--task-type", default="general", help="Task type for storage")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")

    args = parser.parse_args()

    integration = EpisodicMemoryIntegration()

    if args.command == "setup":
        success = integration.setup_database()
        sys.exit(0 if success else 1)

    elif args.command == "store":
        if not args.task_description or not args.input_text or not args.output_text:
            print("❌ --task-description, --input-text, and --output-text are required for store command")
            sys.exit(1)

        success = integration.store_task_completion(
            task_description=args.task_description,
            input_text=args.input_text,
            output_text=args.output_text,
            agent=args.agent or "cursor_ai",
            task_type=args.task_type,
        )
        sys.exit(0 if success else 1)

    elif args.command == "retrieve":
        if not args.query:
            print("❌ --query is required for retrieve command")
            sys.exit(1)

        context = integration.get_episodic_context(args.query, args.agent)
        if context:
            if args.format == "json":
                print(json.dumps(context, indent=2))
            else:
                print("📋 Episodic Context:")
                print(f"   Similar episodes: {len(context['similar_episodes'])}")
                print(f"   What worked: {context['what_worked_bullets']}")
                print(f"   What to avoid: {context['what_to_avoid_bullets']}")
                print(f"   Confidence: {context['confidence_score']:.2f}")
        else:
            sys.exit(1)

    elif args.command == "stats":
        stats = integration.get_stats()
        if stats and args.format == "json":
            print(json.dumps(stats, indent=2))
        sys.exit(0 if stats else 1)


if __name__ == "__main__":
    main()
