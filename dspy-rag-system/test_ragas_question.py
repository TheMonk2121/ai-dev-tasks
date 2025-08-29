#!/usr/bin/env python3
"""
Simple test to ask the RAGAS question directly.
"""

import os
import sys

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from dspy_modules.model_switcher import ModelSwitcher


def test_ragas_question():
    """Test asking the RAGAS question directly to each role."""

    question = """Do you agree that RAGAS is the right starting point for evaluating our DSPy RAG memory system?

BACKGROUND:
- We have a working DSPy RAG system with memory capabilities
- We need to evaluate retrieval quality and memory system effectiveness
- We're considering using RAGAS (RAG Assessment Framework) for evaluation
- We want to avoid over-engineering but get meaningful metrics

PROPOSED APPROACH:
- Use RAGAS for core evaluation (Context Relevancy, Context Recall, Faithfulness, Answer Relevancy)
- Create 10-20 test queries with expected relevant documents
- Measure baseline performance before considering any enhancements
- Keep evaluation simple and focused

YOUR TASK: Answer YES or NO to whether RAGAS is the right starting point, then provide your reasoning. Keep your response focused and direct."""

    roles = ["planner", "researcher", "implementer", "coder", "reviewer"]

    print("🤖 Testing RAGAS question with DSPy agents...\n")

    for role in roles:
        print(f"📋 {role.upper()} ANSWER:")
        print("-" * 50)

        try:
            switcher = ModelSwitcher()
            switcher.switch_model(switcher.get_model_for_role(role))
            response = switcher.current_lm(question)
            print(f"Response: {response}")
            print("\n" + "=" * 60 + "\n")

        except Exception as e:
            print(f"Error getting {role} answer: {e}")
            print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    test_ragas_question()
