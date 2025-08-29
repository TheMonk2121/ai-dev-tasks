#!/usr/bin/env python3
"""
Verification script to test if the codebase index is accessible to the models.
"""

import os
import sys

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from dspy_modules.model_switcher import ModelSwitcher


def test_codebase_index_access():
    """Test if the codebase index is accessible to the models."""

    print("🧠 VERIFYING CODEBASE INDEX ACCESS")
    print("=" * 80)

    # Initialize model switcher
    switcher = ModelSwitcher()
    switcher.switch_model(switcher.get_model_for_role("researcher"))

    # Test queries to verify codebase index access
    test_queries = [
        {
            "question": "What is the CONTEXT_INDEX and what files are included in it?",
            "expected_keywords": ["context_index", "files", "role", "path"],
            "description": "CONTEXT_INDEX understanding",
        },
        {
            "question": "What are the main entry points in the codebase according to the index?",
            "expected_keywords": ["entry", "getting-started", "priorities", "roadmap"],
            "description": "Entry points access",
        },
        {
            "question": "What roles are defined in the CONTEXT_INDEX?",
            "expected_keywords": ["planner", "implementer", "researcher", "coder", "role"],
            "description": "Role definitions access",
        },
        {
            "question": "What files are mapped to the 'architecture' role in the CONTEXT_INDEX?",
            "expected_keywords": ["architecture", "system-overview", "400_03"],
            "description": "Role-specific file mapping",
        },
        {
            "question": "What is the purpose of the CONTEXT_INDEX in the memory system?",
            "expected_keywords": ["context", "memory", "index", "files", "mapping"],
            "description": "CONTEXT_INDEX purpose",
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
    print("📈 CODEBASE INDEX VERIFICATION RESULTS")
    print("=" * 80)
    print(f"Total Queries: {total_queries}")
    print(f"Average Score: {average_score:.1f}%")

    if average_score >= 80:
        print("✅ EXCELLENT: Codebase index is fully accessible")
    elif average_score >= 60:
        print("✅ GOOD: Codebase index is mostly accessible")
    elif average_score >= 40:
        print("⚠️ FAIR: Codebase index is partially accessible")
    else:
        print("❌ POOR: Codebase index is not properly accessible")

    return average_score


def test_index_file_access():
    """Test access to specific files mentioned in the index."""

    print("\n" + "=" * 80)
    print("🔍 TESTING INDEX FILE ACCESS")
    print("=" * 80)

    switcher = ModelSwitcher()
    switcher.switch_model(switcher.get_model_for_role("researcher"))

    # Test specific files from the CONTEXT_INDEX
    index_files = [
        {
            "file": "400_guides/400_00_getting-started-and-index.md",
            "question": "What is the getting started guide about?",
            "expected_content": ["getting started", "index", "entry point"],
        },
        {
            "file": "000_core/000_backlog.md",
            "question": "What is the backlog file about?",
            "expected_content": ["backlog", "priorities", "tasks"],
        },
        {
            "file": "400_guides/400_03_system-overview-and-architecture.md",
            "question": "What is the system architecture?",
            "expected_content": ["architecture", "system", "overview"],
        },
    ]

    for test in index_files:
        print(f"\n📋 Testing {test['file']}:")
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


def test_role_mapping():
    """Test if role-based file mapping is working."""

    print("\n" + "=" * 80)
    print("🎭 TESTING ROLE MAPPING")
    print("=" * 80)

    roles = ["planner", "implementer", "researcher", "coder"]

    for role in roles:
        print(f"\n📋 Testing {role.upper()} role:")
        print("-" * 50)

        try:
            switcher = ModelSwitcher()
            switcher.switch_model(switcher.get_model_for_role(role))

            question = f"What files are available for the {role} role according to the CONTEXT_INDEX?"
            response = switcher.current_lm(question)
            response_text = response[0] if isinstance(response, list) else str(response)

            print(f"Question: {question}")
            print(f"Response: {response_text[:200]}...")

            # Check if response mentions role-specific content
            if role.lower() in response_text.lower():
                print(f"✅ Role-specific content found for {role}")
            else:
                print(f"⚠️ No role-specific content found for {role}")

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Test codebase index access
    score = test_codebase_index_access()

    # Test specific file access
    test_index_file_access()

    # Test role mapping
    test_role_mapping()

    print("\n✅ Codebase index verification complete!")
    print(f"🎯 Overall Score: {score:.1f}%")

    if score >= 60:
        print("🎉 SUCCESS: Codebase index is properly accessible!")
    else:
        print("⚠️ NEEDS IMPROVEMENT: Codebase index access needs work")
