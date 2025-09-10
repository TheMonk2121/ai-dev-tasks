#!/usr/bin/env python3
"""
Simple test to ask a direct question to each role.
"""

import os
import sys

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from dspy_modules.model_switcher import cursor_orchestrate_task


def test_simple_question():
    """Test asking a simple question to each role."""

    question = "What is 2 + 2? Please answer with just the number."

    roles = ["planner", "researcher", "implementer", "coder", "reviewer"]

    print("🤖 Testing simple question with DSPy agents...\n")

    for role in roles:
        print(f"📋 {role.upper()} ANSWER:")
        print("-" * 50)

        try:
            result = cursor_orchestrate_task(question, "simple_question", role)
            print(f"Result: {result}")
            print("\n" + "=" * 60 + "\n")

        except Exception as e:
            print(f"Error getting {role} answer: {e}")
            print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    test_simple_question()
