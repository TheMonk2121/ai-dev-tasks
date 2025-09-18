from __future__ import annotations

import json
import os
import sys

#!/usr/bin/env python3
"""
Diversify Query Patterns in Gold Cases
"""


def diversify_query_patterns():
    """Replace repetitive query patterns with varied ones."""
    # Load gold cases
    with open("evals/gold/v1/gold_cases.jsonl") as f:
        cases = [json.loads(line) for line in f if line.strip()]
    
    # Define pattern replacements
    pattern_replacements = {
        "What is the main purpose of 400_09_ai-frameworks-dspy.md?": "How do I integrate DSPy into my project?",
        "What is the main purpose of 000_backlog.md?": "How do I manage project priorities and backlog items?",
        "What is the main purpose of 400_11_performance-optimization.md?": "What are the RAGChecker performance metrics and how do I optimize them?",
        "What is the main purpose of 100_database-troubleshooting-patterns.md?": "How do I troubleshoot database issues in this project?",
        "What is the main purpose of 100_governance-by-code-insights.md?": "How does governance-by-code work in this project?",
        "What is the main purpose of 100_implementation-patterns-library.md?": "What implementation patterns are available in this project?",
        "What is the main purpose of 400_05_codebase-organization-patterns.md?": "How is the codebase organized and what patterns should I follow?",
        "What is the main purpose of 400_01_memory-system-architecture.md?": "How does the memory system architecture work?",
        "What is the main purpose of 400_08_task-management-workflows.md?": "How do I manage tasks and workflows in this project?",
        "What is the main purpose of 400_12_advanced-configurations.md?": "How do I configure advanced settings in this project?"
    }
    
    changes_made = 0
    
    for case in cases:
        query = result.get("key", "")
        
        if query in pattern_replacements:
            result.get("key", "")
            changes_made += 1
            print(f"Improved: '{query}' → '{result.get("key", "")
    
    # Save updated cases
    with open("evals/gold/v1/gold_cases.jsonl", "w") as f:
        for case in cases:
            f.write(json.dumps(case) + "\n")
    
    print(f"\n✅ Diversified {changes_made} query patterns")

if __name__ == "__main__":
    diversify_query_patterns()
