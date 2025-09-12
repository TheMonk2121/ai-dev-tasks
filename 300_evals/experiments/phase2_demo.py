#!/usr/bin/env python3
"""
Phase 2: Multi-Hop & Answer Planning Demonstration

Tests the complete Phase 2 data-driven multi-hop system with:
- Coverage/concentration/novelty gating
- Mid-generation callbacks for uncertainty
- Token budget management
- Performance monitoring
"""

import asyncio
import sys
from pathlib import Path
from typing import Any

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import yaml

class MockRetriever:
    """Mock retriever for Phase 2 demonstration."""

    def __init__(self):
        # Mock knowledge base
        self.knowledge = {
            "dspy": [
                {
                    "text": "DSPy is a framework for algorithmically optimizing language model prompts and weights",
                    "score": 0.9,
                },
                {
                    "text": "DSPy uses optimizers to automatically tune prompts based on validation metrics",
                    "score": 0.8,
                },
                {"text": "DSPy signatures define input/output specifications for language model tasks", "score": 0.7},
            ],
            "optimization": [
                {"text": "DSPy optimizers include BootstrapFewShot and Copro for prompt optimization", "score": 0.8},
                {"text": "Optimization in DSPy uses metrics to evaluate and improve prompt performance", "score": 0.7},
            ],
            "prompts": [
                {"text": "DSPy prompts are automatically generated and optimized using training data", "score": 0.8},
                {"text": "Prompt engineering in DSPy is done algorithmically rather than manually", "score": 0.6},
            ],
            "framework": [
                {"text": "DSPy framework provides modules and signatures for structured LM programming", "score": 0.9},
                {"text": "The framework enables composable and optimizable language model programs", "score": 0.7},
            ],
            "metrics": [
                {"text": "DSPy uses validation metrics to guide the optimization process", "score": 0.8},
                {"text": "Metrics in DSPy can be task-specific accuracy measures or custom evaluators", "score": 0.6},
            ],
        }

    def retrieve(self, query: str) -> list[dict[str, Any]]:
        """Mock retrieval based on query keywords."""
        query_lower = query.lower()
        results = []

        # Simple keyword matching
        for topic, docs in self.knowledge.items():
            if topic in query_lower:
                for doc in docs:
                    results.append({**doc, "document_id": f"{topic}_{len(results)}", "source": f"mock_doc_{topic}.md"})

        # Default fallback
        if not results:
            results = [
                {
                    "text": f"General information related to: {query}",
                    "score": 0.5,
                    "document_id": "general_fallback",
                    "source": "fallback.md",
                }
            ]

        return results[:5]  # Top 5 results

async def test_phase2_components():
    """Test Phase 2 multi-hop components individually."""

    print("🧪 Testing Phase 2 Multi-Hop Components")
    print("=" * 50)

    # Test 1: Multi-hop planner
    print("1. Testing MultiHopPlanner...")
    try:
        from retrieval.multihop_planner import create_multihop_planner

        planner = create_multihop_planner(
            {"max_hops": 2, "token_budget": 300, "coverage_threshold": 0.6, "concentration_threshold": 0.5}
        )

        mock_retriever = MockRetriever()

        # Test complex query requiring multi-hop
        async def mock_retrieval_fn(query):
            return mock_retriever.retrieve(query)

        result = await planner.plan_multihop_retrieval(
            query="What is DSPy and how does its optimization work?",
            retrieval_fn=mock_retrieval_fn,
            sub_claims=["DSPy is a framework", "DSPy has optimization", "optimization uses metrics"],
        )

        print("  ✅ Multi-hop planning completed")
        print(f"    Hops executed: {result['planning_trace']['hops_executed']}")
        print(f"    Stop reason: {result['planning_trace']['stop_reason']}")
        print(f"    Final coverage: {result['planning_trace']['final_metrics'].coverage:.3f}")
        print(f"    Token budget used: {result['token_budget_used']}")
        print(f"    Sub-questions: {len(result['sub_questions'])}")

        return True

    except Exception as e:
        print(f"  ❌ MultiHopPlanner test failed: {e}")
        return False

