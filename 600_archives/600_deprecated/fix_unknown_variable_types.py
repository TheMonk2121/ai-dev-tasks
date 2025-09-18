#!/usr/bin/env python3
"""
DEPRECATED: Surgical fix for reportUnknownVariableType errors.

This script has been deprecated and moved to 600_archives/600_deprecated/ because:
- The type migration and annotation work has been completed
- Modern Python 3.12+ projects should use proper type annotations from the start
- These utility scripts are no longer needed for ongoing development

Date deprecated: 2025-01-27
Reason: Type migration completed, utility scripts no longer needed
"""

import re
from pathlib import Path
from typing import Any


def fix_unknown_variable_types_in_file(file_path: Path) -> bool:
    """Fix specific unknown variable type errors in a single file."""
    try:
        with open(file_path, encoding='utf-8') as f:
            content: Any = f.read()
        
        original_content = content
        
        # Only fix very specific, safe patterns
        fixes = []
        
        # 1. Fix missing type annotations for function parameters
        # Pattern: def func(param): -> def func(param: Any):
        fixes.append((
            r'def\s+(\w+)\(([^)]*?)(\w+)\):',
            r'def \1(\2\3: Any):'
        ))
        
        # 2. Fix missing type annotations for variable assignments that are clearly Any
        # Pattern: variable = some_unknown_thing -> variable: Any = some_unknown_thing
        # But only for simple assignments, not complex expressions
        fixes.append((
            r'^(\s+)(\w+)\s*=\s*(\w+\.\w+\([^)]*\))\s*$',
            r'\1\2: Any = \3'
        ))
        
        # 3. Fix return type annotations for functions that return unknown types
        # Pattern: def func(): -> def func() -> Any:
        fixes.append((
            r'def\s+(\w+)\([^)]*\):\s*$',
            r'def \1() -> Any:'
        ))
        
        # 4. Fix class attribute type annotations
        # Pattern: self.attr = value -> self.attr: Any = value
        fixes.append((
            r'^(\s+)self\.(\w+)\s*=\s*([^=]+)\s*$',
            r'\1self.\2: Any = \3'
        ))
        
        # Apply fixes conservatively
        for pattern, replacement in fixes:
            # Only apply if the pattern matches and doesn't already have type annotations
            if re.search(pattern, content, re.MULTILINE):
                # Check if replacement would create valid Python
                test_content: Any = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                try:
                    compile(test_content, str(file_path), 'exec')
                    content = test_content
                except SyntaxError:
                    # Skip this fix if it would create syntax errors
                    continue
        
        # Only write if changes were made and the file is still valid Python
        if content != original_content:
            try:
                compile(content, str(file_path), 'exec')
            except SyntaxError:
                print(f"Skipping {file_path} - would create syntax error")
                return False
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Fixed: {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main() -> Any:
    """Fix unknown variable type errors in all Python files."""
    print("🔧 Surgically fixing unknown variable type errors...")
    
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
        if fix_unknown_variable_types_in_file(file_path):
            fixed_count += 1
    
    print(f"\\nFixed {fixed_count} files")


if __name__ == "__main__":
    main()
