#!/usr/bin/env python3
"""
Tests for Production Monitoring System

Tests the production monitoring, health checks, and security event tracking.
"""

import os
import sys
import json
import time
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add src to path for imports
sys.path.append('src')

from monitoring.production_monitor import (
    ProductionMonitor, SecurityEvent, HealthCheck, SystemMetrics,
    get_production_monitor, initialize_production_monitoring
)
from monitoring.health_endpoints import (
    HealthEndpointManager, DependencyStatus,
    get_health_manager, initialize_health_endpoints
)

class TestProductionMonitor(unittest.TestCase):
    """Test production monitoring functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.monitor = ProductionMonitor(
            service_name="test-service",
            service_version="0.1.0",
            environment="test"
        )
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self.monitor, 'shutdown'):
            self.monitor.shutdown()
    
    def test_production_monitor_initialization(self):
        """Test production monitor initialization"""
        self.assertIsNotNone(self.monitor)
        self.assertEqual(self.monitor.service_name, "test-service")
        self.assertEqual(self.monitor.service_version, "0.1.0")
        self.assertEqual(self.monitor.environment, "test")
        self.assertFalse(self.monitor.monitoring_active)
    
    def test_security_event_creation(self):
        """Test security event creation"""
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type="test_event",
            severity="medium",
            source="test",
            description="Test security event"
        )
        
        self.assertEqual(event.event_type, "test_event")
        self.assertEqual(event.severity, "medium")
        self.assertEqual(event.source, "test")
    
    def test_health_check_creation(self):
        """Test health check creation"""
        check = HealthCheck(
            name="test_check",
            status="healthy",
            response_time=0.1,
            last_check=datetime.now()
        )
        
        self.assertEqual(check.name, "test_check")
        self.assertEqual(check.status, "healthy")
        self.assertEqual(check.response_time, 0.1)
    
    def test_system_metrics_creation(self):
        """Test system metrics creation"""
        metrics = SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=50.0,
            memory_percent=60.0,
            disk_usage_percent=70.0,
            network_io={"bytes_sent": 1000, "bytes_recv": 2000},
            active_connections=10,
            queue_depth=5
        )
        
        self.assertEqual(metrics.cpu_percent, 50.0)
        self.assertEqual(metrics.memory_percent, 60.0)
        self.assertEqual(metrics.active_connections, 10)
    
    @patch('monitoring.production_monitor.psutil')
    def test_collect_system_metrics(self, mock_psutil):
        """Test system metrics collection"""
        # Mock psutil responses
        mock_psutil.cpu_percent.return_value = 25.0
        mock_psutil.virtual_memory.return_value = Mock(percent=50.0)
        mock_psutil.disk_usage.return_value = Mock(percent=30.0)
        mock_psutil.net_io_counters.return_value = Mock(
            bytes_sent=1000, bytes_recv=2000,
            packets_sent=10, packets_recv=20
        )
        mock_psutil.net_connections.return_value = [Mock(), Mock(), Mock()]
        
        # Collect metrics
        self.monitor._collect_system_metrics()
        
        # Verify metrics were collected
        self.assertGreater(len(self.monitor.system_metrics), 0)
        latest_metrics = self.monitor.system_metrics[-1]
        self.assertEqual(latest_metrics.cpu_percent, 25.0)
        self.assertEqual(latest_metrics.memory_percent, 50.0)
        self.assertEqual(latest_metrics.active_connections, 3)
    
    def test_record_security_event(self):
        """Test security event recording"""
        initial_count = len(self.monitor.security_events)
        
        self.monitor._record_security_event(
            event_type="test_event",
            severity="high",
            source="test",
            description="Test security event"
        )
        
        # Verify event was recorded
        self.assertEqual(len(self.monitor.security_events), initial_count + 1)
        latest_event = self.monitor.security_events[-1]
        self.assertEqual(latest_event.event_type, "test_event")
        self.assertEqual(latest_event.severity, "high")
    
    def test_get_health_status(self):
        """Test health status retrieval"""
        health_status = self.monitor.get_health_status()
        
        self.assertIn("status", health_status)
        self.assertIn("timestamp", health_status)
        self.assertIn("health_checks", health_status)
        self.assertIn("unhealthy_count", health_status)
        self.assertIn("degraded_count", health_status)
    
    def test_get_security_events(self):
        """Test security events retrieval"""
        # Add some test events
        self.monitor._record_security_event(
            event_type="test_event_1",
            severity="low",
            source="test",
            description="Test event 1"
        )
        
        self.monitor._record_security_event(
            event_type="test_event_2",
            severity="high",
            source="test",
            description="Test event 2"
        )
        
        # Get events from last 24 hours
        events = self.monitor.get_security_events(hours=24)
        self.assertGreaterEqual(len(events), 2)
        
        # Get events from last 1 hour
        events = self.monitor.get_security_events(hours=1)
        self.assertGreaterEqual(len(events), 2)
    
    def test_get_system_metrics(self):
        """Test system metrics retrieval"""
        # Add some test metrics
        metrics1 = SystemMetrics(
            timestamp=datetime.now() - timedelta(minutes=30),
            cpu_percent=25.0,
            memory_percent=50.0,
            disk_usage_percent=30.0,
            network_io={"bytes_sent": 1000, "bytes_recv": 2000},
            active_connections=5,
            queue_depth=2
        )
        
        metrics2 = SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=35.0,
            memory_percent=60.0,
            disk_usage_percent=40.0,
            network_io={"bytes_sent": 2000, "bytes_recv": 4000},
            active_connections=8,
            queue_depth=3
        )
        
        self.monitor.system_metrics.append(metrics1)
        self.monitor.system_metrics.append(metrics2)
        
        # Get metrics from last 60 minutes
        metrics = self.monitor.get_system_metrics(minutes=60)
        self.assertGreaterEqual(len(metrics), 2)
        
        # Get metrics from last 30 minutes
        metrics = self.monitor.get_system_metrics(minutes=30)
        self.assertGreaterEqual(len(metrics), 1)
    
    def test_alert_callback_registration(self):
        """Test alert callback registration"""
        callback_called = False
        callback_event = None
        
        def test_callback(event):
            nonlocal callback_called, callback_event
            callback_called = True
            callback_event = event
        
        self.monitor.register_alert_callback(test_callback)
        
        # Record a security event
        self.monitor._record_security_event(
            event_type="test_event",
            severity="high",
            source="test",
            description="Test event"
        )
        
        # Verify callback was called
        self.assertTrue(callback_called)
        self.assertIsNotNone(callback_event)
        self.assertEqual(callback_event.event_type, "test_event")
    
    def test_monitoring_start_stop(self):
        """Test monitoring start and stop"""
        # Start monitoring
        self.monitor.start_monitoring(interval_seconds=1)
        self.assertTrue(self.monitor.monitoring_active)
        self.assertIsNotNone(self.monitor.monitoring_thread)
        
        # Stop monitoring
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.monitoring_active)
    
    def test_global_instance(self):
        """Test global production monitor instance"""
        # Get global instance
        global_monitor = get_production_monitor()
        self.assertIsNotNone(global_monitor)
        
        # Initialize with custom parameters
        custom_monitor = initialize_production_monitoring(
            service_name="custom-service",
            service_version="1.0.0",
            environment="production"
        )
        
        self.assertEqual(custom_monitor.service_name, "custom-service")
        self.assertEqual(custom_monitor.service_version, "1.0.0")
        self.assertEqual(custom_monitor.environment, "production")

class TestHealthEndpointManager(unittest.TestCase):
    """Test health endpoint manager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.health_manager = HealthEndpointManager()
    
    def test_health_manager_initialization(self):
        """Test health endpoint manager initialization"""
        self.assertIsNotNone(self.health_manager)
        self.assertIsNotNone(self.health_manager.production_monitor)
        self.assertGreater(len(self.health_manager.dependencies), 0)
    
    def test_dependency_registration(self):
        """Test dependency registration"""
        initial_count = len(self.health_manager.dependencies)
        
        def test_check():
            return DependencyStatus(
                name="test_dep",
                status="healthy",
                response_time=0.1,
                last_check=datetime.now(),
                endpoint="http://test.com"
            )
        
        self.health_manager.register_dependency(
            "test_dependency",
            "http://test.com",
            test_check
        )
        
        # Verify dependency was registered
        self.assertEqual(len(self.health_manager.dependencies), initial_count + 1)
        self.assertIn("test_dependency", self.health_manager.dependencies)
    
    def test_dependency_status_creation(self):
        """Test dependency status creation"""
        status = DependencyStatus(
            name="test_dep",
            status="healthy",
            response_time=0.1,
            last_check=datetime.now(),
            endpoint="http://test.com"
        )
        
        self.assertEqual(status.name, "test_dep")
        self.assertEqual(status.status, "healthy")
        self.assertEqual(status.response_time, 0.1)
        self.assertEqual(status.endpoint, "http://test.com")
    
    @patch('monitoring.health_endpoints.requests.get')
    def test_ollama_dependency_check(self, mock_get):
        """Test Ollama dependency health check"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.health_manager._check_ollama_dependency()
        
        self.assertEqual(result.status, "healthy")
        self.assertGreater(result.response_time, 0)
        self.assertEqual(result.name, "ollama")
    
    @patch('monitoring.health_endpoints.requests.get')
    def test_ollama_dependency_check_failure(self, mock_get):
        """Test Ollama dependency health check failure"""
        # Mock failed response
        mock_get.side_effect = Exception("Connection failed")
        
        result = self.health_manager._check_ollama_dependency()
        
        self.assertEqual(result.status, "unhealthy")
        self.assertIsNotNone(result.error_message)
    
    def test_filesystem_dependency_check(self):
        """Test filesystem dependency health check"""
        result = self.health_manager._check_filesystem_dependency()
        
        self.assertEqual(result.status, "healthy")
        self.assertGreater(result.response_time, 0)
        self.assertEqual(result.name, "file_system")
    
    def test_run_dependency_checks(self):
        """Test running all dependency checks"""
        results = self.health_manager.run_dependency_checks()
        
        self.assertIsInstance(results, dict)
        self.assertGreater(len(results), 0)
        
        # Verify all dependencies were checked
        for name, result in results.items():
            self.assertIsInstance(result, DependencyStatus)
            self.assertEqual(result.name, name)
    
    def test_get_health_status(self):
        """Test comprehensive health status"""
        health_status = self.health_manager.get_health_status()
        
        self.assertIn("status", health_status)
        self.assertIn("timestamp", health_status)
        self.assertIn("service", health_status)
        self.assertIn("monitor_health", health_status)
        self.assertIn("dependencies", health_status)
        self.assertIn("unhealthy_dependencies", health_status)
        self.assertIn("degraded_dependencies", health_status)
        self.assertIn("total_dependencies", health_status)
    
    def test_get_ready_status(self):
        """Test readiness status for Kubernetes"""
        ready_status = self.health_manager.get_ready_status()
        
        self.assertIn("ready", ready_status)
        self.assertIn("status", ready_status)
        self.assertIn("timestamp", ready_status)
        self.assertIn("details", ready_status)
        
        # Ready should be boolean
        self.assertIsInstance(ready_status["ready"], bool)
    
    def test_health_callback_registration(self):
        """Test health callback registration"""
        callback_called = False
        callback_data = None
        
        def test_callback(data):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = data
        
        self.health_manager.register_health_callback(test_callback)
        
        # Get health status (should trigger callback)
        health_status = self.health_manager.get_health_status()
        
        # Verify callback was called
        self.assertTrue(callback_called)
        self.assertIsNotNone(callback_data)
        self.assertEqual(callback_data, health_status)
    
    def test_global_instance(self):
        """Test global health manager instance"""
        # Get global instance
        global_manager = get_health_manager()
        self.assertIsNotNone(global_manager)
        
        # Initialize with custom production monitor
        custom_monitor = ProductionMonitor(
            service_name="custom-service",
            service_version="1.0.0",
            environment="production"
        )
        
        custom_manager = initialize_health_endpoints(custom_monitor)
        self.assertEqual(custom_manager.production_monitor, custom_monitor)

if __name__ == '__main__':
    unittest.main() 