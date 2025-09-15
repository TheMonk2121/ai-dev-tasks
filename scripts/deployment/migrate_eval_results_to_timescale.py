#!/usr/bin/env python3
"""
Migrate evaluation results to TimescaleDB hypertables for better time-series performance.
"""

import json
import os
import sys
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    """Get database connection using the same DSN resolution as the project."""
    # Add src to path for common module
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from src.common.db_dsn import resolve_dsn

    dsn = resolve_dsn()
    return psycopg2.connect(dsn)


def migrate_memory_performance_metrics(conn):
    """Convert memory_performance_metrics to TimescaleDB hypertable."""
    print("🔄 Migrating memory_performance_metrics to TimescaleDB...")

    with conn.cursor() as cur:
        # First, ensure the table has proper time column and update primary key
        print("  📅 Ensuring proper time column and updating primary key...")
        cur.execute(
            """
            ALTER TABLE memory_performance_metrics 
            ALTER COLUMN created_at SET NOT NULL;
        """
        )

        # Drop existing primary key and create new composite one
        cur.execute(
            """
            ALTER TABLE memory_performance_metrics 
            DROP CONSTRAINT memory_performance_metrics_pkey;
        """
        )

        cur.execute(
            """
            ALTER TABLE memory_performance_metrics 
            ADD CONSTRAINT memory_performance_metrics_pkey 
            PRIMARY KEY (metric_id, created_at);
        """
        )

        # Convert to hypertable with data migration
        print("  🚀 Creating hypertable (migrating data)...")
        cur.execute(
            """
            SELECT create_hypertable(
                'memory_performance_metrics', 
                'created_at',
                chunk_time_interval => INTERVAL '1 day',
                migrate_data => TRUE,
                if_not_exists => TRUE
            );
        """
        )

        # Enable columnstore and add compression policy
        print("  🗜️  Enabling columnstore and setting up compression policy...")
        cur.execute(
            """
            ALTER TABLE memory_performance_metrics SET (
                timescaledb.compress,
                timescaledb.compress_segmentby = 'metric_id, operation_type',
                timescaledb.compress_orderby = 'created_at DESC'
            );
        """
        )

        cur.execute(
            """
            SELECT add_compression_policy(
                'memory_performance_metrics', 
                INTERVAL '7 days',
                if_not_exists => TRUE
            );
        """
        )

        # Add retention policy (keep data for 90 days)
        print("  🗑️  Setting up retention policy...")
        cur.execute(
            """
            SELECT add_retention_policy(
                'memory_performance_metrics', 
                INTERVAL '90 days',
                if_not_exists => TRUE
            );
        """
        )

        conn.commit()
        print("  ✅ memory_performance_metrics migrated successfully!")


def migrate_mission_metrics(conn):
    """Convert mission_metrics to TimescaleDB hypertable."""
    print("🔄 Migrating mission_metrics to TimescaleDB...")

    with conn.cursor() as cur:
        # First, ensure the table has proper time column and update primary key
        print("  📅 Ensuring proper time column and updating primary key...")
        cur.execute(
            """
            ALTER TABLE mission_metrics 
            ALTER COLUMN timestamp SET NOT NULL;
        """
        )

        # Drop existing primary key and create new composite one
        cur.execute(
            """
            ALTER TABLE mission_metrics 
            DROP CONSTRAINT mission_metrics_pkey;
        """
        )

        cur.execute(
            """
            ALTER TABLE mission_metrics 
            ADD CONSTRAINT mission_metrics_pkey 
            PRIMARY KEY (id, timestamp);
        """
        )

        # Convert to hypertable with data migration
        print("  🚀 Creating hypertable (migrating data)...")
        cur.execute(
            """
            SELECT create_hypertable(
                'mission_metrics', 
                'timestamp',
                chunk_time_interval => INTERVAL '1 day',
                migrate_data => TRUE,
                if_not_exists => TRUE
            );
        """
        )

        # Enable columnstore and add compression policy
        print("  🗜️  Enabling columnstore and setting up compression policy...")
        cur.execute(
            """
            ALTER TABLE mission_metrics SET (
                timescaledb.compress,
                timescaledb.compress_segmentby = 'id',
                timescaledb.compress_orderby = 'timestamp DESC'
            );
        """
        )

        cur.execute(
            """
            SELECT add_compression_policy(
                'mission_metrics', 
                INTERVAL '7 days',
                if_not_exists => TRUE
            );
        """
        )

        # Add retention policy (keep data for 180 days)
        print("  🗑️  Setting up retention policy...")
        cur.execute(
            """
            SELECT add_retention_policy(
                'mission_metrics', 
                INTERVAL '180 days',
                if_not_exists => TRUE
            );
        """
        )

        conn.commit()
        print("  ✅ mission_metrics migrated successfully!")


