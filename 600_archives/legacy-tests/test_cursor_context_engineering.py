#!/usr/bin/env python3.11
"""
Test script for Cursor Native AI Context Engineering
Demonstrates intelligent model routing using DSPy
"""

import json
import time

import pytest

from src.dspy_modules.cursor_model_router import CursorModel, create_cursor_model_router

@pytest.mark.tier1
@pytest.mark.integration
def test_context_engineering():
    """Test the context engineering system with various query types"""

    print("🎯 Testing Cursor Native AI Context Engineering")
    print("=" * 60)

    # Create router
    router = create_cursor_model_router()

    # Test queries with different characteristics
    test_queries = [
        {
            "query": "Implement a REST API with authentication and rate limiting",
            "description": "Complex coding task",
            "expected_model": CursorModel.GPT_4_TURBO.value,
        },
        {
            "query": "Analyze the performance implications of using Redis vs PostgreSQL for session storage",
            "description": "Complex reasoning task",
            "expected_model": CursorModel.CLAUDE_3_OPUS.value,
        },
        {
            "query": "Fix the syntax error in this function",
            "description": "Simple debugging task",
            "expected_model": CursorModel.MISTRAL_7B_INSTRUCT.value,
        },
        {
            "query": "Design a microservices architecture for an e-commerce platform",
            "description": "Complex planning task",
            "expected_model": CursorModel.CLAUDE_3_OPUS.value,
        },
        {
            "query": "Add input validation to this form",
            "description": "Simple coding task",
            "expected_model": CursorModel.MIXTRAL_8X7B.value,
        },
    ]

    results = []

    for i, test_case in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {test_case['description']}")
        print(f"Query: {test_case['query']}")

        start_time = time.time()

        # Route the query
        result = router.route_query(query=test_case["query"], urgency="medium")

        latency = (time.time() - start_time) * 1000

        if result["status"] == "success":
            selected_model = result["selected_model"]
            expected_model = test_case["expected_model"]
            match = selected_model == expected_model

            print(f"✅ Selected: {selected_model}")
            print(f"🎯 Expected: {expected_model}")
            print(f"📊 Match: {'✅' if match else '❌'}")
            print(f"🧠 Reasoning: {result['reasoning']}")
            print(f"⚡ Confidence: {result['confidence']:.2f}")
            print(f"⏱️  Latency: {latency:.1f}ms")

            # Show context engineering details
            if "context_engineering" in result:
                print(f"🔧 Context Engineering: {result['context_engineering']}")
                print(f"📝 Prompt Pattern: {result['prompt_pattern']}")

            results.append(
                {
                    "test": i,
                    "description": test_case["description"],
                    "selected_model": selected_model,
                    "expected_model": expected_model,
                    "match": match,
                    "confidence": result["confidence"],
                    "latency": latency,
                    "reasoning": result["reasoning"],
                }
            )
        else:
            print(f"❌ Routing failed: {result.get('error', 'Unknown error')}")
            results.append(
                {"test": i, "description": test_case["description"], "error": result.get("error", "Unknown error")}
            )

    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)

    successful_tests = [r for r in results if "error" not in r]
    failed_tests = [r for r in results if "error" in r]

    print(f"Total tests: {len(results)}")
    print(f"Successful: {len(successful_tests)}")
    print(f"Failed: {len(failed_tests)}")

    if successful_tests:
        matches = [r for r in successful_tests if r["match"]]
        avg_confidence = sum(r["confidence"] for r in successful_tests) / len(successful_tests)
        avg_latency = sum(r["latency"] for r in successful_tests) / len(successful_tests)

        print(
            f"Model selection accuracy: {len(matches)}/{len(successful_tests)} ({len(matches)/len(successful_tests)*100:.1f}%)"
        )
        print(f"Average confidence: {avg_confidence:.2f}")
        print(f"Average latency: {avg_latency:.1f}ms")

        # Model distribution
        model_counts = {}
        for result in successful_tests:
            model = result["selected_model"]
            model_counts[model] = model_counts.get(model, 0) + 1

        print("\n📈 Model Distribution:")
        for model, count in model_counts.items():
            percentage = count / len(successful_tests) * 100
            print(f"  {model}: {count} ({percentage:.1f}%)")

    # Get router statistics
    stats = router.get_routing_stats()
    print("\n📊 Router Statistics:")
    print(f"  Total routes: {stats['total_routes']}")
    if stats["model_distribution"]:
        print(f"  Model distribution: {stats['model_distribution']}")
        print(f"  Average confidence: {stats['average_confidence']:.2f}")

    return results

