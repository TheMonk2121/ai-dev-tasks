#!/usr/bin/env python3
"""
Test Database Resilience Module

Comprehensive unit tests for database connection pooling, retry logic,
health checks, and graceful degradation.
"""

import unittest
import os
import sys
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.database_resilience import (
    DatabaseResilienceManager,
    DatabaseHealth,
    ConnectionStats,
    get_database_manager,
    initialize_database_resilience,
    execute_query,
    execute_transaction,
    get_database_health,
    is_database_healthy
)

class TestDatabaseHealth(unittest.TestCase):
    """Test DatabaseHealth dataclass"""
    
    def test_database_health_creation(self):
        """Test creating DatabaseHealth instance"""
        timestamp = datetime.now()
        health = DatabaseHealth(
            timestamp=timestamp,
            status="healthy",
            response_time=0.5,
            active_connections=5,
            max_connections=10,
            error_message=None,
            metadata={"test": "value"}
        )
        
        self.assertEqual(health.timestamp, timestamp)
        self.assertEqual(health.status, "healthy")
        self.assertEqual(health.response_time, 0.5)
        self.assertEqual(health.active_connections, 5)
        self.assertEqual(health.max_connections, 10)
        self.assertIsNone(health.error_message)
        self.assertEqual(health.metadata, {"test": "value"})

class TestConnectionStats(unittest.TestCase):
    """Test ConnectionStats dataclass"""
    
    def test_connection_stats_creation(self):
        """Test creating ConnectionStats instance"""
        timestamp = datetime.now()
        stats = ConnectionStats(
            total_connections=10,
            active_connections=5,
            idle_connections=5,
            max_connections=20,
            connection_timeout=30.0,
            last_health_check=timestamp
        )
        
        self.assertEqual(stats.total_connections, 10)
        self.assertEqual(stats.active_connections, 5)
        self.assertEqual(stats.idle_connections, 5)
        self.assertEqual(stats.max_connections, 20)
        self.assertEqual(stats.connection_timeout, 30.0)
        self.assertEqual(stats.last_health_check, timestamp)

