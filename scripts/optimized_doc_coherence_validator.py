#!/usr/bin/env python3
"""
Optimized Documentation Coherence Validation System

Enhanced version with parallel processing, only-changed mode, and caching.
Target: 50% performance improvement (0.80s → <0.40s)

Usage: python scripts/optimized_doc_coherence_validator.py [--dry-run] [--only-changed] [--workers N] [--json]
"""

import argparse
import json
import multiprocessing
import pickle
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Set

# Pre-compile all regex patterns at module level for performance
HEADING_INCREMENT_PATTERN = re.compile(r"^#{1,6}\s")
HEADING_STYLE_PATTERN = re.compile(r"^(#{1,6}|\={3,}|\-{3,})")
LIST_INDENT_PATTERN = re.compile(r"^\s*[-*+]\s")
TRAILING_SPACES_PATTERN = re.compile(r"\s+$")
HARD_TABS_PATTERN = re.compile(r"\t")
LINE_LENGTH_PATTERN = re.compile(r"^.{121,}$")
CROSS_REFERENCE_PATTERN = re.compile(r"<!--\s*([A-Z_]+):\s*([^>]+)\s*-->")
FILE_REFERENCE_PATTERN = re.compile(r"`([^`]+\.md)`")
BACKLOG_REFERENCE_PATTERN = re.compile(r"B‑\d+")
TLDR_ANCHOR_PATTERN = re.compile(r'<a\s+id="tldr"\s*>\s*</a>|<a\s+id="tldr"\s*>|\{#tldr\}', re.IGNORECASE)
TLDR_HEADING_PATTERN = re.compile(r"^##\s+🔎\s+TL;DR\s*$", re.MULTILINE)
AT_A_GLANCE_HEADER_PATTERN = re.compile(
    r"^\|\s*what this file is\s*\|\s*read when\s*\|\s*do next\s*\|\s*$", re.MULTILINE
)
HTML_ANCHOR_PATTERN = re.compile(r'<a\s+id="([^"]+)"\s*>', re.IGNORECASE)
MARKDOWN_ANCHOR_PATTERN = re.compile(r"\{#([^}]+)\}", re.IGNORECASE)


