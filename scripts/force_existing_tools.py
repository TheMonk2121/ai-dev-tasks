#!/usr/bin/env python3
"""
Force usage of existing tools instead of creating new ones.

This script enforces the use of existing infrastructure
instead of creating redundant tools.
"""

import sys
from pathlib import Path


def find_existing_tools(keyword: str) -> list[str]:
    """Find existing tools that match the given keyword."""

    search_paths = [
        "scripts/",
        "dspy-rag-system/scripts/",
        "dspy-rag-system/src/",
        "dspy-rag-system/src/utils/",
        "dspy-rag-system/src/monitoring/",
        "dspy-rag-system/src/n8n_workflows/",
    ]

    existing_tools = []

    for search_path in search_paths:
        if Path(search_path).exists():
            for file_path in Path(search_path).rglob("*.py"):
                try:
                    content = file_path.read_text().lower()
                    if keyword.lower() in file_path.name.lower() or keyword.lower() in content:
                        existing_tools.append(str(file_path))
                except Exception:
                    continue

    return existing_tools


def get_tool_mapping() -> dict[str, list[str]]:
    """Get mapping of common tasks to existing tools."""

    return {
        "performance": [
            "scripts/performance_benchmark.py",
            "scripts/performance_optimization.py",
            "scripts/workflow_performance_monitor.py",
        ],
        "security": [
            "scripts/security_enhancement.py",
            "scripts/security_improvements.py",
            "dspy-rag-system/scripts/security_scan.py",
        ],
        "testing": [
            "./dspy-rag-system/run_tests.sh",
            "scripts/run_existing_tests.py",
            "scripts/select_existing_tests.py",
        ],
        "monitoring": [
            "scripts/system_health_check.py",
            "dspy-rag-system/src/monitoring/production_monitor.py",
            "dspy-rag-system/src/monitoring/health_endpoints.py",
        ],
        "validation": [
            "scripts/doc_coherence_validator.py",
            "scripts/quick_conflict_check.py",
            "scripts/conflict_audit.py",
        ],
        "memory": [
            "scripts/memory_up.sh",
            "scripts/update_cursor_memory.py",
            "dspy-rag-system/src/utils/memory_rehydrator.py",
        ],
        "workflow": ["scripts/single_doorway.py", "scripts/process_tasks.py", "scripts/executor.py"],
        "backlog": ["scripts/backlog_intake.py", "scripts/backlog_parser.py", "scripts/backlog_status_tracking.py"],
        "documentation": [
            "scripts/documentation_retrieval_cli.py",
            "scripts/documentation_indexer.py",
            "scripts/documentation_navigator.py",
        ],
    }


def suggest_existing_tools(task_description: str) -> dict[str, list[str]]:
    """Suggest existing tools based on task description."""

    tool_mapping = get_tool_mapping()
    suggestions = {}

    task_lower = task_description.lower()

    for category, tools in tool_mapping.items():
        if category in task_lower:
            # Check which tools actually exist
            existing_tools = []
            for tool in tools:
                if Path(tool).exists():
                    existing_tools.append(tool)

            if existing_tools:
                suggestions[category] = existing_tools

    # Also search for specific keywords
    specific_tools = find_existing_tools(task_description.split()[0])
    if specific_tools:
        suggestions["specific"] = specific_tools

    return suggestions


def force_tool_usage(task_description: str, dry_run: bool = False) -> bool:
    """Force usage of existing tools for the given task."""

    print(f"🔍 ANALYZING TASK: {task_description}")
    print("=" * 50)

    suggestions = suggest_existing_tools(task_description)

    if not suggestions:
        print("⚠️  No existing tools found for this task")
        print("   Consider creating a new tool, but check for similar functionality first")
        return True

    print("✅ FOUND EXISTING TOOLS:")
    for category, tools in suggestions.items():
        print(f"\n  {category.upper()}:")
        for tool in tools:
            print(f"    - {tool}")

    if dry_run:
        print("\n🔍 DRY RUN - Would use existing tools instead of creating new ones")
        return True

    # Ask user to confirm usage of existing tools
    print("\n💡 RECOMMENDATION: Use existing tools instead of creating new ones")
    print("   This ensures consistency and leverages existing infrastructure")

    return True


def check_tool_duplication(new_tool_name: str) -> list[str]:
    """Check if a new tool would duplicate existing functionality."""

    similar_tools = []

    # Search for similar tool names
    for file_path in Path("scripts/").rglob("*.py"):
        if new_tool_name.lower() in file_path.name.lower() or file_path.name.lower() in new_tool_name.lower():
            similar_tools.append(str(file_path))

    # Search for similar functionality
    tool_mapping = get_tool_mapping()
    for category, tools in tool_mapping.items():
        if category in new_tool_name.lower():
            for tool in tools:
                if Path(tool).exists():
                    similar_tools.append(tool)

    return similar_tools


def prevent_tool_creation(new_tool_name: str, task_description: str) -> bool:
    """Prevent creation of new tools when existing ones are available."""

    print(f"🚫 PREVENTING TOOL CREATION: {new_tool_name}")
    print("=" * 50)

    # Check for duplicates
    duplicates = check_tool_duplication(new_tool_name)
    if duplicates:
        print("❌ DUPLICATE TOOLS DETECTED:")
        for duplicate in duplicates:
            print(f"    - {duplicate}")
        print("\n💡 RECOMMENDATION: Use existing tools instead of creating duplicates")
        return False

    # Check for existing tools for the task
    suggestions = suggest_existing_tools(task_description)
    if suggestions:
        print("✅ EXISTING TOOLS AVAILABLE:")
        for category, tools in suggestions.items():
            print(f"    {category}: {', '.join(tools)}")
        print("\n💡 RECOMMENDATION: Use existing tools instead of creating new ones")
        return False

    print("✅ No duplicates or existing tools found - tool creation allowed")
    return True


def main():
    """Main function for tool usage enforcement."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/force_existing_tools.py <task_description>")
        print("  python scripts/force_existing_tools.py --check <new_tool_name> <task_description>")
        print("  python scripts/force_existing_tools.py --suggest <task_description> --dry-run")
        sys.exit(1)

    if sys.argv[1] == "--check" and len(sys.argv) >= 4:
        new_tool_name = sys.argv[2]
        task_description = sys.argv[3]
        allowed = prevent_tool_creation(new_tool_name, task_description)
        sys.exit(0 if allowed else 1)

    elif sys.argv[1] == "--suggest":
        task_description = sys.argv[2]
        dry_run = "--dry-run" in sys.argv
        success = force_tool_usage(task_description, dry_run)
        sys.exit(0 if success else 1)

    else:
        task_description = sys.argv[1]
        success = force_tool_usage(task_description)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
