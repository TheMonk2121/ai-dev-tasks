#!/usr/bin/env python3
"""
Unit tests for Real-time Mission Dashboard
Tests mission tracking, dashboard functionality, and API endpoints
"""

import json
import time
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

try:
    from mission_dashboard.mission_tracker import (
        MissionTracker,
        Mission,
        MissionStatus,
        MissionPriority,
        MissionMetrics,
    )
    from utils.logger import get_logger

    LOG = get_logger("test_mission_dashboard")
except ImportError as e:
    import logging

    logging.basicConfig(level=logging.INFO)
    LOG = logging.getLogger("test_mission_dashboard")
    LOG.warning(f"Some components not available: {e}")

# Import app separately to handle potential import errors
try:
    from mission_dashboard.mission_dashboard import app, dashboard_state
except ImportError as e:
    app = None
    dashboard_state = None
    LOG.warning(f"Dashboard app not available: {e}")


class TestMissionTracker(unittest.TestCase):
    """Test MissionTracker functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.tracker = MissionTracker(max_history=10)
        self.test_mission_data = {
            "title": "Test Mission",
            "description": "Test mission description",
            "priority": MissionPriority.MEDIUM,
            "metadata": {"test": True},
        }

    def tearDown(self):
        """Clean up test fixtures"""
        if hasattr(self.tracker, "shutdown"):
            self.tracker.shutdown()

    def test_create_mission(self):
        """Test mission creation"""
        mission_id = self.tracker.create_mission(**self.test_mission_data)

        self.assertIsInstance(mission_id, str)
        self.assertTrue(len(mission_id) > 0)

        mission = self.tracker.get_mission(mission_id)
        self.assertIsNotNone(mission)
        self.assertEqual(mission.title, self.test_mission_data["title"])
        self.assertEqual(mission.description, self.test_mission_data["description"])
        self.assertEqual(mission.priority, self.test_mission_data["priority"])
        self.assertEqual(mission.status, MissionStatus.PENDING)

    def test_start_mission(self):
        """Test mission start"""
        mission_id = self.tracker.create_mission(**self.test_mission_data)

        success = self.tracker.start_mission(mission_id=mission_id, agent_type="TestAgent", model_used="test-model")

        self.assertTrue(success)

        mission = self.tracker.get_mission(mission_id)
        self.assertEqual(mission.status, MissionStatus.RUNNING)
        self.assertEqual(mission.agent_type, "TestAgent")
        self.assertEqual(mission.model_used, "test-model")
        self.assertIsNotNone(mission.started_at)

    def test_update_mission_progress(self):
        """Test mission progress updates"""
        mission_id = self.tracker.create_mission(**self.test_mission_data)
        self.tracker.start_mission(mission_id=mission_id)

        # Test progress update
        success = self.tracker.update_mission_progress(mission_id=mission_id, progress=50.0, result={"step": "halfway"})

        self.assertTrue(success)

        mission = self.tracker.get_mission(mission_id)
        self.assertEqual(mission.progress, 50.0)
        self.assertEqual(mission.result, {"step": "halfway"})

    def test_complete_mission(self):
        """Test mission completion"""
        mission_id = self.tracker.create_mission(**self.test_mission_data)
        self.tracker.start_mission(mission_id=mission_id)

        success = self.tracker.complete_mission(
            mission_id=mission_id, result={"status": "completed"}, tokens_used=1000, cost_estimate=0.1
        )

        self.assertTrue(success)

        mission = self.tracker.get_mission(mission_id)
        self.assertEqual(mission.status, MissionStatus.COMPLETED)
        self.assertEqual(mission.progress, 100.0)
        self.assertEqual(mission.result, {"status": "completed"})
        self.assertEqual(mission.tokens_used, 1000)
        self.assertEqual(mission.cost_estimate, 0.1)
        self.assertIsNotNone(mission.completed_at)
        self.assertIsNotNone(mission.duration)

    def test_fail_mission(self):
        """Test mission failure"""
        mission_id = self.tracker.create_mission(**self.test_mission_data)
        self.tracker.start_mission(mission_id=mission_id)

        error_message = "Test error occurred"
        success = self.tracker.fail_mission(mission_id=mission_id, error_message=error_message)

        self.assertTrue(success)

        mission = self.tracker.get_mission(mission_id)
        self.assertEqual(mission.status, MissionStatus.FAILED)
        self.assertEqual(mission.error_message, error_message)
        self.assertIsNotNone(mission.completed_at)

    def test_cancel_mission(self):
        """Test mission cancellation"""
        mission_id = self.tracker.create_mission(**self.test_mission_data)
        self.tracker.start_mission(mission_id=mission_id)

        success = self.tracker.cancel_mission(mission_id=mission_id)

        self.assertTrue(success)

        mission = self.tracker.get_mission(mission_id)
        self.assertEqual(mission.status, MissionStatus.CANCELLED)
        self.assertIsNotNone(mission.completed_at)

    def test_get_all_missions(self):
        """Test getting all missions"""
        # Create multiple missions
        mission_ids = []
        for i in range(3):
            mission_id = self.tracker.create_mission(
                title=f"Mission {i}", description=f"Description {i}", priority=MissionPriority.MEDIUM
            )
            mission_ids.append(mission_id)

        missions = self.tracker.get_all_missions()
        self.assertEqual(len(missions), 3)

        # Test filtering by status
        pending_missions = self.tracker.get_all_missions(status=MissionStatus.PENDING)
        self.assertEqual(len(pending_missions), 3)

    def test_get_running_missions(self):
        """Test getting running missions"""
        mission_id = self.tracker.create_mission(**self.test_mission_data)
        self.tracker.start_mission(mission_id=mission_id)

        running_missions = self.tracker.get_running_missions()
        self.assertEqual(len(running_missions), 1)
        self.assertEqual(running_missions[0].id, mission_id)

    def test_get_metrics(self):
        """Test metrics calculation"""
        # Create and complete a mission
        mission_id = self.tracker.create_mission(**self.test_mission_data)
        self.tracker.start_mission(mission_id=mission_id)
        self.tracker.complete_mission(mission_id=mission_id, tokens_used=1000, cost_estimate=0.1)

        # Force metrics update since database might not be available
        self.tracker._update_metrics()

        metrics = self.tracker.get_metrics()
        self.assertIsInstance(metrics, MissionMetrics)
        self.assertEqual(metrics.total_missions, 1)
        self.assertEqual(metrics.completed_missions, 1)
        self.assertEqual(metrics.running_missions, 0)
        self.assertEqual(metrics.success_rate, 100.0)
        self.assertEqual(metrics.total_tokens, 1000)
        self.assertEqual(metrics.total_cost, 0.1)

    def test_invalid_mission_id(self):
        """Test handling of invalid mission IDs"""
        invalid_id = "invalid-mission-id"

        # Test getting non-existent mission
        mission = self.tracker.get_mission(invalid_id)
        self.assertIsNone(mission)

        # Test starting non-existent mission
        success = self.tracker.start_mission(mission_id=invalid_id)
        self.assertFalse(success)

        # Test updating non-existent mission
        success = self.tracker.update_mission_progress(invalid_id, 50.0)
        self.assertFalse(success)

    def test_mission_status_transitions(self):
        """Test valid and invalid status transitions"""
        mission_id = self.tracker.create_mission(**self.test_mission_data)

        # Cannot start a mission that's not pending
        mission = self.tracker.get_mission(mission_id)
        mission.status = MissionStatus.COMPLETED

        success = self.tracker.start_mission(mission_id=mission_id)
        self.assertFalse(success)


class TestMissionDashboardAPI(unittest.TestCase):
    """Test Mission Dashboard API endpoints"""

    def setUp(self):
        """Set up test client"""
        if app is None:
            self.skipTest("Dashboard app not available")

        self.app = app.test_client()
        self.app.testing = True

        # Mock mission tracker
        self.mock_tracker = Mock()
        with patch("mission_dashboard.mission_dashboard.mission_tracker", self.mock_tracker):
            pass

    def test_index_route(self):
        """Test main dashboard page"""
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)

    def test_get_missions_api(self):
        """Test GET /api/missions endpoint"""
        # Mock mission data
        mock_mission = Mock()
        mock_mission.id = "test-id"
        mock_mission.title = "Test Mission"
        mock_mission.description = "Test Description"
        mock_mission.status.value = "pending"
        mock_mission.priority.value = "medium"
        mock_mission.created_at = datetime.now()
        mock_mission.started_at = None
        mock_mission.completed_at = None
        mock_mission.duration = None
        mock_mission.progress = 0.0
        mock_mission.error_message = None
        mock_mission.result = None
        mock_mission.metadata = {}
        mock_mission.agent_type = None
        mock_mission.model_used = None
        mock_mission.tokens_used = None
        mock_mission.cost_estimate = None

        self.mock_tracker.get_all_missions.return_value = [mock_mission]

        response = self.app.get("/api/missions")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn("missions", data)
        self.assertIn("total", data)
        self.assertIn("timestamp", data)

    def test_get_mission_api(self):
        """Test GET /api/missions/<id> endpoint"""
        # Mock mission data
        mock_mission = Mock()
        mock_mission.id = "test-id"
        mock_mission.title = "Test Mission"
        mock_mission.description = "Test Description"
        mock_mission.status.value = "pending"
        mock_mission.priority.value = "medium"
        mock_mission.created_at = datetime.now()
        mock_mission.started_at = None
        mock_mission.completed_at = None
        mock_mission.duration = None
        mock_mission.progress = 0.0
        mock_mission.error_message = None
        mock_mission.result = None
        mock_mission.metadata = {}
        mock_mission.agent_type = None
        mock_mission.model_used = None
        mock_mission.tokens_used = None
        mock_mission.cost_estimate = None

        self.mock_tracker.get_mission.return_value = mock_mission

        response = self.app.get("/api/missions/test-id")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn("mission", data)
        self.assertIn("timestamp", data)

    def test_create_mission_api(self):
        """Test POST /api/missions endpoint"""
        self.mock_tracker.create_mission.return_value = "new-mission-id"

        response = self.app.post(
            "/api/missions", json={"title": "New Mission", "description": "New Description", "priority": "medium"}
        )

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data)
        self.assertIn("mission_id", data)
        self.assertIn("message", data)
        self.assertIn("timestamp", data)

    def test_start_mission_api(self):
        """Test POST /api/missions/<id>/start endpoint"""
        self.mock_tracker.start_mission.return_value = True

        response = self.app.post(
            "/api/missions/test-id/start", json={"agent_type": "TestAgent", "model_used": "test-model"}
        )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn("message", data)
        self.assertIn("timestamp", data)

    def test_update_mission_progress_api(self):
        """Test POST /api/missions/<id>/progress endpoint"""
        self.mock_tracker.update_mission_progress.return_value = True

        response = self.app.post(
            "/api/missions/test-id/progress", json={"progress": 50.0, "result": {"step": "halfway"}}
        )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn("message", data)
        self.assertIn("timestamp", data)

    def test_complete_mission_api(self):
        """Test POST /api/missions/<id>/complete endpoint"""
        self.mock_tracker.complete_mission.return_value = True

        response = self.app.post(
            "/api/missions/test-id/complete",
            json={"result": {"status": "completed"}, "tokens_used": 1000, "cost_estimate": 0.1},
        )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn("message", data)
        self.assertIn("timestamp", data)

    def test_fail_mission_api(self):
        """Test POST /api/missions/<id>/fail endpoint"""
        self.mock_tracker.fail_mission.return_value = True

        response = self.app.post("/api/missions/test-id/fail", json={"error_message": "Test error"})

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn("message", data)
        self.assertIn("timestamp", data)

    def test_cancel_mission_api(self):
        """Test POST /api/missions/<id>/cancel endpoint"""
        self.mock_tracker.cancel_mission.return_value = True

        response = self.app.post("/api/missions/test-id/cancel")

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn("message", data)
        self.assertIn("timestamp", data)

    def test_get_metrics_api(self):
        """Test GET /api/metrics endpoint"""
        # Mock metrics
        mock_metrics = Mock()
        mock_metrics.total_missions = 10
        mock_metrics.completed_missions = 8
        mock_metrics.failed_missions = 1
        mock_metrics.running_missions = 1
        mock_metrics.average_duration = 30.5
        mock_metrics.success_rate = 80.0
        mock_metrics.total_tokens = 5000
        mock_metrics.total_cost = 0.5

        self.mock_tracker.get_metrics.return_value = mock_metrics

        response = self.app.get("/api/metrics")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn("metrics", data)
        self.assertIn("timestamp", data)

    def test_get_running_missions_api(self):
        """Test GET /api/running endpoint"""
        # Mock running missions
        mock_mission = Mock()
        mock_mission.id = "running-id"
        mock_mission.title = "Running Mission"
        mock_mission.description = "Running Description"
        mock_mission.status.value = "running"
        mock_mission.priority.value = "high"
        mock_mission.created_at = datetime.now()
        mock_mission.started_at = datetime.now()
        mock_mission.completed_at = None
        mock_mission.duration = None
        mock_mission.progress = 50.0
        mock_mission.error_message = None
        mock_mission.result = None
        mock_mission.metadata = {}
        mock_mission.agent_type = "TestAgent"
        mock_mission.model_used = "test-model"
        mock_mission.tokens_used = None
        mock_mission.cost_estimate = None

        self.mock_tracker.get_running_missions.return_value = [mock_mission]

        response = self.app.get("/api/running")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn("missions", data)
        self.assertIn("count", data)
        self.assertIn("timestamp", data)

    def test_health_check_api(self):
        """Test GET /api/health endpoint"""
        response = self.app.get("/api/health")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn("status", data)
        self.assertIn("timestamp", data)
        self.assertIn("mission_tracker", data)

    def test_error_handling(self):
        """Test error handling in API endpoints"""
        # Test missing mission tracker
        with patch("mission_dashboard.mission_dashboard.mission_tracker", None):
            response = self.app.get("/api/missions")
            self.assertEqual(response.status_code, 503)

            data = json.loads(response.data)
            self.assertIn("error", data)

        # Test invalid JSON
        response = self.app.post("/api/missions", data="invalid json")
        self.assertEqual(response.status_code, 400)

        # Test missing required fields
        response = self.app.post("/api/missions", json={})
        self.assertEqual(response.status_code, 400)


class TestMissionDashboardIntegration(unittest.TestCase):
    """Integration tests for Mission Dashboard"""

    def setUp(self):
        """Set up integration test fixtures"""
        self.tracker = MissionTracker(max_history=10)

        if app is None:
            self.skipTest("Dashboard app not available")

        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        """Clean up integration test fixtures"""
        if hasattr(self.tracker, "shutdown"):
            self.tracker.shutdown()

    def test_full_mission_lifecycle(self):
        """Test complete mission lifecycle through API"""
        # Create mission
        response = self.app.post(
            "/api/missions",
            json={"title": "Integration Test Mission", "description": "Testing full lifecycle", "priority": "high"},
        )
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data)
        mission_id = data["mission_id"]

        # Start mission
        response = self.app.post(
            f"/api/missions/{mission_id}/start",
            json={"agent_type": "IntegrationAgent", "model_used": "integration-model"},
        )
        self.assertEqual(response.status_code, 200)

        # Update progress
        response = self.app.post(
            f"/api/missions/{mission_id}/progress", json={"progress": 50.0, "result": {"step": "halfway"}}
        )
        self.assertEqual(response.status_code, 200)

        # Complete mission
        response = self.app.post(
            f"/api/missions/{mission_id}/complete",
            json={"result": {"status": "completed"}, "tokens_used": 2000, "cost_estimate": 0.2},
        )
        self.assertEqual(response.status_code, 200)

        # Verify mission state
        response = self.app.get(f"/api/missions/{mission_id}")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        mission = data["mission"]
        self.assertEqual(mission["status"], "completed")
        self.assertEqual(mission["progress"], 100.0)
        self.assertEqual(mission["tokens_used"], 2000)
        self.assertEqual(mission["cost_estimate"], 0.2)


def run_tests():
    """Run all tests"""
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestMissionTracker))
    test_suite.addTest(unittest.makeSuite(TestMissionDashboardAPI))
    test_suite.addTest(unittest.makeSuite(TestMissionDashboardIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print(f"\n{'='*50}")
    print(f"Test Results:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(
        f"  Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"
    )
    print(f"{'='*50}")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
