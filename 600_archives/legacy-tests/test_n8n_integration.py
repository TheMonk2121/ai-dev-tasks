#!/usr/bin/env python3
"""
Test n8n Workflow Integration

Comprehensive unit tests for n8n workflow integration, event processing,
and automated task execution.
"""

import unittest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any

from n8n_workflows.n8n_integration import (
    N8nWorkflowManager,
    Event,
    TaskExecution,
    EventType,
    TaskStatus,
    get_n8n_manager,
    create_event,
    execute_workflow,
    poll_events,
)
from n8n_workflows.n8n_event_processor import N8nEventProcessor


class TestEvent(unittest.TestCase):
    """Test Event dataclass"""

    def test_event_creation(self):
        """Test creating Event instance"""
        event_data = {"test": "value"}
        event = Event(event_type="test_event", event_data=event_data, priority=5, metadata={"source": "test"})

        self.assertEqual(event.event_type, "test_event")
        self.assertEqual(event.event_data, event_data)
        self.assertEqual(event.priority, 5)
        self.assertEqual(event.metadata, {"source": "test"})


class TestTaskExecution(unittest.TestCase):
    """Test TaskExecution dataclass"""

    def test_task_execution_creation(self):
        """Test creating TaskExecution instance"""
        parameters = {"param1": "value1"}
        task = TaskExecution(
            task_id="test-task-001",
            task_type="document_process",
            parameters=parameters,
            workflow_id="test-workflow",
            status="pending",
        )

        self.assertEqual(task.task_id, "test-task-001")
        self.assertEqual(task.task_type, "document_process")
        self.assertEqual(task.parameters, parameters)
        self.assertEqual(task.workflow_id, "test-workflow")
        self.assertEqual(task.status, "pending")


