from __future__ import annotations
import argparse
import ast
import importlib
import sys
from pathlib import Path
import csv
import os
#!/usr/bin/env python3
"""
Static import checker for scripts to identify missing dependencies.

This script parses Python files in the scripts directory and attempts to import
top-level modules to identify missing dependencies and internal module issues.
"""

def extract_imports(file_path: Path) -> set[str]:
    """Extract all import statements from a Python file."""
    imports = set()

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])  # Top-level module only
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])  # Top-level module only

    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"Warning: Could not parse {file_path}: {e}")

    return imports

def check_import_availability(module_name: str) -> tuple[bool, str]:
    """Check if a module can be imported."""
    try:
        importlib.import_module(module_name)
        return True, ""
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {e}"

def analyze_scripts_directory(scripts_dir: Path, exclude_tests: bool = True) -> dict[str, list[tuple[str, str]]]:
    """Analyze all Python files in the scripts directory."""
    results = {
        "missing_external": [],  # (module, error)
        "missing_internal": [],  # (module, error)
        "available": [],  # (module, file)
        "parse_errors": [],  # (file, error)
    }

    # Find all Python files
    pattern = "**/*.py"
    if exclude_tests:
        # Exclude test files and lib directory
        python_files = []
        for file_path in scripts_dir.rglob("*.py"):
            if not any(part in str(file_path) for part in ["test_", "_test.py", "/lib/", "/tests/"]):
                python_files.append(file_path)
    else:
        python_files = list(scripts_dir.rglob("*.py"))

    print(f"Analyzing {len(python_files)} Python files...")

    all_imports = set()
    file_imports = {}

    # Extract imports from all files
    for file_path in python_files:
        try:
            imports = extract_imports(file_path)
            file_imports[file_path] = imports
            all_imports.update(imports)
        except Exception as e:
            results["parse_errors"].append((str(file_path), str(e)))

    print(f"Found {len(all_imports)} unique top-level modules to check")

    # Check each import
    for module_name in sorted(all_imports):
        # Skip built-in modules
        if module_name in sys.builtin_module_names:
            continue

        available, error = check_import_availability(module_name)

        if available:
            # Find which files use this module
            using_files = [str(f) for f, imports in file_imports.items() if module_name in imports]
            results["available"].append((module_name, ", ".join(using_files[:3])))  # Limit to 3 files
        else:
            # Categorize the error
            if any(keyword in error.lower() for keyword in ["no module named", "cannot import"]):
                if any(
                    prefix in module_name
                    for prefix in ["dspy_modules", "src.", "utils.", "monitoring", "n8n_workflows"]
                ):
                    results["missing_internal"].append((module_name, error))
                else:
                    results["missing_external"].append((module_name, error))
            else:
                results["missing_external"].append((module_name, error))

    return results

def print_results(results: dict[str, list[tuple[str, str]]], verbose: bool = False):
    """Print the analysis results in a readable format."""

    print("\n" + "=" * 60)
    print("STATIC IMPORT ANALYSIS RESULTS")
    print("=" * 60)

    # Available modules
    if results["available"]:
        print(f"\n✅ AVAILABLE MODULES ({len(results['available'])}):")
        for module, files in results["available"]:
            if verbose:
                print(f"  {module} (used in: {files})")
            else:
                print(f"  {module}")

    # Missing external dependencies
    if results["missing_external"]:
        print(f"\n❌ MISSING EXTERNAL DEPENDENCIES ({len(results['missing_external'])}):")
        for module, error in results["missing_external"]:
            print(f"  {module}: {error}")

    # Missing internal modules
    if results["missing_internal"]:
        print(f"\n⚠️  MISSING INTERNAL MODULES ({len(results['missing_internal'])}):")
        for module, error in results["missing_internal"]:
            print(f"  {module}: {error}")

    # Parse errors
    if results["parse_errors"]:
        print(f"\n🔧 PARSE ERRORS ({len(results['parse_errors'])}):")
        for file, error in results["parse_errors"]:
            print(f"  {file}: {error}")

    # Summary
    total_missing = len(results["missing_external"]) + len(results["missing_internal"])
    print("\n📊 SUMMARY:")
    print(f"  Available modules: {len(results['available'])}")
    print(f"  Missing external: {len(results['missing_external'])}")
    print(f"  Missing internal: {len(results['missing_internal'])}")
    print(f"  Parse errors: {len(results['parse_errors'])}")
    print(f"  Total issues: {total_missing + len(results['parse_errors'])}")

def generate_csv_report(results: dict[str, list[tuple[str, str]]], output_file: Path):
    """Generate a CSV report of missing dependencies."""

    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Module", "Type", "Error", "Status"])

        # Missing external
        for module, error in results["missing_external"]:
            writer.writerow([module, "external", error, "missing"])

        # Missing internal
        for module, error in results["missing_internal"]:
            writer.writerow([module, "internal", error, "missing"])

        # Available
        for module, files in results["available"]:
            writer.writerow([module, "external", "", "available"])

def main():
    parser = argparse.ArgumentParser(description="Check static imports in scripts directory")
    parser.add_argument(
        "--scripts-dir", default="scripts", help="Directory containing scripts to analyze (default: scripts)"
    )
    parser.add_argument("--include-tests", action="store_true", help="Include test files in analysis")
    parser.add_argument("--verbose", action="store_true", help="Show which files use each module")
    parser.add_argument("--csv", type=Path, help="Generate CSV report to specified file")

    args = parser.parse_args()

    scripts_dir = Path(args.scripts_dir)
    if not scripts_dir.exists():
        print(f"Error: Scripts directory '{scripts_dir}' does not exist")
        return 1

    print(f"🔍 Analyzing imports in: {scripts_dir}")
    print(f"   Include tests: {args.include_tests}")

    results = analyze_scripts_directory(scripts_dir, exclude_tests=not args.include_tests)
    print_results(results, verbose=args.verbose)

    if args.csv:
        generate_csv_report(results, args.csv)
        print(f"\n📄 CSV report saved to: {args.csv}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
