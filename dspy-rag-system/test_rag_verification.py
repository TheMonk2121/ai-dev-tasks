#!/usr/bin/env python3
"""
Test the RAG pipeline directly to verify context access and citations.
"""

import os
import sys

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from dspy_modules.model_switcher import cursor_orchestrate_task


def test_rag_verification():
    """Test the RAG pipeline with specific questions that should find context."""

    print("🧠 TESTING RAG PIPELINE VERIFICATION")
    print("=" * 80)

    # Test queries that should find specific content
    test_queries = [
        {
            "question": "What is DSPy according to 400_07_ai-frameworks-dspy.md?",
            "expected_citations": ["400_07_ai-frameworks-dspy.md"],
            "expected_keywords": ["framework", "ai", "language models", "signatures", "teleprompter"],
            "description": "DSPy framework identification",
        },
        {
            "question": "List the core workflow guides in 000_core.",
            "expected_citations": ["000_core", "000_backlog.md", "001_create-prd.md"],
            "expected_keywords": ["create-prd", "generate-tasks", "process-task-list", "development-roadmap"],
            "description": "Core workflow guides access",
        },
        {
            "question": "What is the CONTEXT_INDEX and what files are included in it?",
            "expected_citations": ["100_cursor-memory-context.md"],
            "expected_keywords": ["context_index", "files", "role", "path"],
            "description": "CONTEXT_INDEX understanding",
        },
        {
            "question": "What roles are defined in the CONTEXT_INDEX?",
            "expected_citations": ["100_cursor-memory-context.md"],
            "expected_keywords": ["planner", "implementer", "researcher", "coder"],
            "description": "Role definitions access",
        },
        {
            "question": "What is the memory system in this project?",
            "expected_citations": ["memory", "context"],
            "expected_keywords": ["memory", "context", "system", "rehydration"],
            "description": "Memory system understanding",
        },
    ]

    total_score = 0
    total_queries = len(test_queries)

    for i, query_info in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}/{total_queries}: {query_info['description']}")
        print(f"Question: {query_info['question']}")
        print("-" * 60)

        try:
            # Test with researcher role (should use RAG)
            result = cursor_orchestrate_task(query_info["question"], task_type="question", role="researcher")

            if result.get("success"):
                answer = result.get("analysis", result.get("response", ""))
                method = result.get("method", "unknown")
                citations = result.get("citations", [])
                context_used = result.get("context_used", False)
                retrieval_count = result.get("retrieval_count", 0)

                print(f"🤖 Method: {method}")
                print(f"📚 Context Used: {context_used}")
                print(f"🔍 Retrieval Count: {retrieval_count}")
                print(f"📄 Citations: {citations}")
                print(f"💬 Answer: {answer[:300]}...")

                # Calculate score based on multiple factors
                score = 0

                # Check if context was used
                if context_used:
                    score += 30
                    print("✅ Context was used")
                else:
                    print("❌ Context was not used")

                # Check citations
                citation_score = 0
                for expected_citation in query_info["expected_citations"]:
                    if any(expected_citation.lower() in citation.lower() for citation in citations):
                        citation_score += 20

                score += min(citation_score, 40)  # Max 40 points for citations
                print(f"📄 Citation score: {citation_score}/40")

                # Check for expected keywords
                keyword_score = 0
                answer_lower = answer.lower()
                for keyword in query_info["expected_keywords"]:
                    if keyword.lower() in answer_lower:
                        keyword_score += 10

                score += min(keyword_score, 30)  # Max 30 points for keywords
                print(f"🔑 Keyword score: {keyword_score}/30")

                print(f"📊 Total Score: {score}/100")
                total_score += score

            else:
                print(f"❌ Query failed: {result.get('error', 'Unknown error')}")
                total_score += 0

        except Exception as e:
            print(f"❌ Error: {e}")
            total_score += 0

    # Calculate overall score
    average_score = total_score / total_queries if total_queries > 0 else 0

    print("\n" + "=" * 80)
    print("📈 RAG PIPELINE VERIFICATION RESULTS")
    print("=" * 80)
    print(f"Total Queries: {total_queries}")
    print(f"Average Score: {average_score:.1f}%")

    if average_score >= 80:
        print("✅ EXCELLENT: RAG pipeline is working perfectly")
    elif average_score >= 60:
        print("✅ GOOD: RAG pipeline is mostly working")
    elif average_score >= 40:
        print("⚠️ FAIR: RAG pipeline needs improvement")
    else:
        print("❌ POOR: RAG pipeline is not working properly")

    return average_score


def test_role_comparison():
    """Test different roles to see if they use RAG appropriately."""

    print("\n" + "=" * 80)
    print("🎭 TESTING ROLE COMPARISON")
    print("=" * 80)

    question = "What is DSPy in this project?"
    roles = ["planner", "implementer", "researcher", "coder"]

    for role in roles:
        print(f"\n📋 Testing {role.upper()} role:")
        print("-" * 50)

        try:
            result = cursor_orchestrate_task(question, task_type="question", role=role)

            if result.get("success"):
                method = result.get("method", "unknown")
                context_used = result.get("context_used", False)
                citations = result.get("citations", [])

                print(f"Method: {method}")
                print(f"Context Used: {context_used}")
                print(f"Citations: {citations}")

                if context_used and citations:
                    print(f"✅ {role} is using RAG properly")
                elif role in ["planner", "implementer", "researcher"]:
                    print(f"⚠️ {role} should be using RAG but isn't")
                else:
                    print(f"ℹ️ {role} is using direct LM (expected)")
            else:
                print(f"❌ {role} failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"❌ Error with {role}: {e}")


def test_retrieval_debug():
    """Debug retrieval to see what's being found."""

    print("\n" + "=" * 80)
    print("🔍 TESTING RETRIEVAL DEBUG")
    print("=" * 80)

    try:
        from dspy_modules.model_switcher import ModelSwitcher

        switcher = ModelSwitcher()

        if hasattr(switcher, "rag_pipeline") and switcher.rag_pipeline:
            question = "What is DSPy?"

            print(f"Question: {question}")
            print("-" * 50)

            # Debug retrieval
            debug_result = switcher.rag_pipeline.debug_retrieval(question, k=5)

            if debug_result["status"] == "success":
                hits = debug_result["hits"]
                print(f"Found {len(hits)} hits:")

                for i, hit in enumerate(hits, 1):
                    print(f"  {i}. Score: {hit['score']}")
                    print(f"     Title: {hit['title']}")
                    print(f"     Content: {hit['content']}")
                    print(f"     Has CONTEXT_INDEX: {hit['has_context_index']}")
                    print()
            else:
                print(f"❌ Retrieval failed: {debug_result.get('error', 'Unknown error')}")
        else:
            print("❌ RAG pipeline not available")

    except Exception as e:
        print(f"❌ Debug failed: {e}")


if __name__ == "__main__":
    # Test RAG verification
    score = test_rag_verification()

    # Test role comparison
    test_role_comparison()

    # Test retrieval debug
    test_retrieval_debug()

    print("\n✅ RAG verification complete!")
    print(f"🎯 Overall Score: {score:.1f}%")

    if score >= 60:
        print("🎉 SUCCESS: RAG pipeline is working!")
    else:
        print("⚠️ NEEDS IMPROVEMENT: RAG pipeline needs work")
