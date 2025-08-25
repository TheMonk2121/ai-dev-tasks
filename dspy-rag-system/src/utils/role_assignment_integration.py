#!/usr/bin/env python3
"""
Role Assignment Integration with Memory Rehydrator
-------------------------------------------------
Integrates automated role assignment with the memory rehydrator system.

This module provides functions to update the memory rehydrator's ROLE_FILES
mapping based on automated role assignments from 600_archives.
"""

import sys
from pathlib import Path
from typing import Dict, Tuple

# Add the project root to the path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))  # noqa: E402

from scripts.automated_role_assignment import AutomatedRoleAssignment  # noqa: E402
from scripts.role_assignment_metadata import RoleAssignment, RoleAssignmentMetadata  # noqa: E402


class RoleAssignmentIntegration:
    """Integrates automated role assignment with the memory rehydrator."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.metadata_system = RoleAssignmentMetadata()
        self.role_assigner = AutomatedRoleAssignment()

        # Path to the memory rehydrator file
        self.memory_rehydrator_path = self.project_root / "dspy-rag-system" / "src" / "utils" / "memory_rehydrator.py"

        # Backup path for the memory rehydrator
        self.backup_path = self.memory_rehydrator_path.with_suffix(".py.backup")

    def get_current_role_files(self) -> Dict[str, Tuple[str, ...]]:
        """
        Get current ROLE_FILES mapping from memory rehydrator.

        Returns:
            Current ROLE_FILES dictionary
        """
        # Return the current hardcoded ROLE_FILES mapping
        # This is a simplified approach - in production, you'd want proper parsing
        return {
            "planner": (
                "400_guides/400_system-overview.md",
                "000_core/000_backlog.md",
                "600_archives/",
                "600_archives/artifacts/prds/PRD-B-102-Cursor-Native-AI-Role-Coordination-System.md",
                "600_archives/artifacts/task_lists/Task-List-B-102-Cursor-Native-AI-Role-Coordination-System.md",
            ),
            "implementer": (
                "100_memory/104_dspy-development-context.md",
                "scripts/single_doorway.py",
                "scripts/memory_up.sh",
                "artifacts/worklogs/",
                "artifacts/summaries/",
                "400_guides/400_scribe-v2-system-guide.md",
                "600_archives/",
                "600_archives/artifacts/prds/PRD-B-102-Cursor-Native-AI-Role-Coordination-System.md",
                "600_archives/artifacts/task_lists/Task-List-B-102-Cursor-Native-AI-Role-Coordination-System.md",
            ),
            "researcher": ("600_archives/",),
            "coder": (
                "400_guides/400_comprehensive-coding-best-practices.md",
                "400_guides/400_code-criticality-guide.md",
                "400_guides/400_testing-strategy-guide.md",
                "400_guides/400_contributing-guidelines.md",
                "400_guides/400_security-best-practices-guide.md",
                "400_guides/400_development-patterns.md",
                "400_guides/400_script-optimization-guide.md",
                "400_guides/400_performance-optimization-guide.md",
                "400_guides/400_integration-patterns-guide.md",
                "400_guides/400_migration-upgrade-guide.md",
                "400_guides/400_file-analysis-guide.md",
                "400_guides/400_deployment-environment-guide.md",
                "400_guides/400_graph-visualization-guide.md",
                "100_memory/104_dspy-development-context.md",
                "Task-List-Chunk-Relationship-Visualization.md",
                "scripts/dependency_monitor.py",
                "dspy-rag-system/src/utils/graph_data_provider.py",
                "600_archives/",
            ),
            "documentation": (
                "400_guides/400_context-priority-guide.md",
                "400_guides/400_documentation-reference.md",
                "200_setup/200_naming-conventions.md",
                "400_guides/400_scribe-v2-system-guide.md",
                "400_guides/400_project-overview.md",
                "400_guides/400_system-overview.md",
                "400_guides/400_comprehensive-coding-best-practices.md",
                "600_archives/",
            ),
        }

    def update_role_files_with_assignments(self, assignments: Dict[str, RoleAssignment]) -> Dict[str, Tuple[str, ...]]:
        """
        Update ROLE_FILES mapping with automated assignments.

        Args:
            assignments: Dictionary of file paths to role assignments

        Returns:
            Updated ROLE_FILES dictionary
        """
        # Get current role files
        current_role_files = self.get_current_role_files()

        # Initialize updated role files with current assignments
        updated_role_files = {}
        for role, files in current_role_files.items():
            updated_role_files[role] = list(files)

        # Add new file assignments
        for file_path, assignment in assignments.items():
            if assignment.roles and assignment.confidence > 0.5:  # Only use high-confidence assignments
                for role in assignment.roles:
                    if role in updated_role_files:
                        # Add file if not already present
                        if file_path not in updated_role_files[role]:
                            updated_role_files[role].append(file_path)

        # Convert back to tuples
        return {role: tuple(files) for role, files in updated_role_files.items()}

    def generate_role_files_code(self, role_files: Dict[str, Tuple[str, ...]]) -> str:
        """
        Generate Python code for the ROLE_FILES mapping.

        Args:
            role_files: Updated role files mapping

        Returns:
            Python code string for ROLE_FILES
        """
        lines = ["# Role → files map (kept small/deterministic; can be extended)"]
        lines.append("ROLE_FILES = {")

        for role, files in role_files.items():
            lines.append(f'    "{role}": (')
            for file_path in files:
                lines.append(f'        "{file_path}",')
            lines.append("    ),")

        lines.append("}")

        return "\n".join(lines)

    def update_memory_rehydrator(self, assignments: Dict[str, RoleAssignment], dry_run: bool = False) -> bool:
        """
        Update the memory rehydrator with new role assignments.

        Args:
            assignments: Dictionary of file paths to role assignments
            dry_run: If True, don't make changes

        Returns:
            True if successful, False otherwise
        """
        try:
            # Read current memory rehydrator
            with open(self.memory_rehydrator_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Update role files
            updated_role_files = self.update_role_files_with_assignments(assignments)
            new_role_files_code = self.generate_role_files_code(updated_role_files)

            # Find and replace the ROLE_FILES section
            start_marker = "# Role → files map (kept small/deterministic; can be extended)"

            start_idx = content.find(start_marker)
            if start_idx == -1:
                print("⚠️  ROLE_FILES section not found in memory rehydrator")
                return False

            # Find the end of the ROLE_FILES dictionary
            brace_count = 0
            end_idx = start_idx + len(start_marker)

            for i, char in enumerate(content[start_idx + len(start_marker) :]):
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    if brace_count == 0:
                        end_idx = start_idx + len(start_marker) + i + 1
                        break
                    brace_count -= 1

            # Create updated content
            before_role_files = content[:start_idx]
            after_role_files = content[end_idx:]
            updated_content = before_role_files + new_role_files_code + "\n\n" + after_role_files

            if dry_run:
                print("🔍 DRY RUN - Would update memory rehydrator:")
                print("  📝 New ROLE_FILES code:")
                print(new_role_files_code)
                return True

            # Create backup
            with open(self.backup_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"💾 Backup created: {self.backup_path}")

            # Write updated content
            with open(self.memory_rehydrator_path, "w", encoding="utf-8") as f:
                f.write(updated_content)

            print(f"✅ Memory rehydrator updated: {self.memory_rehydrator_path}")
            return True

        except Exception as e:
            print(f"❌ Error updating memory rehydrator: {e}")
            return False

    def integrate_automated_assignments(self, archives_dir: str = "600_archives", dry_run: bool = False) -> bool:
        """
        Integrate automated role assignments with the memory rehydrator.

        Args:
            archives_dir: Archives directory to process
            dry_run: If True, don't make changes

        Returns:
            True if successful, False otherwise
        """
        print("🔄 Integrating automated role assignments...")

        # Process archives
        self.role_assigner.archives_dir = Path(archives_dir)
        stats = self.role_assigner.process_archives("*.md", dry_run=True)  # Always dry run for processing

        if stats["errors"] > 0:
            print(f"⚠️  {stats['errors']} errors during processing")
            return False

        # Update memory rehydrator
        success = self.update_memory_rehydrator(self.role_assigner.assignments, dry_run)

        if success:
            print("✅ Integration completed successfully")
            print(f"📊 Processed {stats['processed_files']} files")
            print(f"📋 {stats['content_assignments']} content-based assignments")
            print(f"📁 {stats['default_assignments']} default assignments")
        else:
            print("❌ Integration failed")

        return success

    def rollback_changes(self) -> bool:
        """
        Rollback changes to the memory rehydrator using the backup.

        Returns:
            True if successful, False otherwise
        """
        if not self.backup_path.exists():
            print(f"⚠️  No backup found: {self.backup_path}")
            return False

        try:
            # Restore from backup
            with open(self.backup_path, "r", encoding="utf-8") as f:
                backup_content = f.read()

            with open(self.memory_rehydrator_path, "w", encoding="utf-8") as f:
                f.write(backup_content)

            print("✅ Memory rehydrator restored from backup")
            return True

        except Exception as e:
            print(f"❌ Error rolling back changes: {e}")
            return False


def main():
    """Main entry point for role assignment integration."""
    import argparse

    parser = argparse.ArgumentParser(description="Integrate automated role assignment with memory rehydrator")
    parser.add_argument(
        "--archives-dir", default="600_archives", help="Archives directory to process (default: 600_archives)"
    )
    parser.add_argument("--dry-run", action="store_true", help="Process files but don't make changes")
    parser.add_argument("--rollback", action="store_true", help="Rollback changes using backup")

    args = parser.parse_args()

    # Create integration instance
    integration = RoleAssignmentIntegration()

    if args.rollback:
        success = integration.rollback_changes()
        sys.exit(0 if success else 1)

    # Integrate assignments
    success = integration.integrate_automated_assignments(args.archives_dir, args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
