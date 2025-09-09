#!/usr/bin/env python3
"""
Relaxed Documentation Coherence Validator
Ignores line length violations but enforces critical structural issues.
"""

import sys
from pathlib import Path

# Add the scripts directory to the path so we can import the main validator
sys.path.insert(0, str(Path(__file__).parent))

from doc_coherence_validator import DocCoherenceValidator


class RelaxedDocValidator(DocCoherenceValidator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override the line length pattern to not match anything (effectively disabling MD013)
        self.line_length_pattern = None

    def task_7_validate_markdown_rules(self) -> bool:
        """Validate VS Code markdown rules compliance (ignoring line length)."""
        self.log("Task 7: Validating VS Code markdown rules (relaxed - ignoring line length)", "INFO")

        markdown_issues = []

        for file_path in self.markdown_files:
            content = self.read_file(file_path)
            if not content:
                continue

            lines = content.splitlines()
            prev_heading_level = 0

            for line_num, line in enumerate(lines, 1):
                # MD001: Heading increment (CRITICAL - must enforce)
                if self.heading_increment_pattern.match(line):
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
                if self.trailing_spaces_pattern.search(line):
                    markdown_issues.append(
                        {"file": str(file_path), "line": line_num, "rule": "MD009", "issue": "Trailing spaces detected"}
                    )

                # MD010: Hard tabs
                if self.hard_tabs_pattern.search(line):
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


def main():
    """Main entry point for relaxed validation."""
    import argparse

    parser = argparse.ArgumentParser(description="Relaxed Documentation Coherence Validator")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry run mode")
    parser.add_argument("--check-all", action="store_true", help="Check all files")
    parser.add_argument("--file", help="Check specific file")
    parser.add_argument("--enforce-invariants", action="store_true", help="Enforce invariants")
    parser.add_argument("--check-anchors", action="store_true", help="Check anchors")
    parser.add_argument("--emit-json", help="Emit JSON report")
    parser.add_argument("--safe-fix", action="store_true", help="Safe fix mode")
    parser.add_argument("--only-changed", action="store_true", help="Only check changed files")
    parser.add_argument("--rules-path", default="config/validator_rules.json", help="Rules path")
    parser.add_argument("--strict-anchors", action="store_true", help="Strict anchors mode")

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
