#!/usr/bin/env python3
"""
Test the retriever directly to see if it can find context.
"""

import os
import sys

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from dspy_modules.vector_store import HybridVectorStore


def test_retriever_directly():
    """Test the retriever directly, bypassing DSPy."""

    print("🔍 TESTING RETRIEVER DIRECTLY")
    print("=" * 80)

    try:
        # Get database connection string from environment
        db_connection_string = os.getenv("DATABASE_URL")
        if not db_connection_string:
            print("❌ DATABASE_URL environment variable not set")
            return

        # Initialize vector store
        vector_store = HybridVectorStore(db_connection_string)

        # Test queries that should find CONTEXT_INDEX
        test_queries = [
            "What is the CONTEXT_INDEX?",
            "What files are in the CONTEXT_INDEX?",
            "What roles are defined in the CONTEXT_INDEX?",
            "What is DSPy in this project?",
            "What is the memory system?",
        ]

        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Query {i}: {query}")
            print("-" * 60)

            try:
                # Get retrieval results directly
                result = vector_store.forward("search", query=query, limit=5)

                if result["status"] == "success":
                    results = result["results"]
                    print(f"Found {len(results)} results:")

                    for j, res in enumerate(results, 1):
                        score = res.get("score", "N/A")
                        title = res.get("file_path", "No title")
                        doc_id = res.get("document_id", "No ID")

                        print(f"  {j}. Score: {score}, Title: {title}, ID: {doc_id}")
                        print(f"     Content: {res.get('content', '')[:150]}...")

                        # Check if this result contains CONTEXT_INDEX
                        if "CONTEXT_INDEX" in res.get("content", ""):
                            print("     ✅ CONTAINS CONTEXT_INDEX!")

                        print()
                else:
                    print(f"❌ Search failed: {result}")

            except Exception as e:
                print(f"❌ Error retrieving for query: {e}")

    except Exception as e:
        print(f"❌ Error initializing vector store: {e}")


def test_specific_context_retrieval():
    """Test retrieval for specific context we know should be there."""

    print("\n" + "=" * 80)
    print("🎯 TESTING SPECIFIC CONTEXT RETRIEVAL")
    print("=" * 80)

    try:
        # Get database connection string from environment
        db_connection_string = os.getenv("DATABASE_URL")
        if not db_connection_string:
            print("❌ DATABASE_URL environment variable not set")
            return

        vector_store = HybridVectorStore(db_connection_string)

        # Test for specific content we know exists
        specific_queries = [
            "CONTEXT_INDEX files role path",
            "planner implementer researcher coder roles",
            "100_cursor-memory-context.md",
            "400_guides/400_00_getting-started-and-index.md",
        ]

        for query in specific_queries:
            print(f"\n🔍 Query: {query}")
            print("-" * 50)

            try:
                result = vector_store.forward("search", query=query, limit=3)

                if result["status"] == "success":
                    results = result["results"]

                    for i, res in enumerate(results, 1):
                        score = res.get("score", "N/A")
                        print(f"  {i}. Score: {score}")
                        print(f"     Content: {res.get('content', '')[:100]}...")

                        # Check for key terms
                        key_terms = ["CONTEXT_INDEX", "role", "path", "planner", "implementer"]
                        found_terms = [term for term in key_terms if term in res.get("content", "")]
                        if found_terms:
                            print(f"     ✅ Found terms: {', '.join(found_terms)}")

                        print()
                else:
                    print(f"❌ Search failed: {result}")

            except Exception as e:
                print(f"❌ Error: {e}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Test retriever directly
    test_retriever_directly()

    # Test specific context retrieval
    test_specific_context_retrieval()

    print("\n✅ Retriever testing complete!")
