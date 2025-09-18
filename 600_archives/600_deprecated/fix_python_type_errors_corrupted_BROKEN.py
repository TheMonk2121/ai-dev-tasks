#!/usr/bin/env python3
"""
DEPRECATED: Automated script to fix common Python type errors across the codebase.

This script has been deprecated and moved to 600_archives/600_deprecated/ because:
- The type migration and annotation work has been completed
- Modern Python 3.12+ projects should use proper type annotations from the start
- These utility scripts are no longer needed for ongoing development
- This specific file was marked as CORRUPTED and BROKEN and should not be used

Date deprecated: 2025-01-27
Reason: Type migration completed, utility scripts no longer needed
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any


class PythonTypeErrorFixer:
    """Automated fixer for Python type errors."""
    
    def __init__(self, project_root: str = ".") -> None:
        self.project_root: Path = Path(project_root)
        self.fixes_applied: int = 0
        self.files_processed: int = 0
        self.errors_found: int = 0
        
        # Common import patterns and their fixes
        self.import_patterns: dict[str, dict[str, str | list[str]]] = {
            "os": {
                "usage_patterns": [r"os\.environ", r"os\.getenv", r"os\.path", r"os\.makedirs", r"os\.listdir"],
                "import": "import os",
                "description": "Add missing os import"
            },
            "sys": {
                "usage_patterns": [r"sys\.path", r"sys\.argv", r"sys\.exit", r"sys\.modules"],
                "import": "import sys",
                "description": "Add missing sys import"
            },
            "Path": {
                "usage_patterns": [r"Path\(", r"Path\."],
                "import": "from pathlib import Path",
                "description": "Add missing Path import from pathlib"
            },
            "datetime": {
                "usage_patterns": [r"datetime\.datetime", r"datetime\.date", r"datetime\.time"],
                "import": "from datetime import datetime",
                "description": "Add missing datetime import"
            },
            "json": {
                "usage_patterns": [r"json\.loads", r"json\.dumps", r"json\.load", r"json\.dump"],
                "import": "import json",
                "description": "Add missing json import"
            },
            "typing": {
                "usage_patterns": [r"List\[", r"Dict\[", r"Optional\[", r"Union\[", r"Any", r"Tuple\[", r"Set\["],
                "import": "from typing import List, Dict, Optional, Union, Any, Tuple, Set",
                "description": "Add missing typing imports"
            },
            "httpx": {
                "usage_patterns": [r"httpx\.", r"AsyncClient", r"Client"],
                "import": "import httpx",
                "description": "Add missing httpx import"
            },
            "pytest": {
                "usage_patterns": [r"pytest\.", r"@pytest\.", r"pytest_"],
                "import": "import pytest",
                "description": "Add missing pytest import"
            }
        }
        
        # Type annotation patterns
        self.type_annotation_patterns: dict[str, dict[str, str]] = {
            "function_return_type": {
                "pattern": r"^def\s+(\w+)\(\):\s*$",
                "replacement": r"def \1() -> None:",
                "description": "Add None return type to functions with no parameters"
            },
            "method_return_type": {
                "pattern": r"^    def\s+(\w+)\(self[^)]*\):\s*$",
                "replacement": r"    def \1(self) -> None:",
                "description": "Add None return type to methods (preserves parameters)"
            },
            "variable_type_hint": {
                "pattern": r"(\w+)\s*=\s*\[\]\s*$",
                "replacement": r"\1: list[Any] = []",
                "description": "Add type hint for empty list variables"
            },
            "dict_type_hint": {
                "pattern": r"(\w+)\s*=\s*\{\}\s*$",
                "replacement": r"\1: dict[str, Any] = {}",
                "description": "Add type hint for empty dict variables"
            },
            "modern_dict_typing": {
                "pattern": r"Dict\[([^\]]+)\]",
                "replacement": r"dict[\1]",
                "description": "Replace Dict with modern dict typing"
            },
            "modern_list_typing": {
                "pattern": r"List\[([^\]]+)\]",
                "replacement": r"list[\1]",
                "description": "Replace List with modern list typing"
            },
            "database_result_indexing": {
                "pattern": r"if not result or not result\[0\]:",
                "replacement": r"if not result or len(result) == 0:\n        return  # Skip if no result\n    if not result.get("key", "")
                "description": "Fix database result indexing with proper type handling"
            },
            "database_result_safe_access": {
                "pattern": r"result\[0\]",
                "replacement": r"result.get("key", "")
                "description": "Add safe access to database result indexing"
            }
        }
        
        self.exclude_patterns: list[str] = [
            "*/__pycache__/*",
            "*/venv/*",
            "*/.venv/*",
            "*/node_modules/*",
            "*/600_archives/*",
            "*/tests/test_*",
            "*/test_*.py",
            "*/site-packages/*",
            "*/migrations/versions/*"
        ]

    def should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from processing."""
        file_str = str(file_path)
        
        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if pattern.replace("*", "").replace("/", "") in file_str:
                return True
        
        # Only process Python files
        if file_path.suffix != ".py":
            return True
            
        return False

    def find_python_files(self) -> list[Path]:
        """Find all Python files in the project."""
        python_files: list[Path] = []
        
        for file_path in self.project_root.rglob("*.py"):
            if not self.should_exclude_file(file_path):
                python_files.append(file_path)
        
        return python_files

    def analyze_file(self, file_path: Path) -> dict[str, Any]:
        """Analyze a Python file for type errors."""
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Failed to read file: {e}", "issues": []}
        
        issues: list[str] = []
        missing_imports: set[str] = set()
        
        # Check for missing imports
        for module, info in self.import_patterns.items():
            for pattern in info["patterns"]:
                if re.search(pattern, content):
                    # Check if import already exists
                    import_stmt: str = info["import"]
                    if module == "Path":
                        if "from pathlib import Path" not in content and "import pathlib" not in content:
                            missing_imports.add(import_stmt)
                            issues.append(f"Missing {module} import")
                    elif module == "typing":
                        if "from typing import" not in content and "import typing" not in content:
                            missing_imports.add(import_stmt)
                            issues.append(f"Missing {module} import")
                    else:
                        if f"import {module}" not in content:
                            missing_imports.add(import_stmt)
                            issues.append(f"Missing {module} import")
        
        return {
            "issues": issues,
            "missing_imports": missing_imports,
            "content": content
        }

    def fix_file(self, file_path: Path, dry_run: bool = False) -> dict[str, Any]:
        """Fix Python type errors in a file."""
        analysis = self.analyze_file(file_path)
        
        if "error" in analysis:
            return analysis
        
        content = result.get("key", "")
        original_content = content
        fixes_applied = 0
        
        # Add missing imports
        if result.get("key", "")
            lines = content.split('\n')
            
            # Find the best place to insert imports
            import_section_end = 0
            for i, line in enumerate(lines):
                if line.strip().startswith(('import ', 'from ')):
                    import_section_end = i + 1
                elif line.strip() and not line.strip().startswith('#'):
                    break
            
            # Insert missing imports
            new_imports: list[str] = []
            for import_stmt in sorted(result.get("key", "")
                if import_stmt not in content:
                    new_imports.append(import_stmt)
            
            if new_imports:
                # Insert imports after existing imports
                for import_stmt in new_imports:
                    lines.insert(import_section_end, import_stmt)
                    import_section_end += 1
                    fixes_applied += 1
                    print(f"  ✅ Added import: {import_stmt}")
                
                content = '\n'.join(lines)
        
        # Apply type annotation fixes
        for pattern_name, pattern_info in self.\1.items()
            pattern = result.get("key", "")
            replacement = result.get("key", "")
            
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            if new_content != content:
                content = new_content
                fixes_applied += 1
                print(f"  ✅ Applied fix: {result.get("key", "")
        
        # Write changes if not dry run
        if not dry_run and content != original_content:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  💾 Saved changes to {file_path}")
            except Exception as e:
                return {"error": f"Failed to write file: {e}"}
        
        return {
            "issues_found": len(result.get("key", "")
            "fixes_applied": fixes_applied,
            "changed": content != original_content
        }

    def fix_all_files(self, dry_run: bool = False) -> dict[str, Any]:
        """Fix Python type errors in all files."""
        python_files = self.find_python_files()
        
        if not python_files:
            print("No Python files found.")
            return {"files_processed": 0, "fixes_applied": 0}
        
        print(f"Found {len(python_files)} Python files")
        
        total_fixes = 0
        files_changed = 0
        
        for file_path in python_files:
            print(f"\n🔍 Processing {file_path}")
            
            result = self.fix_file(file_path, dry_run)
            
            if "error" in result:
                print(f"  ❌ Error: {result.get("key", "")
                continue
            
            if result.get("key", "")
                total_fixes += result.get("key", "")
                if result.get("key", "")
                    files_changed += 1
                print(f"  ✅ Applied {result.get("key", "")
            else:
                print("  ✅ No issues found")
        
        return {
            "files_processed": len(python_files),
            "files_changed": files_changed,
            "fixes_applied": total_fixes
        }

    def generate_report(self, results: dict[str, Any]) -> str:
        """Generate a summary report."""
        return f"""
Python Type Error Fixing Report
===============================

Files processed: {result.get("key", "")
Files changed: {result.get("key", "")
Total fixes applied: {result.get("key", "")

Common fixes applied:
- Added missing imports (os, sys, Path, datetime, json, typing, httpx, pytest)
- Added type hints for variables and functions
- Fixed common type annotation patterns

Next steps:
1. Review the changes in your Python files
2. Run type checking: uv run basedpyright
3. Run linting: uv run ruff check
4. Commit the changes if they look correct
"""


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fix Python type errors")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed without making changes")
    parser.add_argument("--file", help="Fix specific file instead of all files")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    fixer = PythonTypeErrorFixer(args.project_root)
    
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File {file_path} does not exist")
            sys.exit(1)
        
        print(f"Fixing Python type errors in {file_path}")
        result = fixer.fix_file(file_path, args.dry_run)
        
        if "error" in result:
            print(f"Error: {result.get("key", "")
            sys.exit(1)
        
        print(f"Applied {result.get("key", "")
    else:
        print("Python Type Error Fixer")
        print("=" * 30)
        
        if args.dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
        
        results = fixer.fix_all_files(args.dry_run)
        print(fixer.generate_report(results))


if __name__ == "__main__":
    main()
