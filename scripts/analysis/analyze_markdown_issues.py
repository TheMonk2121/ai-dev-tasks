from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

#!/usr/bin/env python3
"""
Markdown Linting Issues Analyzer
Analyzes markdown files and provides a prioritized summary of issues.
"""

def run_markdownlint():
    """Run markdownlint and return JSON output."""
    try:
        # Find all markdown files excluding venv, node_modules, and .git
        cmd = [
            "find",
            ".",
            "-name",
            "*.md",
            "-not",
            "-path",
            "./venv/*",
            "-not",
            "-path",
            "./node_modules/*",
            "-not",
            "-path",
            "./.git/*",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("Error finding markdown files")
            return []

        markdown_files = result.stdout.strip().split("\n")
        if not markdown_files or markdown_files == [""]:
            print("No markdown files found")
            return []

        print(f"Found {len(markdown_files)} markdown files")

        # Process files in batches to avoid command line length limits
        batch_size = 20
        all_issues = []

        for i in range(0, len(markdown_files), batch_size):
            batch = markdown_files[i : i + batch_size]
            print(
                f"Processing batch {i//batch_size + 1}/{(len(markdown_files) + batch_size - 1)//batch_size} ({len(batch)} files)"
            )

            # Run markdownlint on batch
            lint_cmd = ["markdownlint", "--config", ".markdownlint.jsonc", "--json"] + batch
            result = subprocess.run(lint_cmd, capture_output=True, text=True)

            # markdownlint returns exit code 1 when issues are found, 0 when clean
            if result.returncode == 0:
                continue

            # Parse JSON output (markdownlint outputs to stderr when using --json)
            try:
                batch_issues = json.loads(result.stderr)
                all_issues.extend(batch_issues)
            except json.JSONDecodeError as e:
                print(f"Error parsing markdownlint JSON output for batch {i//batch_size + 1}: {e}")
                print(f"Output: {result.stderr[:200]}...")
                continue

        return all_issues

    except Exception as e:
        print(f"Error running markdownlint: {e}")
        return []

def analyze_issues(issues):
    """Analyze and categorize issues."""
    issue_counts = defaultdict(int)
    file_issues = defaultdict(list)
    rule_descriptions = {}

    for issue in issues:
        rule_name = issue.get("ruleNames", ["unknown"])[0]
        rule_desc = issue.get("ruleDescription", "Unknown rule")
        file_path = issue.get("fileName", "unknown")

        issue_counts[rule_name] += 1
        rule_descriptions[rule_name] = rule_desc
        file_issues[file_path].append(
            {
                "rule": rule_name,
                "line": issue.get("lineNumber", 0),
                "description": rule_desc,
                "context": issue.get("errorContext", ""),
            }
        )

    return issue_counts, file_issues, rule_descriptions

def print_summary(issue_counts, rule_descriptions):
    """Print prioritized summary of issues."""
    print("=" * 80)
    print("MARKDOWN LINTING ISSUES - PRIORITIZED BY FREQUENCY")
    print("=" * 80)
    print()

    # Sort by count (descending)
    sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)

    total_issues = sum(issue_counts.values())
    print(f"Total Issues Found: {total_issues}")
    print(f"Unique Rule Types: {len(issue_counts)}")
    print()

    print("ISSUE PRIORITY RANKING:")
    print("-" * 50)

    for i, (rule, count) in enumerate(sorted_issues, 1):
        percentage = (count / total_issues) * 100
        description = rule_descriptions.get(rule, "Unknown rule")
        print(f"{i:2d}. {rule:15} - {count:3d} instances ({percentage:5.1f}%)")
        print(f"     {description}")
        print()

    return sorted_issues

def print_file_breakdown(file_issues, top_rules):
    """Print breakdown by file for top issues."""
    print("FILE BREAKDOWN FOR TOP ISSUES:")
    print("-" * 50)

    # Get top 5 rules
    top_rule_names = [rule for rule, _ in top_rules[:5]]

    for rule in top_rule_names:
        print(f"\n{rule} - Files affected:")
        rule_files = defaultdict(int)

        for file_path, issues in file_issues.items():
            for issue in issues:
                if issue["rule"] == rule:
                    rule_files[file_path] += 1

        # Sort files by issue count
        sorted_files = sorted(rule_files.items(), key=lambda x: x[1], reverse=True)

        for file_path, count in sorted_files[:10]:  # Show top 10 files
            relative_path = Path(file_path).relative_to(".")
            print(f"  {relative_path}: {count} issues")

        if len(sorted_files) > 10:
            print(f"  ... and {len(sorted_files) - 10} more files")

def print_fix_recommendations(top_rules, rule_descriptions):
    """Print fix recommendations for top issues."""
    print("\n" + "=" * 80)
    print("FIX RECOMMENDATIONS")
    print("=" * 80)

    recommendations = {
        "MD033": 'Convert HTML anchor tags to markdown-style anchors: <a id="name"></a> → {#name}',
        "MD047": 'Add single newline at end of files: echo "" >> filename.md',
        "MD012": "Remove multiple consecutive blank lines, keep only one",
        "MD040": "Add language specification to code blocks: ``` → ```python",
        "MD041": "Add H1 heading at top of file (after comments): # Title",
        "MD034": "Wrap bare URLs in angle brackets: http://example.com → <http://example.com>",
        "MD037": "Remove spaces inside emphasis markers: ** text ** → **text**",
        "MD032": "Add blank lines around lists",
        "MD005": "Fix list indentation consistency",
        "MD007": "Fix unordered list indentation",
        "MD029": "Fix ordered list numbering (should start with 1)",
        "MD004": "Use consistent unordered list style (asterisk, dash, or plus)",
        "MD001": "Fix heading increment (should only increment by one level)",
    }

    for rule, count in top_rules[:10]:
        desc = rule_descriptions.get(rule, "Unknown rule")
        rec = recommendations.get(rule, "Manual review required")
        print(f"\n{rule}: {desc}")
        print(f"  Recommendation: {rec}")
        print(f"  Instances: {count}")

def main():
    """Main analysis function."""
    print("Analyzing markdown linting issues...")

    issues = run_markdownlint()
    if not issues:
        print("No markdown linting issues found!")
        return

    print(f"Found {len(issues)} total issues")

    issue_counts, file_issues, rule_descriptions = analyze_issues(issues)
    top_rules = print_summary(issue_counts, rule_descriptions)
    print_file_breakdown(file_issues, top_rules)
    print_fix_recommendations(top_rules, rule_descriptions)

    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("1. Start with the highest frequency issues (MD033, MD047)")
    print("2. Use automated fixes where possible")
    print("3. Create a systematic plan to address each rule type")
    print("4. Update pre-commit hooks to prevent new issues")
    print("=" * 80)

if __name__ == "__main__":
    main()
