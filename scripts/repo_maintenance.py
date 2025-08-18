#!/usr/bin/env python3
"""
Repository Maintenance Script - Cursor-First Edition

Automated maintenance for AI development ecosystem documentation alignment.
Checks and fixes model references, 003 role descriptions, PRD-skip rules, and duplicate files.

Usage: python scripts/repo_maintenance.py [--dry-run] [--auto-commit]
"""

import os
import re
import sys
import json
import argparse
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import subprocess

class RepoMaintenance:
    def __init__(self, dry_run: bool = True, auto_commit: bool = False, skip_git_check: bool = False):
        self.dry_run = dry_run
        self.auto_commit = auto_commit
        self.changes_made = []
        self.errors = []
        
        # Run pre-flight checks (skip during testing)
        if not skip_git_check:
            self.preflight_git_check()
        
        # Configuration
        self.prd_threshold_points = 5
        self.prd_skip_if_score_ge = 3.0
        
        # File patterns to check
        self.markdown_files = list(Path('.').rglob('*.md'))
        self.python_files = list(Path('.').rglob('*.py'))
        
        # Exclude patterns
        self.exclude_patterns = [
            'venv/',
            'node_modules/',
            'docs/legacy/',
            '__pycache__/',
            '.git/',
            '999_repo-maintenance.md',
            'REPO_MAINTENANCE_SUMMARY.md'
        ]

    def log(self, message: str, level: str = "INFO"):
        """Log messages with consistent formatting."""
        print(f"[{level}] {message}")

    def preflight_git_check(self) -> None:
        """Pre-flight checks for git safety."""
        try:
            # Check for dirty working tree
            dirty = subprocess.run(['git', 'status', '--porcelain'], 
                                 capture_output=True, text=True, check=True)
            if dirty.stdout.strip():
                self.log("Working tree dirty; aborting", "ERROR")
                self.log("Please commit or stash changes before running maintenance", "ERROR")
                sys.exit(1)
            
            # Check branch if auto-commit is enabled
            if self.auto_commit:
                branch = subprocess.run(['git', 'branch', '--show-current'], 
                                      capture_output=True, text=True, check=True)
                current_branch = branch.stdout.strip()
                if current_branch != 'main':
                    self.log(f"Auto-commit enabled but not on main branch ({current_branch}); aborting", "ERROR")
                    self.log("Auto-commit is only allowed on main branch", "ERROR")
                    sys.exit(1)
                    
        except subprocess.CalledProcessError as e:
            self.log(f"Git check failed: {e}", "ERROR")
            sys.exit(1)

    def should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded from processing."""
        return any(pattern in str(file_path) for pattern in self.exclude_patterns)

    def read_file(self, file_path: Path) -> str | None:
        """Read file content with error handling."""
        try:
            with open(file_path, encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.errors.append(f"Error reading {file_path}: {e}")
            return None

    def write_file(self, file_path: Path, content: str) -> bool:
        """Write file content with error handling."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            self.errors.append(f"Error writing {file_path}: {e}")
            return False

    def task_1_align_model_references(self) -> bool:
        """T-1: Align model references to "Cursor-Native AI (default); Mistral & Yi optional"."""
        self.log("Running T-1: Align model references...")
        
        changes_made = False
        patterns_to_fix = [
            (r'"defaultModel":\s*"mistral"', '"defaultModel": "cursor-native-ai"'),
            (r'"defaultModel":\s*"yi-coder"', '"defaultModel": "cursor-native-ai"'),
            (r'"defaultModel":\s*"mistral-7b-instruct"', '"defaultModel": "cursor-native-ai"'),
            (r'\(default:\s*mistral\)', '(default: cursor-native-ai)'),
            (r'\(default:\s*Yi-Coder-9B-Chat-Q6_K\)', '(default: cursor-native-ai)'),
        ]
        
        for file_path in self.markdown_files:
            if self.should_exclude(file_path):
                continue
                
            content = self.read_file(file_path)
            if content is None:
                continue
                
            original_content = content
            for pattern, replacement in patterns_to_fix:
                if re.search(pattern, content, re.IGNORECASE):
                    content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            
            if content != original_content:
                if not self.dry_run:
                    if self.write_file(file_path, content):
                        self.changes_made.append(f"Updated model references in {file_path}")
                        changes_made = True
                else:
                    self.log(f"Would update model references in {file_path}")
                    changes_made = True
        
        return changes_made

    def task_2_clarify_003_role(self) -> bool:
        """T-2: Clarify 003 role across docs."""
        self.log("Running T-2: Clarify 003 role...")
        
        changes_made = False
        patterns_to_fix = [
            (r'003.*optional.*default_executor', '003_process-task-list.md is the execution engine; it loads whether or not a PRD was created'),
            (r'loads.*003.*only if.*default_executor', '003_process-task-list.md is the execution engine; it loads whether or not a PRD was created'),
            (r'\b003\s+optional\b(?=\s|$)', '003_process-task-list.md (the execution engine)'),
            (r'\b\(optional\)\b', '(the execution engine)'),
        ]
        
        for file_path in self.markdown_files:
            if self.should_exclude(file_path):
                continue
                
            content = self.read_file(file_path)
            if content is None:
                continue
                
            original_content = content
            for pattern, replacement in patterns_to_fix:
                if re.search(pattern, content, re.IGNORECASE):
                    content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            
            if content != original_content:
                if not self.dry_run:
                    if self.write_file(file_path, content):
                        self.changes_made.append(f"Updated 003 role description in {file_path}")
                        changes_made = True
                else:
                    self.log(f"Would update 003 role description in {file_path}")
                    changes_made = True
        
        return changes_made

    def calculate_file_hash(self, file_path: Path) -> str | None:
        """Calculate SHA-256 hash of file content."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception as e:
            self.errors.append(f"Error calculating hash for {file_path}: {e}")
            return None

    def find_content_duplicates(self) -> dict[str, list[Path]]:
        """Find files with identical content using SHA-256 hashes."""
        self.log("Scanning for content-based duplicates...")
        
        hash_to_files = {}
        
        # Scan all markdown files
        for file_path in self.markdown_files:
            if self.should_exclude(file_path):
                continue
                
            file_hash = self.calculate_file_hash(file_path)
            if file_hash:
                if file_hash not in hash_to_files:
                    hash_to_files[file_hash] = []
                hash_to_files[file_hash].append(file_path)
        
        # Filter to only hashes with multiple files
        duplicates = {hash_val: files for hash_val, files in hash_to_files.items() 
                     if len(files) > 1}
        
        return duplicates

    def analyze_duplicate_groups(self, duplicates: dict[str, list[Path]]) -> list[tuple[Path, list[Path]]]:
        """Analyze duplicate groups and determine which files to keep vs archive."""
        decisions = []
        
        for hash_val, files in duplicates.items():
            # Sort files by priority (main files first, then archives)
            main_files = [f for f in files if not any(pattern in str(f) for pattern in ['archives', 'backup', 'legacy'])]
            archive_files = [f for f in files if any(pattern in str(f) for pattern in ['archives', 'backup', 'legacy'])]
            
            if main_files and archive_files:
                # Keep the first main file, archive the rest
                keep_file = main_files[0]
                archive_candidates = main_files[1:] + archive_files
                decisions.append((keep_file, archive_candidates))
            elif len(files) > 1:
                # All files are in same category, keep the first
                keep_file = files[0]
                archive_candidates = files[1:]
                decisions.append((keep_file, archive_candidates))
        
        return decisions

    def task_3_remove_duplicate_files(self) -> bool:
        """T-3: Remove or archive duplicate files using content-based detection."""
        self.log("Running T-3: Check for duplicate files...")
        
        # Find content-based duplicates
        duplicates = self.find_content_duplicates()
        
        if not duplicates:
            self.log("No content-based duplicates found")
            return True
        
        self.log(f"Found {len(duplicates)} groups of duplicate files")
        
        # Analyze and decide what to keep vs archive
        decisions = self.analyze_duplicate_groups(duplicates)
        
        changes_made = False
        for keep_file, archive_files in decisions:
            self.log(f"Duplicate group:")
            self.log(f"  Keep: {keep_file}")
            for archive_file in archive_files:
                self.log(f"  Archive: {archive_file}")
                
                if not self.dry_run:
                    # Archive duplicate to legacy
                    legacy_dir = Path('docs/legacy')
                    legacy_dir.mkdir(exist_ok=True)
                    
                    new_path = legacy_dir / archive_file.name
                    if archive_file.exists():
                        archive_file.rename(new_path)
                        self.changes_made.append(f"Archived duplicate {archive_file} to {new_path}")
                        changes_made = True
                else:
                    self.log(f"Would archive duplicate {archive_file}")
                    changes_made = True
        
        return changes_made

    def task_4_validate_prd_skip_rule(self) -> bool:
        """T-4: Validate PRD-skip rule wording."""
        self.log("Running T-4: Validate PRD-skip rule...")
        
        expected_rule = "Skip PRD when points<5 AND score_total≥3.0"
        rule_variations = [
            r"skip.*items.*5.*pts.*score.*3\.0",
            r"points.*5.*score.*3\.0",
            r"Skip PRD.*points.*5.*score.*3\.0",
            r"points.*5.*pts.*score.*3\.0",
            r"pts.*5.*score.*3\.0"
        ]
        
        all_consistent = True
        for file_path in self.markdown_files:
            if self.should_exclude(file_path):
                continue
                
            content = self.read_file(file_path)
            if content is None:
                continue
            
            # Check if file contains PRD-skip rules
            if any(re.search(pattern, content, re.IGNORECASE) for pattern in rule_variations):
                # Verify consistency - check for various patterns
                has_valid_rule = (re.search(r"points.*5.*score.*3\.0", content, re.IGNORECASE) or 
                                re.search(r"points.*5.*pts.*score.*3\.0", content, re.IGNORECASE) or
                                re.search(r"pts.*5.*score.*3\.0", content, re.IGNORECASE) or
                                re.search(r"skip.*items.*5.*pts.*score.*3\.0", content, re.IGNORECASE))
                
                if not has_valid_rule:
                    self.log(f"PRD-skip rule inconsistency found in {file_path}")
                    self.log(f"  Content snippet: {content[:200]}...")
                    all_consistent = False
        
        if not all_consistent:
            self.log("PRD-skip rule inconsistencies found - manual review needed")
            return False
        
        return True

    def task_5_contradiction_scan(self) -> bool:
        """T-5: Contradiction scan."""
        self.log("Running T-5: Contradiction scan...")
        
        contradiction_patterns = [
            r"yi-coder.*default",
            r"mistral 7b instruct.*default", 
            r"003 optional"
        ]
        
        contradictions_found = []
        for file_path in self.markdown_files:
            if self.should_exclude(file_path):
                continue
                
            content = self.read_file(file_path)
            if content is None:
                continue
            
            for pattern in contradiction_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    contradictions_found.append(f"{file_path}: {pattern}")
        
        if contradictions_found:
            self.log("Contradictions found:")
            for contradiction in contradictions_found:
                self.log(f"  - {contradiction}")
            return False
        
        return True

    def task_6_commit_changes(self) -> bool:
        """T-6: Commit changes."""
        if not self.changes_made:
            self.log("No changes to commit")
            return True
        
        if self.dry_run:
            self.log("Would commit the following changes:")
            for change in self.changes_made:
                self.log(f"  - {change}")
            return True
        
        if self.auto_commit:
            try:
                # Stage changes
                subprocess.run(['git', 'add', '.'], check=True)
                
                # Commit with descriptive message
                commit_message = "chore: cursor-first doc alignment and langextract integration"
                subprocess.run(['git', 'commit', '-m', commit_message], check=True)
                
                self.log("Changes committed successfully")
                return True
            except subprocess.CalledProcessError as e:
                self.errors.append(f"Git commit failed: {e}")
                return False
        else:
            self.log("Changes ready for manual commit")
            return True

    def run_all_tasks(self) -> bool:
        """Run all maintenance tasks."""
        self.log("Starting repository maintenance...")
        
        tasks = [
            ("T-1: Align model references", self.task_1_align_model_references),
            ("T-2: Clarify 003 role", self.task_2_clarify_003_role),
            ("T-3: Remove duplicate files", self.task_3_remove_duplicate_files),
            ("T-4: Validate PRD-skip rule", self.task_4_validate_prd_skip_rule),
            ("T-5: Contradiction scan", self.task_5_contradiction_scan),
            ("T-6: Commit changes", self.task_6_commit_changes),
        ]
        
        all_success = True
        for task_name, task_func in tasks:
            try:
                result = task_func()
                if result:
                    self.log(f"✅ {task_name} completed successfully")
                else:
                    self.log(f"❌ {task_name} failed")
                    all_success = False
            except Exception as e:
                self.log(f"❌ {task_name} failed with error: {e}")
                all_success = False
        
        # Report results
        self.log("\n" + "="*50)
        self.log("MAINTENANCE SUMMARY")
        self.log("="*50)
        
        if self.changes_made:
            self.log("Changes made:")
            for change in self.changes_made:
                self.log(f"  ✅ {change}")
        else:
            self.log("No changes needed - repository is already aligned")
        
        if self.errors:
            self.log("Errors encountered:")
            for error in self.errors:
                self.log(f"  ❌ {error}")
        
        if all_success:
            self.log("✅ All maintenance tasks completed successfully")
        else:
            self.log("❌ Some maintenance tasks failed")
        
        return all_success

def main():
    parser = argparse.ArgumentParser(description='Repository Maintenance Script')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Show what would be changed without making changes')
    parser.add_argument('--apply', action='store_true', default=False,
                       help='Apply changes (overrides --dry-run)')
    parser.add_argument('--auto-commit', action='store_true', default=False,
                       help='Automatically commit changes')
    parser.add_argument('--skip-git-check', action='store_true', default=False,
                       help='Skip git preflight checks')
    
    args = parser.parse_args()
    
    # Determine dry_run setting
    dry_run = not args.apply
    
    maintenance = RepoMaintenance(dry_run=dry_run, auto_commit=args.auto_commit, skip_git_check=args.skip_git_check)
    success = maintenance.run_all_tasks()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