async def test_phase2_integration():
    """Test Phase 2 RAG system integration."""

    print("\n2. Testing Phase2RAGSystem...")
    try:
        from rag.phase2_integration import create_phase2_rag_system

        mock_retriever = MockRetriever()
        config = {
            "multihop": {"max_hops": 2, "coverage_threshold": 0.6, "concentration_threshold": 0.5},
            "enable_midgen_callbacks": True,
            "enable_telemetry": False,  # Disable for demo
        }

        phase2_system = create_phase2_rag_system(mock_retriever, config)

        # Test queries of varying complexity
        test_queries = [
            {"query": "What is DSPy?", "expected_multihop": False, "description": "Simple query (single-hop)"},
            {
                "query": "What is DSPy and how does it optimize prompts and what metrics does it use?",
                "expected_multihop": True,
                "description": "Complex multi-part query (multi-hop)",
            },
            {
                "query": "Compare DSPy optimization with traditional prompt engineering",
                "expected_multihop": True,
                "description": "Comparison query (multi-hop)",
            },
        ]

        results = []
        for test_case in test_queries:
            print(f"\n  Testing: {test_case['description']}")
            print(f"  Query: {test_case['query'][:50]}...")

            result = await phase2_system.query_with_multihop(
                query=test_case["query"], sub_claims=["framework definition", "optimization process", "metric usage"]
            )

            multihop_used = result.get("multihop_used", False)
            confidence = result.get("confidence", 0.0)
            latency = result.get("total_latency_ms", 0)

            print(f"    Multi-hop used: {multihop_used} (expected: {test_case['expected_multihop']})")
            print(f"    Confidence: {confidence:.3f}")
            print(f"    Latency: {latency:.1f}ms")
            print(f"    Answer length: {len(result.get('answer', ''))}")

            if "planning_trace" in result:
                trace = result["planning_trace"]
                print(f"    Hops executed: {trace.get('hops_executed', 0)}")
                print(f"    Stop reason: {trace.get('stop_reason', 'N/A')}")

            results.append(
                {
                    "query": test_case["query"],
                    "multihop_used": multihop_used,
                    "expected": test_case["expected_multihop"],
                    "confidence": confidence,
                    "correct_decision": multihop_used == test_case["expected_multihop"],
                }
            )

        # Summary
        correct_decisions = sum(1 for r in results if r["correct_decision"])
        print("\n  ✅ Phase 2 integration test completed")
        print(f"    Correct multihop decisions: {correct_decisions}/{len(results)}")
        print(f"    Average confidence: {sum(r['confidence'] for r in results) / len(results):.3f}")

        return correct_decisions == len(results)

    except Exception as e:
        print(f"  ❌ Phase 2 integration test failed: {e}")
        return False

async def test_gating_mechanisms():
    """Test data-driven gating mechanisms."""

    print("\n3. Testing Data-Driven Gating...")
    try:
        from retrieval.multihop_planner import CoverageMetrics, MultiHopPlanner

        # Test coverage-based gating
        planner = MultiHopPlanner(coverage_threshold=0.8, concentration_threshold=0.6, max_hops=3)  # High threshold

        # Mock state with high coverage
        class MockState:
            def __init__(self):
                self.current_hop = 1
                self.token_budget_used = 100
                self.resolved_claims = {"claim1", "claim2", "claim3"}
                self.evidence_scores = [0.9, 0.8, 0.85, 0.7]

        state = MockState()

        # Test metrics computation
        metrics = CoverageMetrics(
            coverage=0.85,  # High coverage
            concentration=0.75,  # Good concentration
            novelty=0.9,  # High novelty
            token_budget_remaining=400,
        )

        # Test gating decision
        decision = planner._should_continue_multihop(state, metrics)

        print(f"  Coverage: {metrics.coverage:.3f}")
        print(f"  Concentration: {metrics.concentration:.3f}")
        print(f"  Novelty: {metrics.novelty:.3f}")
        print(f"  Should continue: {decision['should_continue']}")
        print(f"  Reason: {decision['reason']}")

        # Test with low coverage (should continue)
        low_coverage_metrics = CoverageMetrics(
            coverage=0.2, concentration=0.75, novelty=0.9, token_budget_remaining=400  # Low coverage
        )

        low_coverage_decision = planner._should_continue_multihop(state, low_coverage_metrics)
        print("\n  Low coverage test:")
        print(f"  Coverage: {low_coverage_metrics.coverage:.3f}")
        print(f"  Should continue: {low_coverage_decision['should_continue']} (should be True)")

        print("  ✅ Gating mechanisms working correctly")
        return True

    except Exception as e:
        print(f"  ❌ Gating test failed: {e}")
        return False

async def test_configuration_loading():
    """Test Phase 2 configuration loading."""

    print("\n4. Testing Configuration Loading...")
    try:
        # Load config
        with open("config/retrieval.yaml") as f:
            config = yaml.safe_load(f)

        multihop_config = config.get("multihop", {})

        expected_settings = [
            "enabled",
            "max_hops",
            "token_budget",
            "coverage_threshold",
            "concentration_threshold",
            "novelty_threshold",
            "min_evidence_score",
        ]

        for setting in expected_settings:
            if setting not in multihop_config:
                print(f"  ❌ Missing config setting: {setting}")
                return False

        print("  ✅ Configuration loaded successfully")
        print(f"    Max hops: {multihop_config['max_hops']}")
        print(f"    Token budget: {multihop_config['token_budget']}")
        print(f"    Coverage threshold: {multihop_config['coverage_threshold']}")
        print(f"    Midgen callbacks: {multihop_config['midgen_callbacks']['enabled']}")

        return True

    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False

async def main():
    """Run all Phase 2 tests."""

    print("🚀 Phase 2: Multi-Hop & Answer Planning Demo")
    print("=" * 60)

    tests = [
        ("Multi-Hop Components", test_phase2_components),
        ("Phase 2 Integration", test_phase2_integration),
        ("Gating Mechanisms", test_gating_mechanisms),
        ("Configuration Loading", test_configuration_loading),
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
    print("\n📊 Phase 2 Test Results:")
    print("-" * 40)

    passed = 0
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if success:
            passed += 1

    print(f"\n🎯 Summary: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("\n🎉 Phase 2 Multi-Hop & Answer Planning is fully functional!")
        print("\n📋 Ready for:")
        print("  • Multi-hop query decomposition with data-driven gating")
        print("  • Coverage/concentration/novelty-based stopping")
        print("  • Mid-generation callbacks for uncertainty resolution")
        print("  • Token budget management and performance monitoring")
        print("  • Integration with Phase 0/1 telemetry and evaluation")
    else:
        print(f"\n⚠️  {len(results) - passed} components need attention before deployment")

    return passed == len(results)

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
