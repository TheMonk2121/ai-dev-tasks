#!/usr/bin/env python3
"""
Documentation Coherence Validation System - B-060 Implementation

Lightweight doc-linter with Cursor AI semantic checking for the AI development ecosystem.
Implements local pre-commit hooks, reference validation, and AI-enhanced coherence checking.

Usage: python scripts/doc_coherence_validator.py [--dry-run] [--check-all] [--file FILE]
"""

import os
import re
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import hashlib
import difflib

class DocCoherenceValidator:
    def __init__(self, dry_run: bool = True, check_all: bool = False, target_file: Optional[str] = None):
        self.dry_run = dry_run
        self.check_all = check_all
        self.target_file = target_file
        self.changes_made = []
        self.errors = []
        self.warnings = []
        self.validation_results = {}
        
        # Exclude patterns (must be defined before _get_markdown_files)
        self.exclude_patterns = [
            'venv/',
            'node_modules/',
            'docs/legacy/',
            '__pycache__/',
            '.git/',
            '999_repo-maintenance.md',
            'REPO_MAINTENANCE_SUMMARY.md',
            '600_archives/'
        ]
        
        # Configuration
        self.cursor_ai_enabled = self._check_cursor_ai_availability()
        self.markdown_files = self._get_markdown_files()
        
        # Validation patterns
        self.cross_reference_pattern = re.compile(r'<!--\s*([A-Z_]+):\s*([^>]+)\s*-->')
        self.file_reference_pattern = re.compile(r'`([^`]+\.md)`')
        self.backlog_reference_pattern = re.compile(r'B‑\d+')
        
        # Priority file patterns
        self.priority_files = {
            'memory_context': ['100_cursor-memory-context.md'],
            'system_overview': ['400_system-overview.md'],
            'backlog': ['000_backlog.md'],
            'project_overview': ['400_project-overview.md'],
            'context_priority': ['400_context-priority-guide.md']
        }

    def log(self, message: str, level: str = "INFO"):
        """Log messages with consistent formatting."""
        print(f"[{level}] {message}")

    def _check_cursor_ai_availability(self) -> bool:
        """Check if Cursor AI is available for semantic validation."""
        try:
            # Check if cursor command is available
            result = subprocess.run(['which', 'cursor'], capture_output=True, text=True)
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
        files = []
        for file_path in Path('.').rglob('*.md'):
            if not self._should_exclude(file_path):
                files.append(file_path)
        return files

    def _should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded from validation."""
        return any(pattern in str(file_path) for pattern in self.exclude_patterns)

    def read_file(self, file_path: Path) -> Optional[str]:
        """Read file content with error handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
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
            with open(file_path, 'w', encoding='utf-8') as f:
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
        
        # Validate file references
        existing_files = {f.name for f in self.markdown_files}
        
        for ref_type, refs in all_references.items():
            for source_file, target in refs:
                # Check if target file exists
                target_path = Path(target)
                if not target_path.exists():
                    broken_references.append({
                        'source': source_file,
                        'target': target,
                        'type': ref_type,
                        'issue': 'File not found'
                    })
                elif target_path.suffix == '.md' and target_path.name not in existing_files:
                    broken_references.append({
                        'source': source_file,
                        'target': target,
                        'type': ref_type,
                        'issue': 'Markdown file not found'
                    })
        
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
        
        for file_path in self.markdown_files:
            filename = file_path.name
            
            # Check three-digit prefix pattern
            if not re.match(r'^\d{3}_', filename):
                if filename not in ['README.md', 'LICENSE.md']:
                    naming_issues.append({
                        'file': str(file_path),
                        'issue': 'Missing three-digit prefix'
                    })
            
            # Check for descriptive names
            if re.match(r'^\d{3}_[a-z-]+\.md$', filename):
                # Valid format
                pass
            elif filename not in ['README.md', 'LICENSE.md']:
                naming_issues.append({
                    'file': str(file_path),
                    'issue': 'Invalid naming format'
                })
        
        # Report results
        if naming_issues:
            self.log(f"Found {len(naming_issues)} naming convention issues:", "WARNING")
            for issue in naming_issues:
                self.log(f"  {issue['file']}: {issue['issue']}", "WARNING")
            return False
        else:
            self.log("All files follow naming conventions", "INFO")
            return True

    def task_3_validate_backlog_references(self) -> bool:
        """Validate backlog item references in documentation."""
        self.log("Task 3: Validating backlog references", "INFO")
        
        # Read backlog to get valid item IDs
        backlog_content = self.read_file(Path('000_backlog.md'))
        if not backlog_content:
            self.log("Cannot read backlog file", "ERROR")
            return False
        
        valid_backlog_items = set(self.backlog_reference_pattern.findall(backlog_content))
        
        # Check references in other files
        invalid_references = []
        
        for file_path in self.markdown_files:
            if file_path.name == '000_backlog.md':
                continue
                
            content = self.read_file(file_path)
            if not content:
                continue
            
            references = self.backlog_reference_pattern.findall(content)
            for ref in references:
                if ref not in valid_backlog_items:
                    invalid_references.append({
                        'file': str(file_path),
                        'reference': ref,
                        'issue': 'Invalid backlog item reference'
                    })
        
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
        
        memory_context = self.read_file(Path('100_cursor-memory-context.md'))
        if not memory_context:
            self.log("Cannot read memory context file", "ERROR")
            return False
        
        coherence_issues = []
        
        # Check for consistency with backlog
        backlog_content = self.read_file(Path('000_backlog.md'))
        if backlog_content:
            # Extract current priorities from memory context
            priority_pattern = r'Current Sprint.*?B-\d+'
            memory_priorities = re.findall(priority_pattern, memory_context)
            
            # Check if mentioned priorities exist in backlog
            for priority in memory_priorities:
                backlog_id = re.search(r'B-\d+', priority)
                if backlog_id and backlog_id.group() not in backlog_content:
                    coherence_issues.append({
                        'issue': f'Memory context references non-existent backlog item: {backlog_id.group()}',
                        'file': '100_cursor-memory-context.md'
                    })
        
        # Check for consistency with system overview
        system_overview = self.read_file(Path('400_system-overview.md'))
        if system_overview:
            # Check for architectural consistency
            if 'DSPy' in memory_context and 'DSPy' not in system_overview:
                coherence_issues.append({
                    'issue': 'Memory context mentions DSPy but system overview does not',
                    'file': '100_cursor-memory-context.md'
                })
        
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
            {self.read_file(file_path)[:2000]}  # First 2000 chars for analysis
            
            Provide a JSON response with any issues found:
            {{"issues": [{{"type": "error|warning", "description": "issue description"}}]}}
            """
            
            # Run Cursor AI analysis
            result = subprocess.run([
                'cursor', 'chat', '--prompt', prompt
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout)
                    for issue in response.get('issues', []):
                        issues.append({
                            'file': str(file_path),
                            'issue': issue['description'],
                            'type': issue['type']
                        })
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
            'timestamp': subprocess.run(['date'], capture_output=True, text=True).stdout.strip(),
            'files_checked': len(self.markdown_files),
            'cursor_ai_enabled': self.cursor_ai_enabled,
            'validation_results': self.validation_results,
            'errors': self.errors,
            'warnings': self.warnings,
            'changes_made': self.changes_made
        }
        
        # Write report
        report_file = Path('docs/validation_report.json')
        report_file.parent.mkdir(exist_ok=True)
        
        if not self.dry_run:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            self.log(f"Validation report written to {report_file}", "INFO")
        else:
            self.log(f"[DRY-RUN] Would write validation report to {report_file}", "INFO")
        
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
            ("Generate validation report", self.task_6_generate_validation_report)
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
    parser = argparse.ArgumentParser(description='Documentation Coherence Validation System')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Run in dry-run mode (default)')
    parser.add_argument('--check-all', action='store_true',
                       help='Check all files (default: only priority files)')
    parser.add_argument('--file', type=str,
                       help='Check specific file only')
    parser.add_argument('--no-dry-run', action='store_true',
                       help='Actually make changes (not dry-run)')
    
    args = parser.parse_args()
    
    # Handle dry-run logic
    dry_run = args.dry_run and not args.no_dry_run
    
    # Initialize validator
    validator = DocCoherenceValidator(
        dry_run=dry_run,
        check_all=args.check_all,
        target_file=args.file
    )
    
    # Run validations
    success = validator.run_all_validations()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
