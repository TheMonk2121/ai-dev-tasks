#!/usr/bin/env python3.12.123.11
"""
Database Maintenance Script
Detect outdated database entries and maintain consistency with repository files.
"""
import json
import os
import sys

import psycopg2

DB_DSN = "postgresql://danieljacobs@localhost:5432/ai_agency"


def get_file_size(file_path):
    """Get the size of a file in bytes."""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def check_database_consistency():
    """Check database consistency with repository files."""
    print("🔍 Checking database consistency...")
    print("=" * 50)

    # Core files to check
    core_files = [
        ("../100_memory/100_cursor-memory-context.md", "100_cursor-memory-context.md"),
        ("../000_core/000_backlog.md", "000_backlog.md"),
        ("../400_guides/400_ai-constitution.md", "400_ai-constitution.md"),
        ("../400_guides/400_code-criticality-guide.md", "400_code-criticality-guide.md"),
        ("../400_guides/400_comprehensive-coding-best-practices.md", "400_comprehensive-coding-best-practices.md"),
        ("../400_guides/400_context-priority-guide.md", "400_context-priority-guide.md"),
        ("../400_guides/400_file-analysis-guide.md", "400_file-analysis-guide.md"),
        ("../400_guides/400_project-overview.md", "400_project-overview.md"),
        ("../400_guides/400_system-overview.md", "400_system-overview.md"),
        ("../400_guides/400_testing-strategy-guide.md", "400_testing-strategy-guide.md"),
        ("tests/README-dev.md", "README-dev.md"),
    ]

    # CONTEXT_INDEX files to check
    context_index_files = [
        ("../400_guides/400_deployment-environment-guide.md", "400_deployment-environment-guide.md"),
        ("../400_guides/400_integration-patterns-guide.md", "400_integration-patterns-guide.md"),
        ("../400_guides/400_migration-upgrade-guide.md", "400_migration-upgrade-guide.md"),
        ("../400_guides/400_performance-optimization-guide.md", "400_performance-optimization-guide.md"),
        ("../400_guides/400_security-best-practices-guide.md", "400_security-best-practices-guide.md"),
        ("../400_guides/400_few-shot-context-examples.md", "400_few-shot-context-examples.md"),
        ("../500_research/500_research-index.md", "500_research-index.md"),
    ]

    all_files = core_files + context_index_files

    try:
        conn = psycopg2.connect(DB_DSN)
        cursor = conn.cursor()

        outdated_files = []
        missing_files = []
        current_files = []

        for file_path, filename in all_files:
            repo_size = get_file_size(file_path)

            if repo_size == 0:
                print(f"❌ File not found: {file_path}")
                continue

            # Check database
            cursor.execute("SELECT file_size, updated_at FROM documents WHERE filename = %s", (filename,))
            result = cursor.fetchone()

            if not result:
                missing_files.append((file_path, filename, repo_size))
                print(f"❌ Missing from database: {filename}")
            else:
                db_size, updated_at = result
                if repo_size != db_size:
                    outdated_files.append((file_path, filename, db_size, repo_size, updated_at))
                    print(f"🔄 Outdated: {filename} ({db_size} → {repo_size} bytes)")
                else:
                    current_files.append((filename, repo_size))
                    print(f"✅ Current: {filename} ({repo_size} bytes)")

        # Database statistics
        cursor.execute(
            """
            SELECT COUNT(*) as total_documents, SUM(chunk_count) as total_chunks
            FROM documents
        """
        )
        db_stats = cursor.fetchone()

        # Cross-reference analysis
        cursor.execute(
            """
            SELECT d.filename, COUNT(dc.id) as chunks_with_refs, d.chunk_count
            FROM documents d
            LEFT JOIN document_chunks dc ON d.id::text = dc.document_id AND dc.content LIKE '%400_%'
            WHERE d.filename LIKE '400_%'
            GROUP BY d.filename, d.chunk_count
            ORDER BY d.filename
        """
        )
        cross_ref_stats = cursor.fetchall()

        cursor.close()
        conn.close()

        # Print summary
        print("=" * 50)
        print("📊 Database Consistency Summary:")

        # Handle potential None values from database query
        if db_stats is not None:
            print(f"  Total Documents: {db_stats[0] or 0}")
            print(f"  Total Chunks: {db_stats[1] or 0}")
        else:
            print("  Total Documents: 0")
            print("  Total Chunks: 0")

        print(f"  Current Files: {len(current_files)}")
        print(f"  Outdated Files: {len(outdated_files)}")
        print(f"  Missing Files: {len(missing_files)}")

        if outdated_files:
            print("\n🔄 Outdated Files:")
            for file_path, filename, db_size, repo_size, updated_at in outdated_files:
                print(f"  - {filename}: {db_size} → {repo_size} bytes (updated: {updated_at})")

        if missing_files:
            print("\n❌ Missing Files:")
            for file_path, filename, repo_size in missing_files:
                print(f"  - {filename}: {repo_size} bytes")

        print("\n🔗 Cross-Reference Analysis:")
        total_coverage = 0
        total_files = 0
        for filename, chunks_with_refs, total_chunks in cross_ref_stats:
            coverage = (chunks_with_refs / total_chunks * 100) if total_chunks > 0 else 0
            total_coverage += coverage
            total_files += 1
            print(f"  - {filename}: {chunks_with_refs}/{total_chunks} chunks ({coverage:.1f}%)")

        if total_files > 0:
            avg_coverage = total_coverage / total_files
            print(f"  Average Coverage: {avg_coverage:.1f}%")

        return {
            "outdated_files": outdated_files,
            "missing_files": missing_files,
            "current_files": current_files,
            "db_stats": db_stats or (0, 0),  # Provide default values if None
            "cross_ref_stats": cross_ref_stats,
        }

    except Exception as e:
        print(f"❌ Error checking database consistency: {e}")
        return None


