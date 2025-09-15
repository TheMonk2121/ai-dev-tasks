#!/usr/bin/env python3
"""
Clean up database content by removing low-value files that inhibit RAG performance.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Files to exclude from RAG indexing
EXCLUDE_PATTERNS = [
    # IDE and editor files
    ".cursor/",
    ".vscode/",
    ".idea/",
    ".vscode/",
    # Cache and generated files
    ".cache/",
    "__pycache__/",
    "node_modules/",
    ".git/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    # Test files
    "tests/",
    "test_",
    "_test.py",
    ".test.",
    # Config files (keep only essential ones)
    ".env",
    ".cspell.json",
    ".pre-commit-config.yaml",
    ".diagnostics/",
    ".logfire/",
    "fontlist-",
    "extensions.json",
    "keybindings.json",
    "settings.json",
    # Archives
    "600_archives/",
    # Temporary files
    ".ai_state.json",
    ".rehydrate_state.json",
    "logfire_credentials.json",
]

# Files to keep (high value for RAG)
KEEP_PATTERNS = [
    "src/",
    "400_guides/",
    "000_core/",
    "scripts/data_processing/",
    "300_evals/scripts/evaluation/",
    "scripts/utilities/",
    "pyproject.toml",
    "README.md",
    "Makefile",
]


def should_exclude_file(file_path: str, file_name: str) -> bool:
    """Determine if a file should be excluded from RAG indexing."""

    # Check exclude patterns
    for pattern in EXCLUDE_PATTERNS:
        if pattern in file_path or pattern in file_name:
            return True

    # Check if it's a keep pattern (override exclude)
    for pattern in KEEP_PATTERNS:
        if pattern in file_path:
            return False

    return False


def cleanup_database():
    """Remove low-value files from the database."""

    dsn = "postgresql://danieljacobs@localhost:5432/ai_agency"

    with psycopg2.connect(dsn, cursor_factory=RealDictCursor) as conn:
        with conn.cursor() as cur:
            # Get all documents
            cur.execute("SELECT id, file_path, file_name FROM documents")
            documents = cur.fetchall()

            print(f"📄 Analyzing {len(documents)} documents...")

            # Categorize files
            to_keep = []
            to_remove = []

            for doc in documents:
                if should_exclude_file(doc["file_path"], doc["file_name"]):
                    to_remove.append(doc["id"])
                else:
                    to_keep.append(doc["id"])

            print(f"✅ Files to keep: {len(to_keep)}")
            print(f"🗑️  Files to remove: {len(to_remove)}")

            if to_remove:
                # Remove documents and their chunks
                cur.execute(
                    """
                    DELETE FROM documents 
                    WHERE id = ANY(%s)
                """,
                    (to_remove,),
                )

                print(f"🗑️  Removed {cur.rowcount} documents and their chunks")

            # Show what's left
            cur.execute(
                """
                SELECT 
                    CASE 
                        WHEN file_path LIKE '%src%' THEN 'source_code'
                        WHEN file_path LIKE '%400_%' OR file_path LIKE '%000_%' THEN 'documentation'
                        WHEN file_path LIKE '%scripts%' THEN 'scripts'
                        ELSE 'other'
                    END as category,
                    COUNT(*) as count
                FROM documents 
                GROUP BY 1
                ORDER BY count DESC
            """
            )

            print("\n📊 Remaining content by category:")
            for row in cur.fetchall():
                print(f"   {row['category']}: {row['count']} files")


if __name__ == "__main__":
    cleanup_database()
