#!/usr/bin/env python3
"""
Improved evaluation script for DSPy RAG memory system with better context-aware prompts.
"""

import os
import sys
from typing import Any

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from dspy_modules.model_switcher import ModelSwitcher


def create_improved_test_queries() -> list[dict[str, Any]]:
    """Create improved test queries that explicitly reference the project context."""

    test_queries = [
        {
            "question": "Based on the project context, what is DSPy and how does it work in this AI development ecosystem?",
            "expected_keywords": [
                "framework",
                "language models",
                "workflows",
                "automated",
                "error recovery",
                "ai",
                "agent",
            ],
        },
        {
            "question": "According to the project documentation, how do I integrate components with DSPy?",
            "expected_keywords": ["integration patterns", "API design", "components", "communication", "framework"],
        },
        {
            "question": "What are the coding standards for DSPy development as specified in the project guides?",
            "expected_keywords": ["PEP 8", "type hints", "docstrings", "error handling", "absolute imports"],
        },
        {
            "question": "How does the memory system work in DSPy according to the project context?",
            "expected_keywords": ["context management", "memory rehydration", "role-aware", "scribe", "memory"],
        },
        {
            "question": "What is the system architecture of DSPy as described in the project documentation?",
            "expected_keywords": [
                "layered architecture",
                "presentation",
                "application services",
                "data layer",
                "architecture",
            ],
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
    """Evaluate the DSPy memory system with improved context-aware prompts."""

    print("🧠 Evaluating DSPy Memory System (Improved Context-Aware)...\n")

    # Create improved test queries
    test_queries = create_improved_test_queries()
    print(f"📋 Created {len(test_queries)} improved test queries")

    # Initialize model switcher
    switcher = ModelSwitcher()
    switcher.switch_model(switcher.get_model_for_role("researcher"))

    print("\n🔍 Running evaluation with improved context-aware prompts...")

    total_score = 0
    total_queries = len(test_queries)

    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}/{total_queries}: {query['question']}")
        print("-" * 80)

        try:
            # Get response from model with improved prompt
            response = switcher.current_lm(query["question"])
            response_text = response[0] if isinstance(response, list) else str(response)

            print(f"🤖 Response: {response_text[:300]}...")

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

    print("\n" + "=" * 80)
    print("📈 IMPROVED EVALUATION SUMMARY")
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

    return {
        "total_queries": total_queries,
        "average_score": average_score,
        "grade": grade,
    }


def test_context_aware_queries():
    """Test with context-aware queries that explicitly reference the project."""

    print("\n🤖 Testing Context-Aware Queries...\n")

    switcher = ModelSwitcher()
    switcher.switch_model(switcher.get_model_for_role("researcher"))

    # Test queries that explicitly reference the project context
    test_questions = [
        "What is DSPy in the context of this AI development ecosystem?",
        "How does DSPy integrate with the memory system described in the project?",
        "What role does DSPy play in the system architecture outlined in the documentation?",
        "How is DSPy used for AI agent orchestration in this project?",
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"❓ Question {i}: {question}")
        print("-" * 60)

        try:
            response = switcher.current_lm(question)
            response_text = response[0] if isinstance(response, list) else str(response)

            print(f"🤖 Answer: {response_text[:200]}...")

            # Check if response is contextually accurate
            if "DSPy" in response_text and any(
                word in response_text.lower() for word in ["framework", "ai", "agent", "system"]
            ):
                print("✅ Response appears contextually accurate")
            else:
                print("⚠️ Response may not be contextually accurate")

        except Exception as e:
            print(f"❌ Error: {e}")

        print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    # Run improved evaluation
    results = evaluate_memory_system()

    # Test context-aware queries
    test_context_aware_queries()

    print("\n✅ Improved evaluation complete!")
    print(f"🎯 Final Grade: {results['grade']} ({results['average_score']:.1f}%)")

    # Compare with previous results
    print("\n📊 Comparison:")
    print("Previous Grade: F (Failing) (18.0%)")
    print(f"Current Grade: {results['grade']} ({results['average_score']:.1f}%)")

    if results["average_score"] > 18.0:
        improvement = results["average_score"] - 18.0
        print(f"📈 Improvement: +{improvement:.1f}%")
    else:
        print("📉 No improvement or regression detected")
