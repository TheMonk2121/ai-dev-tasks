#!/usr/bin/env python3
"""
Documentation Coherence Validation System - B-060 Implementation

Lightweight doc-linter with Cursor AI semantic checking for the AI development ecosystem.
Implements local pre-commit hooks, reference validation, and AI-enhanced coherence checking.

Usage: python scripts/doc_coherence_validator.py [--dry-run] [--check-all] [--file FILE]
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


class DocCoherenceValidator:
    def __init__(
        self,
        dry_run: bool = True,
        check_all: bool = False,
        target_file: Optional[str] = None,
        enforce_invariants: bool = False,
        check_anchors: bool = False,
        emit_json: Optional[str] = None,
        safe_fix: bool = False,
        only_changed: bool = False,
        rules_path: Optional[str] = "config/validator_rules.json",
        strict_anchors: bool = False,
    ):
        self.dry_run = dry_run
        self.check_all = check_all
        self.target_file = target_file
        self.changes_made = []
        self.errors = []
        self.warnings = []
        self.validation_results = {}
        self.enforce_invariants = enforce_invariants
        self.check_anchors_flag = check_anchors
        self.emit_json_path = emit_json
        self.safe_fix = safe_fix
        self.only_changed = only_changed
        self.rules = self._load_rules(rules_path)
        self.strict_anchors = strict_anchors

        # VS Code markdown rules patterns
        self.heading_increment_pattern = re.compile(r"^#{1,6}\s")  # MD001
        self.heading_style_pattern = re.compile(r"^(#{1,6}|\={3,}|\-{3,})")  # MD003
        self.list_indent_pattern = re.compile(r"^\s*[-*+]\s")  # MD007
        self.trailing_spaces_pattern = re.compile(r"\s+$")  # MD009
        self.hard_tabs_pattern = re.compile(r"\t")  # MD010
        self.line_length_pattern = re.compile(r"^.{121,}$")  # MD013 (120 chars)

        # Exclude patterns (must be defined before _get_markdown_files)
        self.exclude_patterns = [
            "venv/",
            "node_modules/",
            "docs/legacy/",
            "__pycache__/",
            ".git/",
            "999_repo-maintenance.md",
            "REPO_MAINTENANCE_SUMMARY.md",
            "600_archives/",
            # Known non-prefixed allowed files
            # START_HERE.md archived; keep excluded implicitly via archives/legacy
            "DOCUMENTATION_UPDATE_SUMMARY.md",
            "RESEARCH_INTEGRATION_QUICK_START.md",
            "RESEARCH_DISPERSAL_SUMMARY.md",
            "CURSOR_NATIVE_AI_STRATEGY.md",
            "MODEL_COMPATIBILITY_ANALYSIS.md",
            "cursor_native_ai_assessment.md",
            "LM_STUDIO_SETUP.md",
            "workflow_improvement_research.md",
        ]

        # Configuration
        self.cursor_ai_enabled = self._check_cursor_ai_availability()
        self.markdown_files = self._get_markdown_files()

        # Validation patterns
        self.cross_reference_pattern = re.compile(r"<!--\s*([A-Z_]+):\s*([^>]+)\s*-->")
        self.file_reference_pattern = re.compile(r"`([^`]+\.md)`")
        self.backlog_reference_pattern = re.compile(r"B‑\d+")
        self.tldr_anchor_pattern = re.compile(r'<a\s+id="tldr"\s*>\s*</a>|<a\s+id="tldr"\s*>|\{#tldr\}', re.IGNORECASE)
        self.tldr_heading_pattern = re.compile(r"^##\s+🔎\s+TL;DR\s*$", re.MULTILINE)
        self.at_a_glance_header_pattern = re.compile(
            r"^\|\s*what this file is\s*\|\s*read when\s*\|\s*do next\s*\|\s*$", re.MULTILINE
        )
        self.html_anchor_pattern = re.compile(r'<a\s+id="([^"]+)"\s*>', re.IGNORECASE)
        self.markdown_anchor_pattern = re.compile(r"\{#([^}]+)\}", re.IGNORECASE)

        # Priority file patterns
        self.priority_files = {
            "memory_context": ["100_cursor-memory-context.md"],
            "system_overview": ["400_system-overview.md"],
            "backlog": ["000_backlog.md"],
            "project_overview": ["400_project-overview.md"],
            "context_priority": ["400_context-priority-guide.md"],
        }

    def log(self, message: str, level: str = "INFO"):
        """Log messages with consistent formatting."""
        print(f"[{level}] {message}")

    def _check_cursor_ai_availability(self) -> bool:
        """Check if Cursor AI is available for semantic validation."""
        try:
            # Check if cursor command is available
            result = subprocess.run(["which", "cursor"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log("Cursor AI available for semantic validation", "INFO")
                return True
            else:
                self.log("Cursor AI not available - using basic validation only", "WARNING")
                return False
        except Exception as e:
            self.log(f"Error checking Cursor AI availability: {e}", "WARNING")
            return False

    def _get_markdown_files(self) -> List[Path]:
        """Get all markdown files to validate."""
        all_files = []
        for file_path in Path(".").rglob("*.md"):
            if not self._should_exclude(file_path):
                all_files.append(file_path)
        if not self.only_changed:
            return all_files
        # Filter by git diff
        try:
            diff = subprocess.run(["git", "diff", "--name-only", "--cached"], capture_output=True, text=True)
            changed = set(p.strip() for p in diff.stdout.splitlines() if p.strip().endswith(".md"))
        except Exception:
            changed = set()
        priority = {
            "100_cursor-memory-context.md",
            "400_system-overview.md",
            "000_backlog.md",
            "400_project-overview.md",
            "400_context-priority-guide.md",
        }
        return [p for p in all_files if p.name in priority or str(p) in changed]

    def _load_rules(self, rules_path: Optional[str]) -> Dict:
        try:
            if rules_path and Path(rules_path).exists():
                return json.loads(Path(rules_path).read_text())
        except Exception:
            pass
        return {"canonical_links": {}, "stable_anchors": {}}

    def _should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded from validation."""
        return any(pattern in str(file_path) for pattern in self.exclude_patterns)

    def read_file(self, file_path: Path) -> Optional[str]:
        """Read file content with error handling."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            self.errors.append(f"Error reading {file_path}: {e}")
            return None

    def write_file(self, file_path: Path, content: str) -> bool:
        """Write file content with error handling."""
        if self.dry_run:
            self.log(f"[DRY-RUN] Would write {file_path}", "INFO")
            return True

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            self.errors.append(f"Error writing {file_path}: {e}")
            return False

    def task_1_validate_cross_references(self) -> bool:
        """Validate cross-references between documentation files."""
        self.log("Task 1: Validating cross-references", "INFO")

        all_references = {}
        broken_references = []

        # Collect all cross-references (only core header tags)
        for file_path in self.markdown_files:
            content = self.read_file(file_path)
            if not content:
                continue

            references = self.cross_reference_pattern.findall(content)
            for ref_type, ref_target in references:
                # Ignore non-core tags like ANCHOR, ESSENTIAL_FILES, etc.
                if ref_type not in {"CONTEXT_REFERENCE", "MODULE_REFERENCE"}:
                    continue
                if ref_type not in all_references:
                    all_references[ref_type] = []
                all_references[ref_type].append((str(file_path), ref_target.strip()))

        # Validate file references (use full repo set to avoid only-changed false negatives)
        try:
            all_md_names = {p.name for p in Path(".").rglob("*.md") if not self._should_exclude(p)}
        except Exception:
            all_md_names = {f.name for f in self.markdown_files}

        for ref_type, refs in all_references.items():
            for source_file, target in refs:
                # Check if target file exists
                target_path = Path(target)
                if not target_path.exists():
                    broken_references.append(
                        {"source": source_file, "target": target, "type": ref_type, "issue": "File not found"}
                    )
                elif target_path.suffix == ".md" and target_path.name not in all_md_names:
                    broken_references.append(
                        {"source": source_file, "target": target, "type": ref_type, "issue": "Markdown file not found"}
                    )

        # Report results
        if broken_references:
            self.log(f"Found {len(broken_references)} broken cross-references:", "WARNING")
            for ref in broken_references:
                self.log(f"  {ref['source']} -> {ref['target']} ({ref['issue']})", "WARNING")
            return False
        else:
            self.log("All cross-references are valid", "INFO")
            return True

    def task_2_validate_file_naming_conventions(self) -> bool:
        """Validate file naming conventions and hierarchy."""
        self.log("Task 2: Validating file naming conventions", "INFO")

        naming_issues = []
        # Allowlist of accepted non-prefixed files
        allowed = {
            "README.md",
            "LICENSE.md",
            "DOCUMENTATION_UPDATE_SUMMARY.md",
            "RESEARCH_INTEGRATION_QUICK_START.md",
            "RESEARCH_DISPERSAL_SUMMARY.md",
            "CURSOR_NATIVE_AI_STRATEGY.md",
            "cursor_native_ai_assessment.md",
            "workflow_improvement_research.md",
        }

        for file_path in self.markdown_files:
            filename = file_path.name

            # Check three-digit prefix pattern
            if not re.match(r"^\d{3}_", filename):
                if filename not in allowed:
                    naming_issues.append({"file": str(file_path), "issue": "Missing three-digit prefix"})

            # Check for descriptive names
            if re.match(r"^\d{3}_[a-z-]+\.md$", filename):
                # Valid format
                pass
            elif filename not in allowed:
                naming_issues.append({"file": str(file_path), "issue": "Invalid naming format"})

        # Report results
        if naming_issues:
            self.log(f"Found {len(naming_issues)} naming convention issues:", "WARNING")
            for issue in naming_issues:
                self.log(f"  {issue['file']}: {issue['issue']}", "WARNING")
            # In dry-run (pre-commit), treat naming issues as warnings only to avoid churn
            if self.dry_run:
                return True
            return False
        else:
            self.log("All files follow naming conventions", "INFO")
            return True

    def task_3_validate_backlog_references(self) -> bool:
        """Validate backlog item references in documentation."""
        self.log("Task 3: Validating backlog references", "INFO")

        # Read backlog to get valid item IDs
        backlog_content = self.read_file(Path("000_backlog.md"))
        if not backlog_content:
            self.log("Cannot read backlog file", "ERROR")
            return False

        valid_backlog_items = set(self.backlog_reference_pattern.findall(backlog_content))

        # Check references in other files
        invalid_references = []

        for file_path in self.markdown_files:
            if file_path.name == "000_backlog.md":
                continue

            content = self.read_file(file_path)
            if not content:
                continue

            references = self.backlog_reference_pattern.findall(content)
            for ref in references:
                if ref not in valid_backlog_items:
                    invalid_references.append(
                        {"file": str(file_path), "reference": ref, "issue": "Invalid backlog item reference"}
                    )

        # Report results
        if invalid_references:
            self.log(f"Found {len(invalid_references)} invalid backlog references:", "WARNING")
            for ref in invalid_references:
                self.log(f"  {ref['file']}: {ref['reference']} ({ref['issue']})", "WARNING")
            return False
        else:
            self.log("All backlog references are valid", "INFO")
            return True

    def task_4_validate_memory_context_coherence(self) -> bool:
        """Validate memory context coherence with other documentation."""
        self.log("Task 4: Validating memory context coherence", "INFO")

        memory_context = self.read_file(Path("100_cursor-memory-context.md"))
        if not memory_context:
            self.log("Cannot read memory context file", "ERROR")
            return False

        coherence_issues = []

        # Check for consistency with backlog
        backlog_content = self.read_file(Path("000_backlog.md"))
        if backlog_content:
            # Extract current priorities from memory context
            priority_pattern = r"Current Sprint.*?B-\d+"
            memory_priorities = re.findall(priority_pattern, memory_context)

            # Check if mentioned priorities exist in backlog
            for priority in memory_priorities:
                backlog_id = re.search(r"B-\d+", priority)
                if backlog_id and backlog_id.group() not in backlog_content:
                    coherence_issues.append(
                        {
                            "issue": f"Memory context references non-existent backlog item: {backlog_id.group()}",
                            "file": "100_cursor-memory-context.md",
                        }
                    )

        # Check for consistency with system overview
        system_overview = self.read_file(Path("400_system-overview.md"))
        if system_overview:
            # Check for architectural consistency
            if "DSPy" in memory_context and "DSPy" not in system_overview:
                coherence_issues.append(
                    {
                        "issue": "Memory context mentions DSPy but system overview does not",
                        "file": "100_cursor-memory-context.md",
                    }
                )

        # Report results
        if coherence_issues:
            self.log(f"Found {len(coherence_issues)} coherence issues:", "WARNING")
            for issue in coherence_issues:
                self.log(f"  {issue['file']}: {issue['issue']}", "WARNING")
            return False
        else:
            self.log("Memory context is coherent with other documentation", "INFO")
            return True

    def task_5_cursor_ai_semantic_validation(self) -> bool:
        """Use Cursor AI for semantic validation of documentation."""
        if not self.cursor_ai_enabled:
            self.log("Skipping Cursor AI validation - not available", "INFO")
            return True

        self.log("Task 5: Running Cursor AI semantic validation", "INFO")

        semantic_issues = []

        # Validate priority files with Cursor AI
        for category, files in self.priority_files.items():
            for filename in files:
                file_path = Path(filename)
                if file_path.exists():
                    issues = self._validate_file_with_cursor_ai(file_path, category)
                    semantic_issues.extend(issues)

        # Report results
        if semantic_issues:
            self.log(f"Found {len(semantic_issues)} semantic issues:", "WARNING")
            for issue in semantic_issues:
                self.log(f"  {issue['file']}: {issue['issue']}", "WARNING")
            return False
        else:
            self.log("All files pass semantic validation", "INFO")
            return True

    def _validate_file_with_cursor_ai(self, file_path: Path, category: str) -> List[Dict]:
        """Validate a file using Cursor AI semantic checking."""
        issues = []

        try:
            # Read file content first
            content = self.read_file(file_path)
            if not content:
                self.log(f"Could not read file {file_path}", "WARNING")
                return issues

            # Create a prompt for Cursor AI validation
            prompt = f"""
            Analyze the following documentation file for coherence and consistency issues.

            File: {file_path.name}
            Category: {category}

            Check for:
            1. Internal consistency and logical flow
            2. Proper use of cross-references and links
            3. Consistent terminology and naming
            4. Completeness of information
            5. Clarity and readability

            File content:
            {content[:2000]}  # First 2000 chars for analysis

            Provide a JSON response with any issues found:
            {{"issues": [{{"type": "error|warning", "description": "issue description"}}]}}
            """

            # Run Cursor AI analysis
            result = subprocess.run(["cursor", "chat", "--prompt", prompt], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout)
                    for issue in response.get("issues", []):
                        issues.append({"file": str(file_path), "issue": issue["description"], "type": issue["type"]})
                except json.JSONDecodeError:
                    self.log(f"Invalid JSON response from Cursor AI for {file_path}", "WARNING")
            else:
                self.log(f"Cursor AI validation failed for {file_path}: {result.stderr}", "WARNING")

        except subprocess.TimeoutExpired:
            self.log(f"Cursor AI validation timed out for {file_path}", "WARNING")
        except Exception as e:
            self.log(f"Error running Cursor AI validation for {file_path}: {e}", "WARNING")

        return issues

    def task_6_generate_validation_report(self) -> bool:
        """Generate a comprehensive validation report."""
        self.log("Task 6: Generating validation report", "INFO")

        report = {
            "timestamp": subprocess.run(["date"], capture_output=True, text=True).stdout.strip(),
            "files_checked": len(self.markdown_files),
            "cursor_ai_enabled": self.cursor_ai_enabled,
            "validation_results": self.validation_results,
            "errors": self.errors,
            "warnings": self.warnings,
            "changes_made": self.changes_made,
        }

        # Write report
        report_file = Path("docs/validation_report.json")
        report_file.parent.mkdir(exist_ok=True)

        if not self.dry_run:
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2, sort_keys=True)
            self.log(f"Validation report written to {report_file}", "INFO")
        else:
            self.log(f"[DRY-RUN] Would write validation report to {report_file}", "INFO")

        return True

    def task_enforce_invariants(self) -> bool:
        if not self.enforce_invariants:
            return True
        self.log("Enforcing core documentation invariants", "INFO")
        passed = True
        for file_path in self.markdown_files:
            content = self.read_file(file_path)
            if not content:
                continue
            issues = []
            # Metadata header
            if "<!-- CONTEXT_REFERENCE:" not in content or "<!-- MEMORY_CONTEXT:" not in content:
                issues.append("Missing metadata header (CONTEXT_REFERENCE or MEMORY_CONTEXT)")
            # TL;DR anchor and heading
            if not self.tldr_anchor_pattern.search(content) or not self.tldr_heading_pattern.search(content):
                issues.append("Missing TL;DR anchor or heading")
            # At-a-glance table header
            if not self.at_a_glance_header_pattern.search(content):
                issues.append("Missing At-a-glance table after TL;DR")
            # Canonical links (best-effort string presence check)
            if (
                self.rules["canonical_links"].get("quick_start")
                and self.rules["canonical_links"]["quick_start"] not in content
                and "Quick Start" in content
            ):
                issues.append("Quick Start present but missing canonical link to 400_project-overview.md")
            if (
                self.rules["canonical_links"].get("critical_path")
                and self.rules["canonical_links"]["critical_path"] not in content
                and "Critical Path" in content
            ):
                issues.append("Critical Path present but missing canonical link to 400_context-priority-guide.md")
            if (
                self.rules["canonical_links"].get("prd_scoring")
                and self.rules["canonical_links"]["prd_scoring"] not in content
                and ("PRD" in content or "Scoring" in content)
            ):
                issues.append("PRD/Scoring mentioned but missing canonical link to 100_backlog-guide.md")
            if issues:
                passed = False
                self.warnings.append({"file": str(file_path), "invariant_issues": issues})
                # Safe fix scaffolding (TL;DR + At-a-glance)
                if self.safe_fix:
                    new_content = content
                    if not self.tldr_anchor_pattern.search(new_content):
                        new_content = (
                            new_content.replace("\n##", '\n<a id="tldr"></a>\n\n##', 1)
                            if "\n##" in new_content
                            else (
                                '<a id="tldr"></a>\n\n## 🔎 TL;DR\n\n'
                                "| what this file is | read when | do next |\n"
                                "|---|---|---|\n"
                                "|  |  |  |\n\n" + new_content
                            )
                        )
                    if not self.tldr_heading_pattern.search(new_content):
                        new_content = new_content.replace('<a id="tldr"></a>', '<a id="tldr"></a>\n\n## 🔎 TL;DR')
                    if not self.at_a_glance_header_pattern.search(new_content):
                        new_content = new_content.replace(
                            "## 🔎 TL;DR",
                            "## 🔎 TL;DR\n\n| what this file is | read when | do next |\n|---|---|---|\n|  |  |  |",
                            1,
                        )
                    if new_content != content:
                        if self.write_file(file_path, new_content):
                            self.changes_made.append(str(file_path))
        return passed

    def task_check_anchors(self) -> bool:
        if not self.check_anchors_flag:
            return True
        self.log("Checking anchors (warn for non-TLDR explicit anchors)", "INFO")
        ok = True
        for file_path in self.markdown_files:
            content = self.read_file(file_path)
            if not content:
                continue
            # Check HTML anchors
            for match in self.html_anchor_pattern.finditer(content):
                anchor_id = match.group(1)
                if anchor_id.lower() != "tldr":
                    ok = False
                    self.warnings.append(
                        {
                            "file": str(file_path),
                            "anchor": anchor_id,
                            "issue": "Non-TLDR explicit HTML anchor - replace with heading-based anchor",
                        }
                    )
            # Check markdown anchors
            for match in self.markdown_anchor_pattern.finditer(content):
                anchor_id = match.group(1)
                if anchor_id.lower() != "tldr":
                    ok = False
                    self.warnings.append(
                        {
                            "file": str(file_path),
                            "anchor": anchor_id,
                            "issue": "Non-TLDR explicit markdown anchor - replace with heading-based anchor",
                        }
                    )
        # Emit JSON if requested
        if self.emit_json_path:
            data = {"warnings": self.warnings, "files_checked": len(self.markdown_files)}
            try:
                with open(self.emit_json_path, "w") as f:
                    json.dump(data, f, indent=2, sort_keys=True)
                self.log(f"Anchor report written to {self.emit_json_path}", "INFO")
            except Exception as e:
                self.log(f"Failed to write {self.emit_json_path}: {e}", "WARNING")
        # In strict mode, treat any non-TLDR explicit anchors as errors
        if self.strict_anchors and not ok:
            self.errors.append("Non-TLDR explicit anchors found (strict mode)")
        return ok if not self.strict_anchors else ok and True

    def task_7_validate_markdown_rules(self) -> bool:
        """Validate VS Code markdown rules compliance."""
        self.log("Task 7: Validating VS Code markdown rules", "INFO")

        markdown_issues = []

        for file_path in self.markdown_files:
            content = self.read_file(file_path)
            if not content:
                continue

            lines = content.splitlines()
            prev_heading_level = 0

            for line_num, line in enumerate(lines, 1):
                # MD001: Heading increment
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

                # MD013: Line length
                if self.line_length_pattern.match(line):
                    markdown_issues.append(
                        {
                            "file": str(file_path),
                            "line": line_num,
                            "rule": "MD013",
                            "issue": "Line length exceeds 120 characters",
                        }
                    )

        # Report results
        if markdown_issues:
            self.log(f"Found {len(markdown_issues)} markdown rule violations:", "WARNING")
            for issue in markdown_issues:
                self.log(f"  {issue['file']}:{issue['line']} - {issue['rule']}: {issue['issue']}", "WARNING")
            return False
        else:
            self.log("All files pass VS Code markdown rules", "INFO")
            return True

    def run_all_validations(self) -> bool:
        """Run all validation tasks."""
        self.log("Starting Documentation Coherence Validation System", "INFO")

        tasks = [
            ("Cross-reference validation", self.task_1_validate_cross_references),
            ("File naming conventions", self.task_2_validate_file_naming_conventions),
            ("Backlog reference validation", self.task_3_validate_backlog_references),
            ("Memory context coherence", self.task_4_validate_memory_context_coherence),
            ("Cursor AI semantic validation", self.task_5_cursor_ai_semantic_validation),
            ("VS Code markdown rules", self.task_7_validate_markdown_rules),
            ("Generate validation report", self.task_6_generate_validation_report),
        ]

        all_passed = True

        for task_name, task_func in tasks:
            try:
                result = task_func()
                self.validation_results[task_name] = result
                if not result:
                    all_passed = False
            except Exception as e:
                self.log(f"Error in {task_name}: {e}", "ERROR")
                self.validation_results[task_name] = False
                all_passed = False

        # Summary
        if all_passed:
            self.log("All validation tasks passed!", "INFO")
        else:
            self.log("Some validation tasks failed. Check the warnings above.", "WARNING")

        return all_passed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Documentation Coherence Validation System")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Run in dry-run mode (default)")
    parser.add_argument("--check-all", action="store_true", help="Check all files (default: only priority files)")
    parser.add_argument("--file", type=str, help="Check specific file only")
    parser.add_argument("--no-dry-run", action="store_true", help="Actually make changes (not dry-run)")
    parser.add_argument("--enforce-invariants", action="store_true", help="Enforce core doc invariants")
    parser.add_argument("--check-anchors", action="store_true", help="Check anchors and flag non-TLDR explicit anchors")
    parser.add_argument("--emit-json", type=str, help="Emit JSON report to path (e.g., docs_health.json)")
    parser.add_argument("--fix", action="store_true", help="Safely scaffold missing TL;DR / At-a-glance")
    parser.add_argument("--only-changed", action="store_true", help="Validate only changed files plus priority set")
    parser.add_argument("--rules", type=str, default="config/validator_rules.json", help="Path to validator rules JSON")
    parser.add_argument("--strict-anchors", action="store_true", help="Treat non-TLDR explicit anchors as errors")

    args = parser.parse_args()

    # Handle dry-run logic
    dry_run = args.dry_run and not args.no_dry_run

    # Initialize validator
    validator = DocCoherenceValidator(
        dry_run=dry_run,
        check_all=args.check_all,
        target_file=args.file,
        enforce_invariants=args.enforce_invariants,
        check_anchors=args.check_anchors,
        emit_json=args.emit_json,
        safe_fix=args.fix,
        only_changed=args.only_changed,
        rules_path=args.rules,
        strict_anchors=args.strict_anchors,
    )

    # Run validations
    success = validator.run_all_validations()
    if args.enforce_invariants:
        success = validator.task_enforce_invariants() and success
    if args.check_anchors:
        success = validator.task_check_anchors() and success

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
