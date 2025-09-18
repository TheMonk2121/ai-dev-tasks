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
        lines: Any = content.split('\n')
        modified_lines = []
        
        for i, line in enumerate(lines):
            modified_line = line
            
            # 1. Fix simple variable assignments that are clearly Any type
            # Pattern: variable = some_function() -> variable: Any = some_function()
            if re.match(r'^(\s+)(\w+)\s*=\s*(\w+\.\w+\([^)]*\))\s*$', line):
                # Only if it doesn't already have a type annotation
                if ': ' not in line and '->' not in line:
                    modified_line = re.sub(
                        r'^(\s+)(\w+)\s*=\s*(\w+\.\w+\([^)]*\))\s*$',
                        r'\1\2: Any = \3',
                        line
                    )
            
            # 2. Fix function parameters that are clearly Any type
            # Pattern: def func(param): -> def func(param: Any):
            elif re.match(r'^(\s*)def\s+(\w+)\(([^)]*?)(\w+)\):', line):
                # Only if the parameter doesn't already have a type annotation
                if ': ' not in line:
                    modified_line = re.sub(
                        r'^(\s*)def\s+(\w+)\(([^)]*?)(\w+)\):',
                        r'\1def \2(\3\4: Any):',
                        line
                    )
            
            # 3. Fix return type annotations for functions that return unknown types
            # Pattern: def func(): -> def func() -> Any:
            elif re.match(r'^(\s*)def\s+(\w+)\([^)]*\):\s*$', line):
                # Only if it doesn't already have a return type annotation
                if '->' not in line:
                    modified_line = re.sub(
                        r'^(\s*)def\s+(\w+)\([^)]*\):\s*$',
                        r'\1def \2() -> Any:',
                        line
                    )
            
            # 4. Fix class attribute assignments
            # Pattern: self.attr = value -> self.attr: Any = value
            elif re.match(r'^(\s+)self\.(\w+)\s*=\s*([^=]+)\s*$', line):
                # Only if it doesn't already have a type annotation
                if ': ' not in line:
                    modified_line = re.sub(
                        r'^(\s+)self\.(\w+)\s*=\s*([^=]+)\s*$',
                        r'\1self.\2: Any = \3',
                        line
                    )
            
            # 5. Fix simple variable assignments in loops
            # Pattern: for item in items: -> for item: Any in items:
            elif re.match(r'^(\s+)for\s+(\w+)\s+in\s+', line):
                # Only if it doesn't already have a type annotation
                if ': ' not in line:
                    modified_line = re.sub(
                        r'^(\s+)for\s+(\w+)\s+in\s+',
                        r'\1for \2: Any in ',
                        line
                    )
            
            modified_lines.append(modified_line)
        
        # Join the lines back together
        modified_content = '\n'.join(modified_lines)
        
        # Only write if changes were made and the file is still valid Python
        if modified_content != original_content:
            try:
                compile(modified_content, str(file_path), 'exec')
            except SyntaxError:
                print(f"Skipping {file_path} - would create syntax error")
                return False
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
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
