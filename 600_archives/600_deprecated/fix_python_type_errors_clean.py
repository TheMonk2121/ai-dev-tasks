#!/usr/bin/env python3
"""
DEPRECATED: Clean automated script to fix common Python type errors across the codebase.

This script has been deprecated and moved to 600_archives/600_deprecated/ because:
- The type migration and annotation work has been completed
- Modern Python 3.12+ projects should use proper type annotations from the start
- These utility scripts are no longer needed for ongoing development

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
                "patterns": [r"os\.environ", r"os\.getenv", r"os\.path", r"os\.makedirs", r"os\.listdir"],
                "import": "import os",
                "description": "Add missing os import"
            },
            "Path": {
                "patterns": [r"Path\(", r"Path\."],
                "import": "from pathlib import Path",
                "description": "Add missing Path import"
            },
            "typing": {
                "patterns": [r"from typing import", r"typing\."],
                "import": "from typing import Any",
                "description": "Add missing typing import"
            },
            "json": {
                "patterns": [r"json\.loads", r"json\.dumps", r"json\.load", r"json\.dump"],
                "import": "import json",
                "description": "Add missing json import"
            },
            "re": {
                "patterns": [r"re\.search", r"re\.match", r"re\.sub", r"re\.findall"],
                "import": "import re",
                "description": "Add missing re import"
            }
        }
        
        # Common type error patterns and their fixes
        self.type_fixes: dict[str, dict[str, str]] = {
            "missing_return_type": {
                "pattern": r"def\s+(\w+)\([^)]*\):\s*$",
                "replacement": r"def \1() -> None:",
                "description": "Add missing return type annotation"
            },
            "missing_method_return_type": {
                "pattern": r"(\s+)def\s+(\w+)\(self[^)]*\):\s*$",
                "replacement": r"\1def \2(self) -> None:",
                "description": "Add missing method return type annotation"
            },
            "list_unknown_type": {
                "pattern": r"(\w+)\s*=\s*\[\]\s*$",
                "replacement": r"\1: list[Any] = []",
                "description": "Add type annotation for empty list"
            },
            "dict_unknown_type": {
                "pattern": r"(\w+)\s*=\s*\{\}\s*$",
                "replacement": r"\1: dict[str, Any] = {}",
                "description": "Add type annotation for empty dict"
            },
            "dict_missing_type_args": {
                "pattern": r"dict\[([^\]]+)\]",
                "replacement": r"dict[\1]",
                "description": "Fix dict type arguments"
            },
            "list_missing_type_args": {
                "pattern": r"list\[([^\]]+)\]",
                "replacement": r"list[\1]",
                "description": "Fix list type arguments"
            }
        }
    
    def analyze_file(self, file_path: Path) -> dict[str, Any]:
        """Analyze a single file for type errors."""
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
            "missing_imports": list(missing_imports),
            "content": content
        }
    
    def fix_file(self, file_path: Path) -> dict[str, Any]:
        """Fix type errors in a single file."""
        analysis = self.analyze_file(file_path)
        if "error" in analysis:
            return analysis
        
        content = analysis["content"]
        original_content = content
        fixes_applied = 0
        
        # Apply import fixes
        if analysis["missing_imports"]:
            # Add imports at the top of the file
            import_lines = []
            for import_stmt in sorted(analysis["missing_imports"]):
                import_lines.append(import_stmt)
            
            # Find the right place to insert imports
            lines = content.split('\n')
            insert_index = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    insert_index = i + 1
                elif line.strip() and not line.startswith('#'):
                    break
            
            # Insert imports
            for import_line in reversed(import_lines):
                lines.insert(insert_index, import_line)
            
            content = '\n'.join(lines)
            fixes_applied += len(analysis["missing_imports"])
        
        # Apply type fixes
        for pattern_name, pattern_info in self.type_fixes.items():
            pattern = pattern_info["pattern"]
            replacement = pattern_info["replacement"]
            
            if re.search(pattern, content, re.MULTILINE):
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                fixes_applied += 1
                print(f"  ✅ Applied fix: {pattern_info['description']}")
        
        # Only write if changes were made
        if content != original_content:
            try:
                # Validate the fixed content
                compile(content, str(file_path), 'exec')
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return {
                    "success": True,
                    "fixes_applied": fixes_applied,
                    "issues_found": len(analysis["issues"])
                }
            except SyntaxError as e:
                return {"error": f"Fixed content has syntax error: {e}"}
        
        return {
            "success": True,
            "fixes_applied": 0,
            "issues_found": len(analysis["issues"])
        }
    
    def fix_all_files(self, dry_run: bool = False) -> dict[str, Any]:
        """Fix type errors in all Python files."""
        python_files = []
        for pattern in ['src/**/*.py', 'scripts/**/*.py', 'evals/**/*.py', 'tests/**/*.py']:
            python_files.extend(self.project_root.glob(pattern))
        
        # Filter out archive and venv directories
        python_files = [
            f for f in python_files 
            if '600_archives' not in str(f) and 'venv' not in str(f) and '.venv' not in str(f)
        ]
        
        total_fixes = 0
        files_changed = 0
        
        for file_path in python_files:
            print(f"Processing: {file_path}")
            
            if dry_run:
                analysis = self.analyze_file(file_path)
                if analysis["issues"]:
                    print(f"  Issues found: {len(analysis['issues'])}")
                    for issue in analysis["issues"]:
                        print(f"    - {issue}")
            else:
                result = self.fix_file(file_path)
                if "error" in result:
                    print(f"  ❌ Error: {result['error']}")
                else:
                    if result["fixes_applied"] > 0:
                        total_fixes += result["fixes_applied"]
                        files_changed += 1
                        print(f"  ✅ Applied {result['fixes_applied']} fixes")
                    else:
                        print("  ℹ️  No fixes needed")
        
        return {
            "files_processed": len(python_files),
            "files_changed": files_changed,
            "total_fixes": total_fixes
        }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fix Python type errors")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed without making changes")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    fixer = PythonTypeErrorFixer(args.project_root)
    
    print("🔧 Python Type Error Fixer")
    print("=" * 50)
    
    result = fixer.fix_all_files(dry_run=args.dry_run)
    
    print("\n" + "=" * 50)
    print("Summary:")
    print(f"Files processed: {result['files_processed']}")
    print(f"Files changed: {result['files_changed']}")
    print(f"Total fixes applied: {result['total_fixes']}")


if __name__ == "__main__":
    main()
