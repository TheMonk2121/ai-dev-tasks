#!/usr/bin/env python3
"""
Fix only the safest corruption patterns in Python files.
"""

import os
import re
import subprocess
from pathlib import Path


def get_corrupted_files():
    """Get list of files with syntax errors."""
    try:
        result = subprocess.run(
            ["uv", "run", "python", "-m", "ruff", "check", "scripts/"],
            capture_output=True,
            text=True
        )
        
        corrupted_files = []
        lines = result.stdout.split('\n')
        
        for line in lines:
            if '-->' in line and 'scripts/' in line and '.py:' in line:
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


def fix_safe_patterns(file_path: Path) -> bool:
    """Fix only the safest corruption patterns in a single file."""
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix 1: result.get("key", "") -> result (simple string replacement)
        content = content.replace('result.get("key", "")', 'result')
        
        # Fix 2: \1.items() -> .items() (simple string replacement)
        content = content.replace('\\1.items()', '.items()')
        content = content.replace('\\1.keys()', '.keys()')
        content = content.replace('\\1.values()', '.values()')
        
        # Fix 3: Incomplete f-strings with result.get artifacts (simple string replacement)
        content = re.sub(r'f"([^"]*)\{result\.get\("key", ""\)\}([^"]*)"', r'f"\1{result}\2"', content)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def main():
    """Main fix process."""
    print("🔍 Finding corrupted files...")
    corrupted_files = get_corrupted_files()
    
    if not corrupted_files:
        print("✅ No corrupted files found!")
        return
    
    print(f"📊 Found {len(corrupted_files)} corrupted files")
    
    # Fix files in batches of 10
    fixed_count = 0
    for i in range(0, len(corrupted_files), 10):
        batch = corrupted_files[i:i+10]
        print(f"\n🔧 Fixing batch {i//10 + 1} ({len(batch)} files)...")
        
        for file_path in batch:
            if fix_safe_patterns(Path(file_path)):
                fixed_count += 1
                print(f"  ✅ Fixed {file_path}")
    
    print(f"\n✅ Fixed {fixed_count} files")
    print("💡 Run 'uv run python -m ruff check scripts/' to verify fixes")


if __name__ == "__main__":
    main()
