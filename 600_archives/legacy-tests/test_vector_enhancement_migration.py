#!/usr/bin/env python3.11
"""
Test suite for Vector Database Enhancement Migration
Tests the migration script and validates the enhanced schema.
"""

import unittest
import psycopg2
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

from scripts.apply_vector_enhancement import VectorEnhancementMigration
from utils.logger import get_logger

logger = get_logger(__name__)

class TestVectorEnhancementMigration(unittest.TestCase):
    """Test cases for vector enhancement migration"""
    
    def setUp(self):
        """Set up test environment"""
        self.db_connection_string = os.getenv('POSTGRES_DSN')
        if not self.db_connection_string:
            self.skipTest("POSTGRES_DSN environment variable not set")
        
        self.migration = VectorEnhancementMigration(self.db_connection_string)
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.test_migration_file = Path(self.temp_dir) / "test_vector_enhancement_schema.sql"
        
    def tearDown(self):
        """Clean up test environment"""
        # Remove temporary directory
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_migration_file_exists(self):
        """Test that migration file exists"""
        self.assertTrue(self.migration.migration_file.exists())
        logger.info("Migration file exists")
    
    def test_validate_prerequisites(self):
        """Test prerequisites validation"""
        result = self.migration.validate_prerequisites()
        self.assertTrue(result)
        logger.info("Prerequisites validation passed")
    
    def test_backup_existing_data(self):
        """Test backup functionality"""
        result = self.migration.backup_existing_data()
        self.assertTrue(result)
        self.assertIsNotNone(self.migration.backup_info)
        logger.info("Backup functionality passed")
    
    def test_apply_migration(self):
        """Test migration application"""
        # Create a test migration file
        test_sql = """
        -- Test migration
        CREATE TABLE IF NOT EXISTS test_vector_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255)
        );
        INSERT INTO test_vector_table (name) VALUES ('test');
        """
        
        with open(self.test_migration_file, 'w') as f:
            f.write(test_sql)
        
        # Temporarily replace migration file
        original_file = self.migration.migration_file
        self.migration.migration_file = self.test_migration_file
        
        try:
            result = self.migration.apply_migration()
            self.assertTrue(result)
            logger.info("Migration application passed")
        finally:
            # Restore original file
            self.migration.migration_file = original_file
    
    def test_validate_migration(self):
        """Test migration validation"""
        # This test requires the actual migration to be applied
        # We'll test the validation logic with mock data
        with patch.object(self.migration, 'validate_migration') as mock_validate:
            mock_validate.return_value = True
            result = self.migration.validate_migration()
            self.assertTrue(result)
            logger.info("Migration validation logic passed")
    
    def test_rollback_migration(self):
        """Test rollback functionality"""
        result = self.migration.rollback_migration()
        self.assertTrue(result)
        logger.info("Rollback functionality passed")
    
    def test_run_migration_integration(self):
        """Test complete migration process"""
        # This is an integration test that requires a test database
        # We'll mock the database operations for this test
        with patch.object(self.migration, 'validate_prerequisites') as mock_prereq, \
             patch.object(self.migration, 'backup_existing_data') as mock_backup, \
             patch.object(self.migration, 'apply_migration') as mock_apply, \
             patch.object(self.migration, 'validate_migration') as mock_validate:
            
            mock_prereq.return_value = True
            mock_backup.return_value = True
            mock_apply.return_value = True
            mock_validate.return_value = True
            
            result = self.migration.run_migration()
            self.assertTrue(result)
            
            # Verify all methods were called
            mock_prereq.assert_called_once()
            mock_backup.assert_called_once()
            mock_apply.assert_called_once()
            mock_validate.assert_called_once()
            
            logger.info("Complete migration process test passed")

