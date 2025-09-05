#!/usr/bin/env python3
"""
Giant Guide Reference Migration Script

Updates all cross-references from the original large guide files to the new
focused modules created by the splitting process.
"""

import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_LOG = logging.getLogger("giant_guide_migration")

class GiantGuideReferenceMigrator:
    """Migrates references from original large guide files to new focused modules"""

    def __init__(self):
        # Original files that were split
        # Note: Excluding project-specific deliverables (B-011, B-049, B-072, etc.) as they should remain intact
        # Only targeting general documentation guides (400_* files) that are meant to be reference materials
        self.original_files = [
            "400_deployment-environment-guide.md",
            "400_few-shot-context-examples.md",
            "400_contributing-guidelines.md",
            "400_migration-upgrade-guide.md",
            "400_testing-strategy-guide.md",
            "400_integration-patterns-guide.md",
            "400_performance-optimization-guide.md",
            "docs/100_ai-development-ecosystem.md",
            "400_system-overview.md",
        ]

        # Mapping of original files to their modules
        self.file_module_mapping = self._build_module_mapping()

        # Context-specific reference mappings
        self.context_mapping = {
            # Deployment and Environment (consolidated into single file)
            "deployment": "400_deployment-environment-guide.md",
            "environment": "400_deployment-environment-guide.md",
            "deployment procedures": "400_deployment-environment-guide.md",
            "environment setup": "400_deployment-environment-guide.md",
            "deployment architecture": "400_deployment-environment-guide.md",

            # Few-shot Context Examples (consolidated into single file)
            "few-shot": "400_few-shot-context-examples.md",
            "context examples": "400_few-shot-context-examples.md",
            "context engineering": "400_few-shot-context-examples.md",
            "backlog analysis": "400_few-shot-context-examples.md",
            "memory context": "400_few-shot-context-examples.md",

            # Contributing Guidelines (consolidated into single file)
            "contributing": "400_contributing-guidelines.md",
            "code standards": "400_contributing-guidelines.md",
            "testing standards": "400_contributing-guidelines.md",
            "security standards": "400_contributing-guidelines.md",
            "performance standards": "400_contributing-guidelines.md",

            # Migration and Upgrade (consolidated into single file)
            "migration": "400_migration-upgrade-guide.md",
            "upgrade": "400_migration-upgrade-guide.md",
            "database migration": "400_migration-upgrade-guide.md",
            "application upgrade": "400_migration-upgrade-guide.md",
            "rollback procedures": "400_migration-upgrade-guide.md",

            # Testing Strategy (consolidated into single file)
            "testing strategy": "400_testing-strategy-guide.md",
            "testing pyramid": "400_testing-strategy-guide.md",
            "test types": "400_testing-strategy-guide.md",
            "quality gates": "400_testing-strategy-guide.md",
            "ai model testing": "400_testing-strategy-guide.md",

            # Note: B-011 files are project deliverables, not general documentation guides

            # Integration Patterns (consolidated into single file)
            "integration patterns": "400_integration-patterns-guide.md",
            "api design": "400_integration-patterns-guide.md",
            "component integration": "400_integration-patterns-guide.md",
            "communication patterns": "400_integration-patterns-guide.md",

            # Performance Optimization (consolidated into single file)
            "performance optimization": "400_performance-optimization-guide.md",
            "performance metrics": "400_performance-optimization-guide.md",
            "optimization strategies": "400_performance-optimization-guide.md",
            "scaling guidelines": "400_performance-optimization-guide.md",

            # AI Development Ecosystem (consolidated into single file)
            "ai development ecosystem": "docs/100_ai-development-ecosystem.md",
            "three lens documentation": "docs/100_ai-development-ecosystem.md",
            "beginner lens": "docs/100_ai-development-ecosystem.md",
            "intermediate lens": "docs/100_ai-development-ecosystem.md",
            "advanced lens": "docs/100_ai-development-ecosystem.md",

            # System Overview (consolidated into single file)
            "system overview": "400_system-overview.md",
            "system architecture": "400_system-overview.md",
            "core components": "400_system-overview.md",
            "development workflow": "400_system-overview.md",
        }

    def _build_module_mapping(self) -> Dict[str, List[str]]:
        """Build mapping of original files to their split modules"""
        mapping = {}

        for original_file in self.original_files:
            if not os.path.exists(original_file):
                continue

            # Find all modules for this file
            base_name = Path(original_file).stem
            modules = []

            # Look for module files
            for file in os.listdir('.'):
                if file.startswith(f"{base_name}_") and file.endswith('.md'):
                    modules.append(file)

            if modules:
                mapping[original_file] = sorted(modules)

        return mapping

    def find_files_to_update(self) -> List[str]:
        """Find all files that need to be updated"""
        files_to_update = []

        # Search for markdown files
        for pattern in ["*.md", "**/*.md"]:
            for file_path in Path('.').rglob(pattern):
                if file_path.is_file():
                    p = str(file_path)
                    # Skip non-project directories
                    if any(skip in p for skip in [
                        "/node_modules/", "/venv/", "/.venv/", "/.git/", "/600_archives/"
                    ]):
                        continue
                    files_to_update.append(p)

        # Filter out the original files and module files
        exclude_files = []
        for original_file in self.original_files:
            exclude_files.append(original_file)
            if original_file in self.file_module_mapping:
                exclude_files.extend(self.file_module_mapping[original_file])

        files_to_update = [f for f in files_to_update if f not in exclude_files]

        return files_to_update

    def update_file_references(self, file_path: str) -> Tuple[bool, List[str]]:
        """Update references in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            changes = []

            # Update direct file references
            for original_file in self.original_files:
                if original_file in content:
                    # Replace with primary module reference
                    if original_file in self.file_module_mapping:
                        primary_module = self.file_module_mapping[original_file][0]
                        content = content.replace(original_file, primary_module)
                        changes.append(f"Updated direct reference: {original_file} → {primary_module}")

            # Update context-specific references
            for context_term, module_pattern in self.context_mapping.items():
                if context_term in content.lower():
                    # Find the most appropriate module
                    appropriate_module = self._find_appropriate_module(context_term, module_pattern)
                    if appropriate_module:
                        # Add module reference comment
                        module_comment = ""
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

                            changes.append(f"Added module reference: {appropriate_module}")

            # Only write if content changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True, changes

            return False, []

        except Exception as e:
            return False, [f"Error updating {file_path}: {str(e)}"]

    def _find_appropriate_module(self, context_term: str, module_pattern: str) -> Optional[str]:
        """Find the most appropriate module for a context term"""
        if module_pattern.endswith('.md'):
            # Direct module reference
            if os.path.exists(module_pattern):
                return module_pattern
            return None

        # Pattern-based search
        if module_pattern.endswith('_'):
            # Find modules that match the pattern
            base_pattern = module_pattern[:-1]  # Remove trailing underscore
            matching_modules = []

            for file in os.listdir('.'):
                if file.startswith(base_pattern) and file.endswith('.md'):
                    matching_modules.append(file)

            if matching_modules:
                # Return the first matching module (usually the primary one)
                return sorted(matching_modules)[0]

        return None

    def create_migration_summary(self, updated_files: List[str], errors: List[str]) -> str:
        """Create a summary of the migration"""
        summary = "# Giant Guide Reference Migration Summary\n\n"
        summary += f"**Migration Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

        summary += "## Files Updated\n"
        if updated_files:
            for file in updated_files:
                summary += f"- `{file}`\n"
        else:
            summary += "- No files required updates\n"

        summary += "\n## Original Files Split\n"
        for original_file in self.original_files:
            if original_file in self.file_module_mapping:
                modules = self.file_module_mapping[original_file]
                summary += f"- **{original_file}** → {len(modules)} modules\n"
                for module in modules[:3]:  # Show first 3 modules
                    summary += f"  - `{module}`\n"
                if len(modules) > 3:
                    summary += f"  - ... and {len(modules) - 3} more modules\n"

        summary += "\n## Context Mapping\n"
        for context_term, module_pattern in self.context_mapping.items():
            summary += f"- `{context_term}` → `{module_pattern}`\n"

        if errors:
            summary += "\n## Errors\n"
            for error in errors:
                summary += f"- {error}\n"

        return summary

    def run_migration(self) -> Dict[str, Any]:
        """Run the complete migration process"""
        print("🔄 Starting Giant Guide Reference Migration...")

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

        # Create migration summary
        summary = self.create_migration_summary(updated_files, errors)

        # Write summary to file
        with open("500_b073-migration-summary.md", 'w', encoding='utf-8') as f:
            f.write(summary)

        print("\n✅ Migration complete!")
        print(f"📊 Updated {len(updated_files)} files")
        print("📝 Summary written to 500_b073-migration-summary.md")

        if errors:
            print(f"⚠️  {len(errors)} errors encountered")
            for error in errors:
                print(f"   - {error}")

        return {
            'updated_files': updated_files,
            'errors': errors,
            'summary': summary,
            'file_module_mapping': self.file_module_mapping
        }

def main():
    """Main function to run the migration."""
    migrator = GiantGuideReferenceMigrator()
    result = migrator.run_migration()

    print("\n" + "="*50)
    print("MIGRATION SUMMARY")
    print("="*50)
    print(f"Files Updated: {len(result['updated_files'])}")
    print(f"Errors: {len(result['errors'])}")
    print("="*50)

if __name__ == "__main__":
    main()
