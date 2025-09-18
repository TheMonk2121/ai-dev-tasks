#!/usr/bin/env python3
"""
Database Migration Script: psycopg2 to psycopg3

This script helps migrate scripts from psycopg2 to psycopg3 with resolve_dsn() integration.
It provides both automated migration suggestions and manual migration helpers.

Usage:
    python scripts/migration/migrate_to_psycopg3.py --scan scripts/
    python scripts/migration/migrate_to_psycopg3.py --migrate scripts/utilities/upgrade_validation.py
"""

import argparse
import ast
import os
import re
import sys
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import httpx

from common.db_dsn import resolve_dsn
from config.settings import get_settings


class PsycopgMigrationAnalyzer:
    """Analyzes Python files for psycopg2 usage patterns."""

    def __init__(self):
        self.psycopg2_patterns = {
            "import": r"import\s+psycopg2",
            "from_import": r"from\s+psycopg2",
            "connect": r"psycopg2\.connect\(",
            "os_getenv": r"os\.getenv\([\"'](?:DATABASE_URL|POSTGRES_DSN)[\"']\)",
            "cursor": r"\.cursor\(\)",
            "execute": r"\.execute\(",
            "fetchone": r"\.fetchone\(\)",
            "fetchall": r"\.fetchall\(\)",
            "commit": r"\.commit\(\)",
            "rollback": r"\.rollback\(\)",
            "close": r"\.close\(\)",
        }

    def scan_file(self, file_path: Path) -> dict[str, Any]:
        """Scan a single file for psycopg2 usage patterns."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            findings = {
                "file": str(file_path),
                "patterns_found": [],
                "line_numbers": {},
                "migration_complexity": "low",
                "suggestions": [],
            }

            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                for pattern_name, pattern in self.psycopg2_patterns.items():
                    if re.search(pattern, line):
                        if pattern_name not in findings["patterns_found"]:
                            findings["patterns_found"].append(pattern_name)
                        if pattern_name not in findings["line_numbers"]:
                            findings["line_numbers"][pattern_name] = []
                        findings["line_numbers"][pattern_name].append(i)

            # Determine migration complexity
            if "connect" in findings["patterns_found"]:
                findings["migration_complexity"] = "high"
            elif "import" in findings["patterns_found"] or "from_import" in findings["patterns_found"]:
                findings["migration_complexity"] = "medium"

            # Generate suggestions
            findings["suggestions"] = self._generate_suggestions(findings)

            return findings

        except Exception as e:
            return {
                "file": str(file_path),
                "error": str(e),
                "patterns_found": [],
                "line_numbers": {},
                "migration_complexity": "unknown",
                "suggestions": [],
            }

    def _generate_suggestions(self, findings: dict[str, Any]) -> list[str]:
        """Generate migration suggestions based on findings."""
        suggestions = []

        if "import" in findings["patterns_found"]:
            suggestions.append("Replace 'import psycopg2' with 'import psycopg'")

        if "from_import" in findings["patterns_found"]:
            suggestions.append("Replace 'from psycopg2' with 'from psycopg'")

        if "os_getenv" in findings["patterns_found"]:
            suggestions.append("Replace os.getenv('DATABASE_URL') with resolve_dsn(strict=False, role='script_name')")

        if "connect" in findings["patterns_found"]:
            suggestions.append("Update psycopg2.connect() to psycopg.connect() with resolve_dsn()")

        if "cursor" in findings["patterns_found"]:
            suggestions.append("Consider using psycopg.rows.dict_row for dictionary-like row access")

        return suggestions

    def scan_directory(self, directory: Path) -> list[dict[str, Any]]:
        """Scan a directory for psycopg2 usage."""
        results = []
        for py_file in directory.rglob("*.py"):
            if py_file.is_file():
                result = self.scan_file(py_file)
                if result["patterns_found"]:
                    results.append(result)
        return results


class PsycopgMigrationHelper:
    """Helper class for migrating psycopg2 to psycopg3."""

    def __init__(self):
        self.settings = get_settings()

    def create_migration_template(self, file_path: Path) -> str:
        """Create a migration template for a specific file."""
        template = f'''#!/usr/bin/env python3
"""
Migration template for {file_path.name}

