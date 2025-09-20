#!/usr/bin/env python3
"""
Safely fix corruption patterns in Python files without deleting anything.

This script identifies and fixes specific corruption patterns:
- result.get("key", "") -> result
- \1.items() -> .items()
- \1.keys() -> .keys()
- \1.values() -> .values()
- Incomplete f-strings
- Missing colons in for loops
"""

import os
import re
import subprocess
from pathlib import Path


def get_corrupted_files():
    """Get list of files with syntax errors."""
    try:
        result = subprocess.run(
            ["uv", "run", "python", "-m", "ruff", "check", "."],
            capture_output=True,
            text=True
        )
        
        corrupted_files = []
        lines = result.stdout.split('\n')
        
        for line in lines:
            if '-->' in line and '.py:' in line:
                # Extract file path
                file_path = line.split('-->')[1].split(':')[0].strip()
                # Remove ANSI escape codes
                file_path = file_path.replace('\x1b[94m', '').replace('\x1b[0m', '')
                # Remove leading/trailing whitespace
                file_path = file_path.strip()
                if file_path and file_path not in corrupted_files:
                    corrupted_files.append(file_path)
        
        return corrupted_files
    except Exception as e:
        print(f"Error getting corrupted files: {e}")
        return []


def fix_file_safely(file_path: Path) -> bool:
    """Safely fix corruption patterns in a single file."""
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix 1: result.get("key", "") -> result
        content = re.sub(r'result\.get\("key", ""\)', 'result', content)
        
        # Fix 2: \1.items() -> .items()
        content = re.sub(r'\\1\.items\(\)', '.items()', content)
        content = re.sub(r'\\1\.keys\(\)', '.keys()', content)
        content = re.sub(r'\\1\.values\(\)', '.values()', content)
        
        # Fix 3: Incomplete for loops - add missing colons
        content = re.sub(r'for\s+([^:]+)\s+in\s+([^:]+)\s*$', r'for \1 in \2:', content, flags=re.MULTILINE)
        
        # Fix 4: Incomplete if statements - add missing colons
        content = re.sub(r'if\s+([^:]+)\s*$', r'if \1:', content, flags=re.MULTILINE)
        
        # Fix 5: Fix incomplete f-strings
        content = re.sub(r'f"([^"]*)\{result\.get\("key", ""\)\}([^"]*)"', r'f"\1{result}\2"', content)
        
        # Fix 6: Fix incomplete function calls
        content = re.sub(r'(\w+)\s*\(\s*([^)]*)\s*$', r'\1(\2)', content, flags=re.MULTILINE)
        
        # Only write if content changed
        if content != original_content:
            # Create backup
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Fixed {file_path} (backup: {backup_path})")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def main():
    """Main fix process."""
    print("🔍 Finding corrupted files...")
    corrupted_files = get_corrupted_files()
    
    if not corrupted_files:
        print("✅ No corrupted files found!")
        return
    
    print(f"📊 Found {len(corrupted_files)} corrupted files")
    
    # Focus on critical files first
    critical_patterns = [
        "evaluation",
        "scripts",
        "src",
        "tests"
    ]
    
    critical_files = []
    other_files = []
    
    for file_path in corrupted_files:
        if any(pattern in file_path for pattern in critical_patterns):
            critical_files.append(file_path)
        else:
            other_files.append(file_path)
    
    print(f"🎯 Critical files: {len(critical_files)}")
    print(f"📁 Other files: {len(other_files)}")
    
    # Fix critical files first (limit to 20 for safety)
    fixed_count = 0
    for file_path in critical_files[:20]:
        print(f"\n🔧 Fixing {file_path}...")
        if fix_file_safely(Path(file_path)):
            fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} critical files")
    print("💡 Run 'uv run ruff check .' to verify fixes")
    print("💡 Backup files created with .backup extension")


if __name__ == "__main__":
    main()
