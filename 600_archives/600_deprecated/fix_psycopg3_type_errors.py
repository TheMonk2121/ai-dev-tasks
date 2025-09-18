#!/usr/bin/env python3
"""
Automated script to fix psycopg3 type errors across the codebase.
This script identifies and fixes common psycopg3 type issues.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


class Psycopg3TypeErrorFixer:
    """Automated fixer for psycopg3 type errors."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.fixes_applied = 0
        self.files_processed = 0
        self.errors_found = 0
        
        # Patterns to identify and fix
        self.patterns = {
            # Pattern 1: Direct connection with row_factory causing type errors
            "connection_with_row_factory": {
                "pattern": r"conn\s*=\s*psycopg\.connect\([^)]*row_factory=dict_row[^)]*\)",
                "replacement": "conn = psycopg.connect(dsn)",
                "description": "Remove row_factory from connection, use cursor-level instead"
            },
            
            # Pattern 2: Type ignore comments for row_factory
            "type_ignore_row_factory": {
                "pattern": r"conn\s*=\s*psycopg\.connect\([^)]*row_factory=dict_row[^)]*\)\s*#\s*type:\s*ignore\[arg-type\]",
                "replacement": "conn = psycopg.connect(dsn)",
                "description": "Remove type ignore and row_factory from connection"
            },
            
            # Pattern 2b: Type ignore with comments
            "type_ignore_with_comments": {
                "pattern": r"conn\s*=\s*psycopg\.connect\([^)]*row_factory=dict_row[^)]*\)\s*#\s*type:\s*ignore\[arg-type\]",
                "replacement": "conn = psycopg.connect(dsn)",
                "description": "Remove type ignore and row_factory from connection"
            },
            
            # Pattern 3: Connection with dict_row import but no usage
            "unused_dict_row_import": {
                "pattern": r"from psycopg\.rows import dict_row\n(?!.*dict_row)",
                "replacement": "from psycopg.rows import dict_row\n",
                "description": "Keep dict_row import for cursor usage"
            },
            
            # Pattern 4: Old connection patterns that need updating
            "old_connection_pattern": {
                "pattern": r"def get_db_connection\(\):\s*\n.*?conn\s*=\s*psycopg\.connect\([^)]*\)\s*\n.*?try:\s*\n.*?conn\.row_factory\s*=\s*dict_row\s*#\s*type:\s*ignore\[attr-defined\]\s*\n.*?except Exception:\s*\n.*?pass\s*\n.*?return conn",
                "replacement": "def get_db_connection():\n    \"\"\"Get database connection with proper configuration.\"\"\"\n    from src.common.psycopg3_config import get_db_connection as _get_db_connection\n    return _get_db_connection()",
                "description": "Replace old connection pattern with new config"
            }
        }
        
        # Files to exclude from processing
        self.exclude_patterns = [
            "*/__pycache__/*",
            "*/venv/*",
            "*/.venv/*",
            "*/node_modules/*",
            "*/migrations/versions/*",
            "*/600_archives/*",
            "*/tests/test_*",
            "*/test_*.py",
            "*/site-packages/*"
        ]
    
    def should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from processing."""
        file_str = str(file_path)
        
        # Check for specific exclusion patterns
        for pattern in self.exclude_patterns:
            if pattern.replace("*", "") in file_str:
                return True
        
        # Additional exclusions
        if "venv" in file_str or ".venv" in file_str:
            return True
        if "site-packages" in file_str:
            return True
        if file_path.name.startswith("test_"):
            return True
        
        return False
    
    def find_python_files(self) -> list[Path]:
        """Find all Python files in the project."""
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(pattern.replace("*", "") in d for pattern in self.exclude_patterns)]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    if not self.should_exclude_file(file_path):
                        python_files.append(file_path)
        
        return python_files
    
    def analyze_file(self, file_path: Path) -> dict[str, Any]:
        """Analyze a file for psycopg3 type issues."""
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Could not read file: {e}"}
        
        issues = []
        
        # Check for common psycopg3 type error patterns
        for pattern_name, pattern_info in self.\1.items()
            matches = re.finditer(result.get("key", "")
            for match in matches:
                issues.append({
                    "pattern_name": pattern_name,
                    "description": result.get("key", "")
                    "line_number": content[:match.start()].count('\n') + 1,
                    "match_text": match.group(0),
                    "replacement": result.get("key", "")
                })
        
        # Check for specific type errors
        if "type: ignore[arg-type]" in content and "row_factory" in content:
            issues.append({
                "pattern_name": "type_ignore_arg_type",
                "description": "Type ignore for arg-type with row_factory",
                "line_number": content.find("type: ignore[arg-type]"),
                "match_text": "type: ignore[arg-type]",
                "replacement": "Use cursor-level row_factory instead"
            })
        
        return {
            "file_path": file_path,
            "issues": issues,
            "total_issues": len(issues)
        }
    
    def fix_file(self, file_path: Path, dry_run: bool = False) -> dict[str, Any]:
        """Fix psycopg3 type issues in a file."""
        analysis = self.analyze_file(file_path)
        
        if "error" in analysis:
            return analysis
        
        if result.get("key", "")
            return {"status": "no_issues", "file_path": file_path}
        
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Could not read file: {e}"}
        
        original_content = content
        fixes_applied = 0
        
        # Apply fixes
        for issue in result.get("key", "")
            if result.get("key", "")
                # Replace connection with row_factory
                pattern = re.compile(result.get("key", "")
                new_content = pattern.sub(result.get("key", "")
                if new_content != content:
                    content = new_content
                    fixes_applied += 1
            
            elif result.get("key", "")
                # Remove type ignore and row_factory
                pattern = re.compile(result.get("key", "")
                new_content = pattern.sub(result.get("key", "")
                if new_content != content:
                    content = new_content
                    fixes_applied += 1
            
            elif result.get("key", "")
                # Replace old connection pattern
                pattern = re.compile(result.get("key", "")
                new_content = pattern.sub(result.get("key", "")
                if new_content != content:
                    content = new_content
                    fixes_applied += 1
        
        # Add import for new config if needed
        if fixes_applied > 0 and "from src.common.psycopg3_config import" not in content:
            # Find the best place to add the import
            import_lines = []
            for line in content.split('\n'):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    import_lines.append(line)
                elif line.strip() and not line.strip().startswith('#'):
                    break
            
            if import_lines:
                # Add after existing imports
                last_import_line = max(i for i, line in enumerate(content.split('\n')) if line.strip().startswith(('import ', 'from ')))
                lines = content.split('\n')
                lines.insert(last_import_line + 1, "from src.common.psycopg3_config import get_db_connection")
                content = '\n'.join(lines)
            else:
                # Add at the top
                content = "from src.common.psycopg3_config import get_db_connection\n" + content
        
        if not dry_run and content != original_content:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                return {"error": f"Could not write file: {e}"}
        
        return {
            "status": "fixed" if fixes_applied > 0 else "no_changes",
            "file_path": file_path,
            "fixes_applied": fixes_applied,
            "total_issues": result.get("key", "")
        }
    
    def fix_all_files(self, dry_run: bool = False) -> dict[str, Any]:
        """Fix psycopg3 type issues in all Python files."""
        python_files = self.find_python_files()
        results = {
            "files_processed": 0,
            "files_fixed": 0,
            "total_fixes": 0,
            "errors": [],
            "fixes_by_file": []
        }
        
        print(f"Found {len(python_files)} Python files to process...")
        
        for file_path in python_files:
            self.files_processed += 1
            print(f"Processing: {file_path}")
            
            result = self.fix_file(file_path, dry_run)
            result.get("key", "")
            
            if "error" in result:
                result.get("key", "")
                print(f"  ❌ Error: {result.get("key", "")
            elif result.get("key", "")
                result.get("key", "")
                result.get("key", "")
                print(f"  ✅ Fixed {result.get("key", "")
            elif result.get("key", "")
                print("  ✅ No issues found")
            else:
                print("  ⚠️  No changes needed")
        
        return results
    
    def generate_report(self, results: dict[str, Any]) -> str:
        """Generate a summary report of fixes applied."""
        report = []
        report.append("=" * 60)
        report.append("PSYCOPG3 TYPE ERROR FIX REPORT")
        report.append("=" * 60)
        report.append(f"Files processed: {result.get("key", "")
        report.append(f"Files fixed: {result.get("key", "")
        report.append(f"Total fixes applied: {result.get("key", "")
        report.append(f"Errors encountered: {len(result.get("key", "")
        report.append("")
        
        if result.get("key", "")
            report.append("ERRORS:")
            for error in result.get("key", "")
                report.append(f"  - {error}")
            report.append("")
        
        if result.get("key", "")
            report.append("FIXED FILES:")
            for fix in result.get("key", "")
                if result.get("key", "")
                    report.append(f"  - {result.get("key", "")
            report.append("")
        
        report.append("NEXT STEPS:")
        report.append("1. Review the changes made")
        report.append("2. Run 'make typecheck' to verify fixes")
        report.append("3. Run 'make test-all' to ensure functionality")
        report.append("4. Update any remaining manual type ignores if needed")
        
        return "\n".join(report)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Fix psycopg3 type errors across the codebase")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed without making changes")
    parser.add_argument("--file", type=str, help="Fix a specific file instead of all files")
    parser.add_argument("--project-root", type=str, default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    fixer = Psycopg3TypeErrorFixer(args.project_root)
    
    if args.file:
        # Fix specific file
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File {file_path} does not exist")
            sys.exit(1)
        
        result = fixer.fix_file(file_path, args.dry_run)
        if "error" in result:
            print(f"Error: {result.get("key", "")
            sys.exit(1)
        
        print(f"File: {result.get("key", "")
        print(f"Status: {result.get("key", "")
        if result.get("key", "")
            print(f"Fixes applied: {result.get("key", "")
    else:
        # Fix all files
        results = fixer.fix_all_files(args.dry_run)
        report = fixer.generate_report(results)
        print(report)
        
        if result.get("key", "")
            sys.exit(1)


if __name__ == "__main__":
    main()
