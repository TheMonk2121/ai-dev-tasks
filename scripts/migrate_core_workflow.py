#!/usr/bin/env python3

import os
import shutil
import re
from pathlib import Path

def migrate_core_workflow():
    """Migrate core workflow files from two-digit to three-digit prefixes."""
    
    # Migration mapping for core workflow files
    MIGRATION_MAP = {
        "00_backlog.md": "000_backlog.md",
        "01_create-prd.md": "001_create-prd.md", 
        "02_generate-tasks.md": "002_generate-tasks.md",
        "03_process-task-list.md": "003_process-task-list.md"
    }
    
    print("🚀 **Core Workflow Migration**")
    print("=" * 50)
    
    # Create backup directory
    backup_dir = "backup_before_core_migration"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"📦 Created backup directory: {backup_dir}")
    
    migrated_files = []
    
    for old_name, new_name in MIGRATION_MAP.items():
        if os.path.exists(old_name):
            # Backup original
            shutil.copy2(old_name, os.path.join(backup_dir, old_name))
            
            # Rename file
            shutil.move(old_name, new_name)
            migrated_files.append((old_name, new_name))
            print(f"✅ Renamed: {old_name} → {new_name}")
            
            # Update references in other files
            update_file_references(old_name, new_name)
        else:
            print(f"⚠️  File not found: {old_name}")
    
    if migrated_files:
        print(f"\n🎉 Core workflow migration completed!")
        print(f"📦 Backup files available in: {backup_dir}")
        print(f"📋 Migrated {len(migrated_files)} files")
    else:
        print("\nℹ️  No files to migrate")

def update_file_references(old_name, new_name):
    """Update references to the old filename in other markdown files."""
    
    # Find all markdown files
    md_files = list(Path(".").glob("*.md"))
    md_files.extend(Path("docs").glob("*.md"))
    md_files.extend(Path("dspy-rag-system").glob("*.md"))
    
    updated_files = []
    
    for file_path in md_files:
        if file_path.name in [old_name, new_name]:
            continue  # Skip the file being renamed
            
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
            
            # Check if file contains reference to old name
            if old_name in content:
                # Replace references
                new_content = content.replace(old_name, new_name)
                
                # Write updated content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                updated_files.append(file_path.name)
                print(f"  ✅ Updated references in {file_path.name}")
                
        except Exception as e:
            print(f"  ⚠️  Error updating {file_path.name}: {e}")
    
    if updated_files:
        print(f"  📝 Updated {len(updated_files)} files")

if __name__ == "__main__":
    migrate_core_workflow() 