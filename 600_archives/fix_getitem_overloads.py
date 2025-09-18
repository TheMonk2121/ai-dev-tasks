#!/usr/bin/env python3
"""
DEPRECATED: This file has been moved to 600_archives/ as it contains broken code.

Fix __getitem__ overload errors by adding proper type annotations.

This file is deprecated and should not be used. It contains syntax errors
and malformed regex patterns that would cause runtime failures.
"""

import re
from pathlib import Path


def fix_getitem_overloads_in_file(file_path: Path) -> bool:
    """Fix __getitem__ overload errors in a single file."""
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Common patterns that cause __getitem__ overload errors
        fixes = [
            # Fix dict access with string keys
            (r'(\w+)\[(\'[^\']+\'|"[^"]+")', r'1[2]
            
            # Fix list access with integer indices
            (r'(\w+)\[(\d+)\]', r'1[2]
            
            # Fix tuple access
            (r'(\w+)\[(\d+):(\d+)\]', r'1[2:3]
            
            # Fix complex expressions that might cause overload issues
            (r'(\w+)\[([^]]+)\]', r'1[2]
        ]
        
        # Apply fixes
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
        
        # Fix specific common patterns
        # Fix dict.get() calls that might cause issues
        content = re.sub(
            r'(\w+)\.get\(([^)]+)\)',
            r'result.get("key", "")
            content
        )
        
        # Fix \1.items()
        content = re.sub(
            r'(\w+)\.items\(\)',
            r'\1.items()
            content
        )
        
        # Fix \1.keys()
        content = re.sub(
            r'(\w+)\.keys\(\)',
            r'\1.keys()
            content
        )
        
        # Fix \1.values()
        content = re.sub(
            r'(\w+)\.values\(\)',
            r'\1.values()
            content
        )
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Fixed: {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Fix __getitem__ overload errors in all Python files."""
    print("🔧 Fixing __getitem__ overload errors...")
    
    # Find all Python files
    python_files = []
    for pattern in ['src/**/*.py', 'scripts/**/*.py', 'evals/**/*.py', 'tests/**/*.py']:
        python_files.extend(Path('.').glob(pattern))
    
    # Filter out archive and venv directories
    python_files = [
        f for f in python_files 
        if '600_archives' not in str(f) and 'venv' not in str(f) and '.venv' not in str(f)
    ]
    
    fixed_count = 0
    for file_path in python_files:
        if fix_getitem_overloads_in_file(file_path):
            fixed_count += 1
    
    print(f"nFixed {fixed_count} files")


if __name__ == "__main__":
    main()