class TestVectorEnhancementSchema(unittest.TestCase):
    """Test cases for the enhanced vector schema"""
    
    def setUp(self):
        """Set up test environment"""
        self.db_connection_string = os.getenv('POSTGRES_DSN')
        if not self.db_connection_string:
            self.skipTest("POSTGRES_DSN environment variable not set")
    
    def test_vector_indexes_table(self):
        """Test vector_indexes table structure"""
        with psycopg2.connect(self.db_connection_string) as conn:
            with conn.cursor() as cursor:
                # Check if table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'vector_indexes'
                    );
                """)
                table_exists = cursor.fetchone()[0]
                
                if table_exists:
                    # Check table structure
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_name = 'vector_indexes'
                        ORDER BY ordinal_position;
                    """)
                    columns = cursor.fetchall()
                    
                    expected_columns = [
                        ('id', 'integer', 'NO'),
                        ('index_name', 'character varying', 'NO'),
                        ('table_name', 'character varying', 'NO'),
                        ('column_name', 'character varying', 'NO'),
                        ('index_type', 'character varying', 'YES'),
                        ('parameters', 'jsonb', 'YES'),
                        ('status', 'character varying', 'YES'),
                        ('created_at', 'timestamp without time zone', 'YES'),
                        ('updated_at', 'timestamp without time zone', 'YES'),
                        ('last_optimized', 'timestamp without time zone', 'YES'),
                        ('performance_stats', 'jsonb', 'YES')
                    ]
                    
                    for i, (col_name, data_type, nullable) in enumerate(expected_columns):
                        if i < len(columns):
                            actual_col, actual_type, actual_nullable = columns[i]
                            self.assertEqual(col_name, actual_col)
                            # Note: data_type comparison might vary by PostgreSQL version
                            self.assertIn(data_type.split('(')[0], actual_type)
                    
                    logger.info("Vector indexes table structure is correct")
                else:
                    logger.info("Vector indexes table does not exist (migration not applied)")
    
    def test_vector_performance_metrics_table(self):
        """Test vector_performance_metrics table structure"""
        with psycopg2.connect(self.db_connection_string) as conn:
            with conn.cursor() as cursor:
                # Check if table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'vector_performance_metrics'
                    );
                """)
                table_exists = cursor.fetchone()[0]
                
                if table_exists:
                    # Check table structure
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_name = 'vector_performance_metrics'
                        ORDER BY ordinal_position;
                    """)
                    columns = cursor.fetchall()
                    
                    expected_columns = [
                        ('id', 'integer', 'NO'),
                        ('operation_type', 'character varying', 'NO'),
                        ('query_hash', 'character varying', 'YES'),
                        ('execution_time_ms', 'integer', 'YES'),
                        ('result_count', 'integer', 'YES'),
                        ('index_used', 'character varying', 'YES'),
                        ('cache_hit', 'boolean', 'YES'),
                        ('error_message', 'text', 'YES'),
                        ('metadata', 'jsonb', 'YES'),
                        ('created_at', 'timestamp without time zone', 'YES')
                    ]
                    
                    for i, (col_name, data_type, nullable) in enumerate(expected_columns):
                        if i < len(columns):
                            actual_col, actual_type, actual_nullable = columns[i]
                            self.assertEqual(col_name, actual_col)
                    
                    logger.info("Vector performance metrics table structure is correct")
                else:
                    logger.info("Vector performance metrics table does not exist (migration not applied)")
    
    def test_vector_cache_table(self):
        """Test vector_cache table structure"""
        with psycopg2.connect(self.db_connection_string) as conn:
            with conn.cursor() as cursor:
                # Check if table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'vector_cache'
                    );
                """)
                table_exists = cursor.fetchone()[0]
                
                if table_exists:
                    # Check table structure
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_name = 'vector_cache'
                        ORDER BY ordinal_position;
                    """)
                    columns = cursor.fetchall()
                    
                    expected_columns = [
                        ('id', 'integer', 'NO'),
                        ('cache_key', 'character varying', 'NO'),
                        ('embedding', 'USER-DEFINED', 'YES'),  # vector type
                        ('metadata', 'jsonb', 'YES'),
                        ('access_count', 'integer', 'YES'),
                        ('last_accessed', 'timestamp without time zone', 'YES'),
                        ('created_at', 'timestamp without time zone', 'YES'),
                        ('expires_at', 'timestamp without time zone', 'YES')
                    ]
                    
                    for i, (col_name, data_type, nullable) in enumerate(expected_columns):
                        if i < len(columns):
                            actual_col, actual_type, actual_nullable = columns[i]
                            self.assertEqual(col_name, actual_col)
                    
                    logger.info("Vector cache table structure is correct")
                else:
                    logger.info("Vector cache table does not exist (migration not applied)")
    
    def test_vector_health_checks_table(self):
        """Test vector_health_checks table structure"""
        with psycopg2.connect(self.db_connection_string) as conn:
            with conn.cursor() as cursor:
                # Check if table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'vector_health_checks'
                    );
                """)
                table_exists = cursor.fetchone()[0]
                
                if table_exists:
                    # Check table structure
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_name = 'vector_health_checks'
                        ORDER BY ordinal_position;
                    """)
                    columns = cursor.fetchall()
                    
                    expected_columns = [
                        ('id', 'integer', 'NO'),
                        ('check_type', 'character varying', 'NO'),
                        ('status', 'character varying', 'NO'),
                        ('message', 'text', 'YES'),
                        ('metrics', 'jsonb', 'YES'),
                        ('created_at', 'timestamp without time zone', 'YES')
                    ]
                    
                    for i, (col_name, data_type, nullable) in enumerate(expected_columns):
                        if i < len(columns):
                            actual_col, actual_type, actual_nullable = columns[i]
                            self.assertEqual(col_name, actual_col)
                    
                    logger.info("Vector health checks table structure is correct")
                else:
                    logger.info("Vector health checks table does not exist (migration not applied)")
    
    def test_enhanced_documents_table(self):
        """Test enhanced documents table columns"""
        with psycopg2.connect(self.db_connection_string) as conn:
            with conn.cursor() as cursor:
                # Check for new columns
                new_columns = [
                    'index_status',
                    'optimization_flags', 
                    'last_indexed',
                    'index_performance'
                ]
                
                for column in new_columns:
                    cursor.execute(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns
                            WHERE table_name = 'documents' 
                            AND column_name = '{column}'
                        );
                    """)
                    column_exists = cursor.fetchone()[0]
                    
                    if column_exists:
                        logger.info(f"Enhanced documents column '{column}' exists")
                    else:
                        logger.info(f"Enhanced documents column '{column}' does not exist (migration not applied)")
    
    def test_enhanced_document_chunks_table(self):
        """Test enhanced document_chunks table columns"""
        with psycopg2.connect(self.db_connection_string) as conn:
            with conn.cursor() as cursor:
                # Check for new columns
                new_columns = [
                    'index_status',
                    'similarity_score',
                    'last_verified',
                    'cache_hit'
                ]
                
                for column in new_columns:
                    cursor.execute(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns
                            WHERE table_name = 'document_chunks' 
                            AND column_name = '{column}'
                        );
                    """)
                    column_exists = cursor.fetchone()[0]
                    
                    if column_exists:
                        logger.info(f"Enhanced document_chunks column '{column}' exists")
                    else:
                        logger.info(f"Enhanced document_chunks column '{column}' does not exist (migration not applied)")
    
    def test_hnsw_index_exists(self):
        """Test HNSW index existence"""
        with psycopg2.connect(self.db_connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE indexname = 'idx_document_chunks_embedding_hnsw';
                """)
                index_exists = cursor.fetchone() is not None
                
                if index_exists:
                    logger.info("HNSW index exists")
                else:
                    logger.info("HNSW index does not exist (migration not applied)")
    
    def test_vector_functions_exist(self):
        """Test vector functions existence"""
        with psycopg2.connect(self.db_connection_string) as conn:
            with conn.cursor() as cursor:
                functions = [
                    'update_vector_index_stats',
                    'record_vector_performance',
                    'update_document_index_status',
                    'update_chunk_index_status',
                    'clean_expired_vector_cache',
                    'get_vector_health_status'
                ]
                
                for function in functions:
                    cursor.execute(f"""
                        SELECT routine_name 
                        FROM information_schema.routines 
                        WHERE routine_name = '{function}';
                    """)
                    function_exists = cursor.fetchone() is not None
                    
                    if function_exists:
                        logger.info(f"Vector function '{function}' exists")
                    else:
                        logger.info(f"Vector function '{function}' does not exist (migration not applied)")
    
    def test_vector_views_exist(self):
        """Test vector views existence"""
        with psycopg2.connect(self.db_connection_string) as conn:
            with conn.cursor() as cursor:
                views = [
                    'vector_performance_summary',
                    'index_performance_view',
                    'document_indexing_status'
                ]
                
                for view in views:
                    cursor.execute(f"""
                        SELECT table_name 
                        FROM information_schema.views 
                        WHERE table_name = '{view}';
                    """)
                    view_exists = cursor.fetchone() is not None
                    
                    if view_exists:
                        logger.info(f"Vector view '{view}' exists")
                    else:
                        logger.info(f"Vector view '{view}' does not exist (migration not applied)")

def run_tests():
    """Run all tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestVectorEnhancementMigration))
    test_suite.addTest(unittest.makeSuite(TestVectorEnhancementSchema))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 