@pytest.mark.tier1
@pytest.mark.unit
def test_context_engineering_patterns():
    """Test specific context engineering patterns for each model"""

    print("\n🧠 Testing Context Engineering Patterns")
    print("=" * 60)

    router = create_cursor_model_router()

    # Test patterns for different task types
    pattern_tests = [
        {
            "task_type": "coding",
            "query": "Create a Python class for handling database connections",
            "expected_model": CursorModel.GPT_4_TURBO.value,
        },
        {
            "task_type": "reasoning",
            "query": "Explain the trade-offs between synchronous and asynchronous programming",
            "expected_model": CursorModel.CLAUDE_3_OPUS.value,
        },
        {
            "task_type": "debugging",
            "query": "Fix this JavaScript error: 'Cannot read property of undefined'",
            "expected_model": CursorModel.MISTRAL_7B_INSTRUCT.value,
        },
        {
            "task_type": "planning",
            "query": "Design a scalable architecture for a real-time chat application",
            "expected_model": CursorModel.CLAUDE_3_OPUS.value,
        },
    ]

    for i, test_case in enumerate(pattern_tests, 1):
        print(f"\n🔍 Pattern Test {i}: {test_case['task_type']}")
        print(f"Query: {test_case['query']}")

        result = router.route_query(query=test_case["query"], task_type=test_case["task_type"])

        if result["status"] == "success":
            print(f"✅ Selected model: {result['selected_model']}")
            print(f"🔧 Context engineering: {result['context_engineering']}")
            print(f"📝 Prompt pattern: {result['prompt_pattern']}")
            print(f"📋 Model instructions: {result['model_instructions']}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")

def test_complexity_analysis():
    """Test complexity analysis and its impact on model selection"""

    print("\n📊 Testing Complexity Analysis")
    print("=" * 60)

    router = create_cursor_model_router()

    # Test queries with different complexity levels
    complexity_tests = [
        {"query": "Hello world", "description": "Simple query", "expected_complexity": "simple"},
        {
            "query": "Implement a function that takes a list of integers and returns the sum of all even numbers, but only if the list contains at least 3 elements and the sum is greater than 10",
            "description": "Moderate complexity",
            "expected_complexity": "moderate",
        },
        {
            "query": "Design and implement a comprehensive microservices architecture for an enterprise e-commerce platform that handles millions of transactions per day, includes real-time inventory management, customer analytics, payment processing with multiple gateways, order fulfillment tracking, customer support integration, and must be scalable across multiple regions with disaster recovery capabilities",
            "description": "High complexity",
            "expected_complexity": "complex",
        },
    ]

    for i, test_case in enumerate(complexity_tests, 1):
        print(f"\n🔍 Complexity Test {i}: {test_case['description']}")
        print(f"Query: {test_case['query'][:100]}...")

        result = router.route_query(query=test_case["query"])

        if result["status"] == "success":
            complexity = result["routing_metadata"]["complexity"]
            selected_model = result["selected_model"]

            print(f"📊 Analyzed complexity: {complexity}")
            print(f"🎯 Expected complexity: {test_case['expected_complexity']}")
            print(f"🤖 Selected model: {selected_model}")
            print(f"🧠 Reasoning: {result['reasoning']}")

def main():
    """Run all context engineering tests"""

    print("🚀 Cursor Native AI Context Engineering Test Suite")
    print("=" * 60)

    try:
        # Test basic context engineering
        results = test_context_engineering()

        # Test context engineering patterns
        test_context_engineering_patterns()

        # Test complexity analysis
        test_complexity_analysis()

        print("\n✅ All tests completed successfully!")

        # Save results to file
        with open("context_engineering_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print("📁 Results saved to context_engineering_test_results.json")

    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
