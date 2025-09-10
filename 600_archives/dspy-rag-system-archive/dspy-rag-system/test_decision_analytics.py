#!/usr/bin/env python3
"""
Test script for Decision Analytics and Insights

This script tests the comprehensive decision analytics functionality.
"""

import os
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from utils.conversation_storage import ConversationSession, ConversationStorage


def test_decision_analytics():
    """Test decision analytics functionality."""
    storage = ConversationStorage()

    print("🧪 Testing Decision Analytics and Insights...")

    try:
        # Connect to database
        if not storage.connect():
            print("❌ Failed to connect to database")
            return False

        # Create test session
        test_session = ConversationSession(
            session_id="test_analytics_session",
            user_id="test_user",
            session_name="Decision Analytics Test",
            session_type="test",
        )

        if not storage.create_session(test_session):
            print("❌ Failed to create test session")
            return False

        print("✅ Test session created")

        # Create test decisions with various patterns
        test_decisions = [
            {
                "decision_head": "use_python_3_11",
                "context_value": "Initial decision to use Python 3.11",
                "entities": ["python", "project", "version"],
                "files": ["requirements.txt"],
                "relevance_score": 0.7,
            },
            {
                "decision_head": "use_python_3_12",
                "context_value": "Upgraded to Python 3.12 for better performance",
                "entities": ["python", "project", "performance"],
                "files": ["requirements.txt", "pyproject.toml"],
                "relevance_score": 0.9,
            },
            {
                "decision_head": "enable_debug_mode",
                "context_value": "Enable debug mode for development",
                "entities": ["debug", "development", "mode"],
                "files": ["config.py"],
                "relevance_score": 0.8,
            },
            {
                "decision_head": "disable_debug_mode",
                "context_value": "Disable debug mode in production",
                "entities": ["debug", "production", "mode"],
                "files": ["config.py"],
                "relevance_score": 0.6,
            },
            {
                "decision_head": "use_postgresql",
                "context_value": "Use PostgreSQL as primary database",
                "entities": ["database", "postgresql", "primary"],
                "files": ["database.py", "config.py"],
                "relevance_score": 0.9,
            },
        ]

        # Store test decisions
        print("\n📝 Storing Test Decisions...")
        for i, decision in enumerate(test_decisions):
            success = storage.store_decision(
                session_id="test_analytics_session",
                decision_head=decision["decision_head"],
                context_value=decision["context_value"],
                entities=decision["entities"],
                files=decision["files"],
                relevance_score=decision["relevance_score"],
                auto_supersede=True,
            )
            if not success:
                print(f"❌ Failed to store decision {i+1}: {decision['decision_head']}")
                return False
            print(f"✅ Decision {i+1} stored: {decision['decision_head']}")

        # Test 1: Basic Analytics
        print("\n🔍 Test 1: Basic Decision Analytics")
        analytics = storage.get_decision_analytics("test_analytics_session", time_range_days=30)

        if "error" in analytics:
            print(f"❌ Analytics failed: {analytics['error']}")
            return False

        print(f"✅ Analytics retrieved: {analytics['total_decisions']} decisions")
        print(f"   - Time range: {analytics['time_range_days']} days")
        print(f"   - Execution time: {analytics['execution_time_ms']:.2f}ms")

        # Test 2: Pattern Analysis
        print("\n🔍 Test 2: Pattern Analysis")
        if "analytics" in analytics:
            patterns = analytics["analytics"]

            # Status distribution
            if "status_distribution" in patterns:
                print("   Status Distribution:")
                for status, count in patterns["status_distribution"].items():
                    print(f"     - {status}: {count}")

            # Entity frequency
            if "entity_frequency" in patterns:
                print("   Top Entities:")
                sorted_entities = sorted(patterns["entity_frequency"].items(), key=lambda x: x[1], reverse=True)[:5]
                for entity, count in sorted_entities:
                    print(f"     - {entity}: {count}")

            # Relevance distribution
            if "relevance_score_distribution" in patterns:
                print("   Relevance Score Distribution:")
                for range_name, count in patterns["relevance_score_distribution"].items():
                    print(f"     - {range_name}: {count}")
        else:
            print("❌ Pattern analysis not available")
            return False

        # Test 3: Trend Analysis
        print("\n🔍 Test 3: Trend Analysis")
        if "trends" in analytics:
            trends = analytics["trends"]

            if "daily_decision_count" in trends:
                print("   Daily Decision Count:")
                for date, count in list(trends["daily_decision_count"].items())[:3]:
                    print(f"     - {date}: {count}")

            if "relevance_trends" in trends:
                print("   Relevance Trends:")
                for date, data in list(trends["relevance_trends"].items())[:3]:
                    print(f"     - {date}: avg={data.get('average', 0):.2f}, count={data.get('count', 0)}")
        else:
            print("❌ Trend analysis not available")
            return False

        # Test 4: Entity Relationship Analysis
        print("\n🔍 Test 4: Entity Relationship Analysis")
        if "entity_analysis" in analytics:
            entity_analysis = analytics["entity_analysis"]

            if "entity_co_occurrence" in entity_analysis:
                print("   Entity Co-occurrences:")
                sorted_co_occurrences = sorted(
                    entity_analysis["entity_co_occurrence"].items(), key=lambda x: x[1], reverse=True
                )[:3]
                for pair, count in sorted_co_occurrences:
                    print(f"     - {pair}: {count}")

            if "entity_relevance_correlation" in entity_analysis:
                print("   Entity Relevance Correlation:")
                for entity, data in list(entity_analysis["entity_relevance_correlation"].items())[:3]:
                    print(f"     - {entity}: avg={data.get('average', 0):.2f}, count={data.get('count', 0)}")
        else:
            print("❌ Entity analysis not available")
            return False

        # Test 5: Effectiveness Analysis
        print("\n🔍 Test 5: Effectiveness Analysis")
        if "effectiveness" in analytics:
            effectiveness = analytics["effectiveness"]

            if "supersedence_effectiveness" in effectiveness:
                supersedence = effectiveness["supersedence_effectiveness"]
                print("   Supersedence Effectiveness:")
                print(f"     - Total decisions: {supersedence.get('total_decisions', 0)}")
                print(f"     - Superseded: {supersedence.get('superseded_count', 0)}")
                print(f"     - Open: {supersedence.get('open_count', 0)}")
                print(f"     - Supersedence rate: {supersedence.get('supersedence_rate', 0):.1%}")

            if "relevance_effectiveness" in effectiveness:
                relevance = effectiveness["relevance_effectiveness"]
                print("   Relevance Effectiveness:")
                print(f"     - Average relevance: {relevance.get('average_relevance', 0):.2f}")
                print(f"     - High relevance (≥0.8): {relevance.get('high_relevance_count', 0)}")
                print(f"     - Low relevance (<0.5): {relevance.get('low_relevance_count', 0)}")
        else:
            print("❌ Effectiveness analysis not available")
            return False

        # Test 6: Decision Recommendations
        print("\n🔍 Test 6: Decision Recommendations")
        recommendations = storage.get_decision_recommendations("test_analytics_session")

        if "error" in recommendations:
            print(f"❌ Recommendations failed: {recommendations['error']}")
            return False

        print("   Recommendations:")
        if "action_items" in recommendations:
            for i, action in enumerate(recommendations["action_items"], 1):
                print(f"     {i}. {action}")

        if "decision_quality" in recommendations:
            print("   Decision Quality Insights:")
            for key, value in recommendations["decision_quality"].items():
                print(f"     - {key}: {value}")

        print("\n🎉 All Decision Analytics Tests Passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Cleanup test data
        try:
            if storage.connection and storage.cursor:
                storage.cursor.execute("DELETE FROM conversation_context WHERE session_id = 'test_analytics_session'")
                storage.cursor.execute("DELETE FROM conversation_sessions WHERE session_id = 'test_analytics_session'")
                storage.connection.commit()
                print("🧹 Test data cleaned up")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")

        storage.disconnect()


if __name__ == "__main__":
    success = test_decision_analytics()
    sys.exit(0 if success else 1)
