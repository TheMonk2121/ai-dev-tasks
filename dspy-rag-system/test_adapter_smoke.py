#!/usr/bin/env python3
"""
Smoke test for the Hit adapter to verify invariants.
"""

import os
import sys

from dotenv import load_dotenv

# Add src to path
sys.path.append("src")

from dspy_modules.hit_adapter import smoke_test
from dspy_modules.vector_store import HybridVectorStore

load_dotenv()


def main():
    """Run the adapter smoke test."""
    print("=== Hit Adapter Smoke Test ===")

    # Initialize the vector store
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not set")
        return False

    try:
        retriever = HybridVectorStore(db_url)
        print("✅ Vector store initialized")

        # Run the smoke test
        success = smoke_test(retriever)

        if success:
            print("✅ All adapter invariants passed!")
            return True
        else:
            print("❌ Adapter smoke test failed")
            return False

    except Exception as e:
        print(f"❌ Smoke test crashed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
