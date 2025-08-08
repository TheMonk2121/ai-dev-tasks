#!/usr/bin/env python3
"""
Documentation Navigator
Helps navigate the complete documentation inventory and provides context-specific guidance
"""

import os
import sys
from typing import Dict, List, Any
from pathlib import Path

def get_documentation_inventory() -> Dict[str, List[str]]:
    """Get the complete documentation inventory organized by category"""
    return {
        "CRITICAL_FILES": [
            "100_cursor-memory-context.md",
            "000_backlog.md", 
            "400_system-overview.md",
            "400_project-overview.md"
        ],
        "WORKFLOW_FILES": [
            "001_create-prd.md",
            "002_generate-tasks.md", 
            "003_process-task-list.md",
            "100_backlog-guide.md"
        ],
        "SYSTEM_ARCHITECTURE": [
            "104_dspy-development-context.md",
            "202_setup-requirements.md",
            "400_context-priority-guide.md",
            # compatibility merged into guide (appendix)
            "400_cursor-context-engineering-guide.md"
        ],
        "OPERATIONAL_GUIDES": [
            "400_testing-strategy-guide.md",
            "400_security-best-practices-guide.md",
            "400_performance-optimization-guide.md",
            "400_deployment-environment-guide.md",
            "400_migration-upgrade-guide.md",
            "400_integration-patterns-guide.md",
            "400_metadata-collection-guide.md",
            "400_metadata-quick-reference.md",
            "400_few-shot-context-examples.md",
            "400_prd-optimization-guide.md",
            "400_n8n-backlog-scrubber-guide.md",
            "400_mistral7b-instruct-integration-guide.md"
        ],
        "RESEARCH_DOCUMENTATION": [
            "500_research-summary.md",
            "500_research-analysis-summary.md",
            "500_research-implementation-summary.md",
            "500_research-infrastructure-guide.md",
            "500_dspy-research.md",
            "500_rag-system-research.md",
            "500_documentation-coherence-research.md",
            "500_maintenance-safety-research.md",
            "500_performance-research.md",
            "500_monitoring-research.md",
            "500_agent-orchestration-research.md"
        ],
        "EXTERNAL_RESEARCH": [
            "docs/research/papers/",
            "docs/research/articles/",
            "docs/research/tutorials/"
        ],
        "DOMAIN_SPECIFIC": [
            "CURSOR_NATIVE_AI_STRATEGY.md",
            "B-011-PRD.md",
            "B-011-Tasks.md",
            "B-011-DEPLOYMENT-GUIDE.md",
            "B-011-DEVELOPER-DOCUMENTATION.md",
            "B-011-USER-DOCUMENTATION.md",
            "B-049-PRD.md",
            "B-049-Tasks.md",
            "B-072-PRD.md",
            "B-072-Tasks.md"
        ],
        "ANALYSIS_MAINTENANCE": [
            "400_file-analysis-guide.md",
            "200_naming-conventions.md",
            "400_cross-reference-strengthening-plan.md",
            "999_repo-maintenance.md"
        ],
        "COMPLETION_SUMMARIES": [
            "500_b002-completion-summary.md",
            "500_b031-completion-summary.md",
            "500_b060-completion-summary.md",
            "500_b065-completion-summary.md"
        ]
    }

