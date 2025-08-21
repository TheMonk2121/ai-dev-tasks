#!/usr/bin/env python3
"""
Add TL;DR Sections Script

This script adds TL;DR sections to markdown files that are missing them.
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional


class TLDRAdder:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.files_processed = 0
        self.tldr_added = 0

        # TL;DR templates for different file types
        self.tldr_templates = {
            "000_core": {
                "000_backlog.md": {
                    "title": "Backlog Management",
                    "description": "Central backlog with prioritized items and AI-executable queues",
                    "read_when": "Starting new work or reviewing priorities",
                    "do_next": "Select next P0/P1 item or update priorities",
                },
                "001_create-prd.md": {
                    "title": "PRD Creation Workflow",
                    "description": "AI-powered Product Requirements Document creation process",
                    "read_when": "Starting new feature development",
                    "do_next": "Run workflow to generate PRD for selected backlog item",
                },
            },
            "100_memory": {
                "100_cursor-memory-context.md": {
                    "title": "Memory Context System",
                    "description": "Primary memory scaffold for AI rehydration and context management",
                    "read_when": "Starting new session or need current project state",
                    "do_next": "Check backlog and system overview for next priorities",
                }
            },
            "200_setup": {
                "200_naming-conventions.md": {
                    "title": "Naming Conventions",
                    "description": "File and directory naming standards for the project",
                    "read_when": "Creating new files or organizing content",
                    "do_next": "Apply conventions to new files and update existing ones",
                }
            },
            "400_guides": {
                "400_broken-links-fix-summary.md": {
                    "title": "Broken Links Fix Summary",
                    "description": "Summary of broken links fixing process and results",
                    "read_when": "After fixing documentation links or reviewing link health",
                    "do_next": "Monitor for new broken links and maintain link integrity",
                },
                "400_comprehensive-coding-best-practices.md": {
                    "title": "Comprehensive Coding Best Practices",
                    "description": "Complete guide to coding standards and best practices",
                    "read_when": "Writing new code or reviewing existing code",
                    "do_next": "Apply practices to current development work",
                },
                "400_context-priority-guide.md": {
                    "title": "Context Priority Guide",
                    "description": "Guide for prioritizing context and documentation access",
                    "read_when": "Organizing documentation or setting up new systems",
                    "do_next": "Apply priority system to current documentation",
                },
                "400_file-analysis-guide.md": {
                    "title": "File Analysis Guide",
                    "description": "Guide for analyzing and understanding file structures",
                    "read_when": "Analyzing codebase or understanding file relationships",
                    "do_next": "Apply analysis techniques to current files",
                },
                "400_markdown-cleanup-progress.md": {
                    "title": "Markdown Cleanup Progress",
                    "description": "Tracking progress of markdown formatting improvements",
                    "read_when": "Reviewing documentation quality or planning cleanup",
                    "do_next": "Continue cleanup work or update progress",
                },
                "400_markdown-fix-plan.md": {
                    "title": "Markdown Fix Plan",
                    "description": "Plan for fixing markdown formatting issues",
                    "read_when": "Planning documentation improvements",
                    "do_next": "Execute fix plan or update priorities",
                },
                "400_optimization-completion-summary.md": {
                    "title": "Script Optimization Completion Summary",
                    "description": "Final summary of completed script optimizations",
                    "read_when": "After completing optimizations or reviewing performance improvements",
                    "do_next": (
                        "All optimizations are complete and deployed - " "monitor performance and maintain as needed"
                    ),
                },
                "400_script-optimization-guide.md": {
                    "title": "Script Optimization Guide",
                    "description": "Guide for optimizing script performance and efficiency",
                    "read_when": "Optimizing scripts or improving performance",
                    "do_next": "Apply optimization techniques to current scripts",
                },
                "400_script-optimization-results.md": {
                    "title": "Script Optimization Results",
                    "description": "Comprehensive results of script optimization efforts",
                    "read_when": "Reviewing optimization results or planning further improvements",
                    "do_next": "Apply successful optimizations to other scripts or monitor performance",
                },
            },
            "dspy-rag-system/docs": {
                "VERSION_HISTORY.md": {
                    "title": "Version History",
                    "description": "Complete version history and changelog for DSPy RAG system",
                    "read_when": "Checking system updates or understanding changes",
                    "do_next": "Review recent changes or plan next version",
                },
                "system_service_guide.md": {
                    "title": "System Service Guide",
                    "description": "Guide for managing and configuring system services",
                    "read_when": "Setting up services or troubleshooting system issues",
                    "do_next": "Configure services or resolve current issues",
                },
                "watch_folder_guide.md": {
                    "title": "Watch Folder Guide",
                    "description": "Guide for setting up and using folder monitoring",
                    "read_when": "Setting up file monitoring or configuring watch services",
                    "do_next": "Configure watch folders or monitor current setup",
                },
            },
        }

    def get_tldr_template(self, file_path: Path) -> Optional[Dict]:
        """Get TL;DR template for a specific file."""
        # Try exact path match first
        for category, files in self.tldr_templates.items():
            if category in str(file_path):
                for filename, template in files.items():
                    if file_path.name == filename:
                        return template

        # Try partial path match
        for category, files in self.tldr_templates.items():
            if category in str(file_path):
                # Return first template in category as fallback
                return next(iter(files.values()))

        return None

    def add_tldr_section(self, file_path: Path) -> bool:
        """Add TL;DR section to a markdown file."""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Check if TL;DR already exists
            if re.search(r"^##\s*🔎\s*TL;DR\s*$", content, re.MULTILINE):
                return False

            # Get template
            template = self.get_tldr_template(file_path)
            if not template:
                print(f"⚠️  No template found for {file_path}")
                return False

            # Create TL;DR section
            tldr_section = f"""## 🔎 TL;DR {{#tldr}}

