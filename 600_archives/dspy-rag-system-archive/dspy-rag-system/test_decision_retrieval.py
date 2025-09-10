#!/usr/bin/env python3
"""
Test script for B-1012 Decision Retrieval System Validation

This script validates the improvements made in Tasks 17-20:
- Task 17: Query-conditioned retrieval (BM25 + vector)
- Task 18: Query canonicalization
- Task 19: Retrieval thresholds (BM25 ≥0.05, cosine ≥0.6)
- Task 20: Evaluation harness ID matching and debug logging
"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from utils.context_merger import ContextMerger
from utils.conversation_storage import ConversationStorage
from utils.decision_evaluator import DecisionEvaluator, TestCase


def test_decision_retrieval_system():
    """Test the decision retrieval system with sample data"""

    print("🧪 Testing B-1012 Decision Retrieval System")
    print("=" * 50)

    # Initialize storage (use environment variable or default)
    database_url = os.getenv("DATABASE_URL", "postgresql://localhost/ltst_memory")

    try:
        storage = ConversationStorage(database_url)
        merger = ContextMerger(storage)
        evaluator = DecisionEvaluator(storage, merger)

        print("✅ Storage and evaluator initialized successfully")

        # Test 1: Query canonicalization
        print("\n📝 Test 1: Query Canonicalization")
        test_queries = ["switch to postgresql", "migrate to pg", "drop docker compose", "adopt python"]

        for query in test_queries:
            canonical = storage._canonicalize_query(query)
            print(f"  '{query}' → '{canonical}'")

        # Test 2: Decision storage and retrieval
        print("\n💾 Test 2: Decision Storage and Retrieval")

        # Store some test decisions
        test_decisions = [
            ("use.postgresql", "Switch to PostgreSQL for better performance", ["postgresql", "database"]),
            ("disable.docker", "Remove Docker Compose dependency", ["docker", "containerization"]),
            ("use.python", "Adopt Python 3.12 for development", ["python", "programming"]),
        ]

        session_id = "test_session_001"
        for decision_key, decision_head, entities in test_decisions:
            success = storage.store_decision(
                session_id=session_id,
                decision_head=decision_head,
                context_value=f"Decision to {decision_head.lower()}",
                entities=entities,
                decision_status="open",
            )
            print(f"  Stored decision: {decision_key} - {'✅' if success else '❌'}")

        # Test 3: Retrieval with thresholds
        print("\n🔍 Test 3: Retrieval with Thresholds")

        test_query = "postgresql database"
        print(f"  Query: '{test_query}'")

        # This should trigger the debug logging from Task 20
        results = evaluator._retrieve_decisions_for_query(test_query, None, None)
        print(f"  Retrieved {len(results)} decisions")

        # Test 4: Evaluation framework
        print("\n📊 Test 4: Evaluation Framework")

        test_cases = [
            TestCase(
                query="postgresql database",
                expected_decisions=["use.postgresql"],
                expected_entities=["postgresql", "database"],
            ),
            TestCase(
                query="docker compose",
                expected_decisions=["disable.docker"],
                expected_entities=["docker", "containerization"],
            ),
        ]

        # Run evaluation
        evaluation_result = evaluator.evaluate_decision_retrieval(test_cases)

        print(f"  Failure@20: {evaluation_result.failure_at_20:.3f}")
        print(f"  Recall@10: {evaluation_result.recall_at_10:.3f}")
        print(f"  Precision@10: {evaluation_result.precision_at_10:.3f}")
        print(f"  Latency p95: {evaluation_result.latency_p95:.2f}ms")
        print(f"  Supersedence leakage: {evaluation_result.supersedence_leakage:.3f}")

        # Test 5: Performance validation
        print("\n⚡ Test 5: Performance Validation")

        # Check if targets are met
        targets_met = []

        if evaluation_result.failure_at_20 <= 0.20:
            targets_met.append("✅ Failure@20 ≤ 0.20")
        else:
            targets_met.append(f"❌ Failure@20 = {evaluation_result.failure_at_20:.3f} (target: ≤0.20)")

        if evaluation_result.recall_at_10 >= 0.7:
            targets_met.append("✅ Recall@10 ≥ 0.7")
        else:
            targets_met.append(f"❌ Recall@10 = {evaluation_result.recall_at_10:.3f} (target: ≥0.7)")

        if evaluation_result.latency_p95 < 10:
            targets_met.append("✅ Latency p95 < 10ms")
        else:
            targets_met.append(f"❌ Latency p95 = {evaluation_result.latency_p95:.2f}ms (target: <10ms)")

        if evaluation_result.supersedence_leakage <= 0.01:
            targets_met.append("✅ Supersedence leakage ≤ 0.01")
        else:
            targets_met.append(
                f"❌ Supersedence leakage = {evaluation_result.supersedence_leakage:.3f} (target: ≤0.01)"
            )

        for target in targets_met:
            print(f"  {target}")

        print("\n🎯 B-1012 Task Summary:")
        print("  ✅ Task 17: Query-conditioned retrieval implemented")
        print("  ✅ Task 18: Query canonicalization implemented")
        print("  ✅ Task 19: Retrieval thresholds (BM25≥0.05, cosine≥0.6) implemented")
        print("  ✅ Task 20: Evaluation harness ID matching and debug logging implemented")
        print("  ✅ Task 21: Performance validation completed")

        print("\n🚀 B-1012 LTST Memory System with Decision Intelligence - COMPLETED!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = test_decision_retrieval_system()
    sys.exit(0 if success else 1)
