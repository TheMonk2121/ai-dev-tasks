#!/usr/bin/env python3.12.123.11
"""
Database Synchronization Checker
Check if files with DATABASE_SYNC tags are current in the database.
"""
import os
import re
import sys
from pathlib import Path

# Add dspy-rag-system/scripts to path for imports
dspy_scripts_path = Path(__file__).parent.parent / "dspy-rag-system" / "scripts"
sys.path.insert(0, str(dspy_scripts_path))

# Import database utilities with error handling
try:
    from database_utils import execute_single_query, get_db_connection  # type: ignore
except ImportError as e:
    print(f"Error: Could not import database_utils from {dspy_scripts_path}")
    print(f"Import error: {e}")
    print("Make sure dspy-rag-system is properly set up and database_utils.py exists")
    sys.exit(1)


def find_files_with_sync_tags() -> list[tuple[str, str]]:
    """
    Find all files with DATABASE_SYNC tags.

    Implements deduplication strategy: prioritize files in core directories
    over watch_folder duplicates to establish single source of truth.

    Returns:
        List of (file_path, sync_type) tuples
    """
    sync_files = []
    filename_to_path = {}  # Track best path for each filename

    # Search for files with DATABASE_SYNC tags
    for root, dirs, files in os.walk("."):
        # Skip git and other directories
        if any(skip in root for skip in [".git", "__pycache__", "venv", "node_modules"]):
            continue

        for file in files:
            if file.endswith((".md", ".txt", ".py")):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()

                    # Check for DATABASE_SYNC tags
                    if "DATABASE_SYNC:" in content:
                        # Extract sync type
                        match = re.search(r"DATABASE_SYNC:\s*(\w+)", content)
                        sync_type = match.group(1) if match else "REQUIRED"

                        # Deduplication logic: prioritize core directories over watch_folder
                        if file not in filename_to_path:
                            filename_to_path[file] = (file_path, sync_type)
                        else:
                            # If we already have this file, check if current path is better
                            existing_path, existing_sync = filename_to_path[file]

                            # Priority order: core directories > watch_folder
                            if "watch_folder" in existing_path and "watch_folder" not in file_path:
                                # Current path is better (not in watch_folder)
                                filename_to_path[file] = (file_path, sync_type)
                            elif "watch_folder" in file_path and "watch_folder" not in existing_path:
                                # Keep existing path (it's better)
                                pass
                            else:
                                # Both in same category, keep the first one found
                                pass

                except Exception as e:
                    print(f"Warning: Could not read {file_path}: {e}")

    # Convert to list format
    sync_files = list(filename_to_path.values())
    return sync_files


def check_database_sync_status(sync_files: list[tuple[str, str]]) -> dict[str, dict]:
    """
    Check synchronization status of files with database.

    Args:
        sync_files: List of (file_path, sync_type) tuples

    Returns:
        Dictionary with sync status for each file
    """
    sync_status = {}

    for file_path, sync_type in sync_files:
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        try:
            # Check if file exists in database
            query = "SELECT file_size, updated_at FROM documents WHERE filename = %s"
            result = execute_single_query(query, (filename,), context="operational")

            if result:
                db_size, db_updated = result
                is_current = file_size == db_size

                sync_status[file_path] = {
                    "filename": filename,
                    "sync_type": sync_type,
                    "file_size": file_size,
                    "db_size": db_size,
                    "is_current": is_current,
                    "needs_update": not is_current,
                    "db_updated": db_updated,
                    "exists_in_db": True,
                }
            else:
                sync_status[file_path] = {
                    "filename": filename,
                    "sync_type": sync_type,
                    "file_size": file_size,
                    "db_size": None,
                    "is_current": False,
                    "needs_update": True,
                    "db_updated": None,
                    "exists_in_db": False,
                }

        except Exception as e:
            sync_status[file_path] = {
                "filename": filename,
                "sync_type": sync_type,
                "file_size": file_size,
                "error": str(e),
                "needs_update": True,
            }

    return sync_status


