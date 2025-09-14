#!/usr/bin/env python3
"""
Capture your current Cursor conversation in real-time.
This script integrates with the Atlas graph system and memory consolidation.
"""

import os
import sys
from typing import Any

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Import our working integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utilities"))
from cursor_working_integration import CursorWorkingIntegration


def capture_conversation() -> Any:
    """Capture the current conversation."""
    print("🚀 Cursor Conversation Capture System")
    print("=" * 50)

    # Initialize integration
    integration = CursorWorkingIntegration()

    print("\n📝 Ready to capture your conversation!")
    print(f"   Session ID: {integration.session_id}")
    print(f"   Thread ID: {integration.thread_id}")
    print("\n💡 Usage:")
    print("   - Call integration.capture_user_query('your question')")
    print("   - Call integration.capture_ai_response('AI response')")
    print("   - Call integration.get_session_stats() for statistics")
    print("   - Call integration.close_session() when done")

    return integration


def main():
    """Main function for testing."""
    print("🧪 Testing conversation capture...")

    # Initialize integration
    integration = CursorWorkingIntegration()

    # Example conversation
    print("\n📝 Capturing example conversation...")

    # User query
    query_turn_id = integration.capture_user_query(
        "How do I implement user authentication in FastAPI with JWT tokens?",
        {"topic": "authentication", "complexity": "intermediate"},
    )

    # AI response
    _ = integration.capture_ai_response(
        "To implement user authentication in FastAPI with JWT tokens, you'll need to use libraries like python-jose and passlib. Here's a step-by-step guide:\n\n1. Install required packages\n2. Create user models\n3. Implement password hashing\n4. Create JWT token functions\n5. Add authentication middleware",
        query_turn_id,
        {"response_type": "tutorial", "steps": 5},
    )

    # Get session stats
    stats = integration.get_session_stats()
    print("\n📊 Session Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

    # Get recent conversation
    recent = integration.get_recent_conversation(2)
    print("\n💬 Recent conversation:")
    for turn in recent:
        print(f"   {turn['role']}: {turn['content'][:60]}...")

    # Close session
    integration.close_session()

    print("\n✅ Conversation captured successfully!")
    print("   Your queries are now stored in the Atlas graph system")
    print("   Memory consolidation is ready for processing")


if __name__ == "__main__":
    main()
