#!/usr/bin/env python3
"""
Comprehensive tests for the enhanced memory consolidation system.

Tests conversation summarization, fact extraction, and entity linking capabilities.
"""

import os
from dataclasses import asdict

import pytest

# Enable memory graph for testing
os.environ["APP_USE_MEMORY_GRAPH"] = "true"

# Import after setting environment variable
from src.memory_graphs.consolidate import (
    ConsolidationResult,
    Entity,
    EntityLink,
    Fact,
    Turn,
    collect_turns,
    extract_entities,
    extract_facts,
    link_entities,
    run,
    summarize,
)


class TestMemoryConsolidation:
    """Test suite for memory consolidation functionality."""

    def test_collect_turns_basic(self):
        """Test basic turn collection."""
        raw_data = [
            {"role": "user", "content": "I need to implement a new feature"},
            {"role": "assistant", "content": "What kind of feature are you thinking about?"},
            {"role": "user", "content": "A user authentication system using FastAPI"},
        ]

        turns = collect_turns(raw_data)

        assert len(turns) == 3
        assert turns[0].role == "user"
        assert turns[0].content == "I need to implement a new feature"
        assert turns[1].role == "assistant"
        assert turns[2].content == "A user authentication system using FastAPI"

    def test_collect_turns_with_timestamps(self):
        """Test turn collection with timestamps."""
        raw_data = [
            {"role": "user", "content": "Hello", "timestamp": 1234567890.0},
            {"role": "assistant", "content": "Hi there!", "created_at": 1234567891.0},
        ]

        turns = collect_turns(raw_data)

        assert len(turns) == 2
        assert turns[0].timestamp == 1234567890.0
        assert turns[1].timestamp == 1234567891.0

    def test_summarize_single_turn(self):
        """Test summarization of single turn."""
        turns = [Turn(role="user", content="I need to implement a new feature for user authentication")]

        summary = summarize(turns)

        assert len(summary) > 0
        assert len(summary) <= 500  # Should be truncated
        assert "implement" in summary.lower()

    def test_summarize_multiple_turns(self):
        """Test summarization of multiple turns."""
        turns = [
            Turn(role="user", content="I need to implement a new feature"),
            Turn(role="assistant", content="What kind of feature?"),
            Turn(role="user", content="A user authentication system using FastAPI and JWT tokens"),
            Turn(role="assistant", content="Great! I'll help you implement that."),
        ]

        summary = summarize(turns)

        assert len(summary) > 0
        assert "authentication" in summary.lower() or "feature" in summary.lower()

    def test_extract_facts_basic(self):
        """Test basic fact extraction."""
        turns = [
            Turn(role="user", content="I need to implement a user authentication system"),
            Turn(role="assistant", content="We should use FastAPI and JWT tokens for this"),
        ]

        facts = extract_facts(turns, "Authentication system discussion")

        assert len(facts) > 0

        # Check for action facts
        action_facts = [f for f in facts if f.fact_type == "action"]
        assert len(action_facts) > 0
        assert any("implement" in fact.text.lower() for fact in action_facts)

        # Check fact structure
        for fact in facts:
            assert isinstance(fact, Fact)
            assert fact.text
            assert fact.fact_type in ["action", "decision", "requirement", "constraint", "metric", "entity"]
            assert 0 <= fact.confidence <= 1
            assert isinstance(fact.entities, list)

    def test_extract_facts_patterns(self):
        """Test fact extraction with various patterns."""
        turns = [
            Turn(role="user", content="We decided to use PostgreSQL for the database"),
            Turn(
                role="assistant", content="Good choice! We need to create a users table with email and password columns"
            ),
            Turn(role="user", content="The system must achieve 99.9% uptime"),
        ]

        facts = extract_facts(turns, "")

        # Check for decision fact
        decision_facts = [f for f in facts if f.fact_type == "decision"]
        assert any("PostgreSQL" in fact.text for fact in decision_facts)

        # Check for requirement fact
        requirement_facts = [f for f in facts if f.fact_type == "requirement"]
        assert any("uptime" in fact.text.lower() for fact in requirement_facts)

    def test_extract_entities_basic(self):
        """Test basic entity extraction."""
        turns = [
            Turn(role="user", content="Let's create auth.py file with FastAPI endpoints"),
            Turn(role="assistant", content="We can use https://jwt.io for token validation"),
        ]

        facts = extract_facts(turns, "")
        entities = extract_entities(turns, facts)

        assert len(entities) > 0

        # Check entity structure
        for entity in entities:
            assert isinstance(entity, Entity)
            assert entity.text
            assert entity.entity_type in ["file", "url", "code", "service", "database", "technology", "concept"]
            assert 0 <= entity.confidence <= 1
            assert isinstance(entity.mentions, list)
            assert isinstance(entity.aliases, list)

    def test_entity_classification(self):
        """Test entity type classification."""
        turns = [
            Turn(role="user", content="Let's create auth.py file with FastAPI endpoints"),
            Turn(role="assistant", content="We can use https://jwt.io for token validation"),
        ]

        facts = extract_facts(turns, "")
        entities = extract_entities(turns, facts)

        # Check for file entity
        file_entities = [e for e in entities if e.entity_type == "file"]
        assert any("auth.py" in e.text for e in file_entities)

        # Check for URL entity
        url_entities = [e for e in entities if e.entity_type == "url"]
        assert any("jwt.io" in e.text for e in url_entities)

    def test_entity_linking(self):
        """Test entity linking functionality."""
        turns = [
            Turn(role="user", content="I need to implement a user authentication system using FastAPI"),
            Turn(role="assistant", content="We should create auth.py file with JWT token handling"),
        ]

        facts = extract_facts(turns, "")
        entities = extract_entities(turns, facts)
        links = link_entities(facts, entities)

        assert len(links) >= 0  # May or may not have links depending on similarity

        # Check link structure
        for link in links:
            assert isinstance(link, EntityLink)
            assert link.source_entity
            assert link.target_entity
            assert link.relationship_type in ["mentions", "depends_on", "implements", "conflicts_with", "similar_to"]
            assert 0 <= link.confidence <= 1
            assert link.context

    def test_full_consolidation_pipeline(self):
        """Test the complete consolidation pipeline."""
        raw_data = [
            {
                "role": "user",
                "content": "I need to implement a user authentication system using FastAPI and JWT tokens",
                "timestamp": 1234567890.0,
            },
            {
                "role": "assistant",
                "content": "Great! We should create auth.py file with login and register endpoints. We'll need a users table in PostgreSQL.",
                "timestamp": 1234567891.0,
            },
            {
                "role": "user",
                "content": "The system must achieve 99.9% uptime and handle 1000 concurrent users",
                "timestamp": 1234567892.0,
            },
        ]

        result = run(raw_data)

        # Check result structure
        assert isinstance(result, ConsolidationResult)
        assert result.summary
        assert isinstance(result.facts, list)
        assert isinstance(result.entities, list)
        assert isinstance(result.entity_links, list)
        assert isinstance(result.upserts, dict)
        assert isinstance(result.processing_metadata, dict)

        # Check processing metadata
        assert result.processing_metadata["turns_processed"] == 3
        assert result.processing_metadata["facts_extracted"] > 0
        assert result.processing_metadata["entities_found"] > 0
        assert result.processing_metadata["processing_time"] > 0

        # Check that we extracted meaningful information
        assert len(result.facts) > 0
        assert any("authentication" in fact.text.lower() for fact in result.facts)

        # Check entities
        assert len(result.entities) > 0
        entity_texts = [e.text for e in result.entities]
        # Check for any entities (the system should find at least some entities)
        assert any(
            entity.entity_type in ["file", "url", "code", "service", "database", "technology", "concept"]
            for entity in result.entities
        )

    def test_consolidation_with_empty_input(self):
        """Test consolidation with empty input."""
        result = run([])

        assert isinstance(result, ConsolidationResult)
        assert result.summary == ""
        assert result.facts == []
        assert result.entities == []
        assert result.entity_links == []
        assert result.upserts == {"vector": 0, "fts": 0}

    def test_consolidation_with_single_turn(self):
        """Test consolidation with single turn."""
        raw_data = [{"role": "user", "content": "Hello world"}]

        result = run(raw_data)

        assert isinstance(result, ConsolidationResult)
        assert result.summary
        assert len(result.facts) >= 0  # May or may not extract facts
        assert len(result.entities) >= 0  # May or may not extract entities

    def test_fact_confidence_calculation(self):
        """Test fact confidence calculation."""
        turns = [
            Turn(
                role="user",
                content="We decided to implement a comprehensive user authentication system with JWT tokens",
            ),
        ]

        facts = extract_facts(turns, "")

        # Check that confidence scores are reasonable
        for fact in facts:
            assert 0 <= fact.confidence <= 1
            # Longer, more specific facts should have higher confidence
            if len(fact.text) > 50 and "authentication" in fact.text.lower():
                assert fact.confidence > 0.5

    def test_entity_deduplication(self):
        """Test entity deduplication."""
        turns = [
            Turn(role="user", content="Let's create auth.py file"),
            Turn(role="assistant", content="The auth.py file should contain login functions"),
        ]

        facts = extract_facts(turns, "")
        entities = extract_entities(turns, facts)

        # Check that we don't have duplicate entities
        entity_texts = [e.text for e in entities]
        assert len(entity_texts) == len(set(entity_texts))

    def test_heuristic_summarization_fallback(self):
        """Test heuristic summarization fallback."""
        # This test would require mocking the advanced summarization to fail
        # For now, we'll test that the function exists and works
        turns = [
            Turn(role="user", content="I need to implement a new feature"),
            Turn(role="assistant", content="What kind of feature?"),
        ]

        summary = summarize(turns)
        assert len(summary) > 0
        assert isinstance(summary, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
