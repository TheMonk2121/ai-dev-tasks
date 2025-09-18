#!/usr/bin/env python3
"""
Fix dict[str, Any] type errors by replacing with dict[str, Any].
"""

import re
from pathlib import Path
from typing import Any


def fix_dict_unknown_in_file(file_path: Path) -> bool:
    """Fix dict[str, Any] type errors in a single file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content: Any = f.read()

        original_content = content

        # Fix dict[str, Any] -> dict[str, Any]
        content = re.sub(r"dict\[str,\s*Unknown\]", "dict[str, Any]", content)

        # Fix dict[Any, str] -> dict[Any, str] (less common but possible)
        content = re.sub(r"dict\[Unknown,\s*str\]", "dict[Any, str]", content)

        # Fix dict[Any, Any] -> dict[Any, Any]
        content = re.sub(r"dict\[Unknown,\s*Unknown\]", "dict[Any, Any]", content)

        # Fix list[Any] -> list[Any]
        content = re.sub(r"list\[Unknown\]", "list[Any]", content)

        # Fix tuple[Any, ...] -> tuple[Any, ...]
        content = re.sub(r"tuple\[Unknown,\s*\.\.\.\]", "tuple[Any, ...]", content)

        # Fix set[Any] -> set[Any]
        content = re.sub(r"set\[Unknown\]", "set[Any]", content)

        # Only write if changes were made
        if content != original_content:
            # Ensure Any is imported
            if (
                "dict[str, Any]" in content
                or "list[Any]" in content
                or "tuple[Any, ...]" in content
                or "set[Any]" in content
            ):
                if "from typing import Any" not in content and "from typing import" in content:
                    # Add Any to existing typing import
                    content = re.sub(r"from typing import ([^n]+)", r"from typing import \1, Any", content)
                elif "from typing import Any" not in content:
                    # Add new typing import
                    import_lines = []
                    lines: Any = content.split("n")
                    for i, line in enumerate(lines):
                        if line.startswith("import ") or line.startswith("from "):
                            import_lines.append(i)

                    if import_lines:
                        # Insert after last import
                        last_import = max(import_lines)
                        lines.insert(last_import + 1, "from typing import Any")
                    else:
                        # Insert at top after shebang
                        if lines and lines[0].startswith("#!"):
                            lines.insert(1, "from typing import Any")
                        else:
                            lines.insert(0, "from typing import Any")

                    content = "n".join(lines)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"Fixed: {file_path}")
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main() -> Any:
    """Fix dict[str, Any] type errors in all Python files."""
    print("🔧 Fixing dict[str, Any] type errors...")

    # Find all Python files
    python_files = []
    for pattern in ["src/**/*.py", "scripts/**/*.py", "evals/**/*.py", "tests/**/*.py"]:
        python_files.extend(Path(".").glob(pattern))

    # Filter out archive and venv directories
    python_files = [
        f for f in python_files if "600_archives" not in str(f) and "venv" not in str(f) and ".venv" not in str(f)
    ]

    fixed_count = 0
    for file_path in python_files:
        if fix_dict_unknown_in_file(file_path):
            fixed_count += 1

    print(f"nFixed {fixed_count} files")


if __name__ == "__main__":
    main()
