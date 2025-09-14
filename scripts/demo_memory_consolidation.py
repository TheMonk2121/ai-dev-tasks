#!/usr/bin/env python3
"""
Demonstration script for the enhanced memory consolidation system.

Shows conversation summarization, fact extraction, and entity linking capabilities.
"""

import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from memory_graphs.consolidate import run


def demo_memory_consolidation():
    """Demonstrate the enhanced memory consolidation system."""

    print("🧠 Enhanced Memory Consolidation System Demo")
    print("=" * 60)

    # Sample conversation data
    conversation_data = [
        {
            "role": "user",
            "content": "I need to implement a user authentication system for our FastAPI application. We should use JWT tokens and store user data in PostgreSQL.",
            "timestamp": 1234567890.0,
        },
        {
            "role": "assistant",
            "content": "Great idea! I'll help you implement that. We should create an auth.py file with login and register endpoints. We'll need a users table with email, password_hash, and created_at columns. We can use python-jose for JWT handling and bcrypt for password hashing.",
            "timestamp": 1234567891.0,
        },
        {
            "role": "user",
            "content": "The system must achieve 99.9% uptime and handle at least 1000 concurrent users. We also need to implement rate limiting to prevent brute force attacks.",
            "timestamp": 1234567892.0,
        },
        {
            "role": "assistant",
            "content": "Perfect! We can use Redis for rate limiting and session management. I'll create the database migration script and the authentication middleware. We should also add comprehensive logging for security monitoring.",
            "timestamp": 1234567893.0,
        },
        {
            "role": "user",
            "content": "Let's also implement password reset functionality and email verification. We can use SendGrid for sending emails and create a password_reset_tokens table.",
            "timestamp": 1234567894.0,
        },
    ]

    print("📝 Input Conversation:")
    for i, turn in enumerate(conversation_data, 1):
        print(f"  {i}. [{turn['role']}]: {turn['content']}")

    print("\n🔄 Processing conversation...")

    # Run the consolidation pipeline
    result = run(conversation_data)

    print(f"\n✅ Processing completed in {result.processing_metadata['processing_time']:.3f}s")
    print(f"   📊 Processed {result.processing_metadata['turns_processed']} turns")
    print(f"   📋 Extracted {result.processing_metadata['facts_extracted']} facts")
    print(f"   🏷️  Found {result.processing_metadata['entities_found']} entities")
    print(f"   🔗 Created {result.processing_metadata['links_created']} entity links")

    # Display summary
    print("\n📄 Conversation Summary:")
    print(f"   {result.summary}")

    # Display facts
    print("\n📋 Extracted Facts:")
    for i, fact in enumerate(result.facts, 1):
        print(f"   {i}. [{fact.fact_type.upper()}] {fact.text}")
        print(f"      Confidence: {fact.confidence:.2f}")
        if fact.entities:
            print(f"      Entities: {', '.join(fact.entities)}")
        print()

    # Display entities
    print("\n🏷️  Extracted Entities:")
    for i, entity in enumerate(result.entities, 1):
        print(f"   {i}. {entity.text} ({entity.entity_type})")
        print(f"      Confidence: {entity.confidence:.2f}")
        print(f"      Context: {entity.context[:100]}...")
        if entity.aliases:
            print(f"      Aliases: {', '.join(entity.aliases)}")
        print(f"      Mentions: {entity.mentions}")
        print()

    # Display entity links
    if result.entity_links:
        print("\n🔗 Entity Relationships:")
        for i, link in enumerate(result.entity_links, 1):
            print(f"   {i}. {link.source_entity} --[{link.relationship_type}]--> {link.target_entity}")
            print(f"      Confidence: {link.confidence:.2f}")
            print(f"      Context: {link.context[:100]}...")
            print()

    # Display processing metadata
    print("\n📊 Processing Metadata:")
    for key, value in result.processing_metadata.items():
        print(f"   {key}: {value}")

    # Save results to JSON for inspection
    output_file = Path("memory_consolidation_demo_results.json")

    # Convert dataclasses to dictionaries for JSON serialization
    result_dict = {
        "summary": result.summary,
        "facts": [
            {
                "text": fact.text,
                "fact_type": fact.fact_type,
                "confidence": fact.confidence,
                "source_turn": fact.source_turn,
                "entities": fact.entities,
                "metadata": fact.metadata,
            }
            for fact in result.facts
        ],
        "entities": [
            {
                "text": entity.text,
                "entity_type": entity.entity_type,
                "confidence": entity.confidence,
                "context": entity.context,
                "mentions": entity.mentions,
                "aliases": entity.aliases,
            }
            for entity in result.entities
        ],
        "entity_links": [
            {
                "source_entity": link.source_entity,
                "target_entity": link.target_entity,
                "relationship_type": link.relationship_type,
                "confidence": link.confidence,
                "context": link.context,
            }
            for link in result.entity_links
        ],
        "upserts": result.upserts,
        "processing_metadata": result.processing_metadata,
    }

    with open(output_file, "w") as f:
        json.dump(result_dict, f, indent=2, default=str)

    print(f"\n💾 Results saved to: {output_file}")

    return result


def demo_edge_cases():
    """Demonstrate handling of edge cases."""

    print("\n🧪 Edge Cases Demo")
    print("=" * 40)

    # Empty conversation
    print("1. Empty conversation:")
    result = run([])
    print(f"   Summary: '{result.summary}'")
    print(f"   Facts: {len(result.facts)}")
    print(f"   Entities: {len(result.entities)}")

    # Single turn
    print("\n2. Single turn:")
    result = run([{"role": "user", "content": "Hello"}])
    print(f"   Summary: '{result.summary}'")
    print(f"   Facts: {len(result.facts)}")
    print(f"   Entities: {len(result.entities)}")

    # Very long conversation
    print("\n3. Long conversation:")
    long_data = []
    for i in range(20):
        long_data.append(
            {
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"This is turn {i+1} with some content about implementing features and fixing bugs.",
            }
        )

    result = run(long_data)
    print(f"   Summary length: {len(result.summary)}")
    print(f"   Facts: {len(result.facts)}")
    print(f"   Entities: {len(result.entities)}")
    print(f"   Processing time: {result.processing_metadata['processing_time']:.3f}s")


if __name__ == "__main__":
    try:
        # Main demonstration
        result = demo_memory_consolidation()

        # Edge cases demonstration
        demo_edge_cases()

        print("\n🎉 Demo completed successfully!")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
