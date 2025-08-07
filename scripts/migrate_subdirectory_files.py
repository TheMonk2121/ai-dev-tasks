#!/usr/bin/env python3

"""
Migrate subdirectory files to main directory with proper naming conventions
"""

import os
import shutil
from pathlib import Path

def migrate_subdirectory_files():
    """Migrate subdirectory files to main directory with proper naming"""
    
    # Files to migrate with their new names
    migrations = [
        {
            "source": "dspy-rag-system/docs/DSPY_INTEGRATION_GUIDE.md",
            "target": "400_dspy-integration-guide.md",
            "category": "Documentation"
        },
        {
            "source": "dspy-rag-system/docs/mistral7b_instruct_integration_guide.md",
            "target": "400_mistral7b-instruct-integration-guide.md",
            "category": "Documentation"
        },
        {
            "source": "dspy-rag-system/docs/N8N_SETUP_GUIDE.md",
            "target": "400_n8n-setup-guide.md",
            "category": "Documentation"
        },
        {
            "source": "dspy-rag-system/docs/MISSION_DASHBOARD_GUIDE.md",
            "target": "400_mission-dashboard-guide.md",
            "category": "Documentation"
        },
        {
            "source": "dspy-rag-system/docs/N8N_BACKLOG_SCRUBBER_GUIDE.md",
            "target": "400_n8n-backlog-scrubber-guide.md",
            "category": "Documentation"
        },
        {
            "source": "dspy-rag-system/docs/CURRENT_STATUS.md",
            "target": "400_current-status.md",
            "category": "Documentation"
        }
    ]
    
    print("🚀 **Subdirectory File Migration**")
    print("=" * 50)
    
    # Create backup directory
    backup_dir = "backup_before_subdirectory_migration"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"📦 Created backup directory: {backup_dir}")
    
    migrated_files = []
    
    for migration in migrations:
        source_path = Path(migration["source"])
        target_path = Path(migration["target"])
        
        if source_path.exists():
            # Backup original
            backup_path = Path(backup_dir) / source_path.name
            shutil.copy2(source_path, backup_path)
            
            # Move file to main directory
            shutil.move(str(source_path), str(target_path))
            migrated_files.append((source_path, target_path))
            print(f"✅ Migrated: {source_path} → {target_path}")
            
            # Update file content to reflect new location
            update_file_references(target_path, source_path.name, target_path.name)
        else:
            print(f"⚠️  File not found: {source_path}")
    
    if migrated_files:
        print(f"\n🎉 Migration completed!")
        print(f"📦 Backup files available in: {backup_dir}")
        print(f"📋 Migrated {len(migrated_files)} files")
    else:
        print("\nℹ️  No files to migrate")

def update_file_references(file_path, old_name, new_name):
    """Update references to the old filename in the migrated file"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update any internal references
        if old_name in content:
            new_content = content.replace(old_name, new_name)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  ✅ Updated references in {file_path.name}")
            
    except Exception as e:
        print(f"  ⚠️  Error updating {file_path.name}: {e}")

if __name__ == "__main__":
    migrate_subdirectory_files() 