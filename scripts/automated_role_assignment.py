#!/usr/bin/env python3
"""
Automated Role Assignment Script
--------------------------------
Processes 600_archives files and automatically assigns appropriate roles.

This script scans the 600_archives directory, analyzes files for role assignment,
and can update the memory rehydrator with the results.
"""

import argparse
import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from role_assignment_metadata import RoleAssignment, RoleAssignmentMetadata


class AutomatedRoleAssignment:
    """Handles automated role assignment for 600_archives files."""

    def __init__(self, archives_dir: str = "600_archives"):
        self.archives_dir = Path(archives_dir)
        self.metadata_system = RoleAssignmentMetadata()
        self.assignments: dict[str, RoleAssignment] = {}
        self.conflicts: list[dict] = []
        self.stats = {
            "total_files": 0,
            "processed_files": 0,
            "metadata_assignments": 0,
            "content_assignments": 0,
            "default_assignments": 0,
            "conflicts": 0,
            "errors": 0,
        }

    def scan_archives(self, file_pattern: str = "*.md") -> list[Path]:
        """
        Scan the archives directory for files to process.

        Args:
            file_pattern: File pattern to match (default: "*.md")

        Returns:
            List of file paths to process
        """
        if not self.archives_dir.exists():
            print(f"⚠️  Archives directory not found: {self.archives_dir}")
            return []

        files = list(self.archives_dir.rglob(file_pattern))
        self.stats["total_files"] = len(files)
        return files

    def process_file(self, file_path: Path) -> RoleAssignment:
        """
        Process a single file for role assignment.

        Args:
            file_path: Path to the file to process

        Returns:
            RoleAssignment for the file
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            assignment = self.metadata_system.assign_roles_to_file(file_path, content)

            # Update statistics
            self.stats["processed_files"] += 1
            if assignment.source == "metadata":
                self.stats["metadata_assignments"] += 1
            elif assignment.source == "content_analysis":
                self.stats["content_assignments"] += 1
            elif assignment.source == "default":
                self.stats["default_assignments"] += 1

            # Check for validation errors
            if not self.metadata_system.validate_role_assignment(assignment):
                self.stats["errors"] += 1
                print(f"⚠️  Validation errors for {file_path}: {self.metadata_system.validation_errors}")

            return assignment

        except Exception as e:
            self.stats["errors"] += 1
            print(f"❌ Error processing {file_path}: {e}")
            return RoleAssignment(roles=set(), source="error", confidence=0.0, metadata={"error": str(e)})

    def process_archives(self, file_pattern: str = "*.md", dry_run: bool = False) -> dict:
        """
        Process all files in the archives directory.

        Args:
            file_pattern: File pattern to match
            dry_run: If True, don't make any changes

        Returns:
            Dictionary with processing results
        """
        print(f"🔍 Scanning {self.archives_dir} for {file_pattern} files...")
        files = self.scan_archives(file_pattern)

        if not files:
            print("No files found to process.")
            return self.stats

        print(f"📁 Found {len(files)} files to process")

        for file_path in files:
            # Handle path conversion safely
            try:
                relative_path = file_path.relative_to(Path.cwd())
            except ValueError:
                # If file is not in current directory, use absolute path
                relative_path = file_path

            print(f"  📄 Processing: {relative_path}")

            assignment = self.process_file(file_path)
            self.assignments[str(relative_path)] = assignment

            # Print assignment details
            roles_str = ", ".join(sorted(assignment.roles)) if assignment.roles else "none"
            print(f"    📋 Roles: {roles_str} (source: {assignment.source}, confidence: {assignment.confidence:.2f})")

        # Detect and report conflicts
        self._detect_conflicts()

        # Print summary
        self._print_summary()

        if not dry_run:
            # Update memory rehydrator if requested
            self._update_memory_rehydrator()

        return self.stats

    def _detect_conflicts(self):
        """Detect conflicts in role assignments."""
        # Group files by assigned roles
        role_groups: dict[tuple, list[str]] = {}
        for file_path, assignment in self.assignments.items():
            if assignment.roles:
                roles_key = tuple(sorted(assignment.roles))
                if roles_key not in role_groups:
                    role_groups[roles_key] = []
                role_groups[roles_key].append(file_path)

        # Check for potential conflicts (files with very different roles)
        for roles1, files1 in role_groups.items():
            for roles2, files2 in role_groups.items():
                if roles1 != roles2:
                    # Check if files are in similar directories but have different roles
                    for file1 in files1:
                        for file2 in files2:
                            path1 = Path(file1)
                            path2 = Path(file2)

                            # Check if files are in the same subdirectory
                            if path1.parent == path2.parent and path1.name != path2.name:

                                # Calculate role similarity
                                common_roles = set(roles1) & set(roles2)
                                total_roles = set(roles1) | set(roles2)
                                similarity = len(common_roles) / len(total_roles) if total_roles else 0

                                if similarity < 0.5:  # Less than 50% role overlap
                                    conflict = {
                                        "file1": file1,
                                        "file2": file2,
                                        "roles1": list(roles1),
                                        "roles2": list(roles2),
                                        "similarity": similarity,
                                    }
                                    self.conflicts.append(conflict)
                                    self.stats["conflicts"] += 1

    def _print_summary(self):
        """Print processing summary."""
        print("\n" + "=" * 60)
        print("📊 PROCESSING SUMMARY")
        print("=" * 60)
        print(f"📁 Total files found: {self.stats['total_files']}")
        print(f"✅ Files processed: {self.stats['processed_files']}")
        print(f"📋 Metadata assignments: {self.stats['metadata_assignments']}")
        print(f"🔬 Content analysis assignments: {self.stats['content_assignments']}")
        print(f"📁 Default assignments: {self.stats['default_assignments']}")
        print(f"⚠️  Conflicts detected: {self.stats['conflicts']}")
        print(f"❌ Errors: {self.stats['errors']}")

        if self.conflicts:
            print("\n⚠️  CONFLICTS DETECTED:")
            for conflict in self.conflicts:
                print(f"  • {conflict['file1']} vs {conflict['file2']}")
                print(
                    f"    Roles: {conflict['roles1']} vs {conflict['roles2']} (similarity: {conflict['similarity']:.2f})"
                )

    def _update_memory_rehydrator(self):
        """Update the memory rehydrator with new role assignments."""
        print("\n🔄 Updating memory rehydrator...")

        # This would integrate with the memory rehydrator system
        # For now, we'll just print what would be updated
        print("  📝 Would update memory rehydrator with role assignments:")

        for file_path, assignment in self.assignments.items():
            if assignment.roles:
                roles_str = ", ".join(sorted(assignment.roles))
                print(f"    • {file_path}: {roles_str}")

    def generate_report(self, output_file: str | None = None) -> str:
        """
        Generate a detailed report of role assignments.

        Args:
            output_file: Optional file to write report to

        Returns:
            Report content as string
        """
        report_lines = [
            "# Automated Role Assignment Report",
            f"Generated: {Path.cwd()}",
            f"Archives Directory: {self.archives_dir}",
            "",
            "## Summary",
            f"- Total files: {self.stats['total_files']}",
            f"- Processed: {self.stats['processed_files']}",
            f"- Metadata assignments: {self.stats['metadata_assignments']}",
            f"- Content analysis: {self.stats['content_assignments']}",
            f"- Default assignments: {self.stats['default_assignments']}",
            f"- Conflicts: {self.stats['conflicts']}",
            f"- Errors: {self.stats['errors']}",
            "",
            "## Role Assignments",
            "",
        ]

        # Group by role source
        by_source = {}
        for file_path, assignment in self.assignments.items():
            source = assignment.source
            if source not in by_source:
                by_source[source] = []
            by_source[source].append((file_path, assignment))

        for source in ["metadata", "content_analysis", "default", "error"]:
            if source in by_source:
                report_lines.append(f"### {source.replace('_', ' ').title()}")
                for file_path, assignment in by_source[source]:
                    roles_str = ", ".join(sorted(assignment.roles)) if assignment.roles else "none"
                    report_lines.append(f"- `{file_path}`: {roles_str} (confidence: {assignment.confidence:.2f})")
                report_lines.append("")

        if self.conflicts:
            report_lines.extend(["## Conflicts", ""])
            for conflict in self.conflicts:
                report_lines.append(f"- **{conflict['file1']}** vs **{conflict['file2']}**")
                report_lines.append(f"  - Roles: {conflict['roles1']} vs {conflict['roles2']}")
                report_lines.append(f"  - Similarity: {conflict['similarity']:.2f}")
                report_lines.append("")

        report_content = "\n".join(report_lines)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report_content)
            print(f"📄 Report written to: {output_file}")

        return report_content


def main():
    """Main entry point for the automated role assignment script."""
    parser = argparse.ArgumentParser(description="Automated role assignment for 600_archives files")
    parser.add_argument(
        "--archives-dir", default="600_archives", help="Archives directory to process (default: 600_archives)"
    )
    parser.add_argument("--pattern", default="*.md", help="File pattern to match (default: *.md)")
    parser.add_argument("--dry-run", action="store_true", help="Process files but don't make changes")
    parser.add_argument("--report", help="Generate detailed report to specified file")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Create role assignment processor
    processor = AutomatedRoleAssignment(args.archives_dir)

    # Process archives
    stats = processor.process_archives(args.pattern, args.dry_run)

    # Generate report if requested
    if args.report:
        processor.generate_report(args.report)

    # Exit with error code if there were errors
    if stats["errors"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
