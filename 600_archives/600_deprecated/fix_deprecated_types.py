#!/usr/bin/env python3
"""
DEPRECATED: Fix deprecated type usage across the codebase.

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
        
        # Fix Type | None -> Type | None
        content = re.sub(r'Optional\[([^\]]+)\]', r'\1 | None', content)
        
        # Fix Type1, Type2 -> Type1 | Type2
        content = re.sub(r'Union\[([^\]]+)\]', r'\1', content)
        
        # Remove unused Optional and Union imports
        lines: Any = content.split('\n')
        new_lines = []
        for line in lines:
            # Skip lines that only import Optional or Union
            if re.match(r'^from typing import.*Optional.*$', line.strip()) and not re.search(r'Optional\[', content):
                continue
            if re.match(r'^from typing import.*Union.*$', line.strip()) and not re.search(r'Union\[', content):
                continue
            # Skip lines that import only Optional or Union
            if re.match(r'^from typing import (Optional|Union)$', line.strip()):
                continue
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
    
    parser: Any = argparse.ArgumentParser(description="Fix deprecated type usage")
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
