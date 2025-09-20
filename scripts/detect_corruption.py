#!/usr/bin/env python3
"""
Corruption Detection Script

This script detects common corruption patterns that can be introduced
by automated tools or corrupted scripts. It exits with non-zero status
if corruption is detected.
"""

import os
import re
import sys
from pathlib import Path


def detect_corruption_markers(file_path: Path) -> list[str]:
    """Detect corruption markers in a file."""
    issues = []
    
    # Skip the detection script itself
    if file_path.name == "detect_corruption.py":
        return issues
    
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                # Check for common corruption patterns
                if 'result.get("key", "")' in line:
                    issues.append(f"{file_path}:{i}: Found corruption marker 'result.get(\"key\", \"\")'")
                
                if re.search(r'for \w+, \w+ in \.items\(\)', line):
                    issues.append(f"{file_path}:{i}: Found incomplete for loop with missing variable")
                
                if re.search(r'\.get\("key", ""\)', line):
                    issues.append(f"{file_path}:{i}: Found incomplete .get() call")
                
                if re.search(r'f"[^"]*\{[^}]*$', line):
                    issues.append(f"{file_path}:{i}: Found unterminated f-string")
                
                # Check for incomplete assertions (single line without proper message)
                # Skip multi-line assertions that are properly formatted
                if (re.search(r'^assert [^=]*$', line.strip()) and 
                    not line.strip().endswith(':') and 
                    not line.strip().endswith('"') and 
                    not line.strip().endswith(')') and
                    not line.strip().endswith('(') and
                    not line.strip().endswith(',')):
                    issues.append(f"{file_path}:{i}: Found incomplete assertion")
                    
    except Exception as e:
        issues.append(f"{file_path}:0: Error reading file: {e}")
    
    return issues


def main():
    """Main detection function."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/detect_corruption.py <path1> [path2] ...")
        sys.exit(1)
    
    all_issues = []
    
    for path_arg in sys.argv[1:]:
        path = Path(path_arg)
        
        if path.is_file() and path.suffix == '.py':
            issues = detect_corruption_markers(path)
            all_issues.extend(issues)
        elif path.is_dir():
            for py_file in path.rglob('*.py'):
                issues = detect_corruption_markers(py_file)
                all_issues.extend(issues)
    
    if all_issues:
        print("Corruption detected:")
        for issue in all_issues:
            print(f"  {issue}")
        sys.exit(1)
    else:
        print("No corruption detected")
        sys.exit(0)


if __name__ == "__main__":
    main()