class TestDatabaseResilienceManager(unittest.TestCase):
    """Test DatabaseResilienceManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.connection_string = "postgresql://test:test@localhost:5432/test"
        self.manager = None
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.manager:
            self.manager.shutdown()
    
    @patch('utils.database_resilience.ThreadedConnectionPool')
    @patch('utils.database_resilience.get_logger')
    def test_initialization(self, mock_logger, mock_pool_class):
        """Test manager initialization"""
        mock_pool = Mock()
        mock_pool_class.return_value = mock_pool
        
        # Mock successful connection test
        with patch.object(DatabaseResilienceManager, '_test_connection', return_value=True):
            self.manager = DatabaseResilienceManager(self.connection_string)
        
        self.assertIsNotNone(self.manager.pool)
        self.assertEqual(self.manager.connection_string, self.connection_string)
        self.assertEqual(self.manager.min_connections, 1)
        self.assertEqual(self.manager.max_connections, 10)
        self.assertEqual(self.manager.connection_timeout, 30)
        self.assertEqual(self.manager.health_check_interval, 60)
        self.assertTrue(self.manager.monitoring_active)
    
    @patch('utils.database_resilience.ThreadedConnectionPool')
    def test_initialization_failure(self, mock_pool_class):
        """Test manager initialization failure"""
        mock_pool_class.side_effect = Exception("Connection failed")
        
        with self.assertRaises(Exception):
            self.manager = DatabaseResilienceManager(self.connection_string)
    
    @patch('utils.database_resilience.ThreadedConnectionPool')
    def test_get_connection(self, mock_pool_class):
        """Test getting connection from pool"""
        mock_pool = Mock()
        mock_conn = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_pool_class.return_value = mock_pool
        
        with patch.object(DatabaseResilienceManager, '_test_connection', return_value=True):
            self.manager = DatabaseResilienceManager(self.connection_string)
        
        with self.manager.get_connection() as conn:
            self.assertEqual(conn, mock_conn)
            mock_conn.ping.assert_called_once()
        
        mock_pool.putconn.assert_called_once_with(mock_conn)
    
    @patch('utils.database_resilience.ThreadedConnectionPool')
    def test_get_connection_failure(self, mock_pool_class):
        """Test getting connection failure"""
        mock_pool = Mock()
        mock_pool.getconn.return_value = None
        mock_pool_class.return_value = mock_pool
        
        with patch.object(DatabaseResilienceManager, '_test_connection', return_value=True):
            self.manager = DatabaseResilienceManager(self.connection_string)
        
        with self.assertRaises(Exception):
            with self.manager.get_connection():
                pass
    
    @patch('utils.database_resilience.ThreadedConnectionPool')
    def test_execute_query(self, mock_pool_class):
        """Test executing query with retry logic"""
        mock_pool = Mock()
        mock_conn = Mock()
        mock_cursor = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [{"id": 1, "name": "test"}]
        mock_pool_class.return_value = mock_pool
        
        with patch.object(DatabaseResilienceManager, '_test_connection', return_value=True):
            self.manager = DatabaseResilienceManager(self.connection_string)
        
        # Mock retry decorator
        with patch('utils.database_resilience.retry') as mock_retry:
            mock_retry.return_value = lambda func: func
            result = self.manager.execute_query("SELECT * FROM test")
        
        self.assertEqual(result, [{"id": 1, "name": "test"}])
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test", None)
    
    @patch('utils.database_resilience.ThreadedConnectionPool')
    def test_execute_transaction(self, mock_pool_class):
        """Test executing transaction with retry logic"""
        mock_pool = Mock()
        mock_conn = Mock()
        mock_cursor = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [{"id": 1}]
        mock_pool_class.return_value = mock_pool
        
        with patch.object(DatabaseResilienceManager, '_test_connection', return_value=True):
            self.manager = DatabaseResilienceManager(self.connection_string)
        
        # Mock retry decorator
        with patch('utils.database_resilience.retry') as mock_retry:
            mock_retry.return_value = lambda func: func
            queries = [("SELECT * FROM test", None), ("INSERT INTO test VALUES (1)", None)]
            result = self.manager.execute_transaction(queries)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(mock_cursor.execute.call_count, 2)
        mock_conn.commit.assert_called_once()
    
    @patch('utils.database_resilience.ThreadedConnectionPool')
    def test_health_monitoring(self, mock_pool_class):
        """Test health monitoring functionality"""
        mock_pool = Mock()
        mock_pool_class.return_value = mock_pool
        
        with patch.object(DatabaseResilienceManager, '_test_connection', return_value=True):
            self.manager = DatabaseResilienceManager(self.connection_string)
        
        # Test health status
        health = self.manager.get_health_status()
        self.assertIn("status", health)
        self.assertIn("last_check", health)
        self.assertIn("response_time", health)
        self.assertIn("connection_stats", health)
    
    @patch('utils.database_resilience.ThreadedConnectionPool')
    def test_connection_stats(self, mock_pool_class):
        """Test connection statistics"""
        mock_pool = Mock()
        mock_pool._pool = [Mock()] * 5  # 5 total connections
        mock_pool._used = 2  # 2 active connections
        mock_pool_class.return_value = mock_pool
        
        with patch.object(DatabaseResilienceManager, '_test_connection', return_value=True):
            self.manager = DatabaseResilienceManager(self.connection_string)
        
        self.manager._update_connection_stats()
        
        self.assertEqual(self.manager.connection_stats.total_connections, 5)
        self.assertEqual(self.manager.connection_stats.active_connections, 2)
        self.assertEqual(self.manager.connection_stats.idle_connections, 3)
    
    @patch('utils.database_resilience.ThreadedConnectionPool')
    def test_is_healthy(self, mock_pool_class):
        """Test health status checking"""
        mock_pool = Mock()
        mock_pool_class.return_value = mock_pool
        
        with patch.object(DatabaseResilienceManager, '_test_connection', return_value=True):
            self.manager = DatabaseResilienceManager(self.connection_string)
        
        # Initially should be healthy
        self.assertTrue(self.manager.is_healthy())
        
        # Add unhealthy record
        self.manager._record_health_check("unhealthy", 0.0, "Test error")
        self.assertFalse(self.manager.is_healthy())
        
        # Add healthy record
        self.manager._record_health_check("healthy", 0.1)
        self.assertTrue(self.manager.is_healthy())
    
    @patch('utils.database_resilience.ThreadedConnectionPool')
    def test_shutdown(self, mock_pool_class):
        """Test graceful shutdown"""
        mock_pool = Mock()
        mock_pool_class.return_value = mock_pool
        
        with patch.object(DatabaseResilienceManager, '_test_connection', return_value=True):
            self.manager = DatabaseResilienceManager(self.connection_string)
        
        self.assertTrue(self.manager.monitoring_active)
        
        self.manager.shutdown()
        
        self.assertFalse(self.manager.monitoring_active)
        mock_pool.closeall.assert_called_once()

class TestDatabaseResilienceFunctions(unittest.TestCase):
    """Test convenience functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Clear global instance
        import utils.database_resilience as db_resilience
        db_resilience._database_manager = None
    
    @patch('utils.database_resilience.DatabaseResilienceManager')
    def test_get_database_manager(self, mock_manager_class):
        """Test getting database manager instance"""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        manager = get_database_manager()
        
        self.assertEqual(manager, mock_manager)
        mock_manager_class.assert_called_once()
    
    @patch('utils.database_resilience.DatabaseResilienceManager')
    def test_initialize_database_resilience(self, mock_manager_class):
        """Test initializing database resilience"""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        manager = initialize_database_resilience("test_connection_string")
        
        self.assertEqual(manager, mock_manager)
        mock_manager_class.assert_called_once_with("test_connection_string")
    
    @patch('utils.database_resilience.get_database_manager')
    def test_execute_query_function(self, mock_get_manager):
        """Test execute_query convenience function"""
        mock_manager = Mock()
        mock_manager.execute_query.return_value = [{"result": "test"}]
        mock_get_manager.return_value = mock_manager
        
        result = execute_query("SELECT * FROM test")
        
        self.assertEqual(result, [{"result": "test"}])
        mock_manager.execute_query.assert_called_once_with("SELECT * FROM test", None)
    
    @patch('utils.database_resilience.get_database_manager')
    def test_execute_transaction_function(self, mock_get_manager):
        """Test execute_transaction convenience function"""
        mock_manager = Mock()
        mock_manager.execute_transaction.return_value = [{"result": "test"}]
        mock_get_manager.return_value = mock_manager
        
        queries = [("SELECT * FROM test", None)]
        result = execute_transaction(queries)
        
        self.assertEqual(result, [{"result": "test"}])
        mock_manager.execute_transaction.assert_called_once_with(queries)
    
    @patch('utils.database_resilience.get_database_manager')
    def test_get_database_health_function(self, mock_get_manager):
        """Test get_database_health convenience function"""
        mock_manager = Mock()
        mock_manager.get_health_status.return_value = {"status": "healthy"}
        mock_get_manager.return_value = mock_manager
        
        health = get_database_health()
        
        self.assertEqual(health, {"status": "healthy"})
        mock_manager.get_health_status.assert_called_once()
    
    @patch('utils.database_resilience.get_database_manager')
    def test_is_database_healthy_function(self, mock_get_manager):
        """Test is_database_healthy convenience function"""
        mock_manager = Mock()
        mock_manager.is_healthy.return_value = True
        mock_get_manager.return_value = mock_manager
        
        is_healthy = is_database_healthy()
        
        self.assertTrue(is_healthy)
        mock_manager.is_healthy.assert_called_once()

