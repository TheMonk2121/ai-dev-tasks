#!/usr/bin/env python3
"""
RAGAS evaluation script for DSPy RAG memory system.
"""

import os
import sys
from typing import Any

from datasets import Dataset
from langchain_ollama import OllamaLLM
from ragas import evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    AnswerRelevancy,
    ContextRecall,
    ContextRelevance,
    Faithfulness,
)

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from dspy_modules.model_switcher import ModelSwitcher


def create_test_queries() -> list[dict[str, Any]]:
    """Create test queries for evaluating the DSPy memory system."""

    test_queries = [
        {
            "question": "What is DSPy and how does it work?",
            "ground_truth": "DSPy is a framework for programming with language models that provides structured workflows, automated task processing, and intelligent error recovery.",
            "context": "DSPy is an AI-powered development ecosystem that transforms ideas into working software using AI agents. It provides structured workflows, automated task processing, and intelligent error recovery.",
        },
        {
            "question": "How do I integrate components with DSPy?",
            "ground_truth": "DSPy provides integration patterns for components and external systems, including API design principles, component integration, and communication patterns.",
            "context": "The Integration Patterns Guide covers API Design Principles, Component Integration, and Communication Patterns for integrating components and external systems with the DSPy framework.",
        },
        {
            "question": "What are the coding standards for DSPy development?",
            "ground_truth": "DSPy development follows PEP 8 coding standards, uses type hints (Python 3.12+), comprehensive docstrings (Google style), proper error handling, and absolute imports.",
            "context": "DSPy development follows PEP 8 coding standards, uses type hints (Python 3.12+ with PEP 585 built-in generics), comprehensive docstrings (Google style), proper error handling with try/except blocks, and absolute imports.",
        },
        {
            "question": "How does the memory system work in DSPy?",
            "ground_truth": "The DSPy memory system includes context management, memory rehydration, role-aware bundles, and real-time context integration through Scribe.",
            "context": "The memory system includes context management, memory rehydration, role-aware bundles, echo verification, and self-critique. Real-time context is integrated through Scribe.",
        },
        {
            "question": "What is the system architecture of DSPy?",
            "ground_truth": "DSPy has a layered architecture with presentation & tooling, application services, data layer, and observability & security components.",
            "context": "DSPy has a layered architecture: Presentation & Tooling (Cursor Native AI, mission dashboard), Application Services (DSPy modules, automation services), Data Layer (PostgreSQL + PGVector), and Observability & Security.",
        },
    ]

    return test_queries


def create_evaluation_dataset(test_queries: list[dict[str, Any]]) -> Dataset:
    """Create a RAGAS evaluation dataset from test queries."""

    # Convert to RAGAS format
    ragas_data = []
    for query in test_queries:
        ragas_data.append(
            {
                "question": query["question"],
                "ground_truth": query["ground_truth"],
                "contexts": [query["context"]],  # RAGAS expects list of contexts
                "answer": query["ground_truth"],  # For now, using ground truth as answer
            }
        )

    return Dataset.from_list(ragas_data)


def evaluate_memory_system():
    """Evaluate the DSPy memory system using RAGAS metrics."""

    print("🧠 Evaluating DSPy Memory System with RAGAS...\n")

    # Create test queries
    test_queries = create_test_queries()
    print(f"📋 Created {len(test_queries)} test queries")

    # Create evaluation dataset
    dataset = create_evaluation_dataset(test_queries)
    print(f"📊 Created evaluation dataset with {len(dataset)} samples")

    # Configure RAGAS to use local Ollama model
    ollama_llm = OllamaLLM(model="llama3.1:8b")
    llm = LangchainLLMWrapper(ollama_llm)

    # Define metrics with local LLM
    metrics = [
        ContextRelevance(llm=llm),
        ContextRecall(llm=llm),
        Faithfulness(llm=llm),
        AnswerRelevancy(llm=llm),
    ]

    print("\n🔍 Running RAGAS evaluation with local Ollama model...")

    # Run evaluation
    results = evaluate(dataset, metrics)

    print("\n📈 Evaluation Results:")
    print("=" * 50)

    # Print results
    for metric_name, score in results.items():
        print(f"{metric_name}: {score:.4f}")

    print("\n" + "=" * 50)

    # Summary
    print("\n📋 Summary:")
    print(f"- Context Relevance: {results['ContextRelevance']:.4f}")
    print(f"- Context Recall: {results['ContextRecall']:.4f}")
    print(f"- Faithfulness: {results['Faithfulness']:.4f}")
    print(f"- Answer Relevancy: {results['AnswerRelevancy']:.4f}")

    # Calculate average score
    avg_score = sum(results.values()) / len(results)
    print(f"- Average Score: {avg_score:.4f}")

    return results


def test_with_real_queries():
    """Test with real queries using the DSPy model switcher."""

    print("\n🤖 Testing with real DSPy model switcher...\n")

    # Initialize model switcher
    switcher = ModelSwitcher()
    switcher.switch_model(switcher.get_model_for_role("researcher"))

    # Test queries
    test_questions = [
        "What is DSPy?",
        "How do I integrate components with DSPy?",
        "What are the coding standards?",
        "How does the memory system work?",
    ]

    for question in test_questions:
        print(f"❓ Question: {question}")
        try:
            response = switcher.current_lm(question)
            print(f"🤖 Answer: {response[0] if isinstance(response, list) else response}")
        except Exception as e:
            print(f"❌ Error: {e}")
        print("-" * 50)


if __name__ == "__main__":
    # Run RAGAS evaluation
    results = evaluate_memory_system()

    # Test with real queries
    test_with_real_queries()

    print("\n✅ Evaluation complete!")
