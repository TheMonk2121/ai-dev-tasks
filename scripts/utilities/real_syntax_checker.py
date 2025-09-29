#!/usr/bin/env python3
"""
Real syntax error checker using Python's AST parser.

This script uses Python's built-in AST parser to identify actual syntax errors,
not false positives from pattern matching.
"""

import ast
import sys
from pathlib import Path
from typing import Any


def check_file_syntax(file_path: Path) -> list[dict[str, Any]]:
    """Check a single file for actual syntax errors."""
    errors = []
    
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse the file
        ast.parse(content)
        
    except SyntaxError as e:
        errors.append({
            'file': str(file_path),
            'line': e.lineno or 0,
            'column': e.offset or 0,
            'error_type': 'SyntaxError',
            'message': e.msg,
            'text': e.text,
            'severity': 'error'
        })
    except Exception as e:
        errors.append({
            'file': str(file_path),
            'line': 0,
            'column': 0,
            'error_type': 'ParseError',
            'message': str(e),
            'text': '',
            'severity': 'error'
        })
    
    return errors


def scan_directory_for_syntax_errors(directory: Path, exclude_patterns: list[str] = None) -> dict[str, list[dict[str, Any]]]:
    """Scan directory for files with actual syntax errors."""
    if exclude_patterns is None:
        exclude_patterns = ['__pycache__', '.git', 'node_modules', '600_archives', 'evals_bundle_']
    
    results = {}
    
    print(f"Scanning {directory} for syntax errors...")
    
    for py_file in directory.rglob('*.py'):
        # Skip excluded patterns
        if any(pattern in str(py_file) for pattern in exclude_patterns):
            continue
            
        errors = check_file_syntax(py_file)
        if errors:
            results[str(py_file)] = errors
    
    return results


def categorize_errors(results: dict[str, list[dict[str, Any]]]) -> dict[str, int]:
    """Categorize errors by type."""
    error_counts = {}
    
    for file_path, errors in results.items():
        for error in errors:
            error_type = error['error_type']
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
    
    return error_counts


def print_summary(results: dict[str, list[dict[str, Any]]]):
    """Print summary of syntax errors found."""
    total_files = len(results)
    total_errors = sum(len(errors) for errors in results.values())
    
    print(f"\n{'='*60}")
    print("REAL SYNTAX ERROR ANALYSIS")
    print(f"{'='*60}")
    print(f"Total files with syntax errors: {total_files}")
    print(f"Total syntax errors found: {total_errors}")
    
    if total_errors == 0:
        print("✅ No syntax errors found!")
        return
    
    # Categorize errors
    error_counts = categorize_errors(results)
    
    print("\nError Types:")
    for error_type, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {error_type}: {count} occurrences")
    
    # Show most common error patterns
    print("\nMost Common Error Types:")
    for error_type, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {error_type}: {count} occurrences")


def print_detailed_errors(results: dict[str, list[dict[str, Any]]], max_files: int = 20):
    """Print detailed error information."""
    if not results:
        return
        
    print(f"\n{'='*60}")
    print("DETAILED ERROR REPORT")
    print(f"{'='*60}")
    
    files_shown = 0
    for file_path, errors in results.items():
        if files_shown >= max_files:
            remaining_files = len(results) - max_files
            print(f"\n... and {remaining_files} more files with syntax errors")
            break
            
        print(f"\n{file_path}:")
        for error in errors:
            print(f"  Line {error['line']}, Column {error['column']}: {error['error_type']}")
            print(f"    Message: {error['message']}")
            if error['text']:
                print(f"    Code: {error['text'].strip()}")
            print()
        
        files_shown += 1


def main():
    """Main function to run syntax error detection."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Find real syntax errors in Python files")
    parser.add_argument("--directory", default=".", help="Directory to scan (default: current directory)")
    parser.add_argument("--max-files", type=int, default=20, help="Maximum files to show detailed errors for")
    parser.add_argument("--output", help="Output file for detailed results")
    
    args = parser.parse_args()
    
    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: Directory '{directory}' does not exist")
        return 1
    
    results = scan_directory_for_syntax_errors(directory)
    print_summary(results)
    print_detailed_errors(results, args.max_files)
    
    if args.output:
        import json
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nDetailed results saved to: {args.output}")
    
    return 1 if results else 0


if __name__ == "__main__":
    sys.exit(main())
