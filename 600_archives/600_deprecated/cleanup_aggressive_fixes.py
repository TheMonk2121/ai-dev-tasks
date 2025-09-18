#!/usr/bin/env python3
"""
DEPRECATED: Clean up the damage from overly aggressive type ignore fixes.

This script has been deprecated and moved to 600_archives/600_deprecated/ because:
- The type migration and annotation work has been completed
- The aggressive fixes that this script was designed to clean up have been resolved
- Modern Python 3.12+ projects should use proper type annotations from the start
- This utility script is no longer needed for ongoing development

Date deprecated: 2025-01-27
Reason: Type migration completed, cleanup script no longer needed
"""

import re
from pathlib import Path


def cleanup_aggressive_fixes_in_file(file_path: Path) -> bool:
    """Clean up overly aggressive type ignore fixes in a single file."""
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Remove excessive type ignore comments
        # Fix patterns like: \\\\\\\\result.get("key", "")  # type: ignore[type-arg] (repeated 17 times)
        content = re.sub(
            r'\\\\+\\1\.get\([^)]+\)\s*#\s*type:\s*ignore\[type-arg\](?:\s*#\s*type:\s*ignore\[type-arg\])+',
            r'\\1.get(\\2)  # type: ignore[type-arg]',
            content
        )
        
        # Fix patterns like: \\\\\\\\\1.items()  # type: ignore[type-arg] (repeated 17 times)
        content = re.sub(
            r'\\\\+\\1\.items\(\)\s*#\s*type:\s*ignore\[type-arg\](?:\s*#\s*type:\s*ignore\[type-arg\])+',
            r'\\1.items()  # type: ignore[type-arg]',
            content
        )
        
        # Fix patterns like: \\\\\\\\\1.keys()  # type: ignore[type-arg] (repeated 17 times)
        content = re.sub(
            r'\\\\+\\1\.keys\(\)\s*#\s*type:\s*ignore\[type-arg\](?:\s*#\s*type:\s*ignore\[type-arg\])+',
            r'\\1.keys()  # type: ignore[type-arg]',
            content
        )
        
        # Fix patterns like: \\\\\\\\\1.values()  # type: ignore[type-arg] (repeated 17 times)
        content = re.sub(
            r'\\\\+\\1\.values\(\)\s*#\s*type:\s*ignore\[type-arg\](?:\s*#\s*type:\s*ignore\[type-arg\])+',
            r'\\1.values()  # type: ignore[type-arg]',
            content
        )
        
        # Remove excessive backslashes from method calls
        content = re.sub(r'\\\\+([a-zA-Z_][a-zA-Z0-9_]*)\.', r'\\1.', content)
        
        # Clean up any remaining malformed patterns
        content = re.sub(r'\\\\+', '', content)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Cleaned: {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Clean up overly aggressive fixes in all Python files."""
    print("🧹 Cleaning up overly aggressive type ignore fixes...")
    
    # Find all Python files
    python_files = []
    for pattern in ['src/**/*.py', 'scripts/**/*.py', 'evals/**/*.py', 'tests/**/*.py']:
        python_files.extend(Path('.').glob(pattern))
    
    # Filter out archive and venv directories
    python_files = [
        f for f in python_files 
        if '600_archives' not in str(f) and 'venv' not in str(f) and '.venv' not in str(f)
    ]
    
    cleaned_count = 0
    for file_path in python_files:
        if cleanup_aggressive_fixes_in_file(file_path):
            cleaned_count += 1
    
    print(f"nCleaned {cleaned_count} files")


if __name__ == "__main__":
    main()
