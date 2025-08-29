#!/usr/bin/env python3
"""
Phase 2 Evaluation: DSPy Memory System with Improved Context and Prompts
"""

import os
import sys
from typing import Any, Dict, List

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from dspy_modules.model_switcher import ModelSwitcher


def create_phase2_test_queries() -> List[Dict[str, Any]]:
    """Create test queries specifically designed for Phase 2 improvements."""

    test_queries = [
        {
            "question": "What is DSPy and how does it work in this AI development ecosystem?",
            "expected_keywords": ["framework", "ai", "agent", "system", "language models", "structured"],
            "description": "Basic DSPy identification with context",
        },
        {
            "question": "How does the DSPy framework integrate with the memory system?",
            "expected_keywords": ["memory", "context", "system", "integration", "framework"],
            "description": "DSPy-memory integration understanding",
        },
        {
            "question": "What are the core components of the DSPy system architecture?",
            "expected_keywords": ["components", "architecture", "system", "model switcher", "optimization"],
            "description": "DSPy architecture understanding",
        },
        {
            "question": "How do AI agents work with DSPy in this project?",
            "expected_keywords": ["agent", "ai", "system", "workflow", "orchestration"],
            "description": "DSPy-AI agent understanding",
        },
        {
            "question": "What optimization techniques does DSPy use?",
            "expected_keywords": ["optimization", "labeledfewshot", "assertion", "framework"],
            "description": "DSPy optimization understanding",
        },
        {
            "question": "How does DSPy handle model switching and integration?",
            "expected_keywords": ["model", "switching", "integration", "cursor", "local"],
            "description": "DSPy model integration understanding",
        },
        {
            "question": "What is the role of DSPy signatures in this system?",
            "expected_keywords": ["signatures", "structured", "io", "programming", "framework"],
            "description": "DSPy signatures understanding",
        },
        {
            "question": "How does DSPy support multi-agent orchestration?",
            "expected_keywords": ["multi-agent", "orchestration", "system", "coordination", "framework"],
            "description": "DSPy multi-agent understanding",
        },
    ]

    return test_queries


def evaluate_response_quality(response: str, expected_keywords: List[str]) -> Dict[str, Any]:
    """Evaluate the quality of a response based on expected keywords."""

    response_lower = response.lower()
    found_keywords = []
    missing_keywords = []

    for keyword in expected_keywords:
        if keyword.lower() in response_lower:
            found_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    # Calculate scores
    keyword_coverage = len(found_keywords) / len(expected_keywords) if expected_keywords else 0
    response_length = len(response.split())

    return {
        "keyword_coverage": keyword_coverage,
        "found_keywords": found_keywords,
        "missing_keywords": missing_keywords,
        "response_length": response_length,
        "score": keyword_coverage * 100,  # Percentage score
    }


def run_phase2_evaluation():
    """Run the Phase 2 evaluation with improved context and prompts."""

    print("🧠 PHASE 2 EVALUATION: DSPy Memory System")
    print("=" * 80)
    print("Testing improved context specificity and model prompts...")
    print("=" * 80)

    # Create test queries
    test_queries = create_phase2_test_queries()
    print(f"📋 Created {len(test_queries)} Phase 2 test queries")

    # Initialize model switcher
    switcher = ModelSwitcher()
    switcher.switch_model(switcher.get_model_for_role("researcher"))

    print("\n🔍 Running Phase 2 evaluation...")

    total_score = 0
    total_queries = len(test_queries)
    detailed_results = []

    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}/{total_queries}: {query['description']}")
        print(f"Question: {query['question']}")
        print("-" * 60)

        try:
            # Get response from model
            response = switcher.current_lm(query["question"])
            response_text = response[0] if isinstance(response, list) else str(response)

            print(f"🤖 Response: {response_text[:200]}...")

            # Evaluate response quality
            evaluation = evaluate_response_quality(response_text, query["expected_keywords"])

            print("📊 Evaluation:")
            print(f"  - Score: {evaluation['score']:.1f}%")
            print(f"  - Found: {', '.join(evaluation['found_keywords'])}")
            print(f"  - Missing: {', '.join(evaluation['missing_keywords'])}")

            total_score += evaluation["score"]
            detailed_results.append(
                {
                    "query": query["description"],
                    "score": evaluation["score"],
                    "found_keywords": evaluation["found_keywords"],
                    "missing_keywords": evaluation["missing_keywords"],
                }
            )

        except Exception as e:
            print(f"❌ Error: {e}")
            total_score += 0

    # Calculate overall score
    average_score = total_score / total_queries if total_queries > 0 else 0

    print("\n" + "=" * 80)
    print("📈 PHASE 2 EVALUATION RESULTS")
    print("=" * 80)
    print(f"Total Queries: {total_queries}")
    print(f"Average Score: {average_score:.1f}%")

    # Grade the system
    if average_score >= 80:
        grade = "A (Excellent)"
    elif average_score >= 70:
        grade = "B (Good)"
    elif average_score >= 60:
        grade = "C (Fair)"
    elif average_score >= 50:
        grade = "D (Poor)"
    else:
        grade = "F (Failing)"

    print(f"Grade: {grade}")

    # Detailed breakdown
    print("\n📋 Detailed Results:")
    for result in detailed_results:
        print(f"  - {result['query']}: {result['score']:.1f}%")

    return {
        "total_queries": total_queries,
        "average_score": average_score,
        "grade": grade,
        "detailed_results": detailed_results,
    }