class TestN8nWorkflowManager(unittest.TestCase):
    """Test N8nWorkflowManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = N8nWorkflowManager(n8n_base_url="http://localhost:5678", n8n_api_key="test-key")

    @patch("n8n_workflows.n8n_integration.execute_query")
    def test_create_event(self, mock_execute_query):
        """Test creating an event"""
        mock_execute_query.return_value = [{"id": 1}]

        event = Event(event_type="test_event", event_data={"test": "data"}, priority=1)

        event_id = self.manager.create_event(event)

        self.assertEqual(event_id, 1)
        mock_execute_query.assert_called_once()

    @patch("n8n_workflows.n8n_integration.execute_query")
    def test_get_pending_events(self, mock_execute_query):
        """Test getting pending events"""
        mock_events = [
            {"id": 1, "event_type": "test1", "status": "pending"},
            {"id": 2, "event_type": "test2", "status": "pending"},
        ]
        mock_execute_query.return_value = mock_events

        events = self.manager.get_pending_events(limit=5)

        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["id"], 1)
        self.assertEqual(events[1]["id"], 2)

    @patch("n8n_workflows.n8n_integration.execute_query")
    def test_update_event_status(self, mock_execute_query):
        """Test updating event status"""
        mock_execute_query.return_value = [{"affected_rows": 1}]

        result = self.manager.update_event_status(
            event_id=1, status="completed", result={"success": True}, error_message=None
        )

        self.assertTrue(result)
        mock_execute_query.assert_called_once()

    @patch("n8n_workflows.n8n_integration.execute_query")
    def test_create_task_execution(self, mock_execute_query):
        """Test creating task execution"""
        mock_execute_query.return_value = [{"id": 1}]

        task = TaskExecution(
            task_id="test-task", task_type="document_process", parameters={"file_path": "/test/file.txt"}
        )

        task_id = self.manager.create_task_execution(task)

        self.assertEqual(task_id, 1)
        mock_execute_query.assert_called_once()

    @patch("requests.Session.post")
    @patch("n8n_workflows.n8n_integration.execute_query")
    def test_execute_workflow(self, mock_execute_query, mock_post):
        """Test executing a workflow"""
        mock_execute_query.return_value = [{"id": 1}]
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        parameters = {"test": "param"}
        execution_id = self.manager.execute_workflow("test-workflow", parameters)

        self.assertIsInstance(execution_id, str)
        mock_execute_query.assert_called_once()
        mock_post.assert_called_once()

    def test_handle_backlog_scrubber(self):
        """Test backlog scrubber handler"""
        with patch("builtins.open", create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = """
            | B-001 | Test Item | 🔥 | 3 | todo | Test | Tech | None |
            <!--score: {"bv":5, "tc":3, "rr":5, "le":4, "effort":3}-->
            """
            mock_open.return_value.__enter__.return_value.write = Mock()

            result = self.manager._handle_backlog_scrubber({})

            self.assertEqual(result["status"], "success")
            mock_open.assert_called()

    def test_handle_task_executor(self):
        """Test task executor handler"""
        event_data = {"task_type": "system_health_check", "parameters": {}}

        result = self.manager._handle_task_executor(event_data)

        self.assertEqual(result["status"], "success")
        self.assertIn("message", result)

    def test_handle_document_processor(self):
        """Test document processor handler"""
        event_data = {"file_path": "/test/file.txt"}

        with patch("n8n_workflows.n8n_integration.process_document") as mock_process:
            mock_process.return_value = {"status": "success"}

            result = self.manager._handle_document_processor(event_data)

            self.assertEqual(result["status"], "success")

    def test_handle_system_monitor(self):
        """Test system monitor handler"""
        with (
            patch("psutil.cpu_percent", return_value=50.0),
            patch("psutil.virtual_memory") as mock_memory,
            patch("psutil.disk_usage") as mock_disk,
            patch("n8n_workflows.n8n_integration.execute_query") as mock_execute,
        ):

            mock_memory.return_value.percent = 60.0
            mock_disk.return_value.percent = 70.0
            mock_execute.return_value = [{"id": 1}]

            result = self.manager._handle_system_monitor({})

            self.assertEqual(result["status"], "success")
            self.assertIn("metrics", result)

    def test_calculate_score(self):
        """Test score calculation"""
        score_json = '{"bv":5, "tc":3, "rr":5, "le":4, "effort":3}'

        result = self.manager._calculate_score(score_json)

        self.assertIn("score_total: 5.7", result)

    @patch("n8n_workflows.n8n_integration.execute_query")
    def test_poll_and_process_events(self, mock_execute_query):
        """Test polling and processing events"""
        mock_events = [
            {"id": 1, "event_type": "backlog-scrubber", "event_data": '{"test": "data"}', "status": "pending"}
        ]
        mock_execute_query.return_value = mock_events

        processed_count = self.manager.poll_and_process_events()

        self.assertEqual(processed_count, 1)

    @patch("n8n_workflows.n8n_integration.execute_query")
    def test_get_workflow_status(self, mock_execute_query):
        """Test getting workflow status"""
        mock_status = {"workflow_id": "test-workflow", "status": "completed", "execution_id": "test-execution"}
        mock_execute_query.return_value = [mock_status]

        status = self.manager.get_workflow_status("test-workflow")

        self.assertEqual(status["status"], "completed")


class TestN8nEventProcessor(unittest.TestCase):
    """Test N8nEventProcessor class"""

    def setUp(self):
        """Set up test fixtures"""
        self.processor = N8nEventProcessor(poll_interval=1)

    def test_initialization(self):
        """Test processor initialization"""
        self.assertFalse(self.processor.running)
        self.assertIsNone(self.processor.thread)
        self.assertEqual(self.processor.stats["events_processed"], 0)

    def test_start_stop(self):
        """Test starting and stopping the processor"""
        self.processor.start()
        self.assertTrue(self.processor.running)
        self.assertIsNotNone(self.processor.thread)

        self.processor.stop()
        self.assertFalse(self.processor.running)

    def test_get_stats(self):
        """Test getting processor statistics"""
        stats = self.processor.get_stats()

        self.assertIn("running", stats)
        self.assertIn("uptime_seconds", stats)
        self.assertIn("events_processed", stats)
        self.assertIn("events_failed", stats)
        self.assertIn("last_poll", stats)
        self.assertIn("poll_interval", stats)

    @patch("n8n_workflows.n8n_event_processor.create_event")
    def test_create_system_event(self, mock_create_event):
        """Test creating system events"""
        mock_create_event.return_value = 1

        event_id = self.processor.create_system_event("test_event", {"test": "data"}, priority=1)

        self.assertEqual(event_id, 1)
        mock_create_event.assert_called_once()

    @patch("n8n_workflows.n8n_event_processor.create_event")
    def test_trigger_backlog_scrubber(self, mock_create_event):
        """Test triggering backlog scrubber"""
        mock_create_event.return_value = 1

        event_id = self.processor.trigger_backlog_scrubber()

        self.assertEqual(event_id, 1)
        mock_create_event.assert_called_once()

    @patch("n8n_workflows.n8n_event_processor.create_event")
    def test_trigger_document_processing(self, mock_create_event):
        """Test triggering document processing"""
        mock_create_event.return_value = 1

        event_id = self.processor.trigger_document_processing("/test/file.txt")

        self.assertEqual(event_id, 1)
        mock_create_event.assert_called_once()

    @patch("n8n_workflows.n8n_event_processor.create_event")
    def test_trigger_system_health_check(self, mock_create_event):
        """Test triggering system health check"""
        mock_create_event.return_value = 1

        event_id = self.processor.trigger_system_health_check()

        self.assertEqual(event_id, 1)
        mock_create_event.assert_called_once()


class TestN8nIntegrationFunctions(unittest.TestCase):
    """Test n8n integration convenience functions"""

    def setUp(self):
        """Set up test fixtures"""
        # Clear global instance
        import n8n_workflows.n8n_integration as n8n_module

        n8n_module._n8n_manager = None

    @patch("n8n_workflows.n8n_integration.N8nWorkflowManager")
    def test_get_n8n_manager(self, mock_manager_class):
        """Test getting n8n manager instance"""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager

        manager = get_n8n_manager()

        self.assertEqual(manager, mock_manager)
        mock_manager_class.assert_called_once()

    @patch("n8n_workflows.n8n_integration.get_n8n_manager")
    def test_create_event_function(self, mock_get_manager):
        """Test create_event convenience function"""
        mock_manager = Mock()
        mock_manager.create_event.return_value = 1
        mock_get_manager.return_value = mock_manager

        event_id = create_event("test_event", {"test": "data"}, priority=1)

        self.assertEqual(event_id, 1)
        mock_manager.create_event.assert_called_once()

    @patch("n8n_workflows.n8n_integration.get_n8n_manager")
    def test_execute_workflow_function(self, mock_get_manager):
        """Test execute_workflow convenience function"""
        mock_manager = Mock()
        mock_manager.execute_workflow.return_value = "test-execution-id"
        mock_get_manager.return_value = mock_manager

        execution_id = execute_workflow("test-workflow", {"test": "param"})

        self.assertEqual(execution_id, "test-execution-id")
        mock_manager.execute_workflow.assert_called_once_with("test-workflow", {"test": "param"})

    @patch("n8n_workflows.n8n_integration.get_n8n_manager")
    def test_poll_events_function(self, mock_get_manager):
        """Test poll_events convenience function"""
        mock_manager = Mock()
        mock_manager.poll_and_process_events.return_value = 3
        mock_get_manager.return_value = mock_manager

        processed_count = poll_events()

        self.assertEqual(processed_count, 3)
        mock_manager.poll_and_process_events.assert_called_once()


class TestN8nIntegrationIntegration(unittest.TestCase):
    """Integration tests for n8n workflow integration"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = N8nWorkflowManager()
        self.processor = N8nEventProcessor(poll_interval=1)

    def test_full_workflow(self):
        """Test complete n8n workflow integration"""
        # Test event creation
        event = Event(event_type="test_event", event_data={"test": "data"}, priority=1)

        # Test workflow execution
        with patch("requests.Session.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            execution_id = self.manager.execute_workflow("test-workflow", {})
            self.assertIsInstance(execution_id, str)

        # Test event processing
        with patch.object(self.manager, "get_pending_events", return_value=[]):
            processed_count = self.manager.poll_and_process_events()
            self.assertEqual(processed_count, 0)


if __name__ == "__main__":
    unittest.main()
