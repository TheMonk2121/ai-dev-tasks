from __future__ import annotations

import json

#!/usr/bin/env python3
"""
Refine Glob Patterns in Gold Cases
"""


def refine_glob_patterns():
    """Replace overly broad glob patterns with specific ones."""
    # Load gold cases
    with open("evals/gold/v1/gold_cases.jsonl") as f:
        cases = [json.loads(line) for line in f if line.strip()]

    # Define glob pattern refinements
    glob_refinements = {
        "**/*.md": {
            "guide_queries": "400_guides/*.md",
            "memory_queries": "100_memory/*.md",
            "core_queries": "000_core/*.md",
            "setup_queries": "200_setup/*.md",
            "research_queries": "500_research/*.md",
        }
    }

    changes_made = 0

    for case in cases:
        query = case.get("query", "")
        globs = case.get("globs", [])

        if "**/*.md" in globs:
            # Determine appropriate pattern based on query content
            if any(keyword in query.lower() for keyword in ["guide", "400_", "documentation"]):
                new_pattern = "400_guides/*.md"
            elif any(keyword in query.lower() for keyword in ["memory", "100_", "context"]):
                new_pattern = "100_memory/*.md"
            elif any(keyword in query.lower() for keyword in ["core", "000_", "workflow", "backlog"]):
                new_pattern = "000_core/*.md"
            elif any(keyword in query.lower() for keyword in ["setup", "200_", "configuration"]):
                new_pattern = "200_setup/*.md"
            elif any(keyword in query.lower() for keyword in ["research", "500_", "analysis"]):
                new_pattern = "500_research/*.md"
            else:
                new_pattern = "400_guides/*.md"  # Default to guides

            # Replace the pattern
            case["globs"] = [new_pattern if g == "**/*.md" else g for g in globs]
            changes_made += 1
            print(f"Refined glob pattern for: '{query}' → {new_pattern}")

    # Save updated cases
    with open("evals/gold/v1/gold_cases.jsonl", "w") as f:
        for case in cases:
            f.write(json.dumps(case) + "\n")

    print(f"\n✅ Refined {changes_made} glob patterns")


if __name__ == "__main__":
    refine_glob_patterns()