def create_evaluation_hypertables(conn):
    """Create new hypertables for evaluation results."""
    print("🔄 Creating new evaluation hypertables...")

    with conn.cursor() as cur:
        # Create evaluation_runs hypertable
        print("  📊 Creating evaluation_runs hypertable...")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS evaluation_runs (
                run_id SERIAL,
                run_name VARCHAR(255) NOT NULL,
                profile VARCHAR(50) NOT NULL,
                model VARCHAR(100),
                dataset_hash VARCHAR(64),
                status VARCHAR(50) NOT NULL,
                precision_score DECIMAL(5,4),
                recall_score DECIMAL(5,4),
                f1_score DECIMAL(5,4),
                faithfulness_score DECIMAL(5,4),
                total_questions INTEGER,
                correct_answers INTEGER,
                execution_time_ms INTEGER,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                PRIMARY KEY (run_id, created_at)
            );
        """
        )

        # Convert to hypertable
        cur.execute(
            """
            SELECT create_hypertable(
                'evaluation_runs', 
                'created_at',
                chunk_time_interval => INTERVAL '1 day',
                if_not_exists => TRUE
            );
        """
        )

        # Create evaluation_questions hypertable
        print("  ❓ Creating evaluation_questions hypertable...")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS evaluation_questions (
                question_id SERIAL,
                run_id INTEGER,
                question_text TEXT NOT NULL,
                expected_answer TEXT,
                retrieved_chunks TEXT[],
                generated_answer TEXT,
                is_correct BOOLEAN,
                confidence_score DECIMAL(5,4),
                retrieval_time_ms INTEGER,
                generation_time_ms INTEGER,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                PRIMARY KEY (question_id, created_at)
            );
        """
        )

        # Convert to hypertable
        cur.execute(
            """
            SELECT create_hypertable(
                'evaluation_questions', 
                'created_at',
                chunk_time_interval => INTERVAL '1 day',
                if_not_exists => TRUE
            );
        """
        )

        # Create indexes
        print("  🔍 Creating indexes...")
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_evaluation_runs_profile 
            ON evaluation_runs (profile);
        """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_evaluation_runs_status 
            ON evaluation_runs (status);
        """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_evaluation_questions_run_id 
            ON evaluation_questions (run_id);
        """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_evaluation_questions_is_correct 
            ON evaluation_questions (is_correct);
        """
        )

        conn.commit()
        print("  ✅ New evaluation hypertables created successfully!")


def verify_migration(conn):
    """Verify the migration was successful."""
    print("🔍 Verifying migration...")

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Check hypertables
        cur.execute(
            """
            SELECT hypertable_name, num_dimensions, num_chunks
            FROM timescaledb_information.hypertables
            WHERE hypertable_schema = 'public'
            ORDER BY hypertable_name;
        """
        )

        hypertables = cur.fetchall()
        print("  📊 Hypertables created:")
        for ht in hypertables:
            print(f"    - {ht['hypertable_name']}: {ht['num_chunks']} chunks, {ht['num_dimensions']} dimensions")

        # Check compression policies
        cur.execute(
            """
            SELECT hypertable_name, config
            FROM timescaledb_information.jobs
            WHERE proc_name = 'policy_compression'
            AND hypertable_schema = 'public';
        """
        )

        compression_policies = cur.fetchall()
        print("  🗜️  Compression policies:")
        for cp in compression_policies:
            print(f"    - {cp['hypertable_name']}: {cp['config']}")

        # Check retention policies
        cur.execute(
            """
            SELECT hypertable_name, schedule_interval
            FROM timescaledb_information.jobs
            WHERE proc_name = 'policy_retention'
            AND hypertable_schema = 'public';
        """
        )

        retention_policies = cur.fetchall()
        print("  🗑️  Retention policies:")
        for rp in retention_policies:
            print(f"    - {rp['hypertable_name']}: {rp['schedule_interval']}")


def main():
    """Main migration function."""
    print("🚀 Starting evaluation results migration to TimescaleDB...")
    print("=" * 60)

    try:
        conn = get_db_connection()
        print("✅ Connected to database")

        # Migrate existing tables
        migrate_memory_performance_metrics(conn)
        migrate_mission_metrics(conn)

        # Create new evaluation hypertables
        create_evaluation_hypertables(conn)

        # Verify migration
        verify_migration(conn)

        print("=" * 60)
        print("🎉 Migration completed successfully!")
        print("\n📈 Benefits of TimescaleDB:")
        print("  • Automatic time-based partitioning")
        print("  • Compression for older data")
        print("  • Retention policies for data cleanup")
        print("  • Optimized time-series queries")
        print("  • Continuous aggregates for analytics")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)
    finally:
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    main()
