"""
Comprehensive Integration Tests for Decision Intelligence

This module provides end-to-end testing of decision intelligence workflows,
integration with existing LTST functionality, and stress testing for concurrent operations.
"""

import json
import logging
import os

# Add the src directory to the path
import sys
import threading
import time
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.context_merger import ContextMerger
from utils.conversation_storage import ConversationStorage
from utils.decision_evaluator import DecisionEvaluator, TestCase
from utils.decision_performance_optimizer import DecisionPerformanceOptimizer
from utils.memory_rehydrator import MemoryRehydrator
from utils.session_manager import SessionManager


class TestDecisionIntegration(unittest.TestCase):
    """Comprehensive integration tests for decision intelligence system"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        # Configure logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        cls.logger = logging.getLogger(__name__)

        # Initialize components
        cls.storage = ConversationStorage()
        if not cls.storage.connect():
            raise RuntimeError("Failed to connect to database")

        cls.session_manager = SessionManager(cls.storage)
        cls.merger = ContextMerger(cls.storage)
        cls.rehydrator = MemoryRehydrator(cls.storage)
        cls.evaluator = DecisionEvaluator(cls.storage, cls.merger)
        cls.optimizer = DecisionPerformanceOptimizer(cls.storage, cls.merger)

        cls.logger.info("Test environment initialized")

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        if cls.storage:
            cls.storage.disconnect()
        cls.logger.info("Test environment cleaned up")

    def setUp(self):
        """Set up each test case"""
        # Create a unique test session for each test
        self.session_id = self.session_manager.create_session(
            f"test_user_{int(time.time())}", f"Integration Test Session {datetime.now().strftime('%H:%M:%S')}"
        )
        self.logger.info(f"Test session created: {self.session_id}")

    def tearDown(self):
        """Clean up after each test case"""
        # Note: In a real scenario, you might want to clean up test data
        # For now, we'll leave it for inspection
        pass

    def test_01_decision_lifecycle_workflow(self):
        """Test complete decision lifecycle: create, update, supersede, retrieve"""
        self.logger.info("Testing decision lifecycle workflow...")

        # Step 1: Create initial decisions
        decision1_id = self.storage.store_decision(
            session_id=self.session_id,
            decision_head="use_python_3_11",
            context_value="Python 3.11 offers good performance improvements",
            entities=["python", "version", "project"],
            files=["requirements.txt", "pyproject.toml"],
        )
        self.assertTrue(decision1_id)

        decision2_id = self.storage.store_decision(
            session_id=self.session_id,
            decision_head="enable_debug_mode",
            context_value="Debug mode is essential for development",
            entities=["debug", "mode", "development"],
            files=["config/app.yml", "scripts/debug.sh"],
        )
        self.assertTrue(decision2_id)

        # Step 2: Verify decisions are stored
        decisions = self.storage.retrieve_decisions(self.session_id)
        self.assertEqual(len(decisions), 2)

        # Step 3: Create superseding decisions
        decision3_id = self.storage.store_decision(
            session_id=self.session_id,
            decision_head="use_python_3_12",
            context_value="Python 3.12 provides even better performance",
            entities=["python", "version", "project"],
            files=["requirements.txt", "pyproject.toml"],
        )
        self.assertTrue(decision3_id)

        decision4_id = self.storage.store_decision(
            session_id=self.session_id,
            decision_head="disable_debug_mode",
            context_value="Debug mode should be disabled in production",
            entities=["debug", "mode", "production"],
            files=["config/app.yml", "scripts/debug.sh"],
        )
        self.assertTrue(decision4_id)

        # Step 4: Verify supersedence logic worked
        decisions_after = self.storage.retrieve_decisions(self.session_id)
        self.assertEqual(len(decisions_after), 4)

        # Check that old decisions are marked as superseded
        superseded_count = sum(1 for d in decisions_after if d.get("decision_status") == "superseded")
        self.assertEqual(superseded_count, 2)

        # Step 5: Test decision retrieval with context merger
        merge_result = self.merger.merge_decision_contexts(
            session_id=self.session_id, query_entities=["python", "version"]
        )
        self.assertIsNotNone(merge_result)
        self.assertTrue(len(merge_result.merged_contexts) > 0)

        # Step 6: Verify supersedence chain
        chain = self.storage.get_supersedence_chain("use_python_3_11", self.session_id)
        self.assertIsNotNone(chain)

        self.logger.info("✅ Decision lifecycle workflow test passed")

    def test_02_decision_integration_with_ltst(self):
        """Test decision integration with existing LTST functionality"""
        self.logger.info("Testing decision integration with LTST...")

        # Step 1: Store conversation context
        context_id = self.storage.store_context(
            session_id=self.session_id,
            context_type="conversation",
            context_key="project_setup",
            context_value="Setting up new project with Python and PostgreSQL",
            relevance_score=0.9,
        )
        self.assertTrue(context_id)

        # Step 2: Store decision context
        decision_id = self.storage.store_decision(
            session_id=self.session_id,
            decision_head="use_postgresql",
            context_value="PostgreSQL provides excellent performance and reliability",
            entities=["database", "postgresql", "primary"],
            files=["config/database.yml", "docs/architecture.md"],
        )
        self.assertTrue(decision_id)

        # Step 3: Test context merging with both types
        # First get conversation contexts (verify they exist)
        conversation_contexts = self.storage.retrieve_context(self.session_id, "conversation", limit=50)
        self.assertIsNotNone(conversation_contexts)
        # Then get decision contexts (verify they exist)
        decision_contexts = self.storage.retrieve_context(self.session_id, "decision", limit=50)
        self.assertIsNotNone(decision_contexts)

        # Combine and test decision-specific merging
        merge_result = self.merger.merge_decision_contexts(
            session_id=self.session_id, query_entities=["postgresql", "database"]
        )
        self.assertIsNotNone(merge_result)
        self.assertTrue(len(merge_result.merged_contexts) > 0)

        # Step 4: Test memory rehydration with decisions
        from src.utils.memory_rehydrator import RehydrationRequest

        request = RehydrationRequest(
            session_id=self.session_id,
            user_id="test_user",
            current_message="What database should we use for the project?",
            context_types=["conversation", "decision"],
            max_context_length=2000,
            include_conversation_history=True,
            history_limit=5,
            relevance_threshold=0.6,
            similarity_threshold=0.8,
        )
        rehydration_result = self.rehydrator.rehydrate_memory(request)
        self.assertIsNotNone(rehydration_result)
        self.assertTrue(len(rehydration_result.merged_contexts) > 0)

        # Verify decision context is included
        decision_context_found = any("use_postgresql" in str(context) for context in rehydration_result.merged_contexts)
        self.assertTrue(decision_context_found)

        self.logger.info("✅ Decision integration with LTST test passed")

    def test_03_decision_context_merging(self):
        """Test decision context merging with conversation context"""
        self.logger.info("Testing decision context merging...")

        # Step 1: Create diverse context types
        contexts = [
            {
                "type": "conversation",
                "key": "user_preferences",
                "value": "User prefers Python and PostgreSQL",
                "relevance": 0.8,
            },
            {
                "type": "decision",
                "key": "use_python_3_12",
                "value": "Python 3.12 provides best performance",
                "relevance": 0.9,
                "entities": ["python", "version", "performance"],
            },
            {
                "type": "conversation",
                "key": "technical_requirements",
                "value": "Need high performance and reliability",
                "relevance": 0.7,
            },
            {
                "type": "decision",
                "key": "use_postgresql",
                "value": "PostgreSQL meets performance requirements",
                "relevance": 0.9,
                "entities": ["database", "postgresql", "performance"],
            },
        ]

        # Store contexts
        for ctx in contexts:
            if ctx["type"] == "conversation":
                self.storage.store_context(
                    session_id=self.session_id,
                    context_type=ctx["type"],
                    context_key=ctx["key"],
                    context_value=ctx["value"],
                    relevance_score=ctx["relevance"],
                )
            else:  # decision
                self.storage.store_decision(
                    session_id=self.session_id,
                    decision_head=ctx["key"],
                    context_value=ctx["value"],
                    entities=ctx.get("entities", []),
                    relevance_score=ctx["relevance"],
                )

        # Step 2: Test context merging
        # Test decision-specific merging
        merge_result = self.merger.merge_decision_contexts(
            session_id=self.session_id, query_entities=["python", "database"]
        )

        self.assertIsNotNone(merge_result)
        self.assertTrue(len(merge_result.merged_contexts) > 0)

        # Step 3: Verify decision contexts are prioritized
        decision_contexts = [
            ctx for ctx in merge_result.merged_contexts if hasattr(ctx, "decision_head") and ctx.decision_head
        ]
        self.assertTrue(len(decision_contexts) > 0)

        # Step 4: Test decision-specific merging
        decision_merge_result = self.merger.merge_decision_contexts(
            session_id=self.session_id, query_entities=["python", "database"]
        )

        self.assertIsNotNone(decision_merge_result)
        self.assertTrue(len(decision_merge_result.merged_contexts) > 0)

        self.logger.info("✅ Decision context merging test passed")

    def test_04_concurrent_decision_operations(self):
        """Test stress tests for concurrent decision operations"""
        self.logger.info("Testing concurrent decision operations...")

        # Step 1: Create multiple threads for concurrent operations
        num_threads = 5
        operations_per_thread = 10
        results = []
        errors = []

        def worker_thread(thread_id):
            """Worker thread for concurrent operations"""
            try:
                for i in range(operations_per_thread):
                    # Store decision
                    decision_id = self.storage.store_decision(
                        session_id=self.session_id,
                        decision_head=f"thread_{thread_id}_decision_{i}",
                        context_value=f"Decision {i} from thread {thread_id}",
                        entities=[f"thread_{thread_id}", f"decision_{i}"],
                        relevance_score=0.7 + (i * 0.01),
                    )

                    if decision_id:
                        results.append(f"thread_{thread_id}_decision_{i}")

                    # Small delay to simulate real work
                    time.sleep(0.001)

            except Exception as e:
                errors.append(f"Thread {thread_id} error: {e}")

        # Step 2: Start concurrent threads
        threads = []
        start_time = time.time()

        for i in range(num_threads):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()

        # Step 3: Wait for all threads to complete
        for thread in threads:
            thread.join()

        execution_time = time.time() - start_time

        # Step 4: Verify results
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), num_threads * operations_per_thread)

        # Step 5: Verify data consistency
        decisions = self.storage.retrieve_decisions(self.session_id)
        self.assertEqual(len(decisions), num_threads * operations_per_thread)

        # Step 6: Test concurrent retrieval
        retrieval_results = []
        retrieval_errors = []

        def retrieval_worker(thread_id):
            """Worker thread for concurrent retrieval"""
            try:
                merge_result = self.merger.merge_decision_contexts(
                    session_id=self.session_id, query_entities=[f"thread_{thread_id}"]
                )
                retrieval_results.append(len(merge_result.merged_contexts))
            except Exception as e:
                retrieval_errors.append(f"Retrieval thread {thread_id} error: {e}")

        # Start concurrent retrieval threads
        retrieval_threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=retrieval_worker, args=(i,))
            retrieval_threads.append(thread)
            thread.start()

        for thread in retrieval_threads:
            thread.join()

        self.assertEqual(len(retrieval_errors), 0, f"Retrieval errors: {retrieval_errors}")
        self.assertEqual(len(retrieval_results), num_threads)

        self.logger.info(f"✅ Concurrent operations test passed: {len(results)} operations in {execution_time:.2f}s")

    def test_05_decision_data_consistency(self):
        """Test decision data consistency and integrity"""
        self.logger.info("Testing decision data consistency...")

        # Step 1: Create decisions with known data
        test_decisions = [
            {
                "head": "use_python_3_12",
                "value": "Python 3.12 provides best performance",
                "entities": ["python", "version", "performance"],
                "files": ["requirements.txt", "pyproject.toml"],
            },
            {
                "head": "use_postgresql",
                "value": "PostgreSQL meets performance requirements",
                "entities": ["database", "postgresql", "performance"],
                "files": ["config/database.yml", "docs/architecture.md"],
            },
        ]

        decision_ids = []
        for decision in test_decisions:
            decision_id = self.storage.store_decision(
                session_id=self.session_id,
                decision_head=decision["head"],
                context_value=decision["value"],
                entities=decision["entities"],
                files=decision["files"],
                relevance_score=0.9,
            )
            decision_ids.append(decision_id)
            self.assertTrue(decision_id)

        # Step 2: Verify data integrity
        for i, decision_id in enumerate(decision_ids):
            # Retrieve decision by ID - use retrieve_context with specific key
            decisions = self.storage.retrieve_context(self.session_id, "decision", limit=100)
            self.assertIsNotNone(decisions, "retrieve_context should not return None")
            decision = None
            for d in decisions:
                if d.get("context_key") == test_decisions[i]["head"]:
                    decision = d
                    break
            self.assertIsNotNone(decision)

            # Verify all fields match
            if decision is None:
                self.fail(f"Decision {test_decisions[i]['head']} not found")
            self.assertEqual(decision["decision_head"], test_decisions[i]["head"])
            self.assertEqual(decision["context_value"], test_decisions[i]["value"])

            # Verify entities (JSONB field)
            stored_entities = decision.get("entities", [])
            if isinstance(stored_entities, str):
                stored_entities = json.loads(stored_entities)
            self.assertEqual(stored_entities, test_decisions[i]["entities"])

            # Verify files (JSONB field)
            stored_files = decision.get("files", [])
            if isinstance(stored_files, str):
                stored_files = json.loads(stored_files)
            self.assertEqual(stored_files, test_decisions[i]["files"])

        # Step 3: Test supersedence consistency
        # Create a superseding decision
        superseding_id = self.storage.store_decision(
            session_id=self.session_id,
            decision_head="use_python_3_13",
            context_value="Python 3.13 provides even better performance",
            entities=["python", "version", "performance"],
            files=["requirements.txt", "pyproject.toml"],
        )
        self.assertTrue(superseding_id)

        # Verify the old decision is marked as superseded
        old_decisions = self.storage.retrieve_context(self.session_id, "decision", limit=100)
        self.assertIsNotNone(old_decisions, "retrieve_context should not return None")
        old_decision = None
        for d in old_decisions:
            if d.get("decision_head") == "use_python_3_12":
                old_decision = d
                break
        if old_decision is None:
            self.fail("Old decision not found")
        self.assertEqual(old_decision["decision_status"], "superseded")

        # Step 4: Test data consistency after updates
        # Update a decision
        update_success = self.storage.update_decision_status(self.session_id, "use_postgresql", "closed")
        self.assertTrue(update_success)

        # Verify update
        updated_decisions = self.storage.retrieve_context(self.session_id, "decision", limit=100)
        self.assertIsNotNone(updated_decisions, "retrieve_context should not return None")
        updated_decision = None
        for d in updated_decisions:
            if d.get("decision_head") == "use_postgresql":
                updated_decision = d
                break
        if updated_decision is None:
            self.fail("Updated decision not found")
        self.assertEqual(updated_decision["decision_status"], "closed")

        self.logger.info("✅ Decision data consistency test passed")

    def test_06_end_to_end_decision_workflow(self):
        """Test complete end-to-end decision workflow"""
        self.logger.info("Testing end-to-end decision workflow...")

        # Step 1: Create session and initial context
        session_id = self.session_manager.create_session("workflow_user", "End-to-End Workflow Test")

        # Step 2: Store initial conversation context
        self.storage.store_context(
            session_id=session_id,
            context_type="conversation",
            context_key="project_requirements",
            context_value="Need high-performance database and modern Python version",
            relevance_score=0.9,
        )

        # Step 3: Make initial decisions
        self.storage.store_decision(
            session_id=session_id,
            decision_head="use_python_3_11",
            context_value="Python 3.11 offers good performance",
            entities=["python", "version", "performance"],
            files=["requirements.txt"],
        )

        self.storage.store_decision(
            session_id=session_id,
            decision_head="use_postgresql",
            context_value="PostgreSQL provides excellent reliability",
            entities=["database", "postgresql", "reliability"],
            files=["config/database.yml"],
        )

        # Step 4: Update decisions based on new information
        self.storage.store_decision(
            session_id=session_id,
            decision_head="use_python_3_12",
            context_value="Python 3.12 provides even better performance",
            entities=["python", "version", "performance"],
            files=["requirements.txt"],
        )

        # Step 5: Test decision evaluation
        test_cases = [
            TestCase(
                query="Python version selection for the project",
                expected_decisions=["use_python_3_12"],
                category="decision",
            ),
            TestCase(
                query="Database selection for the project",
                expected_decisions=["use_postgresql"],
                category="decision",
            ),
        ]

        evaluation_result = self.evaluator.evaluate_decision_retrieval(test_cases=test_cases, session_id=session_id)

        self.assertIsNotNone(evaluation_result)
        self.assertEqual(evaluation_result.total_queries, 2)

        # Step 6: Test performance optimization
        decisions, cache_hit = self.optimizer.optimize_decision_retrieval(
            session_id=session_id, query_entities=["python", "database"]
        )

        self.assertTrue(len(decisions) > 0)

        # Step 7: Test memory rehydration with decisions
        rehydration_result = self.rehydrator.rehydrate_memory_simple(
            query="What are our technology decisions for this project?",
            session_id=session_id,
            user_id="workflow_user",
            limit=10,
        )

        self.assertIsNotNone(rehydration_result)
        self.assertTrue(len(rehydration_result.merged_contexts) > 0)

        # Verify decision context is included
        decision_contexts = [
            ctx
            for ctx in rehydration_result.merged_contexts
            if hasattr(ctx, "context_type") and ctx.context_type == "decision"
        ]
        self.assertTrue(len(decision_contexts) > 0)

        self.logger.info("✅ End-to-end decision workflow test passed")

    def test_07_performance_under_load(self):
        """Test system performance under load"""
        self.logger.info("Testing performance under load...")

        # Step 1: Create many decisions to simulate load
        num_decisions = 50
        for i in range(num_decisions):
            self.storage.store_decision(
                session_id=self.session_id,
                decision_head=f"load_test_decision_{i}",
                context_value=f"Load test decision {i}",
                entities=["load_test", f"decision_{i}"],
                relevance_score=0.5 + (i * 0.01),
            )

        # Step 2: Test retrieval performance
        start_time = time.time()
        merge_result = self.merger.merge_decision_contexts(session_id=self.session_id, query_entities=["load_test"])
        retrieval_time = (time.time() - start_time) * 1000

        self.assertIsNotNone(merge_result)
        self.assertTrue(len(merge_result.merged_contexts) > 0)

        # Step 3: Verify performance targets
        self.assertLess(retrieval_time, 150, f"Retrieval time {retrieval_time:.2f}ms exceeds 150ms target")

        # Step 4: Test concurrent retrieval under load
        num_concurrent = 10
        retrieval_times = []
        errors = []

        def load_worker():
            try:
                start = time.time()
                _ = self.merger.merge_decision_contexts(session_id=self.session_id, query_entities=["load_test"])
                retrieval_time = (time.time() - start) * 1000
                retrieval_times.append(retrieval_time)
            except Exception as e:
                errors.append(str(e))

        # Start concurrent workers
        threads = []
        for _ in range(num_concurrent):
            thread = threading.Thread(target=load_worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Verify no errors and performance targets met
        self.assertEqual(len(errors), 0, f"Errors under load: {errors}")
        self.assertEqual(len(retrieval_times), num_concurrent)

        # Check that all retrievals meet performance targets
        for retrieval_time in retrieval_times:
            self.assertLess(
                retrieval_time, 150, f"Concurrent retrieval time {retrieval_time:.2f}ms exceeds 150ms target"
            )

        avg_retrieval_time = sum(retrieval_times) / len(retrieval_times)
        self.logger.info(f"✅ Performance under load test passed: avg retrieval time {avg_retrieval_time:.2f}ms")


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