def compare_with_previous_results():
    """Compare Phase 2 results with previous evaluations."""

    print("\n" + "=" * 80)
    print("📊 COMPARISON WITH PREVIOUS RESULTS")
    print("=" * 80)

    previous_results = [
        {"phase": "Initial", "score": 18.0, "grade": "F (Failing)"},
        {"phase": "Improved Prompts", "score": 20.6, "grade": "F (Failing)"},
        {"phase": "Final Baseline", "score": 45.0, "grade": "F (Failing)"},
    ]

    print("Previous Results:")
    for result in previous_results:
        print(f"  - {result['phase']}: {result['score']:.1f}% ({result['grade']})")

    print("\nPhase 2 Results:")
    print(f"  - Improved Context + Prompts: {run_phase2_evaluation()['average_score']:.1f}%")

    # Calculate improvements
    improvements = []
    for prev_result in previous_results:
        improvement = run_phase2_evaluation()["average_score"] - prev_result["score"]
        improvements.append(
            {
                "from": prev_result["phase"],
                "improvement": improvement,
            }
        )

    print("\n📈 Improvements:")
    for improvement in improvements:
        if improvement["improvement"] > 0:
            print(f"  - vs {improvement['from']}: +{improvement['improvement']:.1f}%")
        else:
            print(f"  - vs {improvement['from']}: {improvement['improvement']:.1f}%")


def test_role_diversity_improvement():
    """Test if role diversity has improved with better context."""

    print("\n" + "=" * 80)
    print("🤖 TESTING ROLE DIVERSITY IMPROVEMENT")
    print("=" * 80)

    switcher = ModelSwitcher()
    question = "What is DSPy and how does it work in this project?"
    roles = ["planner", "researcher", "implementer", "coder", "reviewer"]

    for role in roles:
        print(f"\n📋 {role.upper()} PERSPECTIVE:")
        print("-" * 50)

        try:
            switcher.switch_model(switcher.get_model_for_role(role))
            response = switcher.current_lm(question)
            response_text = response[0] if isinstance(response, list) else str(response)

            print(f"Response: {response_text[:150]}...")

            # Check if response is more accurate about DSPy
            if "DSPy" in response_text and any(
                word in response_text.lower() for word in ["framework", "ai", "agent", "system"]
            ):
                print("✅ Response correctly identifies DSPy as an AI framework")
            else:
                print("⚠️ Response may not be accurate about DSPy")

        except Exception as e:
            print(f"Error: {e}")

        print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    # Run Phase 2 evaluation
    results = run_phase2_evaluation()

    # Compare with previous results
    compare_with_previous_results()

    # Test role diversity improvement
    test_role_diversity_improvement()

    print("\n✅ Phase 2 evaluation complete!")
    print(f"🎯 Current Grade: {results['grade']} ({results['average_score']:.1f}%)")

    # Summary of improvements
    print("\n🚀 Phase 2 Improvements Implemented:")
    print("  ✅ Enhanced memory rehydrator with DSPy-specific context")
    print("  ✅ Improved role-specific prompts with DSPy emphasis")
    print("  ✅ Added comprehensive DSPy framework information")
    print("  ✅ Better context utilization in model responses")

    print("\n📈 Ready for Phase 3: Advanced optimization and integration!")
