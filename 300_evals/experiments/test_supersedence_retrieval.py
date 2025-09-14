#!/usr/bin/env python3
"""
Test script to verify supersedence and decision-first retrieval functionality
"""

import os
import sys

# Add the dspy-rag-system src to path
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "dspy-rag-system", "src"))  # REMOVED: DSPy venv consolidated into main project

def test_supersedence_retrieval():
    """Test supersedence and decision-first retrieval system"""

    print("🧪 Testing Supersedence and Decision-First Retrieval...")

    try:
        from utils.decision_extractor import DecisionExtractor
        from utils.supersedence_retrieval import SupersedenceRetrieval, create_supersedence_tables

        # Test with a mock connection string (won't actually connect)
        db_connection_string = "postgresql://localhost/test"

        # Create supersedence tables
        create_supersedence_tables(db_connection_string)

        # Initialize systems
        supersedence = SupersedenceRetrieval(db_connection_string)
        extractor = DecisionExtractor(db_connection_string)

        # Test conversation with conflicting decisions
        test_conversations = [
            {
                "session_id": "conflict_test_1",
                "role": "user",
                "text": "We should use PostgreSQL for our database. It's definitely the best choice.",
            },
            {
                "session_id": "conflict_test_2",
                "role": "assistant",
                "text": "Actually, let's use MongoDB instead of PostgreSQL. It's better for our use case.",
            },
            {
                "session_id": "conflict_test_3",
                "role": "user",
                "text": "No, we'll stick with PostgreSQL. It has better ACID compliance.",
            },
        ]

        print("\n📝 Testing conflicting decisions...")

        # Process conversations and extract decisions
        all_decisions = []
        for i, conv in enumerate(test_conversations, 1):
            print(f"\n   Conversation {i}: {conv['text'][:60]}...")

            # Extract decisions
            decisions = extractor.extract_decisions_from_text(conv["text"], conv["session_id"], conv["role"])

            if decisions:
                print(f"   ✅ Extracted {len(decisions)} decisions:")
                for decision in decisions:
                    print(f"      - {decision['head'][:50]}... (confidence: {decision['confidence']:.2f})")
                    all_decisions.append(decision)
            else:
                print("   ⚠️  No decisions extracted")

        # Test conflict detection
        print("\n🔍 Testing conflict detection...")

        if len(all_decisions) >= 2:
            # Test conflict detection between first two decisions
            decision1 = all_decisions[0]
            decision2 = all_decisions[1]

            print(f"   Decision 1: {decision1['head'][:50]}...")
            print(f"   Decision 2: {decision2['head'][:50]}...")

            # Check if they conflict
            conflicts = supersedence.detect_conflicts(decision1)
            print(f"   Conflicts for Decision 1: {len(conflicts)}")

            if conflicts:
                print("   ✅ Conflict detection working!")
                for conflict in conflicts:
                    print(f"      - Conflicting: {conflict['head'][:50]}...")
            else:
                print("   ⚠️  No conflicts detected")

        # Test hybrid search
        print("\n🔍 Testing hybrid search...")

        search_queries = ["postgresql", "database", "mongodb"]

        for query in search_queries:
            print(f"\n   Searching for: '{query}'")

            # Test hybrid search
            decisions = supersedence.hybrid_search_decisions(query, limit=5)

            print(f"   ✅ Found {len(decisions)} decisions")

            for j, decision in enumerate(decisions, 1):
                print(f"      {j}. {decision.get('head', 'N/A')[:50]}...")
                print(f"         Confidence: {decision.get('confidence', 0):.2f}")
                print(f"         Superseded: {decision.get('superseded', False)}")
                print(f"         Final Score: {decision.get('final_score', 0):.2f}")

        # Test decision-first packing
        print("\n📦 Testing decision-first packing...")

        for query in search_queries[:1]:  # Test with first query
            print(f"\n   Packing decisions for: '{query}'")

            packed_result = supersedence.pack_decisions_first(query, limit=5)

            print(f"   ✅ Packed {packed_result['total_decisions']} decisions")

            packed_content = packed_result.get("packed_content", [])
            for item in packed_content:
                if item["type"] == "decision_header":
                    print(f"      📋 {item['content']}")
                elif item["type"] == "decision":
                    print(f"      🎯 {item['content'][:60]}...")
                    print(f"         Rank: {item['rank']}")

        # Test supersedence stats
        print("\n📊 Testing supersedence stats...")

        stats = supersedence.get_supersedence_stats()
        if stats:
            print("   ✅ Supersedence stats:")
            for key, value in stats.items():
                print(f"      {key}: {value}")
        else:
            print("   ⚠️  No stats available (likely due to no database connection)")

        print("\n🎉 Supersedence and retrieval test completed!")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_supersedence_retrieval()
    sys.exit(0 if success else 1)
