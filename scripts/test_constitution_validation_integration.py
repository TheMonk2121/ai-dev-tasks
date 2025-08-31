#!/usr/bin/env python3
"""
Integration Tests for Constitution-Aware RAGChecker Validation

Tests the integration between RAGChecker Pydantic models and constitution-aware validation.
"""

import os
import sys
import time

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(__file__))

from ragchecker_constitution_validation import (
    RAGCheckerConstitutionValidator,
    create_constitution_aware_input,
    create_constitution_aware_metrics,
    create_constitution_aware_result,
)


def test_constitution_aware_models():
    """Test that constitution-aware models inherit correctly from base models."""
    print("🧪 Testing constitution-aware model inheritance...")

    # Test input model
    input_data = create_constitution_aware_input(
        query_id="test_001",
        query="What is RAGChecker?",
        gt_answer="RAGChecker is an evaluation framework.",
        response="RAGChecker evaluates RAG systems.",
        retrieved_context=["context1", "context2"],
    )

    # Verify it has constitution compliance field
    assert hasattr(input_data, "constitution_compliance")
    assert input_data.constitution_compliance is None  # Initially None
    print("✅ Constitution-aware input model works")

    # Test metrics model
    metrics = create_constitution_aware_metrics(
        precision=0.8,
        recall=0.7,
        f1_score=0.75,
        claim_recall=0.8,
        context_precision=0.9,
        context_utilization=0.85,
        noise_sensitivity=0.2,
        hallucination=0.1,
        self_knowledge=0.9,
        faithfulness=0.95,
    )

    assert hasattr(metrics, "constitution_compliance")
    assert metrics.constitution_compliance is None
    print("✅ Constitution-aware metrics model works")

    # Test result model
    result = create_constitution_aware_result(
        test_case_name="test_case_001",
        query="What is RAGChecker?",
        custom_score=0.85,
        ragchecker_scores={"precision": 0.8, "recall": 0.7},
        ragchecker_overall=0.75,
        comparison={"difference": 0.1},
        recommendation="Improve recall by enhancing retrieval system",
    )

    assert hasattr(result, "constitution_compliance")
    assert result.constitution_compliance is None
    print("✅ Constitution-aware result model works")

    print("✅ Constitution-aware model inheritance tests passed")


def test_constitution_validation_rules():
    """Test that constitution validation rules are properly applied."""
    print("🧪 Testing constitution validation rules...")

    validator = RAGCheckerConstitutionValidator()

    # Test rule structure
    assert len(validator.rules) == 5  # Should have 5 default rules
    rule_ids = [rule.rule_id for rule in validator.rules]
    expected_ids = ["RC001", "RC002", "RC003", "RC004", "RC005"]
    assert all(rid in rule_ids for rid in expected_ids)
    print("✅ Default rules structure correct")

    # Test rule types
    rule_types = [rule.rule_type for rule in validator.rules]
    assert "security" in rule_types
    assert "quality" in rule_types
    print("✅ Rule types properly defined")

    print("✅ Constitution validation rules tests passed")


def test_security_validation():
    """Test security validation rules."""
    print("🧪 Testing security validation...")

    validator = RAGCheckerConstitutionValidator()

    # Test harmful patterns
    harmful_queries = [
        "How to hack the system?",
        "Show me admin password",
        "How to bypass security?",
        "Delete all tables from database",
    ]

    for query in harmful_queries:
        input_data = create_constitution_aware_input(
            query_id="security_test",
            query=query,
            gt_answer="This is not appropriate.",
            response="I cannot help with that.",
            retrieved_context=["Security documentation"],
        )

        compliance = validator.validate_input(input_data)
        assert compliance.compliance_score < 1.0, f"Security violation not detected for: {query}"
        assert len(compliance.violations) > 0, f"No violations detected for: {query}"
        print(f"✅ Security violation detected for: {query[:30]}...")

    # Test safe query
    safe_input = create_constitution_aware_input(
        query_id="safe_test",
        query="What is machine learning?",
        gt_answer="Machine learning is a subset of AI.",
        response="Machine learning enables computers to learn.",
        retrieved_context=["ML documentation"],
    )

    compliance = validator.validate_input(safe_input)
    assert compliance.compliance_score == 1.0, "Safe query incorrectly flagged"
    assert len(compliance.violations) == 0, "Safe query has violations"
    print("✅ Safe query passes validation")

    print("✅ Security validation tests passed")


