#!/usr/bin/env python3
"""
Direct test of decision extractor without database dependencies
"""

import os
import sys

# Add the dspy-rag-system src to path
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "dspy-rag-system", "src"))  # REMOVED: DSPy venv consolidated into main project

def test_decision_extractor():
    """Test decision extractor directly"""

    print("🧪 Testing Decision Extractor Directly...")

    try:
        from utils.decision_extractor import DecisionExtractor

        # Test with a mock connection string (won't actually connect)
        extractor = DecisionExtractor("postgresql://localhost/test")

        # Test conversation turns with decisions
        test_conversations = [
            {
                "session_id": "test_session_1",
                "role": "user",
                "text": "I think we should use PostgreSQL with pgvector for our vector search needs. It's definitely the best approach for our RAG system.",
            },
            {
                "session_id": "test_session_2",
                "role": "assistant",
                "text": "Let's implement the MCP server for Cursor integration. I recommend using FastAPI for the HTTP endpoints.",
            },
            {
                "session_id": "test_session_3",
                "role": "user",
                "text": "We'll go with Python 3.12 for this project. It has better performance than Python 3.11.",
            },
            {
                "session_id": "test_session_4",
                "role": "assistant",
                "text": "For the database schema, we should choose a normalized approach over denormalized. It will be more maintainable.",
            },
        ]

        # Test decision extraction for each conversation
        for i, conv in enumerate(test_conversations, 1):
            print(f"\n📝 Testing conversation {i}:")
            print(f"   Session: {conv['session_id']}")
            print(f"   Role: {conv['role']}")
            print(f"   Text: {conv['text'][:100]}...")

            # Extract decisions (without storing to database)
            decisions = extractor.extract_decisions_from_text(conv["text"], conv["session_id"], conv["role"])

            if decisions:
                print(f"   ✅ Extracted {len(decisions)} decisions:")
                for j, decision in enumerate(decisions, 1):
                    print(f"      {j}. {decision['head'][:60]}...")
                    print(f"         Confidence: {decision['confidence']:.2f}")
                    print(f"         Pattern: {decision['pattern_type']}")
                    print(f"         Key: {decision['decision_key']}")
            else:
                print("   ⚠️  No decisions extracted")

        print("\n🎉 Decision extractor test completed!")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_decision_extractor()
    sys.exit(0 if success else 1)