class OptimizedDocCoherenceValidator:
    def __init__(
        self,
        dry_run: bool = True,
        only_changed: bool = False,
        max_workers: Optional[int] = None,
        cache_ttl: int = 300,
        emit_json: Optional[str] = None,
        safe_fix: bool = False,
        rules_path: Optional[str] = "config/validator_rules.json",
        strict_anchors: bool = False,
    ):
        self.dry_run = dry_run
        self.only_changed = only_changed
        self.max_workers = max_workers or min(8, multiprocessing.cpu_count() + 2)
        self.cache_ttl = cache_ttl
        self.emit_json_path = emit_json
        self.safe_fix = safe_fix
        self.rules = self._load_rules(rules_path)
        self.strict_anchors = strict_anchors

        # Cache directory
        self.cache_dir = Path(".cache/doc_validator")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Exclude patterns
        self.exclude_patterns = [
            "venv/",
            "node_modules/",
            "docs/legacy/",
            "__pycache__/",
            ".git/",
            "999_repo-maintenance.md",
            "REPO_MAINTENANCE_SUMMARY.md",
            "600_archives/",
            "DOCUMENTATION_UPDATE_SUMMARY.md",
            "RESEARCH_INTEGRATION_QUICK_START.md",
            "RESEARCH_DISPERSAL_SUMMARY.md",
            "CURSOR_NATIVE_AI_STRATEGY.md",
            "MODEL_COMPATIBILITY_ANALYSIS.md",
            "cursor_native_ai_assessment.md",
            "LM_STUDIO_SETUP.md",
            "workflow_improvement_research.md",
        ]

        # Priority file patterns
        self.priority_files = {
            "memory_context": ["100_memory/100_cursor-memory-context.md"],
            "backlog": ["000_core/000_backlog.md"],
            "system_overview": ["400_guides/400_system-overview.md"],
            "project_overview": ["400_guides/400_project-overview.md"],
        }

        self.changes_made = []
        self.errors = []
        self.warnings = []
        self.validation_results = {}

    def _load_rules(self, rules_path: Optional[str]) -> Dict:
        """Load validation rules from JSON file."""
        if rules_path and Path(rules_path).exists():
            try:
                with open(rules_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def get_cache_key(self, file_path: Path) -> str:
        """Generate cache key for a file."""
        try:
            # Use git hash for cache invalidation
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H", "--", str(file_path)], capture_output=True, text=True, timeout=5
            )
            git_hash = result.stdout.strip()[:8] if result.returncode == 0 else "unknown"
        except Exception:
            git_hash = "unknown"

        return f"{file_path.name}_{git_hash}"

    def load_cached_result(self, file_path: Path) -> Optional[Dict]:
        """Load cached validation result if available and valid."""
        cache_key = self.get_cache_key(file_path)
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        if cache_file.exists():
            try:
                with open(cache_file, "rb") as f:
                    cached_data = pickle.load(f)

                # Check if cache is still valid
                if time.time() - cached_data.get("timestamp", 0) < self.cache_ttl:
                    return cached_data.get("result")
            except Exception:
                pass

        return None

    def save_cached_result(self, file_path: Path, result: Dict):
        """Save validation result to cache."""
        cache_key = self.get_cache_key(file_path)
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        try:
            with open(cache_file, "wb") as f:
                pickle.dump({"result": result, "timestamp": time.time()}, f)
        except Exception:
            pass

    def get_changed_markdown_files(self) -> Set[Path]:
        """Get only changed Markdown files using git diff."""
        if not self.only_changed:
            return set()

        try:
            # Get changed files from git
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                changed_files = set()
                for line in result.stdout.strip().split("\n"):
                    if line.strip() and line.endswith(".md"):
                        file_path = Path(line.strip())
                        if self._should_validate_file(file_path):
                            changed_files.add(file_path)
                return changed_files
        except Exception as e:
            self.warnings.append(f"Could not get changed files: {e}")

        return set()

    def _should_validate_file(self, file_path: Path) -> bool:
        """Check if file should be validated (not excluded)."""
        file_str = str(file_path)
        return not any(pattern in file_str for pattern in self.exclude_patterns)

    def _get_markdown_files(self) -> List[Path]:
        """Get all Markdown files to validate."""
        if self.only_changed:
            changed_files = self.get_changed_markdown_files()
            if changed_files:
                return list(changed_files)
            else:
                print("No changed Markdown files found")
                return []

        # Get all markdown files
        markdown_files = []
        for pattern in ["**/*.md", "*.md"]:
            markdown_files.extend(Path(".").glob(pattern))

        # Filter out excluded files
        return [f for f in markdown_files if self._should_validate_file(f)]

    def validate_single_file(self, file_path: Path) -> Dict:
        """Validate a single file using pre-compiled patterns."""
        # Check cache first
        cached_result = self.load_cached_result(file_path)
        if cached_result is not None:
            return cached_result

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            return {"file": str(file_path), "errors": [f"Could not read file: {e}"], "warnings": [], "valid": False}

        errors = []
        warnings = []

        # Use pre-compiled patterns for faster matching
        lines = content.split("\n")

        # Check line length
        for i, line in enumerate(lines, 1):
            if LINE_LENGTH_PATTERN.match(line):
                warnings.append(f"Line {i}: Line too long (>120 chars)")

        # Check for hard tabs
        if HARD_TABS_PATTERN.search(content):
            warnings.append("Contains hard tabs")

        # Check for trailing spaces
        for i, line in enumerate(lines, 1):
            if TRAILING_SPACES_PATTERN.search(line):
                warnings.append(f"Line {i}: Trailing spaces")

        # Check heading increment
        heading_levels = []
        for i, line in enumerate(lines, 1):
            match = HEADING_INCREMENT_PATTERN.match(line)
            if match:
                level = len(match.group().strip().split()[0])
                heading_levels.append((i, level))

        for i in range(1, len(heading_levels)):
            prev_level = heading_levels[i - 1][1]
            curr_level = heading_levels[i][1]
            if curr_level > prev_level + 1:
                errors.append(f"Line {heading_levels[i][0]}: Heading level skipped")

        # Check for TL;DR section
        if not TLDR_HEADING_PATTERN.search(content):
            warnings.append("Missing TL;DR section")

        # Check for at-a-glance table
        if not AT_A_GLANCE_HEADER_PATTERN.search(content):
            warnings.append("Missing at-a-glance table")

        # Check cross-references
        cross_refs = CROSS_REFERENCE_PATTERN.findall(content)
        for ref_type, ref_target in cross_refs:
            if ref_type == "MODULE_REFERENCE":
                target_path = Path(ref_target)
                if not target_path.exists():
                    errors.append(f"Module reference not found: {ref_target}")

        # Check file references
        file_refs = FILE_REFERENCE_PATTERN.findall(content)
        for file_ref in file_refs:
            if not Path(file_ref).exists():
                warnings.append(f"File reference not found: {file_ref}")

        # Check backlog references
        backlog_refs = BACKLOG_REFERENCE_PATTERN.findall(content)
        for backlog_ref in backlog_refs:
            # Could add validation against actual backlog here
            pass

        result = {"file": str(file_path), "errors": errors, "warnings": warnings, "valid": len(errors) == 0}

        # Cache the result
        self.save_cached_result(file_path, result)

        return result

    def validate_files_parallel(self, files: List[Path]) -> Dict[Path, Dict]:
        """Validate multiple files in parallel."""
        results = {}

        if not files:
            return results

        print(f"Validating {len(files)} files with {self.max_workers} workers...")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(self.validate_single_file, file_path): file_path for file_path in files}

            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    results[file_path] = future.result()
                except Exception as e:
                    results[file_path] = {
                        "file": str(file_path),
                        "errors": [f"Validation error: {e}"],
                        "warnings": [],
                        "valid": False,
                    }

        return results

    def run_validation(self) -> Dict:
        """Run the complete validation process."""
        start_time = time.time()

        print("Starting optimized documentation validation...")

        # Get files to validate
        markdown_files = self._get_markdown_files()

        if not markdown_files:
            return {"execution_time": 0.0, "files_checked": 0, "errors": [], "warnings": [], "all_valid": True}

        # Validate files in parallel
        validation_results = self.validate_files_parallel(markdown_files)

        # Collect results
        all_errors = []
        all_warnings = []
        valid_files = 0

        for file_path, result in validation_results.items():
            if result["valid"]:
                valid_files += 1
            all_errors.extend([f"{result['file']}: {error}" for error in result["errors"]])
            all_warnings.extend([f"{result['file']}: {warning}" for warning in result["warnings"]])

        execution_time = time.time() - start_time

        return {
            "execution_time": execution_time,
            "files_checked": len(markdown_files),
            "valid_files": valid_files,
            "invalid_files": len(markdown_files) - valid_files,
            "errors": all_errors,
            "warnings": all_warnings,
            "all_valid": len(all_errors) == 0,
        }