def update_outdated_files(outdated_files):
    """Update outdated files in the database."""
    if not outdated_files:
        print("✅ No outdated files to update")
        return True

    print(f"\n🔄 Updating {len(outdated_files)} outdated files...")

    try:
        conn = psycopg2.connect(DB_DSN)
        cursor = conn.cursor()

        success_count = 0

        for file_path, filename, db_size, repo_size, updated_at in outdated_files:
            try:
                # Read current file
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                current_size = len(content)

                # Get document ID
                cursor.execute("SELECT id FROM documents WHERE filename = %s", (filename,))
                result = cursor.fetchone()
                if result is None:
                    print(f"❌ Document not found in database: {filename}")
                    continue
                document_id = result[0]

                # Delete existing chunks
                cursor.execute("DELETE FROM document_chunks WHERE document_id = %s::text", (document_id,))

                # Update document
                cursor.execute(
                    """
                    UPDATE documents
                    SET file_size = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """,
                    (current_size, document_id),
                )

                # Re-chunk content
                chunk_size = 500
                chunks = []
                for i in range(0, len(content), chunk_size):
                    chunk_content = content[i : i + chunk_size]
                    chunks.append(
                        {
                            "content": chunk_content,
                            "chunk_index": len(chunks),
                            "start_offset": i,
                            "end_offset": min(i + chunk_size, len(content)),
                            "metadata": json.dumps(
                                {"filename": filename, "chunk_index": len(chunks), "file_size": current_size}
                            ),
                        }
                    )

                # Insert new chunks
                for chunk in chunks:
                    cursor.execute(
                        """
                        INSERT INTO document_chunks
                        (document_id, content, chunk_index, start_offset, end_offset, metadata, created_at, updated_at)
                        VALUES (%s::text, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """,
                        (
                            document_id,
                            chunk["content"],
                            chunk["chunk_index"],
                            chunk["start_offset"],
                            chunk["end_offset"],
                            chunk["metadata"],
                        ),
                    )

                # Update chunk count
                cursor.execute(
                    """
                    UPDATE documents
                    SET chunk_count = %s
                    WHERE id = %s
                """,
                    (len(chunks), document_id),
                )

                print(f"✅ Updated {filename} ({db_size} → {current_size} bytes, {len(chunks)} chunks)")
                success_count += 1

            except Exception as e:
                print(f"❌ Error updating {filename}: {e}")
                continue

        conn.commit()
        cursor.close()
        conn.close()

        print(f"✅ Successfully updated {success_count}/{len(outdated_files)} files")
        return success_count == len(outdated_files)

    except Exception as e:
        print(f"❌ Error in update process: {e}")
        return False


def main():
    """Main database maintenance function."""
    print("🗄️ Database Maintenance Script")
    print("=" * 50)

    # Check consistency
    consistency_data = check_database_consistency()

    if not consistency_data:
        print("❌ Failed to check database consistency")
        return False

    outdated_files = consistency_data["outdated_files"]
    missing_files = consistency_data["missing_files"]

    # Update outdated files if any
    if outdated_files:
        print(f"\n🔄 Found {len(outdated_files)} outdated files")
        update_choice = input("Update outdated files? (y/N): ").strip().lower()

        if update_choice == "y":
            success = update_outdated_files(outdated_files)
            if success:
                print("✅ Database maintenance completed successfully")
            else:
                print("❌ Some updates failed")
        else:
            print("⏭️ Skipping updates")
    else:
        print("✅ No outdated files found")

    # Report on missing files
    if missing_files:
        print(f"\n⚠️ Found {len(missing_files)} files missing from database:")
        for file_path, filename, repo_size in missing_files:
            print(f"  - {filename}: {repo_size} bytes")
        print("Use add_missing_files_to_database.py to add these files")

    print("\n📊 Final Database Status:")
    print(f"  Documents: {consistency_data['db_stats'][0]}")
    print(f"  Chunks: {consistency_data['db_stats'][1]}")
    print(f"  Current: {len(consistency_data['current_files'])}")
    print(f"  Outdated: {len(outdated_files)}")
    print(f"  Missing: {len(missing_files)}")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
