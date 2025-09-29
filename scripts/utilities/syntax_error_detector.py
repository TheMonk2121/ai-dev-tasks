#!/usr/bin/env python3
"""
Comprehensive syntax error detector for Python files.

This script identifies common syntax errors including:
- Missing commas in function calls, lists, dictionaries
- Incomplete statements or malformed code blocks
- Multiple statements on same line
- Malformed f-string syntax
- Incomplete f-string expressions
"""

import ast
import re
import sys
from pathlib import Path
from typing import Any


def detect_syntax_errors(file_path: Path) -> list[dict[str, Any]]:
    """Detect syntax errors in a Python file."""
    errors = []
    
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
        
        # Parse the file
        tree = ast.parse(content)
        
        # Check for common patterns that cause syntax errors
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_errors = check_line_syntax(line, i)
            errors.extend(line_errors)
            
    except SyntaxError as e:
        errors.append({
            'line': e.lineno or 0,
            'column': e.offset or 0,
            'error_type': 'SyntaxError',
            'message': str(e),
            'severity': 'error'
        })
    except Exception as e:
        errors.append({
            'line': 0,
            'column': 0,
            'error_type': 'ParseError',
            'message': str(e),
            'severity': 'error'
        })
    
    return errors


def check_line_syntax(line: str, line_num: int) -> list[dict[str, Any]]:
    """Check a single line for common syntax issues."""
    errors = []
    
    # Check for missing commas in function calls
    if re.search(r'\)\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\(', line):
        errors.append({
            'line': line_num,
            'column': 0,
            'error_type': 'MissingComma',
            'message': 'Expected comma between function arguments',
            'severity': 'error'
        })
    
    # Check for missing commas in lists/dicts
    if re.search(r'[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*', line):
        # Look for patterns like "item1 item2" in lists or dicts
        if '[' in line or '{' in line:
            errors.append({
                'line': line_num,
                'column': 0,
                'error_type': 'MissingComma',
                'message': 'Expected comma between list/dict items',
                'severity': 'error'
            })
    
    # Check for multiple statements on same line (without semicolons)
    if ';' not in line and line.count('=') > 1 and not line.strip().startswith('#'):
        # Look for patterns like "a = 1 b = 2" without semicolons
        if re.search(r'[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[^=]+\s+[a-zA-Z_][a-zA-Z0-9_]*\s*=', line):
            errors.append({
                'line': line_num,
                'column': 0,
                'error_type': 'MultipleStatements',
                'message': 'Multiple statements on same line without semicolons',
                'severity': 'warning'
            })
    
    # Check for malformed f-strings
    if 'f"' in line or "f'" in line:
        # Check for unterminated f-strings
        if line.count('f"') > line.count('"') or line.count("f'") > line.count("'"):
            errors.append({
                'line': line_num,
                'column': 0,
                'error_type': 'UnterminatedFString',
                'message': 'f-string: unterminated string',
                'severity': 'error'
            })
        
        # Check for incomplete f-string expressions
        if re.search(r'\{[^}]*$', line):
            errors.append({
                'line': line_num,
                'column': 0,
                'error_type': 'IncompleteFString',
                'message': 'f-string: expecting \'}\'',
                'severity': 'error'
            })
    
    # Check for incomplete statements
    if line.strip() and not line.strip().endswith((':', ',', ';', '\\', ']', '}', ')')) and not line.strip().startswith(('#', '"""', "'''")):
        # Look for incomplete function calls, list comprehensions, etc.
        if re.search(r'\([^)]*$', line) or re.search(r'\[[^\]]*$', line) or re.search(r'\{[^}]*$', line):
            errors.append({
                'line': line_num,
                'column': 0,
                'error_type': 'IncompleteStatement',
                'message': 'Expected a statement',
                'severity': 'error'
            })
    
    return errors


def scan_directory(directory: Path, exclude_patterns: list[str] = None) -> dict[str, list[dict[str, Any]]]:
    """Scan a directory for syntax errors."""
    if exclude_patterns is None:
        exclude_patterns = ['__pycache__', '.git', 'node_modules', '600_archives', 'evals_bundle_']
    
    results = {}
    
    for py_file in directory.rglob('*.py'):
        # Skip excluded patterns
        if any(pattern in str(py_file) for pattern in exclude_patterns):
            continue
            
        errors = detect_syntax_errors(py_file)
        if errors:
            results[str(py_file)] = errors
    
    return results


def print_error_summary(results: dict[str, list[dict[str, Any]]]):
    """Print a summary of syntax errors found."""
    error_counts = {}
    total_files = len(results)
    total_errors = sum(len(errors) for errors in results.values())
    
    print(f"\n{'='*60}")
    print("SYNTAX ERROR ANALYSIS")
    print(f"{'='*60}")
    print(f"Total files with errors: {total_files}")
    print(f"Total errors found: {total_errors}")
    
    # Count error types
    for file_path, errors in results.items():
        for error in errors:
            error_type = error['error_type']
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
    
    print("\nError Types:")
    for error_type, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {error_type}: {count} occurrences")
    
    # Show most common errors
    print("\nMost Common Error Types:")
    for error_type, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {error_type}: {count} occurrences")


def print_detailed_errors(results: dict[str, list[dict[str, Any]]], max_files: int = 10):
    """Print detailed error information."""
    print(f"\n{'='*60}")
    print("DETAILED ERROR REPORT")
    print(f"{'='*60}")
    
    files_shown = 0
    for file_path, errors in results.items():
        if files_shown >= max_files:
            print(f"\n... and {len(results) - max_files} more files with errors")
            break
            
        print(f"\n{file_path}:")
        for error in errors[:5]:  # Show first 5 errors per file
            print(f"  Line {error['line']}: {error['error_type']} - {error['message']}")
        
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
        
        files_shown += 1


def main():
    """Main function to run syntax error detection."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Detect syntax errors in Python files")
    parser.add_argument("--directory", default=".", help="Directory to scan (default: current directory)")
    parser.add_argument("--max-files", type=int, default=10, help="Maximum files to show detailed errors for")
    parser.add_argument("--output", help="Output file for detailed results")
    
    args = parser.parse_args()
    
    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: Directory '{directory}' does not exist")
        return 1
    
    print(f"Scanning directory: {directory}")
    print("This may take a moment...")
    
    results = scan_directory(directory)
    
    if not results:
        print("✅ No syntax errors found!")
        return 0
    
    print_error_summary(results)
    print_detailed_errors(results, args.max_files)
    
    if args.output:
        with open(args.output, 'w') as f:
            import json
            json.dump(results, f, indent=2)
        print(f"\nDetailed results saved to: {args.output}")
    
    return 1 if results else 0


if __name__ == "__main__":
    sys.exit(main())
