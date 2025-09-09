#!/usr/bin/env python3
"""
Script to automatically remove unused typing imports from Python files.
This is safer than manual removal because it checks if imports are actually used.
"""

import ast
import sys
from pathlib import Path
from typing import Set


def get_used_names(file_path: Path) -> set[str]:
    """Extract all used names from a Python file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        used_names = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                used_names.add(node.attr)
            elif isinstance(node, ast.AnnAssign):
                # Check type annotations
                if hasattr(node.annotation, "id"):
                    used_names.add(node.annotation.id)
                elif hasattr(node.annotation, "slice"):
                    # Handle generic types like Dict[str, int]
                    if hasattr(node.annotation.slice, "elts"):
                        for elt in node.annotation.slice.elts:
                            if hasattr(elt, "id"):
                                used_names.add(elt.id)
            elif isinstance(node, ast.FunctionDef):
                # Check function return type annotations
                if node.returns and hasattr(node.returns, "id"):
                    used_names.add(node.returns.id)
                # Check function parameter type annotations
                for arg in node.args.args:
                    if arg.annotation and hasattr(arg.annotation, "id"):
                        used_names.add(arg.annotation.id)

        return used_names
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return set()


def remove_unused_typing_imports(file_path: Path) -> bool:
    """Remove unused typing imports from a file. Returns True if changes were made."""
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        used_names = get_used_names(file_path)

        # Common typing imports that are often unused
        typing_imports = {
            "Dict",
            "List",
            "Tuple",
            "Set",
            "Optional",
            "Union",
            "Any",
            "Callable",
            "Iterable",
            "Iterator",
            "Generator",
            "Mapping",
            "Sequence",
            "MutableMapping",
            "MutableSequence",
        }

        modified = False
        new_lines = []

        for line in lines:
            if line.strip().startswith("from typing import"):
                # Parse the import line
                try:
                    # Extract the imports
                    import_part = line.split("from typing import")[1].strip()
                    imports = [imp.strip() for imp in import_part.split(",")]

                    # Filter out unused imports
                    used_imports = []
                    for imp in imports:
                        if imp in used_names or imp not in typing_imports:
                            used_imports.append(imp)

                    if used_imports:
                        new_line = f"from typing import {', '.join(used_imports)}\n"
                        new_lines.append(new_line)
                    else:
                        # All imports were unused, remove the line
                        modified = True
                        continue

                except Exception as e:
                    print(f"Error processing import line in {file_path}: {e}")
                    new_lines.append(line)
            else:
                new_lines.append(line)

        if modified or len(new_lines) != len(lines):
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Process all Python files in the scripts directory."""
    scripts_dir = Path("scripts")
    if not scripts_dir.exists():
        print("Scripts directory not found")
        return

    modified_files = []

    for py_file in scripts_dir.rglob("*.py"):
        if remove_unused_typing_imports(py_file):
            modified_files.append(py_file)
            print(f"Modified: {py_file}")

    print(f"\nModified {len(modified_files)} files")
    for file in modified_files:
        print(f"  - {file}")


if __name__ == "__main__":
    main()
