#!/usr/bin/env python3.11
"""
Validation and Monitoring Test Suite for Cursor Context Engineering
Tests that the system is working correctly and not hallucinating
"""

import json
import logging

from src.dspy_modules.cursor_model_router import (
    CursorModel,
    ModelRoutingMonitor,
    ModelRoutingValidator,
    create_validated_cursor_model_router,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_validation_system():
    """Test the validation system for hallucination detection"""

    print("🔍 Testing Validation System")
    print("=" * 60)

    validator = ModelRoutingValidator()

    # Test cases with known expected outcomes
    test_cases = [
        {
            "name": "Valid Complex Coding Task",
            "query": "Implement a comprehensive authentication system with JWT tokens, role-based access control, and rate limiting",
            "routing_result": {
                "status": "success",
                "selected_model": CursorModel.GPT_4_TURBO.value,
                "confidence": 0.85,
                "reasoning": "This is a complex coding task requiring structured implementation. GPT-4 Turbo is ideal for code generation with good practices.",
                "routing_metadata": {"task_type": "coding", "complexity": "complex"},
            },
            "expected_valid": True,
            "expected_hallucination": False,
        },
        {
            "name": "Suspicious High Confidence",
            "query": "Simple hello world",
            "routing_result": {
                "status": "success",
                "selected_model": CursorModel.CLAUDE_3_OPUS.value,
                "confidence": 0.99,  # Suspiciously high for simple task
                "reasoning": "This requires the most powerful model",  # Poor reasoning
                "routing_metadata": {"task_type": "general", "complexity": "simple"},
            },
            "expected_valid": False,
            "expected_hallucination": True,
        },
        {
            "name": "Poor Reasoning Quality",
            "query": "Fix a bug in my code",
            "routing_result": {
                "status": "success",
                "selected_model": CursorModel.CURSOR_NATIVE_AI.value,
                "confidence": 0.6,
                "reasoning": "Yes",  # Very poor reasoning
                "routing_metadata": {"task_type": "debugging", "complexity": "simple"},
            },
            "expected_valid": False,
            "expected_hallucination": True,
        },
        {
            "name": "Invalid Model Selection",
            "query": "Complex architectural design",
            "routing_result": {
                "status": "success",
                "selected_model": "invalid-model-name",
                "confidence": 0.7,
                "reasoning": "This model is best for complex tasks",
                "routing_metadata": {"task_type": "planning", "complexity": "complex"},
            },
            "expected_valid": False,
            "expected_hallucination": True,
        },
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['name']}")
        print(f"Query: {test_case['query']}")

        # Validate the routing result
        validation_result = validator.validate_routing_decision(test_case["routing_result"], test_case["query"])

        # Check if validation matches expectations
        is_valid = validation_result["is_valid"]
        hallucination_detected = validation_result["hallucination_detected"]

        expected_valid = test_case["expected_valid"]
        expected_hallucination = test_case["expected_hallucination"]

        validation_passed = (is_valid == expected_valid) and (hallucination_detected == expected_hallucination)

        print(f"✅ Valid: {is_valid} (expected: {expected_valid})")
        print(f"🚨 Hallucination: {hallucination_detected} (expected: {expected_hallucination})")
        print(f"📊 Confidence Score: {validation_result['confidence_score']:.2f}")
        print(f"🎯 Test Result: {'✅ PASS' if validation_passed else '❌ FAIL'}")

        # Show validation checks
        checks = validation_result["validation_checks"]
        print("🔧 Validation Checks:")
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {check}: {status}")

        if validation_result["recommendations"]:
            print("💡 Recommendations:")
            for rec in validation_result["recommendations"]:
                print(f"  - {rec}")

        results.append(
            {"test": i, "name": test_case["name"], "passed": validation_passed, "validation_result": validation_result}
        )

    # Print summary
    passed_tests = sum(1 for r in results if r["passed"])
    print(f"\n📊 Validation Test Summary: {passed_tests}/{len(results)} passed")

    return results

def test_monitoring_system():
    """Test the monitoring system for anomaly detection"""

    print("\n📊 Testing Monitoring System")
    print("=" * 60)

    monitor = ModelRoutingMonitor()

    # Simulate various routing scenarios
    test_scenarios = [
        {
            "name": "Normal Routing",
            "query": "Implement a simple function",
            "routing_result": {"status": "success", "selected_model": CursorModel.CURSOR_NATIVE_AI.value},
            "latency_ms": 150,
            "expected_anomaly": False,
        },
        {
            "name": "High Latency Anomaly",
            "query": "Complex analysis",
            "routing_result": {"status": "success", "selected_model": CursorModel.CLAUDE_3_OPUS.value},
            "latency_ms": 6000,  # 6 seconds - anomaly
            "expected_anomaly": True,
        },
        {
            "name": "Failed Routing",
            "query": "Invalid query",
            "routing_result": {"status": "error", "error": "Model not available"},
            "latency_ms": 200,
            "expected_anomaly": False,
        },
        {
            "name": "Model Bias Anomaly",
            "query": "Another simple task",
            "routing_result": {
                "status": "success",
                "selected_model": CursorModel.CLAUDE_3_OPUS.value,  # Same model repeatedly
            },
            "latency_ms": 180,
            "expected_anomaly": True,
        },
    ]

    results = []

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🔍 Scenario {i}: {scenario['name']}")
        print(f"Query: {scenario['query']}")
        print(f"Latency: {scenario['latency_ms']}ms")

        # Log the routing attempt
        monitor.log_routing_attempt(scenario["query"], scenario["routing_result"], scenario["latency_ms"])

        # Get performance report
        report = monitor.get_performance_report()

        print(f"📊 Success Rate: {report.get('success_rate', 0):.2f}")
        print(f"📈 Total Routes: {report.get('total_routes', 0)}")
        print(f"🚨 Anomalies: {report.get('anomaly_count', 0)}")

        results.append({"scenario": i, "name": scenario["name"], "report": report})

    # Print final monitoring report
    final_report = monitor.get_performance_report()
    print("\n📊 Final Monitoring Report:")
    print(f"  Total Routes: {final_report.get('total_routes', 0)}")
    print(f"  Success Rate: {final_report.get('success_rate', 0):.2f}")
    print(f"  Average Latency: {final_report.get('average_latency_ms', 0):.1f}ms")
    print(f"  Anomaly Count: {final_report.get('anomaly_count', 0)}")

    return results

def test_real_routing_with_validation():
    """Test real routing with validation enabled"""

    print("\n🎯 Testing Real Routing with Validation")
    print("=" * 60)

    router = create_validated_cursor_model_router()

    # Test queries that should trigger different models
    test_queries = [
        {
            "query": "Implement a REST API with authentication",
            "description": "Complex coding task",
            "expected_model": CursorModel.GPT_4_TURBO.value,
        },
        {
            "query": "Analyze the performance implications of different database choices",
            "description": "Complex reasoning task",
            "expected_model": CursorModel.CLAUDE_3_OPUS.value,
        },
        {
            "query": "Fix this syntax error",
            "description": "Simple debugging task",
            "expected_model": CursorModel.CURSOR_NATIVE_AI.value,
        },
        {
            "query": "Design a microservices architecture",
            "description": "Complex planning task",
            "expected_model": CursorModel.CLAUDE_3_OPUS.value,
        },
    ]

    results = []

    for i, test_case in enumerate(test_queries, 1):
        print(f"\n🔍 Real Test {i}: {test_case['description']}")
        print(f"Query: {test_case['query']}")

        # Route the query
        result = router.route_query(test_case["query"])

        if result["status"] == "success":
            selected_model = result["selected_model"]
            expected_model = test_case["expected_model"]
            match = selected_model == expected_model

            print(f"✅ Selected: {selected_model}")
            print(f"🎯 Expected: {expected_model}")
            print(f"📊 Match: {'✅' if match else '❌'}")
            print(f"⚡ Confidence: {result['confidence']:.2f}")

            # Show validation results
            if "validation" in result:
                validation = result["validation"]
                print("🔍 Validation:")
                print(f"  Valid: {validation['is_valid']}")
                print(f"  Hallucination: {validation['hallucination_detected']}")
                print(f"  Confidence Score: {validation['confidence_score']:.2f}")

                # Show validation checks
                checks = validation.get("validation_checks", {})
                for check, result_check in checks.items():
                    status = "✅" if result_check else "❌"
                    print(f"  {check}: {status}")

            # Show monitoring info
            if "monitoring" in result:
                monitoring = result["monitoring"]
                print("📊 Monitoring:")
                print(f"  Latency: {monitoring['latency_ms']:.1f}ms")

            results.append(
                {
                    "test": i,
                    "description": test_case["description"],
                    "selected_model": selected_model,
                    "expected_model": expected_model,
                    "match": match,
                    "validation": result.get("validation", {}),
                    "monitoring": result.get("monitoring", {}),
                }
            )
        else:
            print(f"❌ Routing failed: {result.get('error', 'Unknown error')}")
            results.append(
                {"test": i, "description": test_case["description"], "error": result.get("error", "Unknown error")}
            )

    # Print comprehensive report
    comprehensive_report = router.get_comprehensive_report()
    print("\n📊 Comprehensive Report:")
    print(json.dumps(comprehensive_report, indent=2))

    return results

def test_hallucination_detection():
    """Test specific hallucination detection scenarios"""

    print("\n🚨 Testing Hallucination Detection")
    print("=" * 60)

    validator = ModelRoutingValidator()

    # Test cases designed to trigger hallucination detection
    hallucination_tests = [
        {
            "name": "Low Confidence + Poor Reasoning",
            "routing_result": {
                "status": "success",
                "selected_model": CursorModel.CLAUDE_3_OPUS.value,
                "confidence": 0.3,  # Low confidence
                "reasoning": "Yes",  # Poor reasoning
                "routing_metadata": {"task_type": "coding", "complexity": "simple"},
            },
            "expected_hallucination": True,
        },
        {
            "name": "Poor Model Capability Match",
            "routing_result": {
                "status": "success",
                "selected_model": CursorModel.CURSOR_NATIVE_AI.value,  # Wrong for complex reasoning
                "confidence": 0.8,
                "reasoning": "This model is best for complex reasoning tasks",
                "routing_metadata": {"task_type": "reasoning", "complexity": "complex"},
            },
            "expected_hallucination": True,
        },
        {
            "name": "Invalid Context Engineering Strategy",
            "routing_result": {
                "status": "success",
                "selected_model": CursorModel.GPT_4_TURBO.value,
                "confidence": 0.7,
                "reasoning": "GPT-4 Turbo is best for this task",
                "context_engineering": "Use the wrong approach",  # Invalid strategy
                "routing_metadata": {"task_type": "coding", "complexity": "moderate"},
            },
            "expected_hallucination": True,
        },
        {
            "name": "Valid Routing Decision",
            "routing_result": {
                "status": "success",
                "selected_model": CursorModel.GPT_4_TURBO.value,
                "confidence": 0.85,
                "reasoning": "This is a coding task requiring structured implementation. GPT-4 Turbo is ideal for code generation with good practices.",
                "context_engineering": "Focus on clean, efficient code with good practices",
                "routing_metadata": {"task_type": "coding", "complexity": "moderate"},
            },
            "expected_hallucination": False,
        },
    ]

    results = []

    for i, test_case in enumerate(hallucination_tests, 1):
        print(f"\n🔍 Hallucination Test {i}: {test_case['name']}")

        validation_result = validator.validate_routing_decision(test_case["routing_result"], "test query")

        hallucination_detected = validation_result["hallucination_detected"]
        expected_hallucination = test_case["expected_hallucination"]

        test_passed = hallucination_detected == expected_hallucination

        print(f"🚨 Hallucination Detected: {hallucination_detected}")
        print(f"🎯 Expected: {expected_hallucination}")
        print(f"📊 Test Result: {'✅ PASS' if test_passed else '❌ FAIL'}")
        print(f"🔍 Confidence Score: {validation_result['confidence_score']:.2f}")

        if validation_result["recommendations"]:
            print("💡 Recommendations:")
            for rec in validation_result["recommendations"]:
                print(f"  - {rec}")

        results.append(
            {
                "test": i,
                "name": test_case["name"],
                "passed": test_passed,
                "hallucination_detected": hallucination_detected,
                "expected_hallucination": expected_hallucination,
            }
        )

    # Print summary
    passed_tests = sum(1 for r in results if r["passed"])
    print(f"\n📊 Hallucination Detection Summary: {passed_tests}/{len(results)} passed")

    return results

def main():
    """Run all validation and monitoring tests"""

    print("🚀 Cursor Context Engineering Validation & Monitoring Test Suite")
    print("=" * 80)

    all_results = {}

    try:
        # Test validation system
        all_results["validation"] = test_validation_system()

        # Test monitoring system
        all_results["monitoring"] = test_monitoring_system()

        # Test real routing with validation
        all_results["real_routing"] = test_real_routing_with_validation()

        # Test hallucination detection
        all_results["hallucination"] = test_hallucination_detection()

        # Print overall summary
        print("\n" + "=" * 80)
        print("📊 OVERALL TEST SUMMARY")
        print("=" * 80)

        total_tests = 0
        total_passed = 0

        for test_type, results in all_results.items():
            if results:
                passed = sum(1 for r in results if r.get("passed", False))
                total = len(results)
                total_tests += total
                total_passed += passed

                print(f"{test_type.upper()}: {passed}/{total} passed")

        print(f"\n🎯 OVERALL: {total_passed}/{total_tests} tests passed")

        if total_passed == total_tests:
            print("✅ All validation and monitoring tests passed!")
            print("✅ The context engineering system is working correctly!")
        else:
            print("⚠️  Some tests failed. Review the results above.")

        # Save results
        with open("validation_test_results.json", "w") as f:
            json.dump(all_results, f, indent=2)
        print("📁 Results saved to validation_test_results.json")

    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