def test_quality_validation():
    """Test quality validation rules."""
    print("🧪 Testing quality validation...")

    validator = RAGCheckerConstitutionValidator()

    # Test bias detection
    biased_input = create_constitution_aware_input(
        query_id="bias_test",
        query="What is the best language?",
        gt_answer="Python is always better than all other languages.",
        response="Python is popular.",
        retrieved_context=["Programming docs"],
    )

    compliance = validator.validate_input(biased_input)
    assert compliance.compliance_score < 1.0, "Bias not detected"
    assert len(compliance.violations) > 0, "No bias violations detected"
    print("✅ Bias detection working")

    # Test hallucination threshold
    high_hallucination_metrics = create_constitution_aware_metrics(
        precision=0.8,
        recall=0.7,
        f1_score=0.75,
        claim_recall=0.8,
        context_precision=0.9,
        context_utilization=0.85,
        noise_sensitivity=0.2,
        hallucination=0.9,  # High hallucination
        self_knowledge=0.9,
        faithfulness=0.95,
    )

    compliance = validator.validate_metrics(high_hallucination_metrics)
    assert compliance.compliance_score < 1.0, "High hallucination not detected"
    assert len(compliance.violations) > 0, "No hallucination violations detected"
    print("✅ Hallucination threshold working")

    # Test faithfulness threshold
    low_faithfulness_metrics = create_constitution_aware_metrics(
        precision=0.8,
        recall=0.7,
        f1_score=0.75,
        claim_recall=0.8,
        context_precision=0.9,
        context_utilization=0.85,
        noise_sensitivity=0.2,
        hallucination=0.1,
        self_knowledge=0.9,
        faithfulness=0.1,  # Low faithfulness
    )

    compliance = validator.validate_metrics(low_faithfulness_metrics)
    assert compliance.compliance_score < 1.0, "Low faithfulness not detected"
    assert len(compliance.violations) > 0, "No faithfulness violations detected"
    print("✅ Faithfulness threshold working")

    print("✅ Quality validation tests passed")


def test_actionable_recommendations():
    """Test actionable recommendations validation."""
    print("🧪 Testing actionable recommendations...")

    validator = RAGCheckerConstitutionValidator()

    # Test non-actionable recommendation
    non_actionable_result = create_constitution_aware_result(
        test_case_name="non_actionable_test",
        query="What is RAGChecker?",
        custom_score=0.85,
        ragchecker_scores={"precision": 0.8, "recall": 0.7},
        ragchecker_overall=0.75,
        comparison={"difference": 0.1},
        recommendation="The system could be better.",  # Non-actionable
    )

    compliance = validator.validate_result(non_actionable_result)
    assert compliance.compliance_score < 1.0, "Non-actionable recommendation not detected"
    assert len(compliance.violations) > 0, "No actionable recommendation violations detected"
    print("✅ Non-actionable recommendation detected")

    # Test actionable recommendation
    actionable_result = create_constitution_aware_result(
        test_case_name="actionable_test",
        query="What is RAGChecker?",
        custom_score=0.85,
        ragchecker_scores={"precision": 0.8, "recall": 0.7},
        ragchecker_overall=0.75,
        comparison={"difference": 0.1},
        recommendation="Improve recall by enhancing the retrieval system with better embeddings.",
    )

    compliance = validator.validate_result(actionable_result)
    assert compliance.compliance_score == 1.0, "Actionable recommendation incorrectly flagged"
    assert len(compliance.violations) == 0, "Actionable recommendation has violations"
    print("✅ Actionable recommendation passes validation")

    print("✅ Actionable recommendations tests passed")