def main():
    parser = argparse.ArgumentParser(description="Optimized documentation coherence validator")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--only-changed", action="store_true", help="Only validate changed files")
    parser.add_argument("--workers", type=int, help="Number of worker threads")
    parser.add_argument("--cache-ttl", type=int, default=300, help="Cache TTL in seconds")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--emit-json", help="Save results to JSON file")
    parser.add_argument("--safe-fix", action="store_true", help="Apply safe fixes")

    args = parser.parse_args()

    validator = OptimizedDocCoherenceValidator(
        dry_run=args.dry_run,
        only_changed=args.only_changed,
        max_workers=args.workers,
        cache_ttl=args.cache_ttl,
        emit_json=args.emit_json,
        safe_fix=args.safe_fix,
    )

    results = validator.run_validation()

    if args.json or args.emit_json:
        output = json.dumps(results, indent=2)
        if args.emit_json:
            with open(args.emit_json, "w") as f:
                f.write(output)
        else:
            print(output)
    else:
        print(f"\nValidation completed in {results['execution_time']:.2f}s")
        print(f"Files checked: {results['files_checked']}")
        print(f"Valid files: {results['valid_files']}")
        print(f"Invalid files: {results['invalid_files']}")
        print(f"Errors: {len(results['errors'])}")
        print(f"Warnings: {len(results['warnings'])}")

        if results["errors"]:
            print("\nErrors:")
            for error in results["errors"][:10]:  # Show first 10 errors
                print(f"  ❌ {error}")
            if len(results["errors"]) > 10:
                print(f"  ... and {len(results['errors']) - 10} more errors")

        if results["warnings"]:
            print("\nWarnings:")
            for warning in results["warnings"][:10]:  # Show first 10 warnings
                print(f"  ⚠️ {warning}")
            if len(results["warnings"]) > 10:
                print(f"  ... and {len(results['warnings']) - 10} more warnings")


if __name__ == "__main__":
    main()
