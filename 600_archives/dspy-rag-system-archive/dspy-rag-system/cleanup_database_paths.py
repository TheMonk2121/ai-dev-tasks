#!/usr/bin/env python3
# ANCHOR_KEY: cleanup-database-paths
# ANCHOR_PRIORITY: 25
# ROLE_PINS: ["implementer", "coder"]
"""
Database Path Cleanup Script
---------------------------
Clean up path names in the database by removing duplicate filenames and standardizing formats.

This script fixes the issue where documents are stored with paths like:
- ../000_core/000_backlog.md/000_backlog.md (duplicate filename)
- ./000_core/001_create-prd.md/001_create-prd.md (duplicate filename)

And standardizes them to:
- 000_core/000_backlog.md
- 000_core/001_create-prd.md
"""

import sys
from typing import Any

# Add src to path
sys.path.append("src")

try:
    from utils.database_resilience import get_database_manager
    from utils.logger import setup_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the dspy-rag-system directory")
    sys.exit(1)

# Setup logging
logger = setup_logger("path_cleanup")


def analyze_path_issues() -> dict[str, Any]:
    """Analyze current path issues in the database"""
    try:
        db = get_database_manager()

        # Get all documents
        result = db.execute_query(
            """
            SELECT id, file_path, filename
            FROM documents
            ORDER BY file_path
        """
        )

        issues = []
        for row in result:
            file_path = row["file_path"]
            filename = row["filename"]

            # Check for inconsistent path formats (./ or ../ prefixes)
            if file_path.startswith("./") or file_path.startswith("../"):
                issues.append(
                    {
                        "id": row["id"],
                        "current_path": file_path,
                        "filename": filename,
                        "issue_type": "inconsistent_format",
                    }
                )

            # Check for duplicate filename in path
            if filename in file_path and file_path.count(filename) > 1:
                issues.append(
                    {
                        "id": row["id"],
                        "current_path": file_path,
                        "filename": filename,
                        "issue_type": "duplicate_filename",
                    }
                )

        # Get total count
        total_result = db.execute_query("SELECT COUNT(*) as count FROM documents")
        total_documents = total_result[0]["count"]

        return {"total_documents": total_documents, "documents_with_issues": len(issues), "issues": issues}

    except Exception as e:
        logger.error(f"Error analyzing path issues: {e}")
        return {"total_documents": 0, "documents_with_issues": 0, "issues": [], "error": str(e)}


def clean_path(file_path: str, filename: str) -> str:
    """Clean a file path by removing duplicate filenames and standardizing format"""
    # Remove the duplicate filename from the path
    if filename in file_path:
        # Split by filename and take the first part
        parts = file_path.split(filename)
        if len(parts) > 1:
            # Remove trailing slash if present
            clean_path = parts[0].rstrip("/")
            # Add filename back
            clean_path = f"{clean_path}/{filename}"
            return clean_path

    return file_path


def fix_path_format(file_path: str) -> str:
    """Standardize path format by removing ./ and ../ prefixes"""
    # Remove ./ prefix
    if file_path.startswith("./"):
        file_path = file_path[2:]

    # Remove ../ prefix
    if file_path.startswith("../"):
        file_path = file_path[3:]

    return file_path


