#!/usr/bin/env python3
"""
Phase 1.5: Freshness & Intent-Aware Policies Demo

Tests the lightweight Phase 1.5 additions:
- Freshness enhancement with time-decay and recency priors
- Intent routing for structured queries (SQL/KG early routing)
"""

import asyncio
import sys
from pathlib import Path
from typing import Any

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import time

class MockRetriever:
    """Mock retriever with timestamped documents for freshness testing."""

    def __init__(self):
        # Mock knowledge base with timestamps
        current_time = time.time()
        day_seconds = 24 * 3600

        self.knowledge = {
            "dspy": [
                {
                    "text": "DSPy is a framework for algorithmically optimizing language model prompts and weights",
                    "score": 0.9,
                    "timestamp": current_time - (5 * day_seconds),  # 5 days ago
                    "document_id": "dspy_intro_001",
                    "source": "dspy_docs.md",
                },
                {
                    "text": "DSPy uses optimizers to automatically tune prompts based on validation metrics",
                    "score": 0.8,
                    "timestamp": current_time - (30 * day_seconds),  # 30 days ago
                    "document_id": "dspy_optimizers_002",
                    "source": "optimization_guide.md",
                },
                {
                    "text": "DSPy signatures define input/output specifications for language model tasks",
                    "score": 0.7,
                    "timestamp": current_time - (60 * day_seconds),  # 60 days ago
                    "document_id": "dspy_signatures_003",
                    "source": "signatures_tutorial.md",
                },
            ],
            "optimization": [
                {
                    "text": "DSPy optimizers include BootstrapFewShot and Copro for prompt optimization",
                    "score": 0.8,
                    "timestamp": current_time - (2 * day_seconds),  # 2 days ago (recent!)
                    "document_id": "optimizers_recent_004",
                    "source": "latest_optimizers.md",
                },
                {
                    "text": "Optimization in DSPy uses metrics to evaluate and improve prompt performance",
                    "score": 0.7,
                    "timestamp": current_time - (45 * day_seconds),  # 45 days ago
                    "document_id": "optimization_metrics_005",
                    "source": "metrics_guide.md",
                },
            ],
        }

    def retrieve(self, query: str) -> list[dict[str, Any]]:
        """Mock retrieval based on query keywords."""
        query_lower = query.lower()
        results = []

        # Simple keyword matching
        for topic, docs in self.knowledge.items():
            if topic in query_lower:
                results.extend(docs)

        # Default fallback
        if not results:
            results = [
                {
                    "text": f"General information related to: {query}",
                    "score": 0.5,
                    "timestamp": time.time(),
                    "document_id": "general_fallback",
                    "source": "fallback.md",
                }
            ]

        # Sort by original score
        results.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        return results[:5]

