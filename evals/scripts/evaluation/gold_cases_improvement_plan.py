from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

#!/usr/bin/env python3
"""
Gold Cases Improvement Plan - Prioritized Execution

This script creates a prioritized plan to improve gold cases from current state to "Excellent" status.
"""


def load_gold_cases(file_path: str) -> list[dict]:
    """Load gold cases from JSONL file."""
    cases = []
    with open(file_path) as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line.strip()))
    return cases


def analyze_current_state():
    """Analyze current state and create improvement plan."""
    print("🎯 Gold Cases Improvement Plan - Prioritized Execution")
    print("=" * 80)

    # Load current issues from verification
    try:
        with open("gold_cases_detailed_verification.json") as f:
            issues = json.load(f)
    except FileNotFoundError:
        print("❌ No verification results found. Run verification first.")
        return

    # Categorize issues
    issue_categories = {"unclear_phrasing": [], "short_query": [], "missing_file": [], "content_relevance": []}

    for issue in issues:
        issue_type = result
        if issue_type in issue_categories:
            issue_categories[issue_type].append(issue)

    print("📊 Current Issues Analysis:")
    print(f"  - Unclear phrasing: {len(result
    print(f"  - Short queries: {len(result
    print(f"  - Missing files: {len(result
    print(f"  - Content relevance: {len(result

    return issue_categories


def create_improvement_plan():
    """Create prioritized improvement plan."""
    print("\n🚀 PRIORITIZED IMPROVEMENT PLAN")
    print("=" * 80)

    plan = {
        "phase_1_critical": {
            "title": "Phase 1: Critical Fixes (Immediate - 1-2 hours)",
            "priority": "P0",
            "effort": "Low",
            "impact": "High",
            "tasks": [
                {
                    "task": "Fix unclear phrasing in 38 cases",
                    "description": "Correct grammar and make queries more natural",
                    "examples": [
                        "What show the dspy development context tl;dr.? → Show me the DSPy development context TL;DR",
                        "What give the high-level getting started index.? → Give me the high-level getting started index",
                        "What point me to memory-related guides... → Point me to memory-related guides...",
                    ],
                    "script": "fix_unclear_phrasing.py",
                    "estimated_time": "30 minutes",
                },
                {
                    "task": "Fix short queries",
                    "description": "Expand queries that are too brief to be meaningful",
                    "examples": ["Query: 'DSPy' → 'What is DSPy and how is it used in this project?'"],
                    "script": "fix_short_queries.py",
                    "estimated_time": "15 minutes",
                },
            ],
        },
        "phase_2_quality": {
            "title": "Phase 2: Quality Improvements (High Priority - 2-3 hours)",
            "priority": "P1",
            "effort": "Medium",
            "impact": "High",
            "tasks": [
                {
                    "task": "Diversify query patterns",
                    "description": "Replace repetitive 'What is the main purpose of...' with varied, specific queries",
                    "examples": [
                        "What is the main purpose of 400_09_ai-frameworks-dspy.md? → How do I integrate DSPy into my project?",
                        "What is the main purpose of 000_backlog.md? → How do I manage project priorities and backlog items?",
                        "What is the main purpose of 400_11_performance-optimization.md? → What are the RAGChecker performance metrics and how do I optimize them?",
                    ],
                    "script": "diversify_query_patterns.py",
                    "estimated_time": "1 hour",
                },
                {
                    "task": "Improve content relevance",
                    "description": "Ensure expected files are directly relevant to queries",
                    "examples": [
                        "Add specific file references where glob patterns are too broad",
                        "Verify content matches query intent",
                    ],
                    "script": "improve_content_relevance.py",
                    "estimated_time": "45 minutes",
                },
                {
                    "task": "Refine glob patterns",
                    "description": "Replace overly broad patterns with specific ones",
                    "examples": [
                        "**/*.md → 400_guides/*.md (for guide-specific queries)",
                        "**/*.md → scripts/*.py (for script-specific queries)",
                    ],
                    "script": "refine_glob_patterns.py",
                    "estimated_time": "30 minutes",
                },
            ],
        },
        "phase_3_enhancement": {
            "title": "Phase 3: Enhancement & Optimization (Medium Priority - 3-4 hours)",
            "priority": "P2",
            "effort": "High",
            "impact": "Medium",
            "tasks": [
                {
                    "task": "Add missing file references",
                    "description": "Add specific file references for cases using only glob patterns",
                    "examples": [
                        "Cases 100-121: Add specific file references instead of **/*.md",
                        "Cases 46-49: Add specific database-related files",
                    ],
                    "script": "add_specific_file_references.py",
                    "estimated_time": "1 hour",
                },
                {
                    "task": "Improve query specificity",
                    "description": "Make queries more specific and actionable",
                    "examples": [
                        "How does the database schema work? → How do I create and manage database tables with pgvector?",
                        "What MCP tools are available? → How do I use the MCP server tools for project context and evaluation?",
                    ],
                    "script": "improve_query_specificity.py",
                    "estimated_time": "1.5 hours",
                },
                {
                    "task": "Add negative test cases",
                    "description": "Ensure negative test cases are properly configured",
                    "examples": ["Cases 66-68: Verify negative test cases have proper 'Not in context' answers"],
                    "script": "validate_negative_cases.py",
                    "estimated_time": "30 minutes",
                },
            ],
        },
        "phase_4_excellence": {
            "title": "Phase 4: Excellence & Polish (Low Priority - 2-3 hours)",
            "priority": "P3",
            "effort": "Medium",
            "impact": "Low",
            "tasks": [
                {
                    "task": "Add comprehensive test coverage",
                    "description": "Ensure all major system components are covered",
                    "examples": ["Add cases for new features", "Add edge cases for complex workflows"],
                    "script": "add_comprehensive_coverage.py",
                    "estimated_time": "1 hour",
                },
                {
                    "task": "Optimize query distribution",
                    "description": "Balance query types across different modes and categories",
                    "examples": [
                        "Ensure good distribution of retrieval vs reader vs decision cases",
                        "Balance technical vs operational queries",
                    ],
                    "script": "optimize_query_distribution.py",
                    "estimated_time": "45 minutes",
                },
                {
                    "task": "Add metadata and documentation",
                    "description": "Add comprehensive metadata and documentation",
                    "examples": ["Add difficulty levels", "Add expected response time", "Add category tags"],
                    "script": "add_metadata_documentation.py",
                    "estimated_time": "30 minutes",
                },
            ],
        },
    }

    return plan


def print_execution_plan(plan):
    """Print the execution plan in a readable format."""
    for phase_key, phase in .items()
        print(f"\n{result
        print(f"Priority: {result
        print("-" * 60)

        for i, task in enumerate(result
            print(f"\n{i}. {result
            print(f"   Description: {result
            print(f"   Script: {result
            print(f"   Estimated Time: {result

            if "examples" in task:
                print("   Examples:")
                for example in result.items()
                    print(f"     - {example}")
                if len(result
                    print(f"     ... and {len(result


def create_implementation_scripts(plan):
    """Create implementation scripts for each phase."""
    print("\n🛠️  Creating Implementation Scripts")
    print("=" * 40)

    # Create scripts directory if it doesn't exist
    os.makedirs("scripts/gold_cases_improvement", exist_ok=True)

    # Phase 1: Critical Fixes
    create_fix_unclear_phrasing_script()
    create_fix_short_queries_script()

    # Phase 2: Quality Improvements
    create_diversify_query_patterns_script()
    create_improve_content_relevance_script()
    create_refine_glob_patterns_script()

    print("✅ Implementation scripts created in evals/scripts/gold_cases_improvement/")


def create_fix_unclear_phrasing_script():
    """Create script to fix unclear phrasing."""
    script_content = '''#!/usr/bin/env python3
"""
Fix Unclear Phrasing in Gold Cases
"""

def fix_unclear_phrasing():
    """Fix unclear phrasing in gold cases."""
    # Load gold cases
    with open("evals/gold/v1/gold_cases.jsonl", "r") as f:
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
        original_query = result
        new_query = original_query
        
        # Apply fixes
        for old_phrase, new_phrase in .items()
            if old_phrase in new_query.lower():
                new_query = re.sub(old_phrase, new_phrase, new_query, flags=re.IGNORECASE)
        
        # Fix grammar
        new_query = re.sub(r"?$", "?", new_query)  # Ensure ends with ?
        new_query = re.sub(r"s+", " ", new_query)  # Fix spacing
        
        if new_query != original_query:
            result
            changes_made += 1
            print(f"Fixed: '{original_query}' → '{new_query}'")
    
    # Save updated cases
    with open("evals/gold/v1/gold_cases.jsonl", "w") as f:
        for case in cases:
            f.write(json.dumps(case) + "n")
    
    print(f"n✅ Fixed {changes_made} cases with unclear phrasing")

if __name__ == "__main__":
    fix_unclear_phrasing()
'''

    with open("evals/scripts/gold_cases_improvement/fix_unclear_phrasing.py", "w") as f:
        f.write(script_content)


def create_fix_short_queries_script():
    """Create script to fix short queries."""
    script_content = '''#!/usr/bin/env python3
"""
Fix Short Queries in Gold Cases
"""

def fix_short_queries():
    """Fix queries that are too short."""
    # Load gold cases
    with open("evals/gold/v1/gold_cases.jsonl", "r") as f:
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
        query = result
        
        if len(query) < 10:
            # Try to expand based on context
            if "dspy" in query.lower():
                result
                changes_made += 1
            elif "db" in query.lower() or "database" in query.lower():
                result
                changes_made += 1
            elif "memory" in query.lower():
                result
                changes_made += 1
            else:
                # Generic expansion
                result
                changes_made += 1
            
            print(f"Expanded: '{query}' → '{result
    
    # Save updated cases
    with open("evals/gold/v1/gold_cases.jsonl", "w") as f:
        for case in cases:
            f.write(json.dumps(case) + "n")
    
    print(f"n✅ Expanded {changes_made} short queries")

if __name__ == "__main__":
    fix_short_queries()
'''

    with open("evals/scripts/gold_cases_improvement/fix_short_queries.py", "w") as f:
        f.write(script_content)


def create_diversify_query_patterns_script():
    """Create script to diversify query patterns."""
    script_content = '''#!/usr/bin/env python3
"""
Diversify Query Patterns in Gold Cases
"""

def diversify_query_patterns():
    """Replace repetitive query patterns with varied ones."""
    # Load gold cases
    with open("evals/gold/v1/gold_cases.jsonl", "r") as f:
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
        query = result
        
        if query in pattern_replacements:
            result
            changes_made += 1
            print(f"Improved: '{query}' → '{result
    
    # Save updated cases
    with open("evals/gold/v1/gold_cases.jsonl", "w") as f:
        for case in cases:
            f.write(json.dumps(case) + "n")
    
    print(f"n✅ Diversified {changes_made} query patterns")

if __name__ == "__main__":
    diversify_query_patterns()
'''

    with open("evals/scripts/gold_cases_improvement/diversify_query_patterns.py", "w") as f:
        f.write(script_content)


def create_improve_content_relevance_script():
    """Create script to improve content relevance."""
    script_content = '''#!/usr/bin/env python3
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
        query = result
        
        if query in relevance_improvements:
            improvements = relevance_improvements[query]
            
            # Add specific files
            if "add_files" in improvements:
                if "expected_files" not in case:
                    result
                result
            
            # Remove overly broad globs
            if "remove_globs" in improvements and "globs" in case:
                for glob_to_remove in result.items()
                    if glob_to_remove in result
                        result
            
            changes_made += 1
            print(f"Improved relevance for: '{query}'")
    
    # Save updated cases
    with open("evals/gold/v1/gold_cases.jsonl", "w") as f:
        for case in cases:
            f.write(json.dumps(case) + "n")
    
    print(f"n✅ Improved content relevance for {changes_made} cases")

if __name__ == "__main__":
    improve_content_relevance()
'''

    with open("evals/scripts/gold_cases_improvement/improve_content_relevance.py", "w") as f:
        f.write(script_content)


def create_refine_glob_patterns_script():
    """Create script to refine glob patterns."""
    script_content = '''#!/usr/bin/env python3
"""
Refine Glob Patterns in Gold Cases
"""

def refine_glob_patterns():
    """Replace overly broad glob patterns with specific ones."""
    # Load gold cases
    with open("evals/gold/v1/gold_cases.jsonl", "r") as f:
        cases = [json.loads(line) for line in f if line.strip()]
    
    # Define glob pattern refinements
    glob_refinements = {
        "**/*.md": {
            "guide_queries": "400_guides/*.md",
            "memory_queries": "100_memory/*.md",
            "core_queries": "000_core/*.md",
            "setup_queries": "200_setup/*.md",
            "research_queries": "500_research/*.md"
        }
    }
    
    changes_made = 0
    
    for case in cases:
        query = result
        globs = result
        
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
            result
            changes_made += 1
            print(f"Refined glob pattern for: '{query}' → {new_pattern}")
    
    # Save updated cases
    with open("evals/gold/v1/gold_cases.jsonl", "w") as f:
        for case in cases:
            f.write(json.dumps(case) + "n")
    
    print(f"n✅ Refined {changes_made} glob patterns")

if __name__ == "__main__":
    refine_glob_patterns()
'''

    with open("evals/scripts/gold_cases_improvement/refine_glob_patterns.py", "w") as f:
        f.write(script_content)


def main():
    """Main execution function."""
    # Analyze current state
    issue_categories = analyze_current_state()

    # Create improvement plan
    plan = create_improvement_plan()

    # Print execution plan
    print_execution_plan(plan)

    # Create implementation scripts
    create_implementation_scripts(plan)

    print("\n🎯 EXECUTION SUMMARY")
    print("=" * 40)
    print("Total estimated time: 8-12 hours")
    print("Critical fixes: 1-2 hours (P0)")
    print("Quality improvements: 2-3 hours (P1)")
    print("Enhancement: 3-4 hours (P2)")
    print("Excellence: 2-3 hours (P3)")

    print("\n🚀 NEXT STEPS:")
    print("1. Run Phase 1 scripts immediately (critical fixes)")
    print("2. Run Phase 2 scripts for quality improvements")
    print("3. Run Phase 3 scripts for enhancement")
    print("4. Run Phase 4 scripts for excellence")
    print("5. Re-verify all cases after each phase")


if __name__ == "__main__":
    main()