class TestDatabaseResilienceIntegration(unittest.TestCase):
    """Integration tests for database resilience"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.connection_string = "postgresql://test:test@localhost:5432/test"
    
    @patch('utils.database_resilience.ThreadedConnectionPool')
    def test_full_workflow(self, mock_pool_class):
        """Test complete database resilience workflow"""
        mock_pool = Mock()
        mock_conn = Mock()
        mock_cursor = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]  # For connection test
        mock_cursor.fetchall.return_value = [{"id": 1, "name": "test"}]
        mock_pool_class.return_value = mock_pool
        
        # Initialize manager
        with patch.object(DatabaseResilienceManager, '_test_connection', return_value=True):
            manager = DatabaseResilienceManager(self.connection_string)
        
        # Test connection
        with manager.get_connection() as conn:
            self.assertEqual(conn, mock_conn)
        
        # Test query execution
        with patch('utils.database_resilience.retry') as mock_retry:
            mock_retry.return_value = lambda func: func
            result = manager.execute_query("SELECT * FROM test")
            self.assertEqual(result, [{"id": 1, "name": "test"}])
        
        # Test health status
        health = manager.get_health_status()
        self.assertIn("status", health)
        
        # Test shutdown
        manager.shutdown()
        self.assertFalse(manager.monitoring_active)

if __name__ == '__main__':
    unittest.main() 