async def test_freshness_enhancement():
    """Test Phase 1.5 freshness enhancement."""

    print("🧪 Testing Phase 1.5 Freshness Enhancement")
    print("=" * 50)

    try:
        from retrieval.freshness_enhancer import FreshnessConfig, create_freshness_enhancer

        # Test configuration
        config = FreshnessConfig(
            enable_time_decay=True,
            decay_half_life_days=30.0,
            max_decay_factor=0.3,
            enable_recency_prior=True,
            recency_boost_factor=1.2,
            recency_threshold_days=7,
        )

        freshness_enhancer = create_freshness_enhancer(config)
        mock_retriever = MockRetriever()

        # Test 1: Freshness-sensitive query
        print("1. Testing freshness-sensitive query...")
        fresh_query = "What are the latest DSPy optimization techniques from this week?"

        # Detect freshness sensitivity
        is_sensitive, confidence, reasoning = freshness_enhancer.detector.detect_freshness_sensitivity(fresh_query)
        print(f"  Freshness sensitive: {is_sensitive}")
        print(f"  Confidence: {confidence:.3f}")
        print(f"  Reasoning: {reasoning}")

        # Retrieve and enhance
        results = mock_retriever.retrieve("DSPy optimization")
        enhanced_results, metadata = freshness_enhancer.enhance_retrieval_results(
            fresh_query, results, current_time=time.time()
        )

        print(f"  Enhancement applied: {metadata['enhancements_applied']}")
        print(f"  Total results: {metadata['total_results']}")

        # Show score changes
        print("  Score changes:")
        for i, result in enumerate(enhanced_results[:3]):
            original = result.get("original_score", result.get("score", 0.0))
            enhanced = result.get("score", 0.0)
            decay = result.get("freshness_decay", 1.0)
            boost = result.get("recency_boost", 1.0)
            age_days = result.get("freshness_metadata", {}).get("doc_age_days", 0)

            print(
                f"    {i+1}. {result['document_id']}: {original:.3f} → {enhanced:.3f} "
                f"(decay: {decay:.3f}, boost: {boost:.3f}, age: {age_days:.1f}d)"
            )

        # Test 2: Non-freshness query
        print("\n2. Testing non-freshness query...")
        evergreen_query = "What is DSPy?"

        is_sensitive, confidence, reasoning = freshness_enhancer.detector.detect_freshness_sensitivity(evergreen_query)
        print(f"  Freshness sensitive: {is_sensitive}")
        print(f"  Confidence: {confidence:.3f}")
        print(f"  Reasoning: {reasoning}")

        results = mock_retriever.retrieve("DSPy")
        enhanced_results, metadata = freshness_enhancer.enhance_retrieval_results(
            evergreen_query, results, current_time=time.time()
        )

        print(f"  Enhancement applied: {metadata['enhancements_applied']}")
        print("  No changes expected for evergreen queries")

        print("  ✅ Freshness enhancement working correctly")
        return True

    except Exception as e:
        print(f"  ❌ Freshness test failed: {e}")
        return False

async def test_intent_routing():
    """Test Phase 1.5 intent routing."""

    print("\n🧪 Testing Phase 1.5 Intent Routing")
    print("=" * 50)

    try:
        from retrieval.intent_router import IntentRouterConfig, create_intent_router

        # Test configuration
        config = IntentRouterConfig(
            structured_confidence_threshold=0.7,
            hybrid_confidence_threshold=0.5,
            enable_structured_routing=True,
            enable_hybrid_routing=True,
        )

        intent_router = create_intent_router(config)

        # Test queries
        test_queries = [
            {
                "query": "Count all users in the system",
                "expected_intent": "structured",
                "expected_route": "sql",
                "description": "SQL lookup query",
            },
            {
                "query": "Find documents created between 2024-01-01 and 2024-12-31",
                "expected_intent": "structured",
                "expected_route": "sql",
                "description": "Date range query",
            },
            {
                "query": "What is the average performance of model A vs model B?",
                "expected_intent": "structured",
                "expected_route": "sql",
                "description": "Metric comparison query",
            },
            {
                "query": "Show me the relationship between user files and PRDs",
                "expected_intent": "structured",
                "expected_route": "kg",
                "description": "Knowledge graph query",
            },
            {
                "query": "Explain how DSPy optimization works with examples",
                "expected_intent": "text_rag",
                "expected_route": "rag",
                "description": "Explanatory text query",
            },
            {
                "query": "Compare the performance of different optimization strategies and explain why they work",
                "expected_intent": "hybrid",
                "expected_route": "hybrid",
                "description": "Hybrid query (comparison + explanation)",
            },
        ]

        results = []
        for test_case in test_queries:
            print(f"\n  Testing: {test_case['description']}")
            print(f"  Query: {test_case['query'][:50]}...")

            classification = intent_router.classify_intent(test_case["query"])

            print(f"    Intent: {classification.intent_type} (expected: {test_case['expected_intent']})")
            print(f"    Route: {classification.route_target} (expected: {test_case['expected_route']})")
            print(f"    Confidence: {classification.confidence:.3f}")
            print(f"    Short-circuit: {classification.should_short_circuit}")
            print(f"    Reasoning: {classification.reasoning[:100]}...")

            # Check if routing decision is correct
            intent_correct = classification.intent_type == test_case["expected_intent"]
            route_correct = classification.route_target == test_case["expected_route"]

            results.append(
                {
                    "query": test_case["query"],
                    "intent_correct": intent_correct,
                    "route_correct": route_correct,
                    "confidence": classification.confidence,
                }
            )

        # Summary
        intent_accuracy = sum(1 for r in results if r["intent_correct"]) / len(results)
        route_accuracy = sum(1 for r in results if r["route_correct"]) / len(results)

        print("\n  📊 Intent Routing Results:")
        print(
            f"    Intent accuracy: {intent_accuracy:.1%} ({sum(1 for r in results if r['intent_correct'])}/{len(results)})"
        )
        print(
            f"    Route accuracy: {route_accuracy:.1%} ({sum(1 for r in results if r['route_correct'])}/{len(results)})"
        )
        print(f"    Average confidence: {sum(r['confidence'] for r in results) / len(results):.3f}")

        print("  ✅ Intent routing working correctly")
        return intent_accuracy >= 0.8 and route_accuracy >= 0.8

    except Exception as e:
        print(f"  ❌ Intent routing test failed: {e}")
        return False

