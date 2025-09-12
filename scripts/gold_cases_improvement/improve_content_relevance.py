from __future__ import annotations
import json
#!/usr/bin/env python3
"""
Improve Content Relevance in Gold Cases
"""


def improve_content_relevance():
    """Improve content relevance by adding specific file references."""
    # Load gold cases
    with open("evals/gold/v1/gold_cases.jsonl", "r") as f:
        cases = [json.loads(line) for line in f if line.strip()]
    
    # Define improvements for specific cases
    relevance_improvements = {
        "How does the database schema work?": {
            "add_files": ["scripts/sql/fix_sparse_vector_ddls.sql", "src/dspy_modules/retriever/pg.py"],
            "remove_globs": ["**/*.md"]
        },
        "What MCP tools are available in this project?": {
            "add_files": ["CURSOR_MCP_SETUP.md", "scripts/mcp_server.py"],
            "remove_globs": ["**/*.md"]
        },
        "How do I run memory rehydration?": {
            "add_files": ["scripts/unified_memory_orchestrator.py", "100_memory/100_cursor-memory-context.md"],
            "remove_globs": ["**/*.md"]
        },
        "What are the evaluation metrics and thresholds?": {
            "add_files": ["scripts/ci_gate_reader.py", "400_guides/400_11_performance-optimization.md"],
            "remove_globs": ["**/*.md"]
        }
    }
    
    changes_made = 0
    
    for case in cases:
        query = case.get("query", "")
        
        if query in relevance_improvements:
            improvements = relevance_improvements[query]
            
            # Add specific files
            if "add_files" in improvements:
                if "expected_files" not in case:
                    case["expected_files"] = []
                case["expected_files"].extend(improvements["add_files"])
            
            # Remove overly broad globs
            if "remove_globs" in improvements and "globs" in case:
                for glob_to_remove in improvements["remove_globs"]:
                    if glob_to_remove in case["globs"]:
                        case["globs"].remove(glob_to_remove)
            
            changes_made += 1
            print(f"Improved relevance for: '{query}'")
    
    # Save updated cases
    with open("evals/gold/v1/gold_cases.jsonl", "w") as f:
        for case in cases:
            f.write(json.dumps(case) + "\n")
    
    print(f"\n✅ Improved content relevance for {changes_made} cases")

if __name__ == "__main__":
    improve_content_relevance()