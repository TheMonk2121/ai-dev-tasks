#!/usr/bin/env python3
"""
Cursor Memory Context Updater

Automatically updates CURSOR_MEMORY_CONTEXT.md based on current backlog state
and system status. This ensures Cursor AI always has current context.
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

def extract_backlog_priorities():
    """Extract current priorities from 000_backlog.md"""
    backlog_file = Path("000_backlog.md")
    if not backlog_file.exists():
        return []
    
    priorities = []
    current_section = None
    
    with open(backlog_file, 'r') as f:
        content = f.read()
    
    # Extract todo items with 🔥 priority
    lines = content.split('\n')
    for line in lines:
        if '| B‑' in line and '🔥' in line and 'todo' in line:
            # Parse backlog item
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 8:
                item_id = parts[1].strip()
                title = parts[2].strip()
                points = parts[3].strip()
                problem = parts[5].strip()
                
                # Clean up the problem description
                problem = problem.replace('<!--score:', '').replace('-->', '').strip()
                
                priorities.append({
                    'id': item_id,
                    'title': title,
                    'points': points,
                    'problem': problem
                })
    
    return priorities[:3]  # Top 3 priorities

def extract_completed_items():
    """Extract recently completed items"""
    backlog_file = Path("000_backlog.md")
    if not backlog_file.exists():
        return []
    
    completed = []
    
    with open(backlog_file, 'r') as f:
        content = f.read()
    
    # Look for completed items section
    if '## ✅ **Completed Items**' in content:
        completed_section = content.split('## ✅ **Completed Items**')[1].split('##')[0]
        
        # Extract last 3 completed items
        lines = completed_section.split('\n')
        for line in lines:
            if '| C‑' in line and '✅ done' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 6:
                    item_id = parts[1].strip()
                    title = parts[2].strip()
                    completion_date = parts[5].strip()
                    
                    completed.append({
                        'id': item_id,
                        'title': title,
                        'date': completion_date
                    })
    
    return completed[-3:]  # Last 3 completed

def update_memory_context():
    """Update CURSOR_MEMORY_CONTEXT.md with current state"""
    
    # Extract current state
    priorities = extract_backlog_priorities()
    completed = extract_completed_items()
    
    # Read current memory context
    memory_file = Path("100_cursor-memory-context.md")
    if not memory_file.exists():
        print("❌ 100_cursor-memory-context.md not found")
        return
    
    with open(memory_file, 'r') as f:
        content = f.read()
    
    # Update priorities section
    if priorities:
        priorities_text = "\n### **Immediate Focus (Next 1-2 weeks)**\n"
        for i, priority in enumerate(priorities, 1):
            priorities_text += f"{i}. **{priority['id']}**: {priority['title']} ({priority['points']} points)\n"
            priorities_text += f"   - {priority['problem']}\n"
        
        # Replace existing priorities section
        content = re.sub(
            r'### \*\*Immediate Focus \(Next 1-2 weeks\)\*\*.*?(?=### \*\*Infrastructure Status\*\*)',
            priorities_text,
            content,
            flags=re.DOTALL
        )
    
    # Update completed items
    if completed:
        completed_text = "\n### **Recently Completed**\n"
        for item in completed:
            completed_text += f"- ✅ **{item['id']}**: {item['title']} ({item['date']})\n"
        
        # Add after infrastructure status
        if '### **Infrastructure Status**' in content:
            infrastructure_section = content.split('### **Infrastructure Status**')[1]
            if '### **Recently Completed**' not in infrastructure_section:
                # Insert after infrastructure status
                content = re.sub(
                    r'(### \*\*Infrastructure Status\*\*.*?)(\n## )',
                    r'\1' + completed_text + r'\2',
                    content,
                    flags=re.DOTALL
                )
    
    # Update timestamp
    content = re.sub(
        r'\*Last Updated: \d{4}-\d{2}-\d{2}\*',
        f'*Last Updated: {datetime.now().strftime("%Y-%m-%d")}*',
        content
    )
    
    # Write updated content
    with open(memory_file, 'w') as f:
        f.write(content)
    
    print("✅ 100_cursor-memory-context.md updated successfully")
    print(f"📋 Current priorities: {len(priorities)} items")
    print(f"✅ Recent completions: {len(completed)} items")

def main():
    """Main function"""
    print("🧠 Updating Cursor Memory Context...")
    
    try:
        update_memory_context()
        print("✅ Memory context updated successfully")
    except Exception as e:
        print(f"❌ Error updating memory context: {e}")

if __name__ == "__main__":
    main() 