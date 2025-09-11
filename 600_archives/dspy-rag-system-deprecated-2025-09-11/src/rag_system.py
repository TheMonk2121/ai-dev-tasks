#!/usr/bin/env python3
"""
DSPy RAG System - Main Entry Point
This is the main RAG system that can be used for evaluation.
"""

import os
import sys
from typing import Any, Dict, List, Optional

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from .dspy_modules.dspy_reader_program import RAGAnswer
from .dspy_modules.retriever.limits import load_limits


class DSPyRAGSystem:
    """
    Main DSPy RAG System for evaluation purposes.
    This provides a clean interface for the evaluation system.
    """

    def __init__(self):
        """Initialize the DSPy RAG system."""
        self.rag_answer = RAGAnswer()

    def query(self, question: str, tag: str = "general") -> Dict[str, Any]:
        """
        Query the RAG system with a question.

        Args:
            question: The question to ask
            tag: The tag/category for the question

        Returns:
            Dictionary containing the answer and metadata
        """
        try:
            # Get the answer from the RAG system
            prediction = self.rag_answer.forward(question, tag)

            return {"answer": prediction.answer, "question": question, "tag": tag, "success": True, "error": None}
        except Exception as e:
            return {"answer": "I don't know", "question": question, "tag": tag, "success": False, "error": str(e)}

    def batch_query(self, questions: List[str], tag: str = "general") -> List[Dict[str, Any]]:
        """
        Process multiple questions in batch.

        Args:
            questions: List of questions to ask
            tag: The tag/category for the questions

        Returns:
            List of dictionaries containing answers and metadata
        """
        results = []
        for question in questions:
            result = self.query(question, tag)
            results.append(result)
        return results

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get information about the RAG system.

        Returns:
            Dictionary containing system information
        """
        return {
            "system_type": "DSPy RAG System",
            "version": "1.0.0",
            "components": {"reader": "RAGAnswer", "retriever": "HybridVectorStore", "reranker": "CrossEncoderReranker"},
            "configuration": {
                "abstain_enabled": self.rag_answer.abstain_enabled,
                "enforce_span": self.rag_answer.enforce_span,
                "precheck_enabled": self.rag_answer.precheck_enabled,
                "precheck_min_overlap": self.rag_answer.precheck_min_overlap,
            },
        }


def main():
    """Main entry point for testing the RAG system."""
    print("🤖 DSPy RAG System - Test Mode")
    print("=" * 40)

    # Initialize the system
    rag_system = DSPyRAGSystem()

    # Get system info
    info = rag_system.get_system_info()
    print(f"System: {info['system_type']} v{info['version']}")
    print(f"Components: {', '.join(info['components'].values())}")
    print()

    # Test queries
    test_queries = [
        "What is DSPy and how does it work?",
        "How do I implement a RAG system?",
        "What are the key components of the memory system?",
    ]

    print("🧪 Running test queries...")
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        result = rag_system.query(query)
        print(f"   Answer: {result['answer']}")
        print(f"   Success: {result['success']}")
        if result["error"]:
            print(f"   Error: {result['error']}")


if __name__ == "__main__":
    main()
