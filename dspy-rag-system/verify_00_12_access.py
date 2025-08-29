#!/usr/bin/env python3
"""
Verification script to test if all 00-12 guides are accessible to the models.
"""

import os
import sys

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from dspy_modules.model_switcher import ModelSwitcher


def test_00_12_guide_access():
    """Test if all 00-12 guides are accessible to the models."""

    print("🧠 VERIFYING 00-12 GUIDE ACCESS")
    print("=" * 80)

    # Initialize model switcher
    switcher = ModelSwitcher()
    switcher.switch_model(switcher.get_model_for_role("researcher"))

    # Test queries to verify guide access
    test_queries = [
        {
            "question": "What is DSPy according to the 400_07_ai-frameworks-dspy.md guide?",
            "expected_keywords": ["framework", "ai", "language models", "structured"],
            "description": "DSPy framework identification",
        },
        {
            "question": "What are the core workflow guides mentioned in the 000_core documentation?",
            "expected_keywords": ["create-prd", "generate-tasks", "process-task-list", "development-roadmap"],
            "description": "Core workflow guides access",
        },
        {
            "question": "What is the system architecture described in 400_03_system-overview-and-architecture.md?",
            "expected_keywords": ["architecture", "layers", "components", "system"],
            "description": "System architecture access",
        },
        {
            "question": "What coding standards are outlined in 400_05_coding-and-prompting-standards.md?",
            "expected_keywords": ["PEP 8", "type hints", "docstrings", "standards"],
            "description": "Coding standards access",
        },
        {
            "question": "What is the governance model described in 400_02_governance-and-ai-constitution.md?",
            "expected_keywords": ["governance", "constitution", "ai", "safety"],
            "description": "Governance access",
        },
    ]

    total_score = 0
    total_queries = len(test_queries)

    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}/{total_queries}: {query['description']}")
        print(f"Question: {query['question']}")
        print("-" * 60)

        try:
            # Get response from model
            response = switcher.current_lm(query["question"])
            response_text = response[0] if isinstance(response, list) else str(response)

            print(f"🤖 Response: {response_text[:300]}...")

            # Check for expected keywords
            response_lower = response_text.lower()
            found_keywords = []
            missing_keywords = []

            for keyword in query["expected_keywords"]:
                if keyword.lower() in response_lower:
                    found_keywords.append(keyword)
                else:
                    missing_keywords.append(keyword)

            # Calculate score
            score = len(found_keywords) / len(query["expected_keywords"]) * 100

            print("📊 Evaluation:")
            print(f"  - Score: {score:.1f}%")
            print(f"  - Found: {', '.join(found_keywords)}")
            print(f"  - Missing: {', '.join(missing_keywords)}")

            total_score += score

        except Exception as e:
            print(f"❌ Error: {e}")
            total_score += 0

    # Calculate overall score
    average_score = total_score / total_queries if total_queries > 0 else 0

    print("\n" + "=" * 80)
    print("📈 VERIFICATION RESULTS")
    print("=" * 80)
    print(f"Total Queries: {total_queries}")
    print(f"Average Score: {average_score:.1f}%")

    if average_score >= 80:
        print("✅ EXCELLENT: All 00-12 guides are accessible")
    elif average_score >= 60:
        print("✅ GOOD: Most 00-12 guides are accessible")
    elif average_score >= 40:
        print("⚠️ FAIR: Some 00-12 guides are accessible")
    else:
        print("❌ POOR: 00-12 guides are not properly accessible")

    return average_score


def test_specific_guide_content():
    """Test specific content from individual guides."""

    print("\n" + "=" * 80)
    print("🔍 TESTING SPECIFIC GUIDE CONTENT")
    print("=" * 80)

    switcher = ModelSwitcher()
    switcher.switch_model(switcher.get_model_for_role("researcher"))

    # Test specific guide content
    specific_tests = [
        {
            "guide": "400_07_ai-frameworks-dspy.md",
            "question": "What is DSPy and how does it work?",
            "expected_content": ["framework", "ai", "language models"],
        },
        {
            "guide": "000_core/001_create-prd.md",
            "question": "What is the PRD creation process?",
            "expected_content": ["PRD", "requirements", "document"],
        },
        {
            "guide": "400_03_system-overview-and-architecture.md",
            "question": "What is the system architecture?",
            "expected_content": ["architecture", "layers", "components"],
        },
    ]

    for test in specific_tests:
        print(f"\n📋 Testing {test['guide']}:")
        print(f"Question: {test['question']}")
        print("-" * 50)

        try:
            response = switcher.current_lm(test["question"])
            response_text = response[0] if isinstance(response, list) else str(response)

            print(f"Response: {response_text[:200]}...")

            # Check for expected content
            found_content = []
            for content in test["expected_content"]:
                if content.lower() in response_text.lower():
                    found_content.append(content)

            if found_content:
                print(f"✅ Found expected content: {', '.join(found_content)}")
            else:
                print(f"❌ Missing expected content: {', '.join(test['expected_content'])}")

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Test 00-12 guide access
    score = test_00_12_guide_access()

    # Test specific guide content
    test_specific_guide_content()

    print("\n✅ Verification complete!")
    print(f"🎯 Overall Score: {score:.1f}%")

    if score >= 60:
        print("🎉 SUCCESS: 00-12 guides are properly accessible!")
    else:
        print("⚠️ NEEDS IMPROVEMENT: 00-12 guide access needs work")
