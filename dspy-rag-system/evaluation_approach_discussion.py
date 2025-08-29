#!/usr/bin/env python3
"""
Discussion with DSPy agents about evaluation approach for memory system.
"""

import os
import sys

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from dspy_modules.model_switcher import cursor_orchestrate_task


def discuss_evaluation_approach():
    """Discuss evaluation approach with DSPy agents."""

    discussion_prompt = """
    ANSWER THIS QUESTION: Do you agree that RAGAS is the right starting point for evaluating our DSPy RAG memory system?

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

    YOUR TASK: Answer YES or NO to whether RAGAS is the right starting point, then provide your reasoning. Keep your response focused and direct.
    """

    roles = ["planner", "researcher", "implementer", "coder", "reviewer"]

    print("🤖 Discussing evaluation approach with DSPy agents...\n")

    for role in roles:
        print(f"📋 {role.upper()} PERSPECTIVE:")
        print("-" * 50)

        try:
            result = cursor_orchestrate_task(role, discussion_prompt)

            # Extract the response based on role
            if role == "planner" and "plan" in result:
                response = result["plan"]
            elif role == "researcher" and "analysis" in result:
                response = result["analysis"]
            elif role == "implementer" and "execution" in result:
                response = result["execution"]
            elif role == "coder" and "implementation" in result:
                response = result["implementation"]
            elif role == "reviewer" and "review" in result:
                response = result["review"]
            elif "response" in result:
                response = result["response"]
            elif "error" in result:
                response = f"Error: {result['error']}"
            else:
                response = str(result)

            print(response)
            print("\n" + "=" * 60 + "\n")

        except Exception as e:
            print(f"Error getting {role} perspective: {e}")
            print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    discuss_evaluation_approach()