This template shows how to migrate from psycopg2 to psycopg3 with resolve_dsn().
"""

# OLD: psycopg2 imports
# import psycopg2
# from psycopg2 import OperationalError

# NEW: psycopg3 imports
import psycopg
import psycopg.rows
from src.common.db_dsn import resolve_dsn

# OLD: Direct environment variable access
# conn = psycopg2.connect(os.getenv("DATABASE_URL"))

# NEW: Using resolve_dsn() with proper role
conn = psycopg.connect(resolve_dsn(strict=False, role="{file_path.stem}"))

# OLD: Basic cursor
# cursor = conn.cursor()

# NEW: Dictionary-like row access (optional)
cursor = conn.cursor(row_factory=psycopg.rows.dict_row)

# Example usage:
try:
    with psycopg.connect(resolve_dsn(strict=False, role="{file_path.stem}")) as conn:
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cursor:
            cursor.execute("SELECT * FROM table_name")
            rows = cursor.fetchall()
            for row in rows:
                print(row)  # row is now a dictionary
except psycopg.Error as e:
    print(f"Database error: {{e}}")
'''
        return template

    def migrate_file(self, file_path: Path, dry_run: bool = True) -> dict[str, Any]:
        """Migrate a specific file from psycopg2 to psycopg3."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content
            changes_made = []

            # Replace imports
            if "import psycopg2" in content:
                content = content.replace("import psycopg2", "import psycopg")
                changes_made.append("Updated psycopg2 import to psycopg")

            if "from psycopg2" in content:
                content = content.replace("from psycopg2", "from psycopg")
                changes_made.append("Updated psycopg2 from import to psycopg")

            # Replace os.getenv patterns
            dsn_pattern = r"os\.getenv\([\"'](?:DATABASE_URL|POSTGRES_DSN)[\"']\)"
            if re.search(dsn_pattern, content):
                content = re.sub(
                    dsn_pattern,
                    'resolve_dsn(strict=False, role="' + file_path.stem + '")',
                    content,
                )
                changes_made.append("Replaced os.getenv DSN with resolve_dsn()")

            # Replace psycopg2.connect
            if "psycopg2.connect" in content:
                content = content.replace("psycopg2.connect", "psycopg.connect")
                changes_made.append("Updated psycopg2.connect to psycopg.connect")

            # Add resolve_dsn import if needed
            if "resolve_dsn" in content and "from src.common.db_dsn import resolve_dsn" not in content:
                # Find the last import statement
                import_lines = []
                for i, line in enumerate(content.split("\n")):
                    if line.strip().startswith(("import ", "from ")):
                        import_lines.append(i)

                if import_lines:
                    last_import_line = max(import_lines)
                    lines = content.split("\n")
                    lines.insert(
                        last_import_line + 1,
                        "from src.common.db_dsn import resolve_dsn",
                    )
                    content = "\n".join(lines)
                    changes_made.append("Added resolve_dsn import")

            if not dry_run and content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

            return {
                "file": str(file_path),
                "changes_made": changes_made,
                "success": True,
                "dry_run": dry_run,
            }

        except Exception as e:
            return {
                "file": str(file_path),
                "error": str(e),
                "changes_made": [],
                "success": False,
                "dry_run": dry_run,
            }


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Psycopg2 to Psycopg3 Migration Tool")
    parser.add_argument("--scan", help="Scan directory for psycopg2 usage")
    parser.add_argument("--migrate", help="Migrate specific file from psycopg2 to psycopg3")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying them")
    parser.add_argument("--template", help="Generate migration template for specific file")

    args = parser.parse_args()

    if args.scan:
        print(f"🔍 Scanning directory: {args.scan}")
        analyzer = PsycopgMigrationAnalyzer()
        results = analyzer.scan_directory(Path(args.scan))

        print(f"\n📊 Found {len(results)} files with psycopg2 usage:")
        print("=" * 60)

        for result in results:
            print(f"\n📁 {result['file']}")
            print(f"   Complexity: {result['migration_complexity']}")
            print(f"   Patterns: {', '.join(result['patterns_found'])}")
            if result["suggestions"]:
                print("   Suggestions:")
                for suggestion in result["suggestions"]:
                    print(f"     • {suggestion}")

    elif args.migrate:
        print(f"🔄 Migrating file: {args.migrate}")
        helper = PsycopgMigrationHelper()
        result = helper.migrate_file(Path(args.migrate), dry_run=args.dry_run)

        if result["success"]:
            print(f"✅ Migration {'completed' if not args.dry_run else 'preview'}:")
            for change in result["changes_made"]:
                print(f"   • {change}")
        else:
            print(f"❌ Migration failed: {result.get('error', 'Unknown error')}")

    elif args.template:
        print(f"📝 Generating template for: {args.template}")
        helper = PsycopgMigrationHelper()
        template = helper.create_migration_template(Path(args.template))
        print(template)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
