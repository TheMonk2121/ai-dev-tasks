from __future__ import annotations

import json
import os
import re

#!/usr/bin/env python3
"""
Fix Unclear Phrasing in Gold Cases
"""


def fix_unclear_phrasing():
    """Fix unclear phrasing in gold cases."""
    # Load gold cases
    with open("evals/gold/v1/gold_cases.jsonl") as f:
        cases = [json.loads(line) for line in f if line.strip()]
    
    # Define fixes
    phrasing_fixes = {
        "what show": "show me",
        "what give": "give me", 
        "what point": "point me to",
        "what is the main purpose of": "what does",
        "tl;dr": "TL;DR",
        "dspy": "DSPy"
    }
    
    changes_made = 0
    
    for case in cases:
        original_query = case.get("query", "")
        new_query = original_query
        
        # Apply fixes
        for old_phrase, new_phrase in phrasing_fixes.items():
            if old_phrase in new_query.lower():
                new_query = re.sub(old_phrase, new_phrase, new_query, flags=re.IGNORECASE)
        
        # Fix grammar
        new_query = re.sub(r"\?$", "?", new_query)  # Ensure ends with ?
        new_query = re.sub(r"\s+", " ", new_query)  # Fix spacing
        
        if new_query != original_query:
            case["query"] = new_query
            changes_made += 1
            print(f"Fixed: '{original_query}' → '{new_query}'")
    
    # Save updated cases
    with open("evals/gold/v1/gold_cases.jsonl", "w") as f:
        for case in cases:
            f.write(json.dumps(case) + "\n")
    
    print(f"\n✅ Fixed {changes_made} cases with unclear phrasing")

if __name__ == "__main__":
    fix_unclear_phrasing()
