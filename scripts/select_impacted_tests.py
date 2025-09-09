#!/usr/bin/env python3
"""
Select tests that are impacted by changed files.

This script reads a list of changed files and outputs the test IDs that
cover those files, based on coverage.json from the test signal system.
"""

import json
import pathlib
import sys
from typing import Set

import typer

COV_JSON = pathlib.Path("metrics/coverage.json")


def load_coverage() -> dict:
    """Load coverage data from metrics/coverage.json"""
    if not COV_JSON.exists():
        print("Warning: metrics/coverage.json not found", file=sys.stderr)
        return {}
    
    try:
        return json.loads(COV_JSON.read_text())
    except Exception as e:
        print(f"Error loading coverage: {e}", file=sys.stderr)
        return {}


def get_tests_for_files(changed_files: Set[str], coverage_data: dict) -> Set[str]:
    """Get test IDs that cover the changed files"""
    impacted_tests = set()
    
    files = coverage_data.get("files", {})
    for file_path, file_data in files.items():
        # Check if this file is in our changed files
        if file_path in changed_files:
            contexts = file_data.get("contexts", {})
            for line_str, tests in contexts.items():
                for test in tests:
                    # Clean up test ID format
                    test_id = test.replace("::()::", "::")
                    impacted_tests.add(test_id)
    
    return impacted_tests


def main(
    files: str = typer.Option(None, "--files", help="File containing list of changed files"),
    file_list: str = typer.Option(None, "--file-list", help="Comma-separated list of changed files"),
    output_format: str = typer.Option("test_ids", "--format", help="Output format: test_ids, pytest_args"),
):
    """Select tests impacted by changed files"""
    
    # Get changed files
    changed_files = set()
    
    if files:
        file_path = pathlib.Path(files)
        if file_path.exists():
            changed_files = set(file_path.read_text().strip().split('\n'))
        else:
            print(f"Warning: File {files} not found", file=sys.stderr)
    
    if file_list:
        changed_files.update(file_list.split(','))
    
    if not changed_files:
        print("No changed files specified", file=sys.stderr)
        return
    
    # Load coverage data
    coverage_data = load_coverage()
    if not coverage_data:
        print("No coverage data available", file=sys.stderr)
        return
    
    # Find impacted tests
    impacted_tests = get_tests_for_files(changed_files, coverage_data)
    
    if not impacted_tests:
        print("No tests found for changed files", file=sys.stderr)
        return
    
    # Output results
    if output_format == "pytest_args":
        # Output as pytest arguments
        for test_id in sorted(impacted_tests):
            print(test_id)
    else:
        # Output as test IDs (default)
        for test_id in sorted(impacted_tests):
            print(test_id)


if __name__ == "__main__":
    typer.run(main)
