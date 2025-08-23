#!/usr/bin/env python3
"""
Fix MD018 - No space after hash on atx style heading.
Adds spaces after hash symbols in headings like #Heading → # Heading.
"""

import glob
import re


def fix_md018_heading_spaces():
    """Fix MD018 violations by adding spaces after hash symbols in headings."""
    print("🔧 Fixing MD018 - Heading Hash Spaces")
    print("=" * 60)
    
    # Find all markdown files
    markdown_files = []
    for pattern in ["**/*.md", "**/*.markdown"]:
        markdown_files.extend(glob.glob(pattern, recursive=True))
    
    # Remove files in certain directories
    markdown_files = [
        f
        for f in markdown_files
        if not any(exclude in f for exclude in ["node_modules", ".git", "__pycache__", ".pytest_cache", "venv"])
    ]
    
    print(f"Found {len(markdown_files)} markdown files")
    
    files_fixed = 0
    files_failed = 0
    files_unchanged = 0
    total_fixes = 0
    
    for file_path in markdown_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            original_content = content
            
            # Fix headings without space after hash: #Heading → # Heading
            # Pattern: # followed by non-space character
            content = re.sub(r'^(#{1,6})([^#\s])', r'\1 \2', content, flags=re.MULTILINE)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                
                # Count the number of fixes
                original_issues = len(re.findall(r'^(#{1,6})([^#\s])', original_content, flags=re.MULTILINE))
                new_issues = len(re.findall(r'^(#{1,6})([^#\s])', content, flags=re.MULTILINE))
                fixes = original_issues - new_issues
                
                print(f"✅ Fixed: {file_path} ({fixes} headings)")
                files_fixed += 1
                total_fixes += fixes
            else:
                files_unchanged += 1
                
        except Exception as e:
            print(f"❌ Failed: {file_path} - {str(e)}")
            files_failed += 1
    
    print("\n📊 Summary:")
    print(f"  Files processed: {len(markdown_files)}")
    print(f"  Files fixed: {files_fixed}")
    print(f"  Files failed: {files_failed}")
    print(f"  Files unchanged: {files_unchanged}")
    print(f"  Total headings fixed: {total_fixes}")
    
    if files_fixed > 0:
        print(f"\n🎉 Successfully fixed {files_fixed} files!")
    else:
        print("\nℹ️  No files needed fixing.")

if __name__ == "__main__":
    fix_md018_heading_spaces()
