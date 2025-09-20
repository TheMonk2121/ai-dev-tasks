#!/usr/bin/env python3
"""
Fix syntax artifacts specifically in evals files.
"""

import os
import re
from pathlib import Path


def fix_file(file_path: Path) -> bool:
    """Fix syntax artifacts in a single file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Fix incomplete f-strings with {result
        content = re.sub(r'f"([^"]*)\{result\s*$', r'f"\1{result}"', content, flags=re.MULTILINE)
        
        # Fix incomplete f-strings with {result in middle
        content = re.sub(r'f"([^"]*)\{result\s*([^"]*)"', r'f"\1{result}\2"', content)
        
        # Fix incomplete for loops with .items()
        content = re.sub(r'for \w+, \w+ in \.items\(\)', r'for key, value in result.items():', content)
        
        # Fix incomplete for loops with missing variable
        content = re.sub(r'for \w+ in result$', r'for item in result:', content, flags=re.MULTILINE)
        
        # Fix incomplete if statements
        content = re.sub(r'if result$', r'if result:', content, flags=re.MULTILINE)
        
        # Fix stray colons
        content = re.sub(r'^\s*:\s*$', '', content, flags=re.MULTILINE)
        
        # Fix incomplete expressions like "result" on its own line
        content = re.sub(r'^\s*result\s*$', r'        result = {}', content, flags=re.MULTILINE)
        
        # Fix incomplete list comprehensions
        content = re.sub(r'if "claude" in result:', r'if "claude" in model.lower():', content)
        
        # Fix incomplete function calls
        content = re.sub(r'print\(f"([^"]*)\{result\s*$', r'print(f"\1{result}")', content, flags=re.MULTILINE)
        
        # Fix incomplete for loops without colon
        content = re.sub(r'for \w+, \w+ in result\.items\(\)$', r'for key, value in result.items():', content, flags=re.MULTILINE)
        
        # Fix incomplete expressions with result
        content = re.sub(r'error_code = e\.result$', r'error_code = e.response[\'Error\'][\'Code\']', content, flags=re.MULTILINE)
        
        # Fix incomplete f-strings with result
        content = re.sub(r'f"([^"]*)\{result\}\s*$', r'f"\1{result}"', content, flags=re.MULTILINE)

        # Only write if content changed
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to fix syntax artifacts in evals files."""
    print("🔧 Fixing syntax artifacts in evals files...")

    # Find all Python files in evals directory
    evals_files = []
    for root, dirs, files in os.walk("evals"):
        for file in files:
            if file.endswith(".py"):
                evals_files.append(Path(root) / file)

    print(f"📁 Found {len(evals_files)} evals Python files to check")

    fixed_count = 0
    for file_path in evals_files:
        if fix_file(file_path):
            print(f"✅ Fixed: {file_path}")
            fixed_count += 1

    print(f"\n🎉 Fixed {fixed_count} evals files with syntax artifacts")


if __name__ == "__main__":
    main()
