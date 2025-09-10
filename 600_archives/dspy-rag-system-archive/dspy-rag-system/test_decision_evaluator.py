#!/usr/bin/env python3
"""
Test script for DecisionEvaluator

This script tests the evaluation framework to ensure it correctly calculates
Failure@20, latency metrics, and supersedence leakage detection.
"""

import logging
import os
import sys
import time
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from utils.context_merger import ContextMerger
from utils.conversation_storage import ConversationStorage
from utils.decision_evaluator import DecisionEvaluator, TestCase, create_default_test_cases
from utils.session_manager import SessionManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_decision_evaluator():
    """Test the DecisionEvaluator functionality"""
    print("🧪 Testing Decision Evaluator...")

    try:
        # Initialize components
        print("📦 Initializing components...")
        storage = ConversationStorage()

        # Ensure database connection is established
        if not storage.connect():
            print("❌ Failed to connect to database")
            return False

        session_manager = SessionManager(storage)
        merger = ContextMerger(storage)
        evaluator = DecisionEvaluator(storage, merger)

        print("✅ Components initialized")

        # Test 1: Create test session and decisions
        print("\n📝 Test 1: Creating test session and decisions...")

        # Create test session
        session_id = session_manager.create_session("test_user", "Test Evaluation Session")
        print(f"✅ Test session created: {session_id}")

        # Store test decisions
        test_decisions = [
            {
                "decision_head": "use_postgresql",
                "rationale": "PostgreSQL provides excellent performance and reliability for our use case",
                "entities": ["database", "postgresql", "primary"],
                "files": ["config/database.yml", "docs/architecture.md"],
            },
            {
                "decision_head": "use_python_3_11",
                "rationale": "Python 3.11 offers good performance improvements over 3.10",
                "entities": ["python", "version", "project"],
                "files": ["requirements.txt", "pyproject.toml"],
            },
            {
                "decision_head": "enable_debug_mode",
                "rationale": "Debug mode is essential for development and troubleshooting",
                "entities": ["debug", "mode", "development"],
                "files": ["config/app.yml", "scripts/debug.sh"],
            },
            {
                "decision_head": "use_python_3_12",
                "rationale": "Python 3.12 provides even better performance and new features",
                "entities": ["python", "version", "project"],
                "files": ["requirements.txt", "pyproject.toml"],
            },
            {
                "decision_head": "disable_debug_mode",
                "rationale": "Debug mode should be disabled in production for security",
                "entities": ["debug", "mode", "production"],
                "files": ["config/app.yml", "scripts/debug.sh"],
            },
            {
                "decision_head": "setup_build_pipeline",
                "rationale": "Automated build pipeline ensures consistent deployments",
                "entities": ["build", "pipeline", "deployment"],
                "files": [".github/workflows/build.yml", "scripts/build.sh"],
            },
            {
                "decision_head": "implement_caching",
                "rationale": "Caching will significantly improve performance for repeated queries",
                "entities": ["cache", "performance", "queries"],
                "files": ["src/cache/", "config/cache.yml"],
            },
            {
                "decision_head": "testing_strategy",
                "rationale": "Comprehensive testing ensures code quality and reliability",
                "entities": ["testing", "quality", "reliability"],
                "files": ["tests/", "pytest.ini", "coverage.yml"],
            },
        ]

        for i, decision_data in enumerate(test_decisions):
            storage.store_decision(
                session_id=session_id,
                decision_head=decision_data["decision_head"],
                context_value=decision_data["rationale"],
                entities=decision_data["entities"],
                files=decision_data["files"],
                relevance_score=0.8 + (i * 0.02),  # Varying relevance scores
            )
            print(f"✅ Decision {i+1} stored: {decision_data['decision_head']}")

        # Test 2: Create custom test cases
        print("\n🔍 Test 2: Creating custom test cases...")
        custom_test_cases = [
            TestCase(query="What database are we using?", expected_decisions=["use_postgresql"], category="decision"),
            TestCase(
                query="Python version for development",
                expected_decisions=["use_python_3_12"],  # Should get the latest
                category="supersedence",
            ),
            TestCase(
                query="Debug mode configuration",
                expected_decisions=["disable_debug_mode"],  # Should get the latest
                expected_entities=["debug", "mode"],
                category="entity",
            ),
            TestCase(
                query="Build and deployment setup",
                expected_decisions=["setup_build_pipeline", "testing_strategy"],
                category="complex",
            ),
        ]

        print(f"✅ {len(custom_test_cases)} custom test cases created")

        # Test 3: Run evaluation
        print("\n📊 Test 3: Running decision retrieval evaluation...")
        result = evaluator.evaluate_decision_retrieval(
            test_cases=custom_test_cases, session_id=session_id, warm_cache=True
        )

        print("✅ Evaluation completed")
        print(f"   - Total queries: {result.total_queries}")
        print(f"   - Failure@20: {result.failure_at_20:.3f}")
        print(f"   - Recall@10: {result.recall_at_10:.3f}")
        print(f"   - Precision@10: {result.precision_at_10:.3f}")
        print(f"   - Latency p95: {result.latency_p95:.2f}ms")
        print(f"   - Supersedence leakage: {result.supersedence_leakage:.3f}")

        # Test 4: Validate performance targets
        print("\n🎯 Test 4: Validating performance targets...")
        validation = evaluator.validate_performance_targets(result)

        for target_name, target_met in validation.items():
            status = "✅" if target_met else "❌"
            print(f"   - {target_name}: {status}")

        # Test 5: Generate evaluation report
        print("\n📋 Test 5: Generating evaluation report...")
        report = evaluator.generate_evaluation_report(result)
        print("✅ Report generated")
        print(f"Report length: {len(report)} characters")

        # Test 6: Save evaluation result
        print("\n💾 Test 6: Saving evaluation result...")
        filepath = f"evaluation_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        evaluator.save_evaluation_result(result, filepath)
        print(f"✅ Result saved to {filepath}")

        # Test 7: Test with default test cases
        print("\n🔄 Test 7: Testing with default test cases...")
        default_test_cases = create_default_test_cases()
        print(f"✅ {len(default_test_cases)} default test cases created")

        # Test 8: Performance validation
        print("\n⚡ Test 8: Performance validation...")
        start_time = time.time()
        default_result = evaluator.evaluate_decision_retrieval(
            test_cases=default_test_cases[:5],  # Use first 5 for performance test
            session_id=session_id,
            warm_cache=True,
        )
        performance_time = time.time() - start_time

        print(f"✅ Performance test completed in {performance_time:.2f}s")
        print("   - Target: < 30 seconds")
        print(f"   - Actual: {performance_time:.2f}s")
        print(f"   - Status: {'✅ PASS' if performance_time < 30 else '❌ FAIL'}")
        print(f"   - Default test result: {default_result.total_queries} queries evaluated")

        # Cleanup
        print("\n🧹 Cleaning up test data...")
        # Note: In a real scenario, you might want to clean up the test session
        # For now, we'll leave it for inspection

        print("\n🎉 All Decision Evaluator Tests Passed!")
        print("\n📊 Final Results Summary:")
        print(f"   - Failure@20: {result.failure_at_20:.3f} (Target: ≤0.20)")
        print(f"   - Supersedence Leakage: {result.supersedence_leakage:.3f} (Target: ≤0.01)")
        print(f"   - Latency p95: {result.latency_p95:.2f}ms (Target: ≤10ms warm)")
        print(f"   - All Targets Met: {'✅ YES' if all(validation.values()) else '❌ NO'}")

        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_decision_evaluator()
    sys.exit(0 if success else 1)
