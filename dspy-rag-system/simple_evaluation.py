#!/usr/bin/env python3
"""
Simple evaluation script for DSPy RAG memory system.
"""

import os
import sys
from typing import Any

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from dspy_modules.model_switcher import ModelSwitcher


def create_test_queries() -> list[dict[str, Any]]:
    """Create test queries for evaluating the DSPy memory system."""

    test_queries = [
        {
            "question": "What is DSPy and how does it work?",
            "expected_keywords": ["framework", "language models", "workflows", "automated", "error recovery"],
        },
        {
            "question": "How do I integrate components with DSPy?",
            "expected_keywords": ["integration patterns", "API design", "components", "communication"],
        },
        {
            "question": "What are the coding standards for DSPy development?",
            "expected_keywords": ["PEP 8", "type hints", "docstrings", "error handling", "absolute imports"],
        },
        {
            "question": "How does the memory system work in DSPy?",
            "expected_keywords": ["context management", "memory rehydration", "role-aware", "Scribe"],
        },
        {
            "question": "What is the system architecture of DSPy?",
            "expected_keywords": ["layered architecture", "presentation", "application services", "data layer"],
        },
    ]

    return test_queries


def evaluate_response_quality(response: str, expected_keywords: list[str]) -> dict[str, Any]:
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


def evaluate_memory_system():
    """Evaluate the DSPy memory system with simple metrics."""

    print("🧠 Evaluating DSPy Memory System...\n")

    # Create test queries
    test_queries = create_test_queries()
    print(f"📋 Created {len(test_queries)} test queries")

    # Initialize model switcher
    switcher = ModelSwitcher()
    switcher.switch_model(switcher.get_model_for_role("researcher"))

    print("\n🔍 Running evaluation with local Ollama model...")

    total_score = 0
    total_queries = len(test_queries)

    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}/{total_queries}: {query['question']}")
        print("-" * 60)

        try:
            # Get response from model
            response = switcher.current_lm(query["question"])
            response_text = response[0] if isinstance(response, list) else str(response)

            print(f"🤖 Response: {response_text[:200]}...")

            # Evaluate response quality
            evaluation = evaluate_response_quality(response_text, query["expected_keywords"])

            print("📊 Evaluation:")
            print(f"  - Keyword Coverage: {evaluation['keyword_coverage']:.2f} ({evaluation['score']:.1f}%)")
            print(f"  - Found Keywords: {', '.join(evaluation['found_keywords'])}")
            print(f"  - Missing Keywords: {', '.join(evaluation['missing_keywords'])}")
            print(f"  - Response Length: {evaluation['response_length']} words")

            total_score += evaluation["score"]

        except Exception as e:
            print(f"❌ Error: {e}")
            total_score += 0  # Zero score for failed queries

    # Calculate overall score
    average_score = total_score / total_queries if total_queries > 0 else 0

    print("\n" + "=" * 60)
    print("📈 EVALUATION SUMMARY")
    print("=" * 60)
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

    return {
        "total_queries": total_queries,
        "average_score": average_score,
        "grade": grade,
    }


def test_role_diversity():
    """Test how different roles respond to the same question."""

    print("\n🤖 Testing Role Diversity...\n")

    question = "What is DSPy?"
    roles = ["planner", "researcher", "implementer", "coder", "reviewer"]

    switcher = ModelSwitcher()

    for role in roles:
        print(f"📋 {role.upper()} PERSPECTIVE:")
        print("-" * 50)

        try:
            switcher.switch_model(switcher.get_model_for_role(role))
            response = switcher.current_lm(question)
            response_text = response[0] if isinstance(response, list) else str(response)

            print(f"Response: {response_text[:150]}...")

        except Exception as e:
            print(f"Error: {e}")

        print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    # Run simple evaluation
    results = evaluate_memory_system()

    # Test role diversity
    test_role_diversity()

    print("\n✅ Evaluation complete!")
    print(f"🎯 Final Grade: {results['grade']} ({results['average_score']:.1f}%)")