def get_context_guidance() -> Dict[str, List[str]]:
    """Get context-specific guidance for when to read what"""
    return {
        "NEW_SESSIONS": [
            "100_cursor-memory-context.md - Current project state",
            "000_backlog.md - Current priorities", 
            "400_system-overview.md - Technical architecture"
        ],
        "DEVELOPMENT_TASKS": {
            "Planning": ["001_create-prd.md", "002_generate-tasks.md", "003_process-task-list.md"],
            "Implementation": ["104_dspy-development-context.md", "400_* guides"],
            "Testing": ["400_testing-strategy-guide.md"],
            "Security": ["400_security-best-practices-guide.md"],
            "Performance": ["400_performance-optimization-guide.md"]
        },
        "RESEARCH_TASKS": [
            "500_research-summary.md - Overview",
            "500_research-analysis-summary.md - Methodology",
            "500_research-implementation-summary.md - Implementation",
            "docs/research/papers/ - External sources",
            "docs/research/articles/ - Industry articles",
            "docs/research/tutorials/ - Implementation guides"
        ],
        "FILE_MANAGEMENT": [
            "400_file-analysis-guide.md - Analysis (MANDATORY)",
            "200_naming-conventions.md - Naming",
            "400_context-priority-guide.md - Organization"
        ],
        "SYSTEM_INTEGRATION": [
            "400_system-overview.md - Architecture",
            "400_integration-patterns-guide.md - Patterns",
            "400_deployment-environment-guide.md - Deployment",
            "400_migration-upgrade-guide.md - Migration"
        ],
        "CONTEXT_ENGINEERING": [
            "400_cursor-context-engineering-guide.md - Strategy",
            "400_context-engineering-compatibility-analysis.md - Compatibility",
            "104_dspy-development-context.md - Implementation"
        ]
    }

def check_file_exists(file_path: str) -> bool:
    """Check if a file exists"""
    return os.path.exists(file_path)

def display_documentation_inventory():
    """Display the complete documentation inventory"""
    inventory = get_documentation_inventory()
    
    print("📚 Complete Documentation Inventory")
    print("=" * 60)
    print()
    
    for category, files in inventory.items():
        print(f"🎯 {category.replace('_', ' ').title()}")
        print("-" * 40)
        
        for file_path in files:
            if check_file_exists(file_path):
                status = "✅"
                size_kb = os.path.getsize(file_path) / 1024 if os.path.exists(file_path) else 0
                print(f"{status} {file_path} ({size_kb:.1f} KB)")
            else:
                print(f"❌ {file_path} (not found)")
        print()

def display_context_guidance():
    """Display context-specific guidance"""
    guidance = get_context_guidance()
    
    print("🎯 Context-Specific Guidance")
    print("=" * 60)
    print()
    
    for context, files in guidance.items():
        print(f"📋 {context.replace('_', ' ').title()}")
        print("-" * 40)
        
        if isinstance(files, dict):
            for subcategory, subfiles in files.items():
                print(f"  🔧 {subcategory}:")
                for file in subfiles:
                    print(f"    - {file}")
        else:
            for file in files:
                print(f"  - {file}")
        print()

def find_relevant_files(task_type: str) -> List[str]:
    """Find relevant files for a specific task type"""
    guidance = get_context_guidance()
    
    relevant_files = []
    
    # Map task types to guidance categories
    task_mapping = {
        "development": "DEVELOPMENT_TASKS",
        "research": "RESEARCH_TASKS", 
        "file_management": "FILE_MANAGEMENT",
        "system_integration": "SYSTEM_INTEGRATION",
        "context_engineering": "CONTEXT_ENGINEERING",
        "new_session": "NEW_SESSIONS"
    }
    
    if task_type.lower() in task_mapping:
        category = task_mapping[task_type.lower()]
        files = guidance.get(category, [])
        
        if isinstance(files, dict):
            # Flatten nested dictionary
            for subfiles in files.values():
                relevant_files.extend(subfiles)
        else:
            relevant_files = files
    
    return relevant_files

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Documentation Navigator")
        print("=" * 30)
        print()
        print("Usage:")
        print("  python3 documentation_navigator.py inventory")
        print("  python3 documentation_navigator.py guidance")
        print("  python3 documentation_navigator.py find <task_type>")
        print()
        print("Task types: development, research, file_management, system_integration, context_engineering, new_session")
        return
    
    command = sys.argv[1]
    
    if command == "inventory":
        display_documentation_inventory()
    elif command == "guidance":
        display_context_guidance()
    elif command == "find" and len(sys.argv) > 2:
        task_type = sys.argv[2]
        relevant_files = find_relevant_files(task_type)
        
        print(f"🎯 Relevant files for {task_type}:")
        print("=" * 40)
        for file in relevant_files:
            print(f"  - {file}")
    else:
        print("Invalid command. Use 'inventory', 'guidance', or 'find <task_type>'")

if __name__ == "__main__":
    main()
