from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from .doc_coherence_validator import DocCoherenceValidator

#!/usr/bin/env python3
"""
Relaxed Documentation Coherence Validator
Ignores line length violations but enforces critical structural issues.
"""

# Add the scripts directory to the path so we can import the main validator
sys.path.insert(0, str(Path(__file__).parent))


class DocumentStyleValidator:
    line_length_pattern: str | None = r"^\s*(.{1,120})\s*$"
    heading_increment_pattern: str | None = r"^(#+)\s*(.+)$"
    trailing_spaces_pattern: str | None = r"\s+$"
    hard_tabs_pattern: str | None = r"\t"

    def validate_document_style(self) -> None:
        # Placeholder implementation
        pass


def process_document_validation(validator: DocumentStyleValidator) -> None:
    # Example of handling unused call results
    _ = validator.validate_document_style()


class RelaxedDocValidator(DocCoherenceValidator):
    line_length_pattern: re.Pattern[str] | None = None
    heading_increment_pattern: re.Pattern[str] | None = None
    trailing_spaces_pattern: re.Pattern[str] | None = None
    hard_tabs_pattern: re.Pattern[str] | None = None

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        # Override the line length pattern to not match anything (effectively disabling MD013)
        self.line_length_pattern = None
        # Ensure required patterns exist for relaxed checks
        self.heading_increment_pattern = re.compile(r"^#{1,6}\s+")
        self.trailing_spaces_pattern = re.compile(r"[ \t]+$")
        self.hard_tabs_pattern = re.compile(r"\t")

    def log(self, message: str, level: str = "INFO") -> None:  # minimal logger shim
        print(f"[{level}] {message}")

    def task_7_validate_markdown_rules(self) -> bool:
        """Validate VS Code markdown rules compliance (ignoring line length)."""
        self.log("Task 7: Validating VS Code markdown rules (relaxed - ignoring line length)", "INFO")

        markdown_issues: list[dict[str, Any]] = []

        for file_path in self.markdown_files:
            content = self.read_file(file_path)
            if not content:
                continue

            lines = content.splitlines()
            prev_heading_level = 0

            for line_num, line in enumerate(lines, 1):
                # MD001: Heading increment (CRITICAL - must enforce)
                if self.heading_increment_pattern and self.heading_increment_pattern.match(line):
                    current_level = len(line.split()[0])  # Count #s
                    if prev_heading_level > 0 and current_level > prev_heading_level + 1:
                        markdown_issues.append(
                            {
                                "file": str(file_path),
                                "line": line_num,
                                "rule": "MD001",
                                "issue": "Heading levels should only increment by one level",
                            }
                        )
                    prev_heading_level = current_level

                # MD009: Trailing spaces
                if self.trailing_spaces_pattern and self.trailing_spaces_pattern.search(line):
                    markdown_issues.append(
                        {"file": str(file_path), "line": line_num, "rule": "MD009", "issue": "Trailing spaces detected"}
                    )

                # MD010: Hard tabs
                if self.hard_tabs_pattern and self.hard_tabs_pattern.search(line):
                    markdown_issues.append(
                        {"file": str(file_path), "line": line_num, "rule": "MD010", "issue": "Hard tabs detected"}
                    )

                # MD013: Line length (IGNORED in relaxed mode)
                # We skip this check by not having the pattern

        # Report results
        if markdown_issues:
            self.log(f"Found {len(markdown_issues)} critical markdown rule violations:", "WARNING")
            for issue in markdown_issues:
                self.log(f"  {issue['file']}:{issue['line']} - {issue['rule']}: {issue['issue']}", "WARNING")
            return False
        else:
            self.log("All files pass critical VS Code markdown rules (line length ignored)", "INFO")
            return True


def main() -> None:
    """Main entry point for relaxed validation."""

    parser = argparse.ArgumentParser(description="Relaxed Documentation Coherence Validator")
    _ = parser.add_argument("--dry-run", action="store_true", default=True, help="Dry run mode")
    _ = parser.add_argument("--check-all", action="store_true", help="Check all files")
    _ = parser.add_argument("--file", help="Check specific file")
    _ = parser.add_argument("--enforce-invariants", action="store_true", help="Enforce invariants")
    _ = parser.add_argument("--check-anchors", action="store_true", help="Check anchors")
    _ = parser.add_argument("--emit-json", help="Emit JSON report")
    _ = parser.add_argument("--safe-fix", action="store_true", help="Safe fix mode")
    _ = parser.add_argument("--only-changed", action="store_true", help="Only check changed files")
    _ = parser.add_argument("--rules-path", default="config/validator_rules.json", help="Rules path")
    _ = parser.add_argument("--strict-anchors", action="store_true", help="Strict anchors mode")

    args = parser.parse_args()

    # Create relaxed validator
    validator = RelaxedDocValidator(
        dry_run=args.dry_run,
        check_all=args.check_all,
        target_file=args.file,
        enforce_invariants=args.enforce_invariants,
        check_anchors=args.check_anchors,
        emit_json=args.emit_json,
        safe_fix=args.safe_fix,
        only_changed=args.only_changed,
        rules_path=args.rules_path,
        strict_anchors=args.strict_anchors,
    )

    # Run validation
    success = validator.run_all_validations()

    if success:
        print("✅ Relaxed validation passed (line length violations ignored)")
        sys.exit(0)
    else:
        print("❌ Relaxed validation failed (critical issues found)")
        sys.exit(1)


if __name__ == "__main__":
    main()
