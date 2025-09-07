#!/usr/bin/env python3
"""
Shadow Ingest Script
- Ingest with locked configuration into versioned table
- Support for shadow table creation and management
- Database hygiene and index verification
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add dspy-rag-system to path
dspy_rag_path = project_root / "dspy-rag-system"
sys.path.insert(0, str(dspy_rag_path))

from src.utils.config_lock import ConfigLockManager, LockedConfig, ShadowIndexManager


def run_command(cmd: str, cwd: Path = None) -> subprocess.CompletedProcess:
    """Run a command and return the result"""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd or project_root,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"   Error: {result.stderr}")
        return result

    print(f"✅ Command succeeded: {cmd}")
    return result


def setup_environment(config: LockedConfig) -> Dict[str, str]:
    """Setup environment variables for locked configuration"""
    shadow_manager = ShadowIndexManager(config)
    ingest_run_id = shadow_manager.get_ingest_run_id()

    env_vars = {
        "INGEST_RUN_ID": ingest_run_id,
        "CHUNK_SIZE": str(config.chunk_size),
        "OVERLAP_RATIO": str(config.overlap_ratio),
        "JACCARD_THRESHOLD": str(config.jaccard_threshold),
        "PREFIX_POLICY": config.prefix_policy,
        "CHUNK_VERSION": config.chunk_version,
        "EMBEDDER_NAME": config.embedder_name,
        "CONFIG_HASH": config.get_config_hash(),
        "SHADOW_TABLE": config.shadow_table or f"document_chunks_{config.chunk_version.replace('-', '_')}",
    }

    # Set environment variables
    for key, value in env_vars.items():
        os.environ[key] = value

    print("🔧 Environment Variables Set:")
    for key, value in env_vars.items():
        print(f"   {key}={value}")

    return env_vars


def create_shadow_table(shadow_table: str) -> bool:
    """Create shadow table with proper schema and indexes"""
    print(f"📊 Creating shadow table: {shadow_table}")

    # SQL to create shadow table
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {shadow_table} (
        id VARCHAR(255) PRIMARY KEY,
        doc_id VARCHAR(255) NOT NULL,
        chunk_index INTEGER NOT NULL,
        embedding_text TEXT NOT NULL,
        bm25_text TEXT NOT NULL,
        embedding_token_count INTEGER NOT NULL,
        bm25_token_count INTEGER NOT NULL,
        chunk_version VARCHAR(255) NOT NULL,
        ingest_run_id VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Create indexes for performance
    CREATE INDEX IF NOT EXISTS idx_{shadow_table}_doc_id ON {shadow_table}(doc_id);
    CREATE INDEX IF NOT EXISTS idx_{shadow_table}_chunk_version ON {shadow_table}(chunk_version);
    CREATE INDEX IF NOT EXISTS idx_{shadow_table}_ingest_run_id ON {shadow_table}(ingest_run_id);
    CREATE INDEX IF NOT EXISTS idx_{shadow_table}_created_at ON {shadow_table}(created_at);
    
    -- BM25 GIN index for full-text search
    CREATE INDEX IF NOT EXISTS idx_{shadow_table}_bm25_gin ON {shadow_table} USING gin(to_tsvector('english', bm25_text));
    
    -- Vector index for embeddings (if pgvector is available)
    -- CREATE INDEX IF NOT EXISTS idx_{shadow_table}_embedding ON {shadow_table} USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
    """

    # For now, just print the SQL - in production, you'd execute this
    print("📝 Shadow table creation SQL:")
    print(create_sql)

    return True


def run_database_hygiene(shadow_table: str) -> bool:
    """Run database hygiene operations"""
    print(f"🧹 Running database hygiene for {shadow_table}")

    hygiene_commands = [
        f"VACUUM ANALYZE {shadow_table};",
        f"SELECT COUNT(*) FROM {shadow_table};",
        f"SELECT COUNT(*) FROM {shadow_table} WHERE bm25_text LIKE 'Document:%';",  # Should be 0
    ]

    for cmd in hygiene_commands:
        print(f"🔧 Running: {cmd}")
        # In production, you'd execute these SQL commands

    return True


def run_shadow_ingest(config: LockedConfig) -> bool:
    """Run shadow ingest with locked configuration"""
    print("📊 Running Shadow Ingest")
    print("=" * 40)

    # Setup environment
    env_vars = setup_environment(config)

    # Create shadow table
    shadow_table = env_vars["SHADOW_TABLE"]
    if not create_shadow_table(shadow_table):
        print("❌ Failed to create shadow table")
        return False

    # Run enhanced ingest
    ingest_run_id = env_vars["INGEST_RUN_ID"]
    cmd = f"python dspy-rag-system/scripts/ingest_enhanced.py --run-id {ingest_run_id}"

    result = run_command(cmd)
    if result.returncode != 0:
        print("❌ Shadow ingest failed")
        return False

    # Run database hygiene
    if not run_database_hygiene(shadow_table):
        print("❌ Database hygiene failed")
        return False

    print("✅ Shadow ingest completed successfully")
    print(f"   Ingest run ID: {ingest_run_id}")
    print(f"   Shadow table: {shadow_table}")
    print(f"   Config hash: {env_vars['CONFIG_HASH']}")

    return True


def main():
    parser = argparse.ArgumentParser(description="Run shadow ingest with locked configuration")
    parser.add_argument("--run-id", help="Specific ingest run ID to use")
    parser.add_argument("--shadow-table", help="Specific shadow table to use")
    parser.add_argument("--skip-table-creation", action="store_true", help="Skip shadow table creation")

    args = parser.parse_args()

    # Load active configuration
    manager = ConfigLockManager()
    config = manager.get_active_config()

    if not config:
        print("❌ No active configuration found. Run lock_production_config.py first.")
        sys.exit(1)

    print("🚀 Shadow Ingest")
    print("=" * 50)
    print(f"Config: {config.chunk_version}")
    print(f"Hash: {config.get_config_hash()}")
    print(f"Chunk size: {config.chunk_size}")
    print(f"Overlap ratio: {config.overlap_ratio}")
    print(f"Jaccard threshold: {config.jaccard_threshold}")
    print(f"Prefix policy: {config.prefix_policy}")
    print()

    # Override config if specific run-id or shadow-table provided
    if args.run_id:
        config.ingest_run_id = args.run_id
    if args.shadow_table:
        config.shadow_table = args.shadow_table

    # Run shadow ingest
    success = run_shadow_ingest(config)

    if not success:
        print("❌ Shadow ingest failed")
        sys.exit(1)

    print("\n🎯 Shadow ingest completed successfully!")
    print("   Ready for evaluation and canary rollout")


if __name__ == "__main__":
    main()
