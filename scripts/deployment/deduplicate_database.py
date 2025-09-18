#!/usr/bin/env python3
"""
Remove duplicate files from database, keeping only the most recent version of each file.
"""

# Add project paths
import sys

import psycopg

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def deduplicate_database():
    """Remove duplicate files, keeping only the most recent version."""

    dsn = "postgresql://danieljacobs@localhost:5432/ai_agency"

    with psycopg.connect(dsn, cursor_factory=RealDictCursor) as conn:
        with conn.cursor() as cur:
            print("🔍 Analyzing duplicate files in database...")

            # Find files with duplicates
            cur.execute(
                """
                SELECT 
                    file_path,
                    COUNT(*) as version_count,
                    MIN(created_at) as oldest,
                    MAX(created_at) as newest
                FROM documents 
                GROUP BY file_path 
                HAVING COUNT(*) > 1
                ORDER BY version_count DESC, file_path
            """
            )

            duplicates = cur.fetchall()

            if not duplicates:
                print("✅ No duplicate files found in database")
                return

            print(f"📊 Found {len(duplicates)} files with duplicates:")
            total_duplicates = 0

            for dup in duplicates:
                print(f"   {dup['file_path']}: {dup['version_count']} versions")
                total_duplicates += dup["version_count"] - 1  # -1 because we keep one

            print(f"\n🗑️  Will remove {total_duplicates} duplicate versions...")

            # Remove duplicates, keeping only the most recent version
            cur.execute(
                """
                WITH latest_versions AS (
                    SELECT 
                        file_path,
                        MAX(created_at) as latest_created_at
                    FROM documents 
                    GROUP BY file_path
                ),
                files_to_keep AS (
                    SELECT d.id
                    FROM documents d
                    JOIN latest_versions lv ON d.file_path = lv.file_path 
                        AND d.created_at = lv.latest_created_at
                )
                DELETE FROM documents 
                WHERE id NOT IN (SELECT id FROM files_to_keep)
            """
            )

            deleted_count = cur.rowcount
            print(f"✅ Removed {deleted_count} duplicate file versions")

            # Verify the cleanup
            cur.execute(
                """
                SELECT 
                    file_path,
                    COUNT(*) as version_count
                FROM documents 
                GROUP BY file_path 
                HAVING COUNT(*) > 1
                ORDER BY version_count DESC
            """
            )

            remaining_duplicates = cur.fetchall()

            if remaining_duplicates:
                print(f"⚠️  Warning: {len(remaining_duplicates)} files still have duplicates:")
                for dup in remaining_duplicates:
                    print(f"   {dup['file_path']}: {dup['version_count']} versions")
            else:
                print("✅ All duplicates successfully removed")

            # Show final statistics
            cur.execute("SELECT COUNT(*) as total_files FROM documents")
            total_files = cur.fetchone()["total_files"]

            cur.execute(
                """
                SELECT 
                    content_type,
                    COUNT(*) as file_count
                FROM documents 
                GROUP BY content_type 
                ORDER BY file_count DESC
            """
            )

            print("\n📊 Final database state:")
            print(f"   Total files: {total_files}")
            print("   Files by type:")

            for row in cur.fetchall():
                print(f"     {row['content_type']}: {row['file_count']} files")


if __name__ == "__main__":
    deduplicate_database()
