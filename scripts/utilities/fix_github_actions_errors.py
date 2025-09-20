#!/usr/bin/env python3
"""
Automated script to fix GitHub Actions workflow errors across the codebase.
This script identifies and fixes common GitHub Actions YAML issues.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any


class GitHubActionsErrorFixer:
    """Automated fixer for GitHub Actions workflow errors."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.fixes_applied = 0
        self.files_processed = 0
        self.errors_found = 0
        
        # Patterns to identify and fix
        self.patterns = {
            # Pattern 1: Missing with: block after uses: action
            "missing_with_block": {
                "pattern": r"(\s+-\s+uses:\s+[^\n]+\n)(\s+)(fetch-depth:\s+\d+)",
                "replacement": r"\1\2with:\n\2  \3",
                "description": "Add missing with: block for uses: actions"
            },
            
            # Pattern 2: Missing with: block for checkout action
            "missing_checkout_with": {
                "pattern": r"(\s+-\s+uses:\s+actions/checkout@v4\n)(\s+)(fetch-depth:\s+\d+)",
                "replacement": r"\1\2with:\n\2  \3",
                "description": "Add missing with: block for checkout action"
            },
            
            # Pattern 3: Missing with: block for setup-python action
            "missing_setup_python_with": {
                "pattern": r"(\s+-\s+uses:\s+actions/setup-python@v5\n)(\s+)(python-version:\s+['\"][^'\"]+['\"])",
                "replacement": r"\1\2with:\n\2  \3",
                "description": "Add missing with: block for setup-python action"
            },
            
            # Pattern 4: Missing with: block for setup-uv action
            "missing_setup_uv_with": {
                "pattern": r"(\s+-\s+uses:\s+astral-sh/setup-uv@v4\n)(\s+)(version:\s+[^\n]+)",
                "replacement": r"\1\2with:\n\2  \3",
                "description": "Add missing with: block for setup-uv action"
            },
            
            # Pattern 5: Missing with: block for cache action
            "missing_cache_with": {
                "pattern": r"(\s+-\s+uses:\s+actions/cache@v4\n)(\s+)(path:\s*\|)",
                "replacement": r"\1\2with:\n\2  \3",
                "description": "Add missing with: block for cache action"
            },
            
            # Pattern 6: Fix matrix strategy syntax
            "matrix_strategy_syntax": {
                "pattern": r"strategy:\s*\n\s*matrix:\s*\n\s*python-version:\s*\[([^\]]+)\]",
                "replacement": r"strategy:\n  matrix:\n    python-version: [\1]",
                "description": "Fix matrix strategy indentation and syntax"
            },
            
            # Pattern 7: Fix python-version array syntax
            "python_version_array": {
                "pattern": r"python-version:\s*\[([^\]]+)\]",
                "replacement": r"python-version: [\1]",
                "description": "Fix python-version array syntax"
            }
        }
        
        self.exclude_patterns = [
            "*/__pycache__/*",
            "*/venv/*",
            "*/.venv/*",
            "*/node_modules/*",
            "*/600_archives/*",
            "*/tests/test_*",
            "*/test_*.py",
            "*/site-packages/*"
        ]

    def should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from processing."""
        file_str = str(file_path)
        
        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if pattern.replace("*", "").replace("/", "") in file_str:
                return True
        
        # Only process GitHub Actions workflow files
        if not (file_path.parent.name == "workflows" and file_path.suffix == ".yml"):
            return True
            
        return False

    def find_workflow_files(self) -> list[Path]:
        """Find all GitHub Actions workflow files."""
        workflow_files = []
        
        for file_path in self.project_root.rglob("*.yml"):
            if not self.should_exclude_file(file_path):
                workflow_files.append(file_path)
        
        return workflow_files

    def analyze_file(self, file_path: Path) -> dict[str, Any]:
        """Analyze a workflow file for common errors."""
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Failed to read file: {e}", "issues": []}
        
        issues = []
        
        # Check for missing with: blocks
        if re.search(r"uses:\s+[^\n]+\n\s+fetch-depth:", content):
            issues.append("Missing with: block for checkout action")
        
        if re.search(r"uses:\s+actions/setup-python@v5\n\s+python-version:", content):
            issues.append("Missing with: block for setup-python action")
        
        if re.search(r"uses:\s+astral-sh/setup-uv@v4\n\s+version:", content):
            issues.append("Missing with: block for setup-uv action")
        
        if re.search(r"uses:\s+actions/cache@v4\n\s+path:", content):
            issues.append("Missing with: block for cache action")
        
        # Check for matrix strategy issues
        if re.search(r"strategy:\s*\n\s*matrix:\s*\n\s*python-version:\s*\[", content):
            issues.append("Matrix strategy syntax issues")
        
        return {"issues": issues, "content": content}

    def fix_file(self, file_path: Path, dry_run: bool = False) -> dict[str, Any]:
        """Fix GitHub Actions errors in a file."""
        analysis = self.analyze_file(file_path)
        
        if "error" in analysis:
            return analysis
        
        content = analysis["content"]
        original_content = content
        fixes_applied = 0
        
        # Apply fixes
        for pattern_name, pattern_info in self.patterns.items():
            pattern = pattern_info.get("pattern", "")
            replacement = pattern_info.get("replacement", "")
            
            # Use multiline flag for complex patterns
            if "\n" in pattern:
                new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            else:
                new_content = re.sub(pattern, replacement, content)
            
            if new_content != content:
                content = new_content
                fixes_applied += 1
                print(f"  ✅ Applied fix: {pattern_name}")
        
        # Write changes if not dry run
        if not dry_run and content != original_content:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  💾 Saved changes to {file_path}")
            except Exception as e:
                return {"error": f"Failed to write file: {e}"}
        
        return {
            "issues_found": len(analysis.get("issues", [])),
            "fixes_applied": fixes_applied,
            "changed": content != original_content
        }

    def fix_all_files(self, dry_run: bool = False) -> dict[str, Any]:
        """Fix GitHub Actions errors in all workflow files."""
        workflow_files = self.find_workflow_files()
        
        if not workflow_files:
            print("No GitHub Actions workflow files found.")
            return {"files_processed": 0, "fixes_applied": 0}
        
        print(f"Found {len(workflow_files)} GitHub Actions workflow files")
        
        total_fixes = 0
        files_changed = 0
        
        for file_path in workflow_files:
            print(f"\n🔍 Processing {file_path}")
            
            result = self.fix_file(file_path, dry_run)
            
            if "error" in result:
                print(f"  ❌ Error: {result.get('error', 'Unknown error')}")
                continue
            
            if result.get("fixes_applied", 0) > 0:
                total_fixes += result.get("fixes_applied", 0)
                if result.get("file_changed", False):
                    files_changed += 1
                print(f"  ✅ Applied {result.get('fixes_applied', 0)} fixes")
            else:
                print("  ✅ No issues found")
        
        return {
            "files_processed": len(workflow_files),
            "files_changed": files_changed,
            "fixes_applied": total_fixes
        }

    def generate_report(self, results: dict[str, Any]) -> str:
        """Generate a summary report."""
        return f"""
GitHub Actions Error Fixing Report
==================================

Files processed: {results.get("files_processed", 0)}
Files changed: {results.get("files_changed", 0)}
Total fixes applied: {results.get("fixes_applied", 0)}

Common fixes applied:
- Added missing with: blocks for uses: actions
- Fixed matrix strategy syntax
- Corrected YAML indentation issues
- Fixed python-version array syntax

Next steps:
1. Review the changes in your workflow files
2. Test the workflows in a pull request
3. Commit the changes if they look correct
"""


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fix GitHub Actions workflow errors")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed without making changes")
    parser.add_argument("--file", help="Fix specific file instead of all files")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    fixer = GitHubActionsErrorFixer(args.project_root)
    
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File {file_path} does not exist")
            sys.exit(1)
        
        print(f"Fixing GitHub Actions errors in {file_path}")
        result = fixer.fix_file(file_path, args.dry_run)
        
        if "error" in result:
            print(f"Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)
        
        print(f"Applied {result.get('fixes_applied', 0)} fixes")
    else:
        print("GitHub Actions Error Fixer")
        print("=" * 40)
        
        if args.dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
        
        results = fixer.fix_all_files(args.dry_run)
        print(fixer.generate_report(results))


if __name__ == "__main__":
    main()
