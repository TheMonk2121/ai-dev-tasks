from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

#!/usr/bin/env python3
"""
Phase 1: Fix All Database References
Updates all hardcoded references from dspy_rag to ai_agency database.
"""

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class DatabaseReferenceFixer:
    """Fixes all database references from dspy_rag to ai_agency."""

    def __init__(self):
        self.project_root = project_root
        self.changes_made = []
        self.errors = []

        # Database reference patterns to fix
        self.patterns = [
            # Hardcoded connection strings
            (
                r"postgresql://danieljacobs@localhost:5432/ai_agency",
                "postgresql://danieljacobs@localhost:5432/ai_agency",
            ),
            (
                r"postgresql://danieljacobs@localhost:5432/ai_agency",
                "postgresql://danieljacobs@localhost:5432/ai_agency",
            ),
            (
                r"postgresql://danieljacobs@localhost:5432/ai_agency",
                "postgresql://danieljacobs@localhost:5432/ai_agency",
            ),
            (
                r"postgresql://danieljacobs@localhost:5432/ai_agency_system",
                "postgresql://danieljacobs@localhost:5432/ai_agency",
            ),
            (
                r"postgresql://danieljacobs@localhost:5432/ai_agency_system",
                "postgresql://danieljacobs@localhost:5432/ai_agency",
            ),
            # Environment variable defaults
            (
                r'os\.getenv\("DATABASE_URL", "postgresql://danieljacobs@localhost:5432/ai_agency"\)',
                'os.getenv("DATABASE_URL", "postgresql://danieljacobs@localhost:5432/ai_agency")',
            ),
            (
                r'os\.getenv\("DATABASE_URL", "postgresql://danieljacobs@localhost:5432/ai_agency"\)',
                'os.getenv("DATABASE_URL", "postgresql://danieljacobs@localhost:5432/ai_agency")',
            ),
            (
                r'os\.getenv\("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency"\)',
                'os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")',
            ),
            # Configuration values
            (r'driver: "dspy_rag"', 'driver: "dspy_rag"'),  # Keep as is - this is the evaluation driver name
            (r"EVAL_DRIVER=dspy_rag", "EVAL_DRIVER=dspy_rag"),  # Keep as is - this is the evaluation driver name
            # Path references (these should stay as they refer to the dspy-rag-system directory)
            (r"dspy-rag-system", "dspy-rag-system"),  # Keep as is - this is a directory name
            (r"DSPY_RAG_PATH", "DSPY_RAG_PATH"),  # Keep as is - this is an environment variable name
        ]

        # Files to exclude from processing
        self.exclude_patterns = [
            "**/__pycache__/**",
            "**/node_modules/**",
            "**/venv/**",
            "**/.venv/**",
            "**/.git/**",
            "**/**",
            "**/artifacts/**",
            "**/logs/**",
            "**/metrics/**",
            "**/traces/**",
            "**/out/**",
            "**/compiled_artifacts/**",
            "**/promoted_artifacts/**",
            "**/baseline_artifacts/**",
            "**/local_storage/**",
            "**/zulip_data/**",
            "**/Library/**",
            "**/node_modules/**",
            "**/venv/**",
            "**/.venv/**",
            "**/.git/**",
            "**/**",
            "**/artifacts/**",
            "**/logs/**",
            "**/metrics/**",
            "**/traces/**",
            "**/out/**",
            "**/compiled_artifacts/**",
            "**/promoted_artifacts/**",
            "**/baseline_artifacts/**",
            "**/local_storage/**",
            "**/zulip_data/**",
            "**/Library/**",
        ]

    def should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed."""
        # Skip excluded patterns
        for pattern in self.exclude_patterns:
            if file_path.match(pattern):
                return False

        # Only process certain file types
        if file_path.suffix not in [".py", ".yaml", ".yml", ".json", ".jsonl", ".md", ".sh", ".bash", ".zsh"]:
            return False

        return True

    def fix_file(self, file_path: Path) -> list[str]:
        """Fix database references in a single file."""
        changes = []

        try:
            # Read file content
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Apply all patterns
            for pattern, replacement in self.patterns:
                if pattern != replacement:  # Skip patterns that don't need changing
                    new_content = re.sub(pattern, replacement, content)
                    if new_content != content:
                        changes.append(f"  - {pattern} → {replacement}")
                        content = new_content

            # Write back if changes were made
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                changes.insert(0, f"✅ Fixed {file_path}")
            else:
                changes.append("  - No changes needed")

        except Exception as e:
            error_msg = f"❌ Error processing {file_path}: {e}"
            self.errors.append(error_msg)
            changes.append(error_msg)

        return changes

    def find_files_to_process(self) -> list[Path]:
        """Find all files that need processing."""
        files = []

        # Process specific file types in specific directories
        target_dirs = ["scripts", "300_experiments", "configs", "src", "tests"]

        for target_dir in target_dirs:
            target_path = self.project_root / target_dir
            if target_path.exists():
                for file_path in target_path.rglob("*"):
                    if file_path.is_file() and self.should_process_file(file_path):
                        files.append(file_path)

        return files

    def fix_specific_critical_files(self):
        """Fix specific critical files that need special handling."""
        critical_fixes = [
            # Hardcoded database connections
            {
                "file": "scripts/documentation_retrieval_cli.py",
                "patterns": [
                    (
                        r"postgresql://danieljacobs@localhost:5432/ai_agency",
                        "postgresql://danieljacobs@localhost:5432/ai_agency",
                    ),
                ],
            },
            {
                "file": "scripts/documentation_indexer.py",
                "patterns": [
                    (
                        r"postgresql://danieljacobs@localhost:5432/ai_agency",
                        "postgresql://danieljacobs@localhost:5432/ai_agency",
                    ),
                ],
            },
            {
                "file": "300_experiments/test_concurrent.py",
                "patterns": [
                    (
                        r"postgresql://danieljacobs@localhost:5432/ai_agency",
                        "postgresql://danieljacobs@localhost:5432/ai_agency",
                    ),
                ],
            },
            {
                "file": "scripts/system_monitor.py",
                "patterns": [
                    (
                        r"postgresql://danieljacobs@localhost:5432/ai_agency",
                        "postgresql://danieljacobs@localhost:5432/ai_agency",
                    ),
                ],
            },
            {
                "file": "300_experiments/test_n8n_ltst_integration.py",
                "patterns": [
                    (
                        r"postgresql://danieljacobs@localhost:5432/ai_agency_system",
                        "postgresql://danieljacobs@localhost:5432/ai_agency",
                    ),
                ],
            },
            {
                "file": "300_experiments/test_ux_ltst_integration.py",
                "patterns": [
                    (
                        r"postgresql://danieljacobs@localhost:5432/ai_agency_system",
                        "postgresql://danieljacobs@localhost:5432/ai_agency",
                    ),
                ],
            },
        ]

        for fix in critical_fixes:
            file_path = self.project_root / fix["file"]
            if file_path.exists():
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()

                    original_content = content
                    for pattern, replacement in fix["patterns"]:
                        content = re.sub(pattern, replacement, content)

                    if content != original_content:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        self.changes_made.append(f"✅ Fixed critical file: {fix['file']}")
                    else:
                        self.changes_made.append(f"ℹ️  No changes needed in: {fix['file']}")

                except Exception as e:
                    error_msg = f"❌ Error fixing {fix['file']}: {e}"
                    self.errors.append(error_msg)
                    self.changes_made.append(error_msg)

    def run(self):
        """Run the database reference fixing process."""
        print("🔧 Phase 1: Fixing All Database References")
        print("=" * 60)

        # Fix critical files first
        print("\n🎯 Step 1: Fixing critical files with hardcoded connections...")
        self.fix_specific_critical_files()

        # Find and process all other files
        print("\n🔍 Step 2: Scanning for other files to process...")
        files_to_process = self.find_files_to_process()
        print(f"   Found {len(files_to_process)} files to process")

        # Process files in batches
        batch_size = 50
        for i in range(0, len(files_to_process), batch_size):
            batch = files_to_process[i : i + batch_size]
            print(
                f"\n📝 Processing batch {i//batch_size + 1}/{(len(files_to_process) + batch_size - 1)//batch_size} ({len(batch)} files)..."
            )

            for file_path in batch:
                changes = self.fix_file(file_path)
                if changes:
                    self.changes_made.extend(changes)

        # Summary
        print("\n" + "=" * 60)
        print("📊 PHASE 1 SUMMARY")
        print("=" * 60)

        if self.changes_made:
            print(f"✅ Changes made: {len([c for c in self.changes_made if c.startswith('✅')])}")
            print(f"ℹ️  Files checked: {len([c for c in self.changes_made if c.startswith('ℹ️')])}")

        if self.errors:
            print(f"❌ Errors: {len(self.errors)}")
            for error in self.errors:
                print(f"   {error}")

        print("\n🎉 Phase 1 completed!")
        print("📋 Next steps:")
        print("   1. Review changes made")
        print("   2. Test critical scripts")
        print("   3. Proceed to Phase 2 (Schema Consolidation)")

        return len(self.errors) == 0

def main():
    """Main entry point."""
    fixer = DatabaseReferenceFixer()
    success = fixer.run()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
