#!/usr/bin/env python3
"""
Fix Duplicate TL;DR Sections

This script removes duplicate TL;DR sections and ensures only one correct format exists.
"""

import re
from pathlib import Path


def fix_duplicate_tldr(file_path: Path) -> bool:
    """Fix duplicate TL;DR sections in a file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Find all TL;DR sections
        tldr_sections = []
        for i, line in enumerate(lines):
            if re.match(r"^##\s*🔎\s*TL;DR\s*.*$", line):
                tldr_sections.append(i)

        if len(tldr_sections) <= 1:
            return False  # No duplicates to fix

        print(f"Found {len(tldr_sections)} TL;DR sections in {file_path}")

        # Remove all TL;DR sections except the first one
        new_lines = []
        skip_until = -1

        for i, line in enumerate(lines):
            if i in tldr_sections[1:]:  # Skip duplicate TL;DR sections
                skip_until = len(lines)
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith("## ") and not lines[j].startswith("## 🔎 TL;DR"):
                        skip_until = j
                        break
                continue

            if i >= skip_until:
                skip_until = -1

            if skip_until == -1:
                new_lines.append(line)

        # Write the cleaned content
        file_path.write_text("\n".join(new_lines), encoding="utf-8")
        print(f"✅ Fixed duplicate TL;DR sections in {file_path}")
        return True

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main execution."""
    files_to_fix = [
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

    fixed_count = 0
    for file_path_str in files_to_fix:
        file_path = Path(file_path_str)
        if file_path.exists():
            if fix_duplicate_tldr(file_path):
                fixed_count += 1

    print(f"\n📊 Fixed {fixed_count} files with duplicate TL;DR sections")

if __name__ == "__main__":
    main()