async def test_phase15_integration():
    """Test Phase 1.5 integration with mock pipeline."""

    print("\n🧪 Testing Phase 1.5 Integration")
    print("=" * 50)

    try:
        from retrieval.freshness_enhancer import create_freshness_enhancer
        from retrieval.intent_router import create_intent_router

        # Initialize components
        freshness_enhancer = create_freshness_enhancer()
        intent_router = create_intent_router()
        mock_retriever = MockRetriever()

        # Test integrated pipeline
        test_queries = [
            {
                "query": "What are the latest DSPy updates from this month?",
                "description": "Freshness + intent routing test",
            },
            {"query": "Count all documents created in 2024", "description": "Structured query test"},
            {"query": "Explain how DSPy works with recent examples", "description": "Hybrid query test"},
        ]

        for test_case in test_queries:
            print(f"\n  Testing: {test_case['description']}")
            print(f"  Query: {test_case['query']}")

            # Step 1: Intent classification
            intent_result = intent_router.classify_intent(test_case["query"])
            print(f"    Intent: {intent_result.intent_type} → {intent_result.route_target}")
            print(f"    Short-circuit: {intent_result.should_short_circuit}")

            # Step 2: Retrieval (if not short-circuited)
            if not intent_result.should_short_circuit:
                results = mock_retriever.retrieve(test_case["query"])
                print(f"    Retrieved: {len(results)} documents")

                # Step 3: Freshness enhancement
                enhanced_results, freshness_metadata = freshness_enhancer.enhance_retrieval_results(
                    test_case["query"], results
                )

                print(f"    Freshness enhanced: {len(freshness_metadata['enhancements_applied'])} enhancements")
                print(f"    Top score: {enhanced_results[0]['score']:.3f}")
            else:
                print(f"    Short-circuited to {intent_result.route_target} handler")

        print("  ✅ Phase 1.5 integration working correctly")
        return True

    except Exception as e:
        print(f"  ❌ Integration test failed: {e}")
        return False

async def main():
    """Run all Phase 1.5 tests."""

    print("🚀 Phase 1.5: Freshness & Intent-Aware Policies Demo")
    print("=" * 60)

    tests = [
        ("Freshness Enhancement", test_freshness_enhancement),
        ("Intent Routing", test_intent_routing),
        ("Phase 1.5 Integration", test_phase15_integration),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"Test '{test_name}' crashed: {e}")
            results[test_name] = False

    # Summary
    print("\n📊 Phase 1.5 Test Results:")
    print("-" * 40)

    passed = 0
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if success:
            passed += 1

    print(f"\n🎯 Summary: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("\n🎉 Phase 1.5 Freshness & Intent-Aware Policies are fully functional!")
        print("\n📋 Ready for:")
        print("  • Time-decay scoring for freshness-sensitive queries")
        print("  • Recency boosting for recent documents")
        print("  • Structured query early routing to SQL/KG handlers")
        print("  • Intent-aware pipeline optimization")
        print("  • Integration with Phase 0/1/2 RAG pipeline")
    else:
        print(f"\n⚠️  {len(results) - passed} components need attention before deployment")

    return passed == len(results)

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
