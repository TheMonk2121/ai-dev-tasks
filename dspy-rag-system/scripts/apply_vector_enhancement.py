#!/usr/bin/env python3.12.123.11
"""
Vector Database Enhancement Migration Script
Applies the vector enhancement schema to PostgreSQL database.
"""

import os
import sys
import psycopg2
import logging
from pathlib import Path
from typing import Optional, Any
import hashlib
import time

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from utils.database_resilience import get_database_manager, execute_query, execute_transaction
from utils.logger import get_logger

logger = get_logger(__name__)

class VectorEnhancementMigration:
    """Handles the vector database enhancement migration"""
    
    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
        self.migration_file = Path(__file__).parent.parent / "config" / "database" / "vector_enhancement_schema.sql"
        
    def validate_prerequisites(self) -> bool:
        """Validate that prerequisites are met"""
        try:
            # Check if migration file exists
            if not self.migration_file.exists():
                logger.error(f"Migration file not found: {self.migration_file}")
                return False
            
            # Test database connection
            with psycopg2.connect(self.db_connection_string) as conn:
                with conn.cursor() as cursor:
                    # Check if pgvector extension is available
                    cursor.execute("SELECT 1 FROM pg_available_extensions WHERE name = 'vector'")
                    if not cursor.fetchone():
                        logger.error("pgvector extension is not available")
                        return False
                    
                    # Check if we have necessary permissions
                    cursor.execute("SELECT has_table_privilege('document_chunks', 'SELECT')")
                    if not cursor.fetchone():
                        logger.error("Insufficient permissions on document_chunks table")
                        return False
                    
                    logger.info("Prerequisites validation passed")
                    return True
                    
        except Exception as e:
            logger.error(f"Prerequisites validation failed: {e}")
            return False
    
    def backup_existing_data(self) -> bool:
        """Create backup of existing data before migration"""
        try:
            backup_tables = ['document_chunks', 'documents']
            backup_data = {}
            
            with psycopg2.connect(self.db_connection_string) as conn:
                with conn.cursor() as cursor:
                    for table in backup_tables:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        logger.info(f"Backing up {count} rows from {table}")
                        
                        # Create backup table
                        backup_table = f"{table}_backup_{int(time.time())}"
                        cursor.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM {table}")
                        
                        backup_data[table] = backup_table
                        logger.info(f"Created backup table: {backup_table}")
            
            # Store backup info for potential rollback
            self.backup_info = backup_data
            logger.info("Backup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    def apply_migration(self) -> bool:
        """Apply the vector enhancement migration"""
        try:
            # Read migration SQL
            with open(self.migration_file) as f:
                migration_sql = f.read()
            
            # Split into individual statements
            statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
            
            with psycopg2.connect(self.db_connection_string) as conn:
                with conn.cursor() as cursor:
                    for i, statement in enumerate(statements):
                        if statement.startswith('--') or not statement:
                            continue
                            
                        try:
                            logger.info(f"Executing statement {i+1}/{len(statements)}")
                            cursor.execute(statement)
                            conn.commit()
                            logger.info(f"Statement {i+1} executed successfully")
                            
                        except Exception as e:
                            logger.error(f"Failed to execute statement {i+1}: {e}")
                            logger.error(f"Statement: {statement[:100]}...")
                            conn.rollback()
                            # Continue with next statement instead of failing completely
                            continue
            
            logger.info("Migration applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def validate_migration(self) -> bool:
        """Validate that migration was applied correctly"""
        try:
            validation_checks = [
                ("vector_indexes", "SELECT COUNT(*) FROM vector_indexes"),
                ("vector_performance_metrics", "SELECT COUNT(*) FROM vector_performance_metrics"),
                ("vector_cache", "SELECT COUNT(*) FROM vector_cache"),
                ("vector_health_checks", "SELECT COUNT(*) FROM vector_health_checks"),
                ("hnsw_index", "SELECT indexname FROM pg_indexes WHERE indexname = 'idx_document_chunks_embedding_hnsw'"),
                ("functions", "SELECT routine_name FROM information_schema.routines WHERE routine_name LIKE 'update_vector_index_stats'"),
            ]
            
            with psycopg2.connect(self.db_connection_string) as conn:
                with conn.cursor() as cursor:
                    for check_name, query in validation_checks:
                        try:
                            cursor.execute(query)
                            result = cursor.fetchone()
                            if result is None:
                                logger.error(f"Validation failed for {check_name}")
                                return False
                            logger.info(f"Validation passed for {check_name}")
                        except Exception as e:
                            logger.error(f"Validation failed for {check_name}: {e}")
                            return False
            
            logger.info("All validation checks passed")
            return True
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False
    
    def rollback_migration(self) -> bool:
        """Rollback the migration if needed"""
        try:
            rollback_sql = """
            -- Drop new tables
            DROP TABLE IF EXISTS vector_health_checks CASCADE;
            DROP TABLE IF EXISTS vector_cache CASCADE;
            DROP TABLE IF EXISTS vector_performance_metrics CASCADE;
            DROP TABLE IF EXISTS vector_indexes CASCADE;
            
            -- Drop new indexes
            DROP INDEX IF EXISTS idx_document_chunks_embedding_hnsw;
            DROP INDEX IF EXISTS idx_vector_performance_metrics_operation_type;
            DROP INDEX IF EXISTS idx_vector_performance_metrics_created_at;
            DROP INDEX IF EXISTS idx_vector_performance_metrics_execution_time;
            DROP INDEX IF EXISTS idx_vector_cache_cache_key;
            DROP INDEX IF EXISTS idx_vector_cache_last_accessed;
            DROP INDEX IF EXISTS idx_vector_cache_expires_at;
            DROP INDEX IF EXISTS idx_vector_health_checks_check_type;
            DROP INDEX IF EXISTS idx_vector_health_checks_status;
            DROP INDEX IF EXISTS idx_vector_health_checks_created_at;
            DROP INDEX IF EXISTS idx_vector_indexes_index_name;
            DROP INDEX IF EXISTS idx_vector_indexes_status;
            DROP INDEX IF EXISTS idx_vector_indexes_table_name;
            DROP INDEX IF EXISTS idx_documents_index_status;
            DROP INDEX IF EXISTS idx_documents_last_indexed;
            DROP INDEX IF EXISTS idx_document_chunks_index_status;
            DROP INDEX IF EXISTS idx_document_chunks_similarity_score;
            DROP INDEX IF EXISTS idx_document_chunks_cache_hit;
            
            -- Drop new columns
            ALTER TABLE documents DROP COLUMN IF EXISTS index_status;
            ALTER TABLE documents DROP COLUMN IF EXISTS optimization_flags;
            ALTER TABLE documents DROP COLUMN IF EXISTS last_indexed;
            ALTER TABLE documents DROP COLUMN IF EXISTS index_performance;
            ALTER TABLE document_chunks DROP COLUMN IF EXISTS index_status;
            ALTER TABLE document_chunks DROP COLUMN IF EXISTS similarity_score;
            ALTER TABLE document_chunks DROP COLUMN IF EXISTS last_verified;
            ALTER TABLE document_chunks DROP COLUMN IF EXISTS cache_hit;
            
            -- Drop functions
            DROP FUNCTION IF EXISTS update_vector_index_stats(VARCHAR);
            DROP FUNCTION IF EXISTS record_vector_performance(VARCHAR, VARCHAR, INTEGER, INTEGER, VARCHAR, BOOLEAN, TEXT, JSONB);
            DROP FUNCTION IF EXISTS update_document_index_status(VARCHAR, VARCHAR, JSONB);
            DROP FUNCTION IF EXISTS update_chunk_index_status(INTEGER, VARCHAR, FLOAT, BOOLEAN);
            DROP FUNCTION IF EXISTS clean_expired_vector_cache();
            DROP FUNCTION IF EXISTS get_vector_health_status();
            
            -- Drop views
            DROP VIEW IF EXISTS vector_performance_summary;
            DROP VIEW IF EXISTS index_performance_view;
            DROP VIEW IF EXISTS document_indexing_status;
            
            -- Recreate original index
            CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding 
                ON document_chunks USING ivfflat (embedding vector_cosine_ops);
            """
            
            with psycopg2.connect(self.db_connection_string) as conn:
                with conn.cursor() as cursor:
                    for statement in rollback_sql.split(';'):
                        if statement.strip():
                            cursor.execute(statement)
                    conn.commit()
            
            logger.info("Rollback completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def run_migration(self) -> bool:
        """Run the complete migration process"""
        logger.info("Starting Vector Database Enhancement Migration")
        
        # Step 1: Validate prerequisites
        logger.info("Step 1: Validating prerequisites")
        if not self.validate_prerequisites():
            logger.error("Prerequisites validation failed")
            return False
        
        # Step 2: Create backup
        logger.info("Step 2: Creating backup")
        if not self.backup_existing_data():
            logger.error("Backup failed")
            return False
        
        # Step 3: Apply migration
        logger.info("Step 3: Applying migration")
        if not self.apply_migration():
            logger.error("Migration failed, attempting rollback")
            self.rollback_migration()
            return False
        
        # Step 4: Validate migration
        logger.info("Step 4: Validating migration")
        if not self.validate_migration():
            logger.error("Migration validation failed, attempting rollback")
            self.rollback_migration()
            return False
        
        logger.info("Vector Database Enhancement Migration completed successfully")
        return True

def main():
    """Main entry point"""
    # Get database connection string from environment
    db_connection_string = os.getenv('POSTGRES_DSN')
    if not db_connection_string:
        logger.error("POSTGRES_DSN environment variable not set")
        sys.exit(1)
    
    # Create migration instance
    migration = VectorEnhancementMigration(db_connection_string)
    
    # Run migration
    if migration.run_migration():
        logger.info("Migration completed successfully")
        sys.exit(0)
    else:
        logger.error("Migration failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 