| what this file is | read when | do next |
|---|---|---|
| {template['description']} | {template['read_when']} | {template['do_next']} |

"""

            # Find the first heading and insert TL;DR after it
            lines = content.split("\n")
            insert_index = 0

            for i, line in enumerate(lines):
                if line.startswith("# "):
                    insert_index = i + 1
                    break

            # Insert TL;DR section
            lines.insert(insert_index, "")
            lines.insert(insert_index + 1, tldr_section)

            if not self.dry_run:
                file_path.write_text("\n".join(lines), encoding="utf-8")
                print(f"✅ Added TL;DR to {file_path}")
            else:
                print(f"📝 Would add TL;DR to {file_path}")

            return True

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False

    def process_files(self, file_list: List[str]) -> None:
        """Process a list of files to add TL;DR sections."""
        for file_path_str in file_list:
            file_path = Path(file_path_str)
            if file_path.exists():
                self.files_processed += 1
                if self.add_tldr_section(file_path):
                    self.tldr_added += 1
            else:
                print(f"⚠️  File not found: {file_path}")

    def run(self) -> None:
        """Main execution method."""
        print(f"{'🔍 DRY RUN' if self.dry_run else '🚀 APPLYING'} TL;DR Sections")
        print("=" * 50)

        # Files that need TL;DR sections
        files_to_process = [
            "000_core/000_backlog.md",
            "400_guides/400_project-overview.md",
            "100_memory/100_cursor-memory-context.md",
            "200_setup/200_naming-conventions.md",
            "400_guides/400_broken-links-fix-summary.md",
            "400_guides/400_comprehensive-coding-best-practices.md",
            "400_guides/400_context-priority-guide.md",
            "400_guides/400_file-analysis-guide.md",
            "400_guides/400_markdown-cleanup-progress.md",
            "400_guides/400_markdown-fix-plan.md",
            "400_guides/400_optimization-completion-summary.md",
            "400_guides/400_script-optimization-guide.md",
            "400_guides/400_script-optimization-results.md",
            "dspy-rag-system/docs/VERSION_HISTORY.md",
            "dspy-rag-system/docs/system_service_guide.md",
            "dspy-rag-system/docs/watch_folder_guide.md",
        ]

        self.process_files(files_to_process)

        print("\n" + "=" * 50)
        print("📊 Summary:")
        print(f"   Files processed: {self.files_processed}")
        print(f"   TL;DR sections {'would be' if self.dry_run else ''} added: {self.tldr_added}")

        if self.dry_run:
            print("\n💡 Run with --apply to actually add the TL;DR sections")


def main():
    parser = argparse.ArgumentParser(description="Add TL;DR sections to markdown files")
    parser.add_argument("--apply", action="store_true", help="Actually apply the changes (default is dry-run)")
    args = parser.parse_args()

    adder = TLDRAdder(dry_run=not args.apply)
    adder.run()


if __name__ == "__main__":
    main()
