#!/usr/bin/env python3
"""
Pre-workflow hook that forces memory hydration and quality gates.

This script enforces compliance with the established development workflow
by requiring memory hydration and quality checks before any workflow execution.
"""

import subprocess
import sys
from pathlib import Path


def force_memory_hydration(context: str, role: str = "planner") -> bool:
    """Force memory hydration before any workflow."""
    print("🧠 FORCING MEMORY HYDRATION...")

    try:
        result = subprocess.run(
            [sys.executable, "scripts/cursor_memory_rehydrate.py", role, context],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        if result.returncode != 0:
            print("❌ Memory hydration failed!")
            print(result.stderr)
            return False

        print("✅ Memory hydration complete")
        return True

    except Exception as e:
        print(f"❌ Memory hydration error: {e}")
        return False


def _changed_paths() -> list[str]:
    """Return a list of changed files (staged or unstaged)."""
    try:
        # Staged + unstaged
        staged = subprocess.check_output(["git", "diff", "--name-only", "--cached"], text=True).splitlines()
        unstaged = subprocess.check_output(["git", "ls-files", "-m"], text=True).splitlines()
        return sorted(set([p for p in staged + unstaged if p]))
    except Exception:
        return []


def run_quality_gates() -> bool:
    """Run quality gates to ensure compliance."""
    print("🛡️ RUNNING QUALITY GATES...")

    py = sys.executable

    # Build doc validation in warn-only, only-changed mode to avoid hard block on known warnings
    doc_cmd = [py, "scripts/doc_coherence_validator.py", "--warn-only", "--only-changed"]

    # Limit Ruff to changed Python files to keep the gate fast and actionable
    changed = [p for p in _changed_paths() if p.endswith(".py")]
    if not changed:
        # Fall back to a minimal safe set
        changed = [
            "scripts/pre_workflow_hook.py",
            "scripts/single_doorway.py",
            "scripts/cursor_memory_rehydrate.py",
        ]
    code_cmd = [py, "-m", "ruff", "check", *changed]

    gates = [
        ("Conflict Check", [py, "scripts/quick_conflict_check.py"]),
        ("Documentation Validation", doc_cmd),
        ("Code Quality", code_cmd),
    ]

    failed_gates = []

    for gate_name, command in gates:
        print(f"  Running {gate_name}...")
        try:
            result = subprocess.run(command, capture_output=True, text=True, cwd=Path.cwd())
            if result.returncode != 0:
                failed_gates.append(gate_name)
                print(f"    ❌ {gate_name} failed")
            else:
                print(f"    ✅ {gate_name} passed")
        except Exception as e:
            failed_gates.append(gate_name)
            print(f"    ❌ {gate_name} error: {e}")

    if failed_gates:
        print(f"❌ Quality gates failed: {', '.join(failed_gates)}")
        return False

    print("✅ All quality gates passed")
    return True


def check_existing_tools(keyword: str) -> bool:
    """Check if existing tools exist for the given keyword."""
    print(f"🔍 CHECKING EXISTING TOOLS FOR: {keyword}")

    # Search for existing tools
    search_paths = ["scripts/", "dspy-rag-system/scripts/", "dspy-rag-system/src/"]
    existing_tools = []

    for search_path in search_paths:
        if Path(search_path).exists():
            for file_path in Path(search_path).rglob("*.py"):
                if keyword.lower() in file_path.name.lower() or keyword.lower() in file_path.read_text().lower():
                    existing_tools.append(str(file_path))

    if existing_tools:
        print(f"✅ Found existing tools: {existing_tools}")
        return True
    else:
        print(f"⚠️  No existing tools found for '{keyword}'")
        return False


def force_existing_test_usage(test_type: str) -> bool:
    """Force usage of existing tests instead of creating new ones."""
    print(f"🧪 FORCING EXISTING TEST USAGE: {test_type}")

    test_mapping = {
        "smoke": ["./dspy-rag-system/run_tests.sh", "--tiers", "3", "--kinds", "unit"],
        "unit": ["./dspy-rag-system/run_tests.sh", "--tiers", "3", "--kinds", "unit"],
        "integration": ["./dspy-rag-system/run_tests.sh", "--tiers", "2", "--kinds", "integration"],
        "performance": [sys.executable, "scripts/performance_benchmark.py"],
        "security": [sys.executable, "scripts/security_enhancement.py"],
        "system_health": [sys.executable, "scripts/system_health_check.py"],
    }

    if test_type not in test_mapping:
        print(f"❌ Unknown test type: {test_type}")
        return False

    command = test_mapping[test_type]
    print(f"  Running: {' '.join(command)}")

    try:
        result = subprocess.run(command, cwd=Path.cwd())
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Test execution error: {e}")
        return False


def main():
    """Main function for pre-workflow enforcement."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/pre_workflow_hook.py <context> [role] [test_type]")
        sys.exit(1)

    context = sys.argv[1]
    role = sys.argv[2] if len(sys.argv) > 2 else "planner"
    test_type = sys.argv[3] if len(sys.argv) > 3 else "smoke"

    print("🚀 PRE-WORKFLOW ENFORCEMENT")
    print("=" * 50)

    # Step 1: Force memory hydration
    if not force_memory_hydration(context, role):
        print("❌ Memory hydration failed - cannot proceed")
        sys.exit(1)

    # Step 2: Run quality gates
    if not run_quality_gates():
        print("❌ Quality gates failed - cannot proceed")
        sys.exit(1)

    # Step 3: Check for existing tools
    if not check_existing_tools(context.split()[0]):
        print("⚠️  No existing tools found - proceed with caution")

    # Step 4: Force existing test usage
    if not force_existing_test_usage(test_type):
        print("❌ Existing test usage failed - cannot proceed")
        sys.exit(1)

    print("✅ Pre-workflow enforcement complete - proceed with workflow")


if __name__ == "__main__":
    main()
