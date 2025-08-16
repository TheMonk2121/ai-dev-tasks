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
    parser.add_argument("--no-entity-expansion", action="store_true", help="Disable entity expansion")
    parser.add_argument("--max-tokens", type=int, default=6000, help="Maximum tokens (default: 6000)")
    parser.add_argument("--debug", action="store_true", help="Show debug information")

    args = parser.parse_args()

    print("🧠 Building memory rehydration bundle...")
    print(f"   Role: {args.role}")
    print(f"   Task: {args.task}")
    print(f"   Stability: {args.stability}")
    print(f"   RRF: {'disabled' if args.no_rrf else 'enabled'}")
    print(f"   Dedupe: {args.dedupe}")
    print(f"   Query expansion: {args.expand_query}")
    print(f"   Entity expansion: {'disabled' if args.no_entity_expansion else 'enabled'}")
    print()

    try:
        # Build the hydration bundle using new rehydrate function
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system", "src"))
        from utils.memory_rehydrator import rehydrate

        bundle = rehydrate(
            query=args.task,
            stability=args.stability,
            max_tokens=args.max_tokens,
            use_rrf=(not args.no_rrf),
            dedupe=args.dedupe,
            expand_query=args.expand_query,
            use_entity_expansion=(not args.no_entity_expansion),
            role=args.role,
        )

        # Format for Cursor
        formatted_text = format_bundle_for_cursor(bundle.text, bundle.meta)

        # Display the context
        print("=" * 80)
        print("🎯 CURSOR AI MEMORY REHYDRATION BUNDLE")
        print("=" * 80)
        print()
        print(formatted_text)
        print()
        print("=" * 80)
        print("📊 BUNDLE METADATA")
        print("=" * 80)
        print(f"Role: {bundle.meta.get('role', 'unknown')}")
        print(f"Task: {bundle.meta.get('task', 'unknown')}")
        print(f"Tokens: {bundle.meta.get('tokens_est', 'unknown')}")
        print(f"Sections: {bundle.meta.get('sections', 'unknown')}")
        print(f"Elapsed: {bundle.meta.get('elapsed_s', 'unknown')}s")
        print(f"Dense results: {bundle.meta.get('dense_count', 'unknown')}")
        print(f"Sparse results: {bundle.meta.get('sparse_count', 'unknown')}")
        print()
        print("💡 Copy the bundle text above into your Cursor conversation for context!")
        print("🔧 Next time, try: python3 scripts/cursor_memory_rehydrate.py [role] [task]")

    except Exception as e:
        print(f"❌ Error building bundle: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check POSTGRES_DSN environment variable")
        print("3. Verify database has document chunks")
        print("4. Try: python3 scripts/cursor_memory_rehydrate.py planner 'test'")
        sys.exit(1)


if __name__ == "__main__":
    main()
