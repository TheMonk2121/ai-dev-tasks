from __future__ import annotations
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any
import yaml
            from dspy_rag_system.src.utils.database_resilience import get_database_manager
import json
import sys
from pathlib import Path
        from utils.database_resilience import get_database_manager
            from dspy_rag_system.src.utils.database_resilience import get_database_manager
        import hashlib
    import argparse
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Backup System for Production Cutover
Snapshots document_chunks_* and active-pointer tables before cutover.
"""

class ProductionBackupSystem:
    """Production backup system for safe cutover operations."""

    def __init__(self, backup_dir: str = "backups/production_cutover"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_id = f"cutover_backup_{self.timestamp}"

        # Tables to backup
        self.critical_tables = [
            "documents",
            "document_chunks",
            "conversation_memory",
            "evaluation_results",
            "lessons_learned",
        ]

        # Active pointer tables (if they exist)
        self.pointer_tables = ["active_configuration", "active_model_versions", "active_evaluation_baseline"]

    def create_cutover_backup(self, description: str = "Production cutover backup") -> dict[str, Any]:
        """Create comprehensive backup before production cutover."""
        print("🔄 Creating Production Cutover Backup")
        print("=" * 50)

        backup_info = {
            "backup_id": self.backup_id,
            "timestamp": self.timestamp,
            "description": description,
            "created_by": os.getenv("USER", "unknown"),
            "hostname": os.getenv("HOSTNAME", "unknown"),
            "tables_backed_up": [],
            "backup_files": [],
            "metadata": {},
            "status": "in_progress",
        }

        try:
            # Backup critical tables
            for table in self.critical_tables:
                print(f"📊 Backing up table: {table}")
                backup_file = self._backup_table(table)
                if backup_file:
                    backup_info["tables_backed_up"].append(table)
                    backup_info["backup_files"].append(backup_file)

            # Backup active pointer tables
            for table in self.pointer_tables:
                print(f"📍 Backing up pointer table: {table}")
                backup_file = self._backup_table(table)
                if backup_file:
                    backup_info["tables_backed_up"].append(table)
                    backup_info["backup_files"].append(backup_file)

            # Create backup manifest
            manifest_file = self._create_backup_manifest(backup_info)
            backup_info["manifest_file"] = manifest_file

            # Create restore script
            restore_script = self._create_restore_script(backup_info)
            backup_info["restore_script"] = restore_script

            # Validate backup integrity
            validation_result = self._validate_backup_integrity(backup_info)
            backup_info["validation"] = validation_result

            backup_info["status"] = "completed" if validation_result["valid"] else "failed"

            print(f"✅ Backup completed: {backup_info['status']}")
            return backup_info

        except Exception as e:
            backup_info["status"] = "failed"
            backup_info["error"] = str(e)
            print(f"❌ Backup failed: {e}")
            return backup_info

    def _backup_table(self, table_name: str) -> str | None:
        """Backup a single table to file."""
        try:

            db_manager = get_database_manager()

            backup_file = self.backup_dir / f"{self.backup_id}_{table_name}.json"

            with db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get table schema
                    cur.execute(
                        """
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns 
                        WHERE table_name = %s 
                        ORDER BY ordinal_position
                    """,
                        (table_name,),
                    )
                    schema = cur.fetchall()

                    # Get table data
                    cur.execute(f"SELECT * FROM {table_name}")
                    rows = cur.fetchall()

                    # Get column names
                    column_names = [desc[0] for desc in cur.description]

                    # Create backup data structure
                    backup_data = {
                        "table_name": table_name,
                        "schema": [
                            {
                                "column_name": col[0],
                                "data_type": col[1],
                                "is_nullable": col[2],
                                "column_default": col[3],
                            }
                            for col in schema
                        ],
                        "column_names": column_names,
                        "row_count": len(rows),
                        "data": [dict(zip(column_names, row)) for row in rows],
                        "backup_timestamp": datetime.now().isoformat(),
                    }

                    # Save to file
                    with open(backup_file, "w") as f:
                        json.dump(backup_data, f, indent=2, default=str)

                    print(f"    ✅ Backed up {len(rows)} rows to {backup_file}")
                    return str(backup_file)

        except Exception as e:
            print(f"    ❌ Failed to backup {table_name}: {e}")
            return None

    def _create_backup_manifest(self, backup_info: dict[str, Any]) -> str:
        """Create backup manifest file."""
        manifest_file = self.backup_dir / f"{self.backup_id}_manifest.json"

        manifest = {
            "backup_info": backup_info,
            "system_info": {
                "python_version": sys.version,
                "platform": os.name,
                "working_directory": os.getcwd(),
                "environment_variables": self._get_relevant_env_vars(),
            },
            "database_info": self._get_database_info(),
            "file_sizes": self._get_backup_file_sizes(backup_info["backup_files"]),
            "checksums": self._calculate_checksums(backup_info["backup_files"]),
        }

        with open(manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)

        print(f"📋 Backup manifest created: {manifest_file}")
        return str(manifest_file)

    def _create_restore_script(self, backup_info: dict[str, Any]) -> str:
        """Create restore script for the backup."""
        restore_script = self.backup_dir / f"{self.backup_id}_restore.py"

        script_content = f'''#!/usr/bin/env python3
"""
Restore Script for Backup: {backup_info['backup_id']}
Created: {backup_info['timestamp']}
Description: {backup_info['description']}
"""

def restore_backup():
    """Restore backup from {backup_info['backup_id']}."""
    print("🔄 Restoring Production Backup: {backup_info['backup_id']}")
    print("="*50)
    
    backup_dir = Path("{self.backup_dir}")
    
    # Restore tables
    tables_to_restore = {json.dumps(backup_info['tables_backed_up'])}
    
    for table in tables_to_restore:
        backup_file = backup_dir / f"{backup_info['backup_id']}_{{table}}.json"
        if backup_file.exists():
            print(f"📊 Restoring table: {{table}}")
            restore_table(backup_file, table)
        else:
            print(f"❌ Backup file not found: {{backup_file}}")

def restore_table(backup_file: Path, table_name: str):
    """Restore a single table from backup file."""
    try:
        with open(backup_file, "r") as f:
            backup_data = json.load(f)
        
        # Import database utilities
# sys.path.insert(0, "src")  # DSPy modules now in main src directory
        
        db_manager = get_database_manager()
        
        with db_manager.get_connection() as conn:
            with conn.cursor() as cur:
                # Clear existing data
                cur.execute(f"TRUNCATE TABLE {{table_name}} CASCADE")
                
                # Restore data
                if backup_data["data"]:
                    column_names = backup_data["column_names"]
                    placeholders = ", ".join(["%s"] * len(column_names))
                    
                    insert_sql = f"INSERT INTO {{table_name}} ({{', '.join(column_names)}}) VALUES ({{placeholders}})"
                    
                    for row in backup_data["data"]:
                        values = [row.get(col) for col in column_names]
                        cur.execute(insert_sql, values)
                
                print(f"    ✅ Restored {{len(backup_data['data'])}} rows to {{table_name}}")
                
    except Exception as e:
        print(f"    ❌ Failed to restore {{table_name}}: {{e}}")

if __name__ == "__main__":
    restore_backup()
'''

        with open(restore_script, "w") as f:
            f.write(script_content)

        # Make script executable
        os.chmod(restore_script, 0o755)

        print(f"🔧 Restore script created: {restore_script}")
        return str(restore_script)

    def _validate_backup_integrity(self, backup_info: dict[str, Any]) -> dict[str, Any]:
        """Validate backup integrity."""
        validation_result = {"valid": True, "checks": {}, "errors": []}

        # Check if all backup files exist
        for backup_file in backup_info["backup_files"]:
            if not os.path.exists(backup_file):
                validation_result["valid"] = False
                validation_result["errors"].append(f"Backup file missing: {backup_file}")
            else:
                # Check file size
                file_size = os.path.getsize(backup_file)
                if file_size == 0:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Empty backup file: {backup_file}")
                else:
                    validation_result["checks"][backup_file] = {
                        "exists": True,
                        "size_bytes": file_size,
                        "size_mb": file_size / (1024 * 1024),
                    }

        # Validate JSON structure
        for backup_file in backup_info["backup_files"]:
            try:
                with open(backup_file) as f:
                    data = json.load(f)

                required_fields = ["table_name", "schema", "data", "backup_timestamp"]
                for field in required_fields:
                    if field not in data:
                        validation_result["valid"] = False
                        validation_result["errors"].append(f"Missing field '{field}' in {backup_file}")

            except json.JSONDecodeError as e:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Invalid JSON in {backup_file}: {e}")

        return validation_result

    def _get_relevant_env_vars(self) -> dict[str, str]:
        """Get relevant environment variables for backup context."""
        relevant_vars = [
            "DATABASE_URL",
            "DSPY_RAG_PATH",
            "EVAL_DRIVER",
            "RETR_TOPK_VEC",
            "RETR_TOPK_BM25",
            "RERANK_ENABLE",
            "AWS_REGION",
            "ENVIRONMENT",
        ]
        return {var: os.getenv(var, "not_set") for var in relevant_vars}

    def _get_database_info(self) -> dict[str, Any]:
        """Get database information for backup context."""
        try:

            db_manager = get_database_manager()

            with db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get database version
                    cur.execute("SELECT version()")
                    version = cur.fetchone()[0]

                    # Get table counts
                    table_counts = {}
                    for table in self.critical_tables:
                        try:
                            cur.execute(f"SELECT COUNT(*) FROM {table}")
                            count = cur.fetchone()[0]
                            table_counts[table] = count
                        except Exception:
                            table_counts[table] = "table_not_found"

                    return {"version": version, "table_counts": table_counts}
        except Exception as e:
            return {"error": str(e)}

    def _get_backup_file_sizes(self, backup_files: list[str]) -> dict[str, int]:
        """Get file sizes for all backup files."""
        file_sizes = {}
        for backup_file in backup_files:
            if os.path.exists(backup_file):
                file_sizes[backup_file] = os.path.getsize(backup_file)
        return file_sizes

    def _calculate_checksums(self, backup_files: list[str]) -> dict[str, str]:
        """Calculate checksums for all backup files."""

        checksums = {}
        for backup_file in backup_files:
            if os.path.exists(backup_file):
                with open(backup_file, "rb") as f:
                    content = f.read()
                    checksum = hashlib.sha256(content).hexdigest()
                    checksums[backup_file] = checksum
        return checksums

    def list_backups(self) -> list[dict[str, Any]]:
        """List all available backups."""
        backups = []

        for manifest_file in self.backup_dir.glob("*_manifest.json"):
            try:
                with open(manifest_file) as f:
                    manifest = json.load(f)
                    backups.append(
                        {
                            "backup_id": manifest["backup_info"]["backup_id"],
                            "timestamp": manifest["backup_info"]["timestamp"],
                            "description": manifest["backup_info"]["description"],
                            "status": manifest["backup_info"]["status"],
                            "tables_count": len(manifest["backup_info"]["tables_backed_up"]),
                            "manifest_file": str(manifest_file),
                        }
                    )
            except Exception as e:
                print(f"Warning: Could not read manifest {manifest_file}: {e}")

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x["timestamp"], reverse=True)
        return backups

    def restore_backup(self, backup_id: str, confirm: bool = False) -> bool:
        """Restore a specific backup."""
        if not confirm:
            print(f"⚠️ This will restore backup {backup_id} and may overwrite current data!")
            response = input("Type 'yes' to confirm: ")
            if response.lower() != "yes":
                print("Restore cancelled")
                return False

        # Find restore script
        restore_script = self.backup_dir / f"{backup_id}_restore.py"
        if not restore_script.exists():
            print(f"❌ Restore script not found: {restore_script}")
            return False

        # Execute restore script
        print(f"🔄 Executing restore script: {restore_script}")
        result = os.system(f"python3 {restore_script}")

        if result == 0:
            print("✅ Restore completed successfully")
            return True
        else:
            print("❌ Restore failed")
            return False

def main():
    """Main entry point for backup system."""

    parser = argparse.ArgumentParser(description="Production backup system")
    parser.add_argument("--action", choices=["create", "list", "restore"], required=True, help="Action to perform")
    parser.add_argument("--backup-dir", default="backups/production_cutover", help="Backup directory")
    parser.add_argument("--description", help="Backup description")
    parser.add_argument("--backup-id", help="Backup ID for restore")
    parser.add_argument("--confirm", action="store_true", help="Confirm restore without prompt")

    args = parser.parse_args()

    backup_system = ProductionBackupSystem(args.backup_dir)

    if args.action == "create":
        description = args.description or "Production cutover backup"
        result = backup_system.create_cutover_backup(description)

        if result["status"] == "completed":
            print(f"✅ Backup created successfully: {result['backup_id']}")
            sys.exit(0)
        else:
            print(f"❌ Backup failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)

    elif args.action == "list":
        backups = backup_system.list_backups()
        print("📋 Available Backups:")
        print("=" * 50)
        for backup in backups:
            status_emoji = "✅" if backup["status"] == "completed" else "❌"
            print(f"{status_emoji} {backup['backup_id']} - {backup['timestamp']}")
            print(f"   Description: {backup['description']}")
            print(f"   Tables: {backup['tables_count']}")
            print()

    elif args.action == "restore":
        if not args.backup_id:
            print("❌ --backup-id required for restore action")
            sys.exit(1)

        success = backup_system.restore_backup(args.backup_id, args.confirm)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
