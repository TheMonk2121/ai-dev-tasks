#!/usr/bin/env python3.12.123.11
"""
Coding Standards Validation Script

Validates Python files against our coding standards:
- Import usage (F401)
- F-string usage (F541)
- Variable usage (F841)
"""

import ast
import sys
from pathlib import Path


class CodingStandardsValidator:
    """Validates Python files against coding standards."""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_file(self, file_path: Path) -> tuple[list[str], list[str]]:
        """Validate a single Python file."""
        self.errors = []
        self.warnings = []

        try:
            with open(file_path) as f:
                content = f.read()

            tree = ast.parse(content)
            self._validate_imports(tree, file_path)
            self._validate_f_strings(tree, file_path)
            self._validate_variables(tree, file_path)

        except Exception as e:
            self.errors.append(f"{file_path}: Error parsing file: {e}")

        return self.errors, self.warnings

    def _validate_imports(self, tree: ast.AST, file_path: Path):
        """Validate import organization and usage."""
        imports = []
        used_names = set()

        # Collect imports and used names
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(("import", alias.name, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(("from", f"{module}.{alias.name}", node.lineno))
            elif isinstance(node, ast.Name):
                used_names.add(node.id)

        # Check for unused imports
        for import_type, name, lineno in imports:
            if name not in used_names and not name.startswith("_"):
                self.warnings.append(f"{file_path}:{lineno}: Potentially unused import '{name}'")

    def _validate_f_strings(self, tree: ast.AST, file_path: Path):
        """Validate f-string usage."""
        for node in ast.walk(tree):
            if isinstance(node, ast.JoinedStr):
                # Check if f-string has placeholders
                has_placeholders = False
                for value in node.values:
                    if isinstance(value, ast.FormattedValue):
                        has_placeholders = True
                        break

                if not has_placeholders:
                    self.warnings.append(
                        f"{file_path}:{node.lineno}: F-string without placeholders - consider using regular string"
                    )

    def _validate_variables(self, tree: ast.AST, file_path: Path):
        """Validate variable usage."""
        assigned_vars = set()
        used_vars = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assigned_vars.add(target.id)
            elif isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Load):
                    used_vars.add(node.id)

        # Check for unused variables (excluding special names)
        unused_vars = assigned_vars - used_vars
        for var in unused_vars:
            if not var.startswith("_") and var not in ["self", "cls", "args", "kwargs"]:
                self.warnings.append(f"{file_path}: Unused variable '{var}'")


def main():
    """Main validation function."""
    validator = CodingStandardsValidator()
    all_errors = []
    all_warnings = []

    # Get Python files to validate
    python_files = list(Path(".").rglob("*.py"))

    # Exclude archived files and common directories
    exclude_patterns = ["600_archives", "__pycache__", ".pytest_cache", ".venv", "venv", "node_modules"]

    files_to_check = []
    for file_path in python_files:
        if not any(pattern in str(file_path) for pattern in exclude_patterns):
            files_to_check.append(file_path)

    print(f"🔍 Validating {len(files_to_check)} Python files...")

    for file_path in files_to_check:
        errors, warnings = validator.validate_file(file_path)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    # Report results
    if all_errors:
        print(f"\n❌ {len(all_errors)} errors found:")
        for error in all_errors:
            print(f"  {error}")

    if all_warnings:
        print(f"\n⚠️  {len(all_warnings)} warnings found:")
        for warning in all_warnings[:10]:  # Show first 10 warnings
            print(f"  {warning}")
        if len(all_warnings) > 10:
            print(f"  ... and {len(all_warnings) - 10} more warnings")

    if not all_errors and not all_warnings:
        print("✅ No coding standard violations found!")
        sys.exit(0)
    else:
        print(f"\n📊 Summary: {len(all_errors)} errors, {len(all_warnings)} warnings")
        if all_errors:
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == "__main__":
    main()
