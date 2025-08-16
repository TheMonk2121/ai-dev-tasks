#!/usr/bin/env python3
"""
Cursor Memory Rehydration Script
--------------------------------
Quick script for Cursor AI to get role-aware context from PostgreSQL database
instead of reading static markdown files.

Usage in Cursor:
1. Run this script to get context bundle
2. Copy the output into your conversation
3. Use the context for informed responses
"""

import os
import sys

# Add the dspy-rag-system src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system", "src"))

# Note: Import of memory_rehydrator functions moved to main() where they're actually used


def detect_role_from_task(task):
    """Automatically detect the most appropriate role based on task content"""
    task_lower = task.lower()

    # Role detection patterns
    planner_keywords = ["plan", "strategy", "priorit", "roadmap", "backlog", "sprint", "project"]
    implementer_keywords = ["code", "implement", "develop", "refactor", "debug", "test", "dspy", "technical"]
    researcher_keywords = ["research", "analyze", "study", "investigate", "explore", "compare"]

    planner_score = sum(1 for keyword in planner_keywords if keyword in task_lower)
    implementer_score = sum(1 for keyword in implementer_keywords if keyword in task_lower)
    researcher_score = sum(1 for keyword in researcher_keywords if keyword in task_lower)

    if researcher_score > max(planner_score, implementer_score):
        return "researcher"
    elif implementer_score > planner_score:
        return "implementer"
    else:
        return "planner"


def format_bundle_for_cursor(bundle_text, metadata):
    """Format the bundle for easy copying into Cursor chat"""
    lines = bundle_text.split("\n")
    formatted_lines = []

    for line in lines:
        # Clean up span source markers for better readability
        if line.startswith("[SPAN SOURCE]"):
            continue
        if line.startswith("— Doc ") and "chars" in line:
            continue
        if line.strip() == "":
            continue

        formatted_lines.append(line)

    return "\n".join(formatted_lines)


def main():
    """Build and display a memory rehydration bundle for Cursor AI"""

    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(description="Cursor Memory Rehydration with Kill-Switches")
    parser.add_argument(
        "role",
        nargs="?",
        default="planner",
        choices=["planner", "implementer", "researcher"],
        help="Role for context filtering",
    )
    parser.add_argument(
        "task",
        nargs="?",
        default="general project context and current state",
        help="Task description for semantic search",
    )
    parser.add_argument(
        "--stability",
        type=float,
        default=float(os.getenv("REHYDRATE_STABILITY", "0.6")),
        help="Stability knob (0.0-1.0, default 0.6)",
    )
    parser.add_argument("--no-rrf", action="store_true", help="Disable BM25+RRF fusion (pure vector similarity)")
    parser.add_argument(
        "--dedupe",
        choices=["file", "file+overlap"],
        default=os.getenv("REHYDRATE_DEDUPE", "file+overlap"),
        help="Deduplication mode (default: file+overlap)",
    )
    parser.add_argument(
        "--expand-query",
        choices=["off", "auto"],
        default=os.getenv("REHYDRATE_EXPAND_QUERY", "auto"),
        help="Query expansion mode (default: auto)",
    )
    parser.add_argument(
        "--no-entity-expansion",
        action="store_true",
        help="Disable entity-aware context expansion",
    )
    parser.add_argument(
        "--few-shot-scaffolding",
        action="store_true",
        default=True,
        help="Enable few-shot cognitive scaffolding (default: True)",
    )
    parser.add_argument(
        "--no-few-shot-scaffolding",
        action="store_true",
        help="Disable few-shot cognitive scaffolding",
    )

    args = parser.parse_args()

    # Import memory rehydrator functions
    try:
        from utils.memory_rehydrator import rehydrate
    except ImportError:
        print("❌ Error: Could not import memory_rehydrator module")
        print("Make sure you're running from the project root directory")
        sys.exit(1)

    # Auto-detect role if not specified
    if args.role == "planner" and args.task != "general project context and current state":
        detected_role = detect_role_from_task(args.task)
        if detected_role != "planner":
            print(f"🤖 Auto-detected role: {detected_role} (was: {args.role})")
            args.role = detected_role

    # Build the memory bundle
    print(f"🧠 Building memory bundle for {args.role} role...")
    print(f"📋 Task: {args.task}")
    print(f"⚙️  Configuration: stability={args.stability}, dedupe={args.dedupe}, expand-query={args.expand_query}")

    try:
        bundle = rehydrate(
            query=args.task,
            stability=args.stability,
            use_rrf=not args.no_rrf,
            dedupe=args.dedupe,
            expand_query=args.expand_query,
            use_entity_expansion=not args.no_entity_expansion,
            role=args.role,
        )

        # Apply few-shot cognitive scaffolding if enabled
        if args.few_shot_scaffolding and not args.no_few_shot_scaffolding:
            try:
                from few_shot_cognitive_scaffolding import FewShotCognitiveScaffolding

                scaffolding = FewShotCognitiveScaffolding()
                scaffold = scaffolding.create_cognitive_scaffold(args.role, args.task, "Base context")
                bundle_text = scaffolding.inject_into_memory_rehydration(scaffold, bundle.text)
                print(f"🎯 Applied few-shot cognitive scaffolding with {len(scaffold.few_shot_examples)} examples")
            except ImportError:
                print("⚠️  Few-shot scaffolding module not available, continuing without it")
                bundle_text = bundle.text
            except Exception as e:
                print(f"⚠️  Few-shot scaffolding failed: {e}, continuing without it")
                bundle_text = bundle.text
        else:
            bundle_text = bundle.text

        # Format the bundle for Cursor
        formatted_bundle = format_bundle_for_cursor(bundle_text, bundle.meta)

        # Display the bundle
        print("\n" + "=" * 80)
        print("🧠 MEMORY REHYDRATION BUNDLE")
        print("=" * 80)
        print("Copy the content below into your Cursor conversation:")
        print("=" * 80)
        print(formatted_bundle)
        print("=" * 80)
        print("📊 Bundle Statistics:")
        print(f"   • Total chunks: {bundle.meta.get('total_chunks', 'N/A')}")
        print(f"   • Bundle size: {len(formatted_bundle)} characters")
        print(f"   • Processing time: {bundle.meta.get('processing_time', 'N/A')}s")
        print(f"   • Role: {args.role}")
        print(f"   • Task: {args.task}")

    except Exception as e:
        print(f"❌ Error building memory bundle: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