def cleanup_database_paths(dry_run: bool = True) -> dict[str, Any]:
    """Clean up path names in the database"""
    try:
        db = get_database_manager()

        # Analyze current issues
        analysis = analyze_path_issues()

        if analysis.get("error"):
            return {"success": False, "error": analysis["error"]}

        print("\n📊 Path Cleanup Analysis:")
        print(f"   • Total Documents: {analysis['total_documents']}")
        print(f"   • Documents with Issues: {analysis['documents_with_issues']}")

        if analysis["documents_with_issues"] == 0:
            print("   ✅ No path issues found!")
            return {"success": True, "message": "No issues to fix"}

        print(f"\n🔧 {'DRY RUN - ' if dry_run else ''}Fixing path issues...")

        updates = []
        for issue in analysis["issues"]:
            current_path = issue["current_path"]
            filename = issue["filename"]

            # Clean the path
            cleaned_path = clean_path(current_path, filename)
            cleaned_path = fix_path_format(cleaned_path)

            if cleaned_path != current_path:
                updates.append(
                    {"id": issue["id"], "old_path": current_path, "new_path": cleaned_path, "filename": filename}
                )

        print(f"   • Paths to update: {len(updates)}")

        if dry_run:
            print("\n📋 DRY RUN - Paths that would be updated:")
            for i, update in enumerate(updates[:10], 1):
                print(f"   {i:2d}. {update['old_path']}")
                print(f"       → {update['new_path']}")

            if len(updates) > 10:
                print(f"       ... and {len(updates) - 10} more")

            return {"success": True, "dry_run": True, "updates_count": len(updates), "updates": updates}

        # Perform actual updates
        updated_count = 0
        for update in updates:
            try:
                db.execute_query(
                    "UPDATE documents SET file_path = %s WHERE id = %s", (update["new_path"], update["id"])
                )
                updated_count += 1
                logger.info(f"Updated document {update['id']}: {update['old_path']} → {update['new_path']}")
            except Exception as e:
                logger.error(f"Failed to update document {update['id']}: {e}")

        print(f"\n✅ Successfully updated {updated_count} document paths")

        return {"success": True, "dry_run": False, "updates_count": updated_count, "updates": updates}

    except Exception as e:
        logger.error(f"Error cleaning up database paths: {e}")
        return {"success": False, "error": str(e)}


def verify_cleanup() -> dict[str, Any]:
    """Verify that the cleanup was successful"""
    try:
        db = get_database_manager()

        # Check for remaining issues
        result = db.execute_query(
            """
            SELECT COUNT(*) as count
            FROM documents
            WHERE file_path LIKE '%/%/%'
        """
        )

        remaining_issues = result[0]["count"]

        # Get sample of cleaned paths
        sample_result = db.execute_query(
            """
            SELECT file_path, filename
            FROM documents
            WHERE file_path LIKE '%000_core%' OR file_path LIKE '%100_memory%' OR file_path LIKE '%400_guides%'
            ORDER BY file_path
            LIMIT 10
        """
        )

        sample_paths = [f"{row['file_path']}/{row['filename']}" for row in sample_result]

        return {"success": True, "remaining_issues": remaining_issues, "sample_paths": sample_paths}

    except Exception as e:
        logger.error(f"Error verifying cleanup: {e}")
        return {"success": False, "error": str(e)}


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Clean up database path names")
    parser.add_argument(
        "--dry-run", action="store_true", default=True, help="Show what would be changed without making changes"
    )
    parser.add_argument("--execute", action="store_true", help="Actually execute the cleanup (overrides --dry-run)")
    parser.add_argument("--verify", action="store_true", help="Verify cleanup results")

    args = parser.parse_args()

    # Determine if this is a dry run
    is_dry_run = not args.execute

    print("🧹 Database Path Cleanup Tool")
    print("=" * 50)

    if args.verify:
        print("\n🔍 Verifying cleanup results...")
        verification = verify_cleanup()

        if verification["success"]:
            print(f"   • Remaining issues: {verification['remaining_issues']}")
            if verification["remaining_issues"] == 0:
                print("   ✅ All path issues resolved!")
            else:
                print("   ⚠️  Some issues remain")

            print("\n📋 Sample cleaned paths:")
            for i, path in enumerate(verification["sample_paths"], 1):
                print(f"   {i:2d}. {path}")
        else:
            print(f"   ❌ Verification failed: {verification['error']}")

        return

    # Perform cleanup
    result = cleanup_database_paths(dry_run=is_dry_run)

    if result["success"]:
        if result.get("dry_run"):
            print("\n💡 To execute the cleanup, run: python3 cleanup_database_paths.py --execute")
        else:
            print("\n✅ Cleanup completed successfully!")

            # Verify the cleanup
            print("\n🔍 Verifying cleanup...")
            verification = verify_cleanup()
            if verification["success"]:
                print(f"   • Remaining issues: {verification['remaining_issues']}")
                if verification["remaining_issues"] == 0:
                    print("   ✅ All path issues resolved!")
                else:
                    print("   ⚠️  Some issues remain")
    else:
        print(f"\n❌ Cleanup failed: {result['error']}")


if __name__ == "__main__":
    main()
