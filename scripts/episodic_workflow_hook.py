#!/usr/bin/env python3
"""
Episodic Workflow Hook

Simple integration hook for existing workflows to automatically inject episodic context.
Can be used as a standalone script or imported into other tools.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after path modification
from scripts.dynamic_few_shot_injector import DynamicFewShotInjector


class EpisodicWorkflowHook:
    """Simple hook for injecting episodic context into workflows."""

    def __init__(self):
        """Initialize the hook."""
        self.injector = DynamicFewShotInjector()
        print("🧠 Episodic Workflow Hook initialized")

    def enhance_query(self, query: str, method: str = "guidance") -> str:
        """Enhance a query with episodic context."""
        result = self.injector.inject_episodic_context(query=query, context_type=method)
        return result["enhanced_query"]

    def enhance_system_prompt(self, prompt: str, task: str) -> str:
        """Enhance a system prompt with episodic context."""
        return self.injector.enhance_system_prompt(prompt, task)

    def store_completion(
        self,
        task_description: str,
        input_text: str,
        output_text: str,
        agent: str = "cursor_ai",
        task_type: str = "general",
    ) -> bool:
        """Store a task completion for future learning."""
        return self.injector.episodic_integration.on_task_completion(
            task_description=task_description,
            input_text=input_text,
            output_text=output_text,
            agent=agent,
            task_type=task_type,
        )

    def get_context_for_task(self, task_description: str, agent: str = "cursor_ai") -> dict[str, Any] | None:
        """Get episodic context for a task."""
        return self.injector.episodic_integration.get_context_for_task(task_description, agent)


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Episodic Workflow Hook")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Enhance query command
    enhance_parser = subparsers.add_parser("enhance", help="Enhance query with episodic context")
    enhance_parser.add_argument("--query", required=True, help="Query to enhance")
    enhance_parser.add_argument(
        "--method", choices=["few_shot", "guidance", "compact"], default="guidance", help="Enhancement method"
    )
    enhance_parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")

    # Enhance prompt command
    prompt_parser = subparsers.add_parser("enhance-prompt", help="Enhance system prompt")
    prompt_parser.add_argument("--prompt", required=True, help="System prompt to enhance")
    prompt_parser.add_argument("--task", required=True, help="Current task description")
    prompt_parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")

    # Store completion command
    store_parser = subparsers.add_parser("store", help="Store task completion")
    store_parser.add_argument("--task-description", required=True, help="Task description")
    store_parser.add_argument("--input-text", required=True, help="Input text")
    store_parser.add_argument("--output-text", required=True, help="Output text")
    store_parser.add_argument("--agent", default="cursor_ai", help="Agent name")
    store_parser.add_argument("--task-type", default="general", help="Task type")

    # Get context command
    context_parser = subparsers.add_parser("context", help="Get episodic context for task")
    context_parser.add_argument("--task", required=True, help="Task description")
    context_parser.add_argument("--agent", default="cursor_ai", help="Agent name")
    context_parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")

    # Test command
    subparsers.add_parser("test", help="Test the hook")

    args = parser.parse_args()

    hook = EpisodicWorkflowHook()

    if args.command == "enhance":
        enhanced_query = hook.enhance_query(args.query, args.method)

        if args.format == "json":
            result = {"original_query": args.query, "enhanced_query": enhanced_query, "method": args.method}
            print(json.dumps(result, indent=2))
        else:
            print("🧠 Enhanced Query:")
            print(enhanced_query)

    elif args.command == "enhance-prompt":
        enhanced_prompt = hook.enhance_system_prompt(args.prompt, args.task)

        if args.format == "json":
            result = {"original_prompt": args.prompt, "enhanced_prompt": enhanced_prompt, "task": args.task}
            print(json.dumps(result, indent=2))
        else:
            print("🧠 Enhanced System Prompt:")
            print(enhanced_prompt)

    elif args.command == "store":
        success = hook.store_completion(
            task_description=args.task_description,
            input_text=args.input_text,
            output_text=args.output_text,
            agent=args.agent,
            task_type=args.task_type,
        )

        if success:
            print("✅ Task completion stored successfully")
        else:
            print("❌ Failed to store task completion")
            sys.exit(1)

    elif args.command == "context":
        context = hook.get_context_for_task(args.task, args.agent)

        if args.format == "json":
            print(json.dumps(context, indent=2, default=str))
        else:
            if context:
                episodic = context["episodic_context"]
                print(f"🧠 Episodic Context (confidence: {episodic['confidence_score']:.2f}):")
                print(f"   Similar episodes: {len(episodic['similar_episodes'])}")
                print(f"   What worked: {len(episodic['what_worked_bullets'])} items")
                print(f"   What to avoid: {len(episodic['what_to_avoid_bullets'])} items")
            else:
                print("🧠 No episodic context available")

    elif args.command == "test":
        print("🧪 Testing Episodic Workflow Hook...")

        # Test query enhancement
        test_query = "implement error handling for database connections"
        enhanced = hook.enhance_query(test_query, "guidance")

        if enhanced != test_query:
            print("✅ Query enhancement test passed")
        else:
            print("⚠️  No query enhancement applied")

        # Test prompt enhancement
        base_prompt = "You are a helpful AI assistant."
        enhanced_prompt = hook.enhance_system_prompt(base_prompt, test_query)

        if enhanced_prompt != base_prompt:
            print("✅ Prompt enhancement test passed")
        else:
            print("⚠️  No prompt enhancement applied")

        # Test context retrieval
        context = hook.get_context_for_task(test_query)
        if context:
            print("✅ Context retrieval test passed")
        else:
            print("⚠️  No context retrieved")

        # Test task completion storage
        success = hook.store_completion(
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

        print("✅ All tests completed")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
