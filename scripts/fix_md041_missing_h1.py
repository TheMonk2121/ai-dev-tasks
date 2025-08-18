#!/usr/bin/env python3.12.123.11
"""
Fix MD041 - First line in a file should be a top-level heading.
Adds H1 headings to files that don't have them.
"""

import re
import os
import glob

def extract_title_from_filename(file_path):
    """Extract a title from the filename."""
    # Get the filename without extension
    filename = os.path.basename(file_path)
    name_without_ext = os.path.splitext(filename)[0]
    
    # Remove common prefixes and convert to title case
    title = name_without_ext
    
    # Remove numeric prefixes like "400_", "100_", etc.
    title = re.sub(r'^\d+_', '', title)
    
    # Convert underscores and hyphens to spaces
    title = re.sub(r'[_-]', ' ', title)
    
    # Convert to title case
    title = title.title()
    
    # Handle special cases
    if title.lower() == 'readme':
        return 'README'
    elif title.lower() == 'index':
        return 'Index'
    
    return title

def extract_title_from_content(content):
    """Attempt to extract a title from the content."""
    lines = content.split('\n')
    
    # Look for existing headings
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if line.startswith('#'):
            # Extract text from heading
            title = re.sub(r'^#+\s*', '', line)
            return title
    
    # Look for patterns that might indicate a title
    for line in lines[:10]:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('<!--'):
            # Check if it looks like a title (not too long, not a list item, etc.)
            if len(line) < 100 and not line.startswith('-') and not line.startswith('*'):
                return line
    
    return None

def fix_md041_missing_h1():
    """Fix MD041 violations by adding H1 headings to files that don't have them."""
    print("🔧 Fixing MD041 - Missing H1 Headings")
    print("=" * 60)
    
    # Find all markdown files
    markdown_files = []
    for pattern in ['**/*.md', '**/*.markdown']:
        markdown_files.extend(glob.glob(pattern, recursive=True))
    
    # Remove files in certain directories
    markdown_files = [f for f in markdown_files if not any(exclude in f for exclude in [
        'node_modules', '.git', '__pycache__', '.pytest_cache', 'venv'
    ])]
    
    print(f"Found {len(markdown_files)} markdown files")
    
    files_fixed = 0
    files_failed = 0
    files_unchanged = 0
    
    for file_path in markdown_files:
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Check if file already has an H1 heading
            lines = content.split('\n')
            has_h1 = False
            
            for line in lines[:10]:  # Check first 10 lines
                if line.strip().startswith('# '):
                    has_h1 = True
                    break
            
            if has_h1:
                files_unchanged += 1
                continue
            
            # Determine the title
            title = extract_title_from_content(content)
            if not title:
                title = extract_title_from_filename(file_path)
            
            # Add H1 heading at the beginning
            if content.startswith('<!--'):
                # If file starts with HTML comment, add heading after it
                lines = content.split('\n')
                insert_index = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('<!--'):
                        insert_index = i + 1
                    else:
                        break
                
                lines.insert(insert_index, f'# {title}')
                lines.insert(insert_index + 1, '')  # Add blank line
                content = '\n'.join(lines)
            else:
                # Add heading at the very beginning
                content = f'# {title}\n\n{content}'
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Fixed: {file_path} (Added: # {title})")
                files_fixed += 1
            else:
                files_unchanged += 1
                
        except Exception as e:
            print(f"❌ Failed: {file_path} - {str(e)}")
            files_failed += 1
    
    print(f"\n📊 Summary:")
    print(f"  Files processed: {len(markdown_files)}")
    print(f"  Files fixed: {files_fixed}")
    print(f"  Files failed: {files_failed}")
    print(f"  Files unchanged: {files_unchanged}")
    
    if files_fixed > 0:
        print(f"\n🎉 Successfully fixed {files_fixed} files!")
    else:
        print(f"\nℹ️  No files needed fixing.")

if __name__ == "__main__":
    fix_md041_missing_h1()
