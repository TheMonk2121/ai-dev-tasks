#!/usr/bin/env python3.12.123.11
"""
Broken Links Fixer

This script systematically fixes broken file references in the documentation.
It analyzes the broken links and applies fixes based on common patterns.
"""

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BrokenLink:
    file: str
    broken_reference: str
    line_number: int = 0
    context: str = ""


class BrokenLinksFixer:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.fixes_applied = 0
        self.fixes_made = []

        # Common file mapping patterns
        self.file_mappings = {
            # Missing files that should be created
            "README.md": "docs/README.md",
            "LICENSE.md": "LICENSE",
            # Files that have been moved
            "100_backlog-automation.md": "100_memory/100_backlog-automation.md",
            "104_dspy-development-context.md": "100_memory/104_dspy-development-context.md",
            "200_naming-conventions.md": "200_setup/200_naming-conventions.md",
            "300_documentation-example.md": "300_examples/300_documentation-example.md",
            # Files that should be in 400_guides
            "400_contributing-guidelines.md": "400_guides/400_contributing-guidelines.md",
            "400_cursor-context-engineering-guide.md": "400_guides/400_cursor-context-engineering-guide.md",
            "400_few-shot-context-examples.md": "400_guides/400_few-shot-context-examples.md",
            "400_integration-patterns-guide.md": "400_guides/400_integration-patterns-guide.md",
            "400_migration-upgrade-guide.md": "400_guides/400_migration-upgrade-guide.md",
            "400_n8n-backlog-scrubber-guide.md": "400_guides/400_n8n-backlog-scrubber-guide.md",
            "400_n8n-setup-guide.md": "400_guides/400_n8n-setup-guide.md",
            "400_timestamp-update-guide.md": "400_guides/400_timestamp-update-guide.md",
            "400_agent-orchestration-guide.md": "400_guides/400_agent-orchestration-guide.md",
            "400_prd-optimization-guide.md": "400_guides/400_prd-optimization-guide.md",
            # Files that should be in 500_research
            "500_documentation-coherence-research.md": "500_research/500_documentation-coherence-research.md",
            "500_maintenance-safety-research.md": "500_research/500_maintenance-safety-research.md",
            "500_research-analysis-summary.md": "500_research/500_research-analysis-summary.md",
            "500_research-implementation-summary.md": "500_research/500_research-implementation-summary.md",
            "500_research-summary.md": "500_research/500_research-summary.md",
            "500_memory-arch-research.md": "500_research/500_memory-arch-research.md",
            "500_ai-development-research.md": "500_research/500_ai-development-research.md",
            "500_documentation-research.md": "500_research/500_documentation-research.md",
            # Files that should be in 600_archives
            "C8_COMPLETION_SUMMARY.md": "600_archives/C8_COMPLETION_SUMMARY.md",
            "C9_COMPLETION_SUMMARY.md": "600_archives/C9_COMPLETION_SUMMARY.md",
            "C10_COMPLETION_SUMMARY.md": "600_archives/C10_COMPLETION_SUMMARY.md",
            # Files that should be in dspy-rag-system
            "CURRENT_STATUS.md": "dspy-rag-system/docs/CURRENT_STATUS.md",
            "N8N_SETUP_GUIDE.md": "dspy-rag-system/docs/N8N_SETUP_GUIDE.md",
            # Remove @ symbols from references
            "@000_core/001_create-prd.md": "000_core/001_create-prd.md",
            "@000_core/002_generate-tasks.md": "000_core/002_generate-tasks.md",
            "@000_core/003_process-task-list.md": "000_core/003_process-task-list.md",
            "@MyFeature-PRD.md": "MyFeature-PRD.md",
            # Fix relative paths
            "../400_guides/400_comprehensive-coding-best-practices.md": (
                "400_guides/400_comprehensive-coding-best-practices.md"
            ),
            # Remove command references
            "markdownlint ./*.md": None,  # This is a command, not a file
            # Files that don't exist and should be removed
            "400_performance-optimization-guide_additional_resources.md": None,
            "400_cross-reference-strengthening-plan_additional_resources.md": None,
            "400_cross-reference-strengthening-plan_advanced_features.md": None,
            "400_cross-reference-strengthening-plan_section.md": None,
            "specialized_agent_requirements.md": None,
            "CURSOR_NATIVE_AI_STRATEGY.md": None,
            "docs/ARCHITECTURE.md": None,
            "dspy-rag-system/400_guides/400_project-overview.md": None,
            "tests/400_guides/400_project-overview.md": None,
            "999_repo-maintenance.md": None,
            "400_markdown-fix-plan.md": None,
            "600_archives/legacy-project-deliverables/CURSOR_NATIVE_AI_MIGRATION_SUMMARY.md": None,
            "600_archives/docs/400_prd-optimization-guide.md": None,
            "500_b002-completion-summary.md": None,
            "500_b031-completion-summary.md": None,
            "500_b060-completion-summary.md": None,
            "500_b065-completion-summary.md": None,
            "500_research-infrastructure-guide.md": None,
            "docs/research/articles/documentation-articles.md": None,
            "docs/research/articles/llm-development-articles.md": None,
            "docs/research/case-studies/documentation-case-studies.md": None,
            "docs/research/case-studies/successful-ai-projects.md": None,
            "docs/research/papers/ai-development-papers.md": None,
            "docs/research/tutorials/ai-development-tutorials.md": None,
            "401_memory-scaffolding-guide.md": None,
            ".github/copilot-instructions.md": None,
        }

    def load_broken_links(self, json_file: str) -> list[BrokenLink]:
        """Load broken links from validation results."""
        with open(json_file) as f:
            data = json.load(f)

        broken_links = []
        for warning in data["warnings"]:
            if "File reference not found:" in warning:
                parts = warning.split(": File reference not found: ")
                if len(parts) == 2:
                    file_path = parts[0]
                    broken_ref = parts[1].strip()
                    broken_links.append(BrokenLink(file_path, broken_ref))

        return broken_links

    def find_file_in_project(self, filename: str) -> str | None:
        """Find a file in the project using git ls-files."""
        try:
            result = subprocess.run(["git", "ls-files", f"*{filename}"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split("\n")[0]
        except Exception:
            pass
        return None

    def fix_file_references(self, file_path: str, broken_ref: str) -> bool:
        """Fix a broken reference in a file."""
        if not Path(file_path).exists():
            print(f"  ⚠️  File not found: {file_path}")
            return False

        # Get the mapping for this broken reference
        new_ref = self.file_mappings.get(broken_ref)

        if new_ref is None:
            # Try to find the file in the project
            found_file = self.find_file_in_project(broken_ref)
            if found_file:
                new_ref = found_file
            else:
                print(f"  ❌ No mapping found for: {broken_ref}")
                return False

        # Read the file content
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"  ❌ Could not read {file_path}: {e}")
            return False

        # Create patterns to match the broken reference
        patterns = [
            rf"\[([^\]]*)\]\({re.escape(broken_ref)}\)",  # Markdown links
            rf"`{re.escape(broken_ref)}`",  # Code references
            rf"{re.escape(broken_ref)}",  # Plain text references
        ]

        original_content = content
        for pattern in patterns:
            if re.search(pattern, content):
                if new_ref is None:
                    # Remove the reference entirely
                    content = re.sub(pattern, "", content)
                    print(f"  🗑️  Removed reference: {broken_ref}")
                else:
                    # Replace with the correct reference
                    content = re.sub(pattern, lambda m: m.group(0).replace(broken_ref, new_ref), content)
                    print(f"  ✅ Fixed: {broken_ref} → {new_ref}")

        # Write back if content changed
        if content != original_content:
            if not self.dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.fixes_applied += 1
                self.fixes_made.append(f"{file_path}: {broken_ref} → {new_ref}")
            else:
                print(f"  🔍 Would fix: {file_path}")
                self.fixes_made.append(f"{file_path}: {broken_ref} → {new_ref}")
            return True

        return False

    def run_fixes(self, json_file: str):
        """Run the broken link fixes."""
        print("🔧 Loading broken links...")
        broken_links = self.load_broken_links(json_file)

        print(f"📊 Found {len(broken_links)} broken references")

        # Group by file
        files_to_fix = {}
        for link in broken_links:
            if link.file not in files_to_fix:
                files_to_fix[link.file] = []
            files_to_fix[link.file].append(link.broken_reference)

        print(f"📁 Files to fix: {len(files_to_fix)}")

        for file_path, broken_refs in files_to_fix.items():
            print(f"\n🔧 Fixing {file_path}:")
            for broken_ref in broken_refs:
                self.fix_file_references(file_path, broken_ref)

        print("\n📊 Summary:")
        print(f"  Files processed: {len(files_to_fix)}")
        print(f"  Fixes {'would be ' if self.dry_run else ''}applied: {len(self.fixes_made)}")

        if self.fixes_made:
            print(f"\n📝 Fixes {'to be ' if self.dry_run else ''}applied:")
            for fix in self.fixes_made[:10]:  # Show first 10
                print(f"  {fix}")
            if len(self.fixes_made) > 10:
                print(f"  ... and {len(self.fixes_made) - 10} more")


def main():
    parser = argparse.ArgumentParser(description="Fix broken file references in documentation")
    parser.add_argument(
        "--json-file", default="broken_links_analysis.json", help="JSON file with broken links analysis"
    )
    parser.add_argument("--apply", action="store_true", help="Apply fixes (default is dry-run)")

    args = parser.parse_args()

    if not Path(args.json_file).exists():
        print(f"❌ JSON file not found: {args.json_file}")
        print(
            "💡 Run: python3 scripts/doc_coherence_validator.py "
            "--dry-run --workers 4 --emit-json broken_links_analysis.json"
        )
        return 1

    fixer = BrokenLinksFixer(dry_run=not args.apply)
    fixer.run_fixes(args.json_file)

    if not args.apply:
        print("\n💡 To apply fixes, run: python3 scripts/fix_broken_links.py --apply")

    return 0


if __name__ == "__main__":
    exit(main())
