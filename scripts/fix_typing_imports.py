#!/usr/bin/env python3.12
"""Fix deprecated typing imports (UP035) across the codebase"""

import re
import subprocess
from pathlib import Path


def fix_typing_imports(file_path: Path) -> bool:
    """Fix typing imports in a single file"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Remove typing imports that are no longer needed
        # Pattern: from typing import ... (where the types are built-in)
        typing_pattern = r"from typing import ([^, \n]+(?:, [^, \n]+)*)"

        def replace_typing_import(match):
            imports = [imp.strip() for imp in match.group(1).split(",")]
            remaining_imports = []

            for imp in imports:
                # Keep imports that aren't built-in types
                if imp not in [
                    "Dict",
                    "List",
                    "Tuple",
                    "Set",
                    "FrozenSet",
                    "Type",
                    "AbstractSet",
                ]:
                    remaining_imports.append(imp)

            if remaining_imports:
                return f'from typing import {", ".join(remaining_imports)}'
            else:
                return ""

        content = re.sub(typing_pattern, replace_typing_import, content)

        # Remove empty import lines
        content = re.sub(r"\n\s*from typing import\s*\n", "\n", content)
        content = re.sub(r"\n\s*from typing import\s*$", "", content)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to fix typing imports across the project"""
    project_dirs = ["scripts", "dspy-rag-system", "tests"]
    fixed_files = 0

    for dir_name in project_dirs:
        if not Path(dir_name).exists():
            continue

        for py_file in Path(dir_name).rglob("*.py"):
            if fix_typing_imports(py_file):
                fixed_files += 1
                print(f"Fixed: {py_file}")

    print(f"\nFixed {fixed_files} files")

    # Run Ruff to check remaining UP035 errors
    print("\nChecking remaining UP035 errors...")
    result = subprocess.run(
        [
            "ruff",
            "check",
            "--select",
            "UP035",
            "scripts/",
            "dspy-rag-system/",
            "tests/",
        ],
        capture_output=True,
        text=True,
    )

    if result.stdout:
        print("Remaining UP035 errors:")
        print(result.stdout)
    else:
        print("No UP035 errors remaining!")


if __name__ == "__main__":
    main()
