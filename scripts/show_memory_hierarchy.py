#!/usr/bin/env python3
"""
Memory Context Hierarchy Display

Shows the memory context hierarchy in a human-readable format
to help both humans and LLMs understand file priorities.
"""

import os
import re
from pathlib import Path

def extract_memory_context(file_path):
    """Extract memory context from file comments"""
    if not file_path.exists():
        return None
    
    with open(file_path) as f:
        content = f.read()
    
    # Look for MEMORY_CONTEXT comment
    match = re.search(r'<!-- MEMORY_CONTEXT: (\w+) - (.+?) -->', content)
    if match:
        return {
            'level': match.group(1),
            'description': match.group(2)
        }
    return None

def get_file_info(file_path):
    """Get basic file information"""
    if not file_path.exists():
        return None
    
    stat = file_path.stat()
    return {
        'size': stat.st_size,
        'modified': stat.st_mtime
    }

def display_memory_hierarchy():
    """Display the memory context hierarchy"""
    
    print("🧠 Memory Context Hierarchy")
    print("=" * 50)
    print()
    
    # Define the hierarchy
    hierarchy = {
        'HIGH': [
                    '100_cursor-memory-context.md',
        '400_system-overview.md', 
        '000_backlog.md',
        'README.md'
        ],
        'MEDIUM': [
            '001_create-prd.md',
            '002_generate-tasks.md',
            '003_process-task-list.md',
            '104_dspy-development-context.md'
        ],
        'LOW': [
            '103_yi-coder-integration.md',
            '100_backlog-guide.md'
        ]
    }
    
    for level, files in hierarchy.items():
        print(f"📋 {level} PRIORITY (Read {'First' if level == 'HIGH' else 'as Needed' if level == 'MEDIUM' else 'for Specific Tasks'})")
        print("-" * 40)
        
        for filename in files:
            file_path = Path(filename)
            memory_info = extract_memory_context(file_path)
            file_info = get_file_info(file_path)
            
            if file_path.exists():
                status = "✅"
                size_kb = file_info['size'] / 1024 if file_info else 0
                print(f"{status} {filename}")
                print(f"   📄 Size: {size_kb:.1f} KB")
                
                if memory_info:
                    print(f"   🧠 Context: {memory_info['description']}")
                else:
                    print(f"   🧠 Context: No memory context comment found")
            else:
                print(f"❌ {filename} (not found)")
            
            print()
    
    print("=" * 50)
    print("💡 Usage:")
    print("- HIGH: Read first for instant context")
    print("- MEDIUM: Read when working on specific workflows")
    print("- LOW: Read for detailed implementation")
    print()
    print("🔄 Update memory context: python3 scripts/update_cursor_memory.py")

def main():
    """Main function"""
    display_memory_hierarchy()

if __name__ == "__main__":
    main() 