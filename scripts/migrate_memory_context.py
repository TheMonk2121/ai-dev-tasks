#!/usr/bin/env python3.12.123.11
"""
Memory Context Migration Script

Updates all references from the old 100_cursor-memory-context.md to the new
modular memory context system with focused modules.
"""

import os
import re
import glob
from pathlib import Path
from typing import List, Dict, Tuple


class MemoryContextMigrator:
    """Migrates references from old memory context file to new modular system."""
    
    def __init__(self):
        self.old_file = "100_cursor-memory-context.md"
        self.new_core_file = "100_cursor-memory-context.md"
        self.modules = [
            "101_memory-context-safety.md",
            "102_memory-context-state.md", 
            "103_memory-context-workflow.md",
            "104_memory-context-guidance.md"
        ]
        
        # Mapping of old references to new modular references
        self.reference_mapping = {
            # Direct file references
            "100_cursor-memory-context.md": "100_cursor-memory-context.md",
            
            # Context-specific references
            "memory scaffold": "100_cursor-memory-context.md",
            "memory context": "100_cursor-memory-context.md",
            "cursor memory context": "100_cursor-memory-context.md",
            
            # Safety and requirements
            "CRITICAL SAFETY REQUIREMENTS": "101_memory-context-safety.md",
            "file analysis guide": "101_memory-context-safety.md",
            "documentation inventory": "101_memory-context-safety.md",
            
            # State and priorities
            "current project state": "102_memory-context-state.md",
            "current priorities": "102_memory-context-state.md",
            "infrastructure status": "102_memory-context-state.md",
            "recently completed": "102_memory-context-state.md",
            
            # Workflow and process
            "development workflow": "103_memory-context-workflow.md",
            "when to read what": "103_memory-context-workflow.md",
            "context-specific guidance": "103_memory-context-workflow.md",
            
            # Guidance and reference
            "quick reference": "104_memory-context-guidance.md",
            "documentation utilization": "104_memory-context-guidance.md",
            "task-specific guidance": "104_memory-context-guidance.md"
        }
    
    def find_files_to_update(self) -> list[str]:
        """Find all files that need to be updated."""
        files_to_update = []
        
        # Search for markdown files
        for pattern in ["*.md", "**/*.md"]:
            files_to_update.extend(glob.glob(pattern, recursive=True))
        
        # Filter out the new modular files and the old file
        exclude_files = [self.old_file] + self.modules + [self.new_core_file]
        files_to_update = [f for f in files_to_update if f not in exclude_files]
        
        return files_to_update
    
    def update_file_references(self, file_path: str) -> tuple[bool, list[str]]:
        """Update references in a single file."""
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            changes = []
            
            # Update direct file references
            if self.old_file in content:
                content = content.replace(self.old_file, self.new_core_file)
                changes.append(f"Updated direct reference: {self.old_file} → {self.new_core_file}")
            
            # Update context-specific references
            for old_ref, new_ref in self.reference_mapping.items():
                if old_ref in content and old_ref != self.old_file:
                    # Add module reference comments
                    if new_ref in self.modules:
                        module_comment = f"<!-- MODULE_REFERENCE: {new_ref} -->"
                        if module_comment not in content:
                            # Find a good place to add the module reference
                            if "<!--" in content:
                                # Add after existing comments
                                content = re.sub(
                                    r'(<!--[^>]*-->\s*)+',
                                    r'\g<0>' + module_comment + '\n',
                                    content,
                                    count=1
                                )
                            else:
                                # Add at the beginning
                                content = module_comment + '\n' + content
                        
                        changes.append(f"Added module reference: {new_ref}")
            
            # Update any remaining references to the old file
            content = re.sub(
                r'100_cursor-memory-context\.md',
                '100_cursor-memory-context.md',
                content
            )
            
            # Only write if content changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True, changes
            
            return False, []
            
        except Exception as e:
            return False, [f"Error updating {file_path}: {str(e)}"]
    
    def update_cross_references(self):
        """Update cross-references in the new modular files."""
        # Update core file to reference modules
        core_file = self.new_core_file
        if os.path.exists(core_file):
            with open(core_file, encoding='utf-8') as f:
                content = f.read()
            
            # Add module references if not already present
            module_refs = []
            for module in self.modules:
                if os.path.exists(module):
                    module_refs.append(f"<!-- MODULE_REFERENCE: {module} -->")
            
            if module_refs:
                module_section = "\n".join(module_refs)
                if "<!-- MODULE_REFERENCE:" not in content:
                    # Add after existing comments
                    if "<!--" in content:
                        content = re.sub(
                            r'(<!--[^>]*-->\s*)+',
                            r'\g<0>' + module_section + '\n',
                            content,
                            count=1
                        )
                    else:
                        content = module_section + '\n' + content
                
                with open(core_file, 'w', encoding='utf-8') as f:
                    f.write(content)
    
    def create_migration_summary(self, updated_files: list[str], errors: list[str]) -> str:
        """Create a summary of the migration."""
        summary = "# Memory Context Migration Summary\n\n"
        summary += f"**Migration Date**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        summary += "## Files Updated\n"
        if updated_files:
            for file in updated_files:
                summary += f"- `{file}`\n"
        else:
            summary += "- No files required updates\n"
        
        summary += "\n## New Modular Structure\n"
        summary += f"- **Core**: `{self.new_core_file}` - Primary memory scaffold\n"
        for module in self.modules:
            if os.path.exists(module):
                summary += f"- **Module**: `{module}` - Focused functionality\n"
        
        summary += "\n## Reference Mapping\n"
        for old_ref, new_ref in self.reference_mapping.items():
            summary += f"- `{old_ref}` → `{new_ref}`\n"
        
        if errors:
            summary += "\n## Errors\n"
            for error in errors:
                summary += f"- {error}\n"
        
        return summary
    
    def run_migration(self) -> dict:
        """Run the complete migration process."""
        print("🔄 Starting Memory Context Migration...")
        
        # Find files to update
        files_to_update = self.find_files_to_update()
        print(f"📁 Found {len(files_to_update)} files to check for updates")
        
        updated_files = []
        errors = []
        
        # Update each file
        for file_path in files_to_update:
            print(f"🔍 Checking {file_path}...")
            was_updated, changes = self.update_file_references(file_path)
            
            if was_updated:
                updated_files.append(file_path)
                print(f"✅ Updated {file_path}")
                for change in changes:
                    print(f"   - {change}")
            elif changes:  # Errors
                errors.extend(changes)
                print(f"❌ Error updating {file_path}")
        
        # Update cross-references in new modular files
        print("🔗 Updating cross-references in modular files...")
        self.update_cross_references()
        
        # Create migration summary
        summary = self.create_migration_summary(updated_files, errors)
        
        # Write summary to file
        with open("500_b071-migration-summary.md", 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"\n✅ Migration complete!")
        print(f"📊 Updated {len(updated_files)} files")
        print(f"📝 Summary written to 500_b071-migration-summary.md")
        
        if errors:
            print(f"⚠️  {len(errors)} errors encountered")
            for error in errors:
                print(f"   - {error}")
        
        return {
            'updated_files': updated_files,
            'errors': errors,
            'summary': summary
        }


def main():
    """Main function to run the migration."""
    migrator = MemoryContextMigrator()
    result = migrator.run_migration()
    
    print("\n" + "="*50)
    print("MIGRATION SUMMARY")
    print("="*50)
    print(f"Files Updated: {len(result['updated_files'])}")
    print(f"Errors: {len(result['errors'])}")
    print("="*50)


if __name__ == "__main__":
    main()
