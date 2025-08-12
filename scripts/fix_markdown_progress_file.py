#!/usr/bin/env python3
"""
Fix markdown issues in the 400_markdown-cleanup-progress.md file.
Addresses MD022 (heading spacing), MD032 (list spacing), and MD029 (ordered list prefix).
"""

import re
import os

def fix_markdown_progress_file():
    """Fix markdown issues in the progress file."""
    file_path = "400_markdown-cleanup-progress.md"
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix MD022: Add blank lines around headings
    # Pattern: heading line followed by non-blank line
    content = re.sub(r'^(#{1,6}\s+.*?)$\n(?!\n)', r'\1\n\n', content, flags=re.MULTILINE)
    
    # Fix MD032: Add blank lines around lists
    # Pattern: list item not preceded by blank line
    content = re.sub(r'^([^\n]*\n)([-*+]\s+)', r'\1\n\2', content, flags=re.MULTILINE)
    # Pattern: list item not followed by blank line
    content = re.sub(r'^([-*+]\s+.*?)$\n(?!\n)', r'\1\n\n', content, flags=re.MULTILINE)
    
    # Fix MD029: Fix ordered list numbering
    # Find all ordered lists and renumber them properly
    lines = content.split('\n')
    fixed_lines = []
    in_ordered_list = False
    list_counter = 1
    
    for i, line in enumerate(lines):
        # Check if this is an ordered list item
        ordered_match = re.match(r'^(\s*)(\d+)\.\s+(.+)$', line)
        
        if ordered_match:
            indent, number, rest = ordered_match.groups()
            if not in_ordered_list:
                # Start of new list
                in_ordered_list = True
                list_counter = 1
                # Add blank line before list if needed
                if i > 0 and lines[i-1].strip() != '':
                    fixed_lines.append('')
            
            # Fix the numbering
            fixed_lines.append(f"{indent}{list_counter}. {rest}")
            list_counter += 1
        else:
            if in_ordered_list:
                # End of list
                in_ordered_list = False
                # Add blank line after list if needed
                if line.strip() != '':
                    fixed_lines.append('')
            
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Additional fixes for specific patterns in this file
    # Fix the numbered lists in the "Next Steps" section
    content = re.sub(r'^(\d+)\.\s+\*\*([^*]+)\*\*', r'\1. **\2**', content, flags=re.MULTILINE)
    
    # Fix the numbered lists in the "Current Issue Distribution" section
    content = re.sub(r'^(\d+)\.\s+\*\*([^*]+)\*\*', r'\1. **\2**', content, flags=re.MULTILINE)
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    if content != original_content:
        print(f"✅ Fixed markdown issues in {file_path}")
        return True
    else:
        print(f"ℹ️  No changes needed for {file_path}")
        return False

if __name__ == "__main__":
    fix_markdown_progress_file()

