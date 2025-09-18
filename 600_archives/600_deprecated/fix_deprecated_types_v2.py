#!/usr/bin/env python3
"""
DEPRECATED: Fix deprecated type usage across the codebase - Improved version.

This script has been deprecated and moved to 600_archives/600_deprecated/ because:
- The type migration from Optional/Union to | syntax has been completed
- Modern Python 3.12+ projects should use the new union syntax natively
- The script is no longer needed for ongoing development

Date deprecated: 2025-01-27
Reason: Type migration completed, script no longer needed
"""

import os
import re
from pathlib import Path
from typing import Any


def fix_deprecated_types_in_file(file_path: Path) -> bool:
    """Fix deprecated types in a single file."""
    try:
        with open(file_path, encoding='utf-8') as f:
            content: Any = f.read()
        
        original_content = content
        
        # Fix Type | None -> Type | None (more precise regex)
        content = re.sub(r'Optional\[([^\]]+)\]', r'\1 | None', content)
        
        # Fix Type1 | Type2 -> Type1 | Type2 (handle multiple types)
        def fix_union(match: Any):
            types_str: Any = match.group(1)
            # Split by comma and join with |
            types = [t.strip() for t in types_str.split(',')]
            return ' | '.join(types)
        
        content = re.sub(r'Union\[([^\]]+)\]', fix_union, content)
        
        # Clean up imports more carefully
        lines: Any = content.split('\n')
        new_lines = []
        typing_imports = set()
        
        for line in lines:
            # Check if this line imports from typing
            if line.strip().startswith('from typing import'):
                # Extract what's being imported
                imports = line.strip().replace('from typing import ', '').split(',')
                imports = [imp.strip() for imp in imports]
                
                # Keep only what's actually used in the file
                for imp in imports:
                    if imp in content and imp not in ['Optional', 'Union']:
                        typing_imports.add(imp)
                
                # Only add the line if we have imports to keep
                if typing_imports:
                    new_line = f"from typing import {', '.join(sorted(typing_imports))}"
                    new_lines.append(new_line)
            else:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main() -> Any:
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix deprecated type usage (improved)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")
    parser.add_argument("--file", type=str, help="Specific file to process")
    
    args: Any = parser.parse_args()
    
    if args.file:
        files = [Path(args.file)]
    else:
        # Find Python files
        files = []
        for root, dirs, filenames in os.walk("."):
            if any(skip in root for skip in ["600_archives", "venv", ".venv", "__pycache__"]):
                continue
            for filename in filenames:
                if filename.endswith(".py"):
                    files.append(Path(root) / filename)
    
    changes_made = 0
    for file_path in files:
        if fix_deprecated_types_in_file(file_path):
            changes_made += 1
            if args.dry_run:
                print(f"Would fix: {file_path}")
            else:
                print(f"Fixed: {file_path}")
    
    print(f"\n{'Would fix' if args.dry_run else 'Fixed'} {changes_made} files")

if __name__ == "__main__":
    main()