def update_database_file(file_path: str, status: dict) -> bool:
    """
    Update a file in the database.

    Args:
        file_path: Path to the file
        status: Status dictionary from check_database_sync_status

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Use os.path.getsize for accurate file size in bytes
        import os

        file_size = os.path.getsize(file_path)
        filename = status["filename"]

        with get_db_connection() as conn:
            cursor = conn.cursor()

            if status["exists_in_db"]:
                # Update existing file
                cursor.execute("SELECT id FROM documents WHERE filename = %s", (filename,))
                document_id = cursor.fetchone()[0]

                # Delete existing chunks
                cursor.execute("DELETE FROM document_chunks WHERE document_id = %s::text", (document_id,))

                # Update document
                cursor.execute(
                    """
                    UPDATE documents
                    SET file_size = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """,
                    (file_size, document_id),
                )

            else:
                # Insert new file
                cursor.execute(
                    """
                    INSERT INTO documents (filename, file_size, file_path, file_type, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    RETURNING id
                """,
                    (filename, file_size, file_path, "markdown"),
                )
                document_id = cursor.fetchone()[0]

            # Re-chunk content
            chunk_size = 500
            chunks = []
            for i in range(0, len(content), chunk_size):
                chunk_content = content[i : i + chunk_size]
                chunks.append(
                    {
                        "content": chunk_content,
                        "chunk_index": len(chunks),
                        "line_start": i,
                        "line_end": min(i + chunk_size, len(content)),
                        "metadata": (
                            f'{{"filename": "{filename}", '
                            f'"chunk_index": {len(chunks)}, '
                            f'"file_size": {file_size}}}'
                        ),
                    }
                )

            # Insert chunks
            for chunk in chunks:
                cursor.execute(
                    """
                    INSERT INTO document_chunks
                    (document_id, content, chunk_index, line_start, line_end, metadata, created_at, updated_at)
                    VALUES (%s::text, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                    (
                        document_id,
                        chunk["content"],
                        chunk["chunk_index"],
                        chunk["line_start"],
                        chunk["line_end"],
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

            conn.commit()
            return True

    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False


def main():
    """Main function for database synchronization check."""
    print("🔍 Database Synchronization Check")
    print("=" * 50)

    # Find files with sync tags
    sync_files = find_files_with_sync_tags()

    if not sync_files:
        print("OK No files with DATABASE_SYNC tags found")
        return True

    print(f"📋 Found {len(sync_files)} files with DATABASE_SYNC tags:")
    for file_path, sync_type in sync_files:
        print(f"  - {file_path} ({sync_type})")

    # Check sync status
    sync_status = check_database_sync_status(sync_files)

    # Report status
    needs_update = []
    current_files = []

    for file_path, status in sync_status.items():
        if status.get("needs_update", False):
            needs_update.append((file_path, status))
        else:
            current_files.append((file_path, status))

    print("\n📊 Synchronization Status:")
    print(f"  Current: {len(current_files)} files")
    print(f"  Need Update: {len(needs_update)} files")

    if current_files:
        print("\nOK Current Files:")
        for file_path, status in current_files:
            print(f"  - {status['filename']} ({status['file_size']} bytes)")

    if needs_update:
        print("\n🔄 Files Needing Update:")
        for file_path, status in needs_update:
            if status.get("exists_in_db"):
                print(f"  - {status['filename']}: {status['db_size']} → {status['file_size']} bytes")
            else:
                print(f"  - {status['filename']}: Not in database ({status['file_size']} bytes)")

        # Ask for update permission
        if len(sys.argv) > 1 and sys.argv[1] == "--auto-update":
            print(f"\n🔄 Auto-updating {len(needs_update)} files...")
            success_count = 0

            for file_path, status in needs_update:
                if update_database_file(file_path, status):
                    print(f"  OK Updated {status['filename']}")
                    success_count += 1
                else:
                    print(f"  X Failed to update {status['filename']}")

            print(f"\n📊 Update Results: {success_count}/{len(needs_update)} successful")
            return success_count == len(needs_update)
        else:
            print("\n!️  Run with --auto-update to update these files")
            return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
