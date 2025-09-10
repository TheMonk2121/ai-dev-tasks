#!/usr/bin/env python3
"""
Debug script to see what the search is returning.
"""

import os
import sys

from dotenv import load_dotenv

# Add src to path
sys.path.append("src")

from dspy_modules.vector_store import HybridVectorStore

load_dotenv()


def main():
    """Debug the search results."""
    print("=== Search Debug ===")

    # Initialize the vector store
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not set")
        return

    try:
        retriever = HybridVectorStore(db_url)
        print("✅ Vector store initialized")

        # Test search
        q = "What is DSPy according to 400_07_ai-frameworks-dspy.md?"
        print(f"Query: {q}")

        result = retriever.forward("search", query=q, limit=12)
        print(f"Search result status: {result['status']}")

        if result["status"] == "success":
            rows = result["results"]
            print(f"Number of rows returned: {len(rows)}")

            if rows:
                print("First row:")
                print(f"  Keys: {list(rows[0].keys())}")
                print(f"  Document ID: {rows[0].get('document_id')}")
                print(f"  Filename: {rows[0].get('filename')}")
                print(f"  Score: {rows[0].get('score')}")
                print(f"  Content preview: {rows[0].get('content', '')[:100]}...")
            else:
                print("No rows returned")
        else:
            print(f"Search failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
