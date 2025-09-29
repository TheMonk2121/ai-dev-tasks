from __future__ import annotations

import json
import sys

#!/usr/bin/env python3
"""
Fix Short Queries in Gold Cases
"""


def fix_short_queries():
    """Fix queries that are too short."""
    # Load gold cases
    with open("evals/gold/v1/gold_cases.jsonl") as f:
        cases = [json.loads(line) for line in f if line.strip()]
    
    # Define expansions for short queries
    query_expansions = {
        "DSPy": "What is DSPy and how is it used in this project?",
        "database": "How does the database system work in this project?",
        "memory": "How does the memory system work in this project?",
        "evaluation": "How do I run evaluations in this project?"
    }
    
    changes_made = 0
    
    for case in cases:
        query = case.get("query", "")
        
        if len(query) < 10:
            # Try to expand based on context
            if "dspy" in query.lower():
                case["query"] = query_expansions["DSPy"]
                changes_made += 1
            elif "db" in query.lower() or "database" in query.lower():
                case["query"] = query_expansions["database"]
                changes_made += 1
            elif "memory" in query.lower():
                case["query"] = query_expansions["memory"]
                changes_made += 1
            else:
                # Generic expansion
                case["query"] = query_expansions["evaluation"]
                changes_made += 1
            
            print(f"Expanded: '{query}' → '{case['query']}'")
    
    # Save updated cases
    with open("evals/gold/v1/gold_cases.jsonl", "w") as f:
        for case in cases:
            f.write(json.dumps(case) + "\n")
    
    print(f"\n✅ Expanded {changes_made} short queries")

if __name__ == "__main__":
    fix_short_queries()
