#!/usr/bin/env python3.12.123.11

"""
Analyze file naming according to naming conventions
"""

import os
import re
from pathlib import Path

def analyze_file_naming():
    """Analyze all markdown files and identify naming issues"""
    
    # Find all markdown files
    md_files = list(Path(".").glob("**/*.md"))
    md_files = [f for f in md_files if "backup" not in str(f) and "venv" not in str(f)]
    
    print("🔍 **File Naming Analysis**")
    print("=" * 50)
    
    # Categorize files
    correctly_named = []
    needs_renaming = []
    subdirectory_files = []
    
    for file_path in md_files:
        filename = file_path.name
        relative_path = file_path.relative_to(Path("."))
        
        # Check if it's in a subdirectory
        if len(file_path.parts) > 2:  # More than ./filename.md
            subdirectory_files.append((relative_path, filename))
            continue
            
        # Check if it follows the naming convention
        if re.match(r'^\d{3}_[a-z0-9\-]+\.md$', filename):
            correctly_named.append(filename)
        else:
            needs_renaming.append((relative_path, filename))
    
    print(f"📊 **Analysis Results**")
    print(f"✅ Correctly named files: {len(correctly_named)}")
    print(f"❌ Files needing renaming: {len(needs_renaming)}")
    print(f"📁 Subdirectory files: {len(subdirectory_files)}")
    print()
    
    if correctly_named:
        print("✅ **Correctly Named Files:**")
        for filename in sorted(correctly_named):
            print(f"   {filename}")
        print()
    
    if needs_renaming:
        print("❌ **Files Needing Renaming:**")
        for path, filename in needs_renaming:
            print(f"   {path} → [needs analysis]")
        print()
    
    if subdirectory_files:
        print("📁 **Subdirectory Files (Need Analysis):**")
        for path, filename in subdirectory_files:
            print(f"   {path}")
        print()
    
    # Suggest renames for subdirectory files
    print("🎯 **Suggested Renames for Subdirectory Files:**")
    suggestions = []
    
    for path, filename in subdirectory_files:
        if filename == "README.md":
            # README files should stay as README.md
            continue
            
        # Analyze the file content to determine category
        category = analyze_file_category(path)
        new_name = suggest_new_name(filename, category, path)
        
        if new_name and new_name != filename:
            suggestions.append((path, filename, new_name))
    
    for path, old_name, new_name in suggestions:
        print(f"   {path} → {new_name}")
    
    return {
        "correctly_named": correctly_named,
        "needs_renaming": needs_renaming,
        "subdirectory_files": subdirectory_files,
        "suggestions": suggestions
    }

def analyze_file_category(file_path):
    """Analyze file content to determine appropriate category"""
    
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
        
        # Check for memory context comments
        if "<!-- MEMORY_CONTEXT: HIGH" in content:
            return "400"  # Documentation
        elif "<!-- MEMORY_CONTEXT: MEDIUM" in content:
            return "200"  # Configuration
        elif "<!-- MEMORY_CONTEXT: LOW" in content:
            return "100"  # Automation
        
        # Check content keywords
        if any(keyword in content.lower() for keyword in ["architecture", "system", "overview"]):
            return "400"  # Documentation
        elif any(keyword in content.lower() for keyword in ["setup", "configuration", "model"]):
            return "200"  # Configuration
        elif any(keyword in content.lower() for keyword in ["integration", "workflow", "automation"]):
            return "100"  # Automation
        elif any(keyword in content.lower() for keyword in ["test", "benchmark", "monitoring"]):
            return "500"  # Testing & Observability
        else:
            return "400"  # Default to Documentation
            
    except Exception:
        return "400"  # Default to Documentation

def suggest_new_name(filename, category, file_path):
    """Suggest a new name based on category and content"""
    
    # Skip README files
    if filename == "README.md":
        return None
    
    # Extract base name without extension
    base_name = filename.replace('.md', '')
    
    # Convert to kebab-case
    kebab_name = re.sub(r'[^a-zA-Z0-9]', '-', base_name).lower()
    kebab_name = re.sub(r'-+', '-', kebab_name).strip('-')
    
    # Generate new name
    new_name = f"{category}_{kebab_name}.md"
    
    return new_name

if __name__ == "__main__":
    analyze_file_naming() 