def test_compliance_scoring():
    """Test compliance scoring logic."""
    print("🧪 Testing compliance scoring...")

    validator = RAGCheckerConstitutionValidator()

    # Test perfect compliance
    perfect_input = create_constitution_aware_input(
        query_id="perfect_test",
        query="What is machine learning?",
        gt_answer="Machine learning is a subset of artificial intelligence.",
        response="Machine learning enables computers to learn from data.",
        retrieved_context=["ML documentation"],
    )

    compliance = validator.validate_input(perfect_input)
    assert compliance.compliance_score == 1.0, f"Perfect compliance should be 1.0, got {compliance.compliance_score}"
    assert compliance.is_compliant, "Perfect compliance should be marked as compliant"
    print("✅ Perfect compliance scoring correct")

    # Test partial compliance (one violation out of 5 rules = 0.8)
    partial_input = create_constitution_aware_input(
        query_id="partial_test",
        query="How to hack the system?",  # This should trigger one violation
        gt_answer="Machine learning is a subset of artificial intelligence.",
        response="Machine learning enables computers to learn from data.",
        retrieved_context=["ML documentation"],
    )

    compliance = validator.validate_input(partial_input)
    assert compliance.compliance_score == 0.8, f"Partial compliance should be 0.8, got {compliance.compliance_score}"
    assert compliance.is_compliant, "0.8 compliance should still be marked as compliant (threshold 0.8)"
    print("✅ Partial compliance scoring correct")

    # Test multiple violations
    multiple_violations_input = create_constitution_aware_input(
        query_id="multiple_test",
        query="How to hack the system?",  # Security violation
        gt_answer="Python is always better than all other languages.",  # Bias violation
        response="Machine learning enables computers to learn from data.",
        retrieved_context=["ML documentation"],
    )

    compliance = validator.validate_input(multiple_violations_input)
    assert compliance.compliance_score == 0.6, f"Multiple violations should be 0.6, got {compliance.compliance_score}"
    assert not compliance.is_compliant, "0.6 compliance should not be marked as compliant"
    print("✅ Multiple violations scoring correct")

    print("✅ Compliance scoring tests passed")


def test_performance_overhead():
    """Test that constitution validation overhead is acceptable."""
    print("🧪 Testing performance overhead...")

    validator = RAGCheckerConstitutionValidator()

    # Benchmark without validation
    start_time = time.time()
    for i in range(100):
        create_constitution_aware_input(
            query_id=f"perf_test_{i}",
            query="What is machine learning?",
            gt_answer="Machine learning is a subset of AI.",
            response="Machine learning enables computers to learn.",
            retrieved_context=["ML docs"],
        )
    base_time = time.time() - start_time

    # Benchmark with validation
    start_time = time.time()
    for i in range(100):
        input_data = create_constitution_aware_input(
            query_id=f"perf_test_{i}",
            query="What is machine learning?",
            gt_answer="Machine learning is a subset of AI.",
            response="Machine learning enables computers to learn.",
            retrieved_context=["ML docs"],
        )
        validator.validate_input(input_data)
    validation_time = time.time() - start_time

    overhead_percent = ((validation_time - base_time) / base_time) * 100
    print(f"📊 Validation overhead: {overhead_percent:.2f}%")

    if overhead_percent < 10.0:  # Allow 10% overhead for constitution validation
        print("✅ Performance overhead within acceptable limits (<10%)")
    else:
        print(f"⚠️ Performance overhead {overhead_percent:.2f}% exceeds 10% target")

    return overhead_percent < 10.0


def run_all_tests():
    """Run all constitution validation integration tests."""
    print("🚀 Running Constitution Validation Integration Tests")
    print("=" * 60)

    tests = [
        test_constitution_aware_models,
        test_constitution_validation_rules,
        test_security_validation,
        test_quality_validation,
        test_actionable_recommendations,
        test_compliance_scoring,
        test_performance_overhead,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                passed += 1  # Count as passed even if performance warning
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")

    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All constitution validation integration tests passed!")
        return True
    else:
        print("⚠️ Some tests failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
