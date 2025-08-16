#!/usr/bin/env python3
"""
Entity Overlay Utility Module
-----------------------------
Entity extraction and expansion functionality for memory rehydration.

Provides entity-aware context expansion by identifying entities in queries
and retrieving related chunks to enhance context retrieval.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .database_resilience import get_database_manager


@dataclass
class Entity:
    """Represents an extracted entity with metadata."""

    text: str
    entity_type: str
    confidence: float
    start_pos: int
    end_pos: int


@dataclass
class ExpansionResult:
    """Result of entity expansion operation."""

    entities: List[Entity]
    expanded_chunks: List[Dict[str, Any]]
    expansion_latency_ms: float
    k_related: int
    stability_threshold: float


def extract_entities_from_query(query: str) -> List[Entity]:
    """
    Extract entities from query text using pattern matching and heuristics.

    Args:
        query: Input query text

    Returns:
        List of extracted entities with metadata
    """
    entities = []

    # Pattern-based entity extraction
    patterns = [
        # CamelCase/PascalCase (likely class names, functions)
        (r"\b[A-Z][a-zA-Z0-9_]*\b", "CLASS_FUNCTION"),
        # snake_case (likely variables, functions)
        (r"\b[a-z_][a-z0-9_]*\b", "VARIABLE_FUNCTION"),
        # UPPER_CASE (likely constants)
        (r"\b[A-Z_][A-Z0-9_]*\b", "CONSTANT"),
        # File paths with extensions
        (r"\b[a-zA-Z0-9_/.-]+\.[a-zA-Z0-9_]+\b", "FILE_PATH"),
        # URLs
        (r"https?://[^\s]+", "URL"),
        # Email addresses
        (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "EMAIL"),
    ]

    for pattern, entity_type in patterns:
        matches = re.finditer(pattern, query)
        for match in matches:
            text = match.group()

            # Filter out common words and short entities
            if len(text) < 3 or text.lower() in {
                "the",
                "and",
                "or",
                "but",
                "for",
                "with",
                "from",
                "to",
                "in",
                "on",
                "at",
                "is",
                "are",
                "was",
                "were",
                "be",
                "been",
                "have",
                "has",
                "had",
                "do",
                "does",
                "did",
                "will",
                "would",
                "could",
                "should",
                "may",
                "might",
            }:
                continue

            # Calculate confidence based on pattern strength
            confidence = 0.8 if entity_type in ["FILE_PATH", "URL", "EMAIL"] else 0.6

            entities.append(
                Entity(
                    text=text,
                    entity_type=entity_type,
                    confidence=confidence,
                    start_pos=match.start(),
                    end_pos=match.end(),
                )
            )

    # Remove overlapping entities (keep highest confidence)
    entities = _deduplicate_entities(entities)

    return entities


def _deduplicate_entities(entities: List[Entity]) -> List[Entity]:
    """
    Remove overlapping entities, keeping the highest confidence ones.

    Args:
        entities: List of entities to deduplicate

    Returns:
        Deduplicated list of entities
    """
    if not entities:
        return []

    # Sort by confidence descending, then by position
    entities.sort(key=lambda e: (-e.confidence, e.start_pos))

    deduplicated = []
    for entity in entities:
        # Check if this entity overlaps with any already selected
        overlaps = False
        for selected in deduplicated:
            if entity.start_pos < selected.end_pos and entity.end_pos > selected.start_pos:
                overlaps = True
                break

        if not overlaps:
            deduplicated.append(entity)

    return deduplicated


def calculate_adaptive_k_related(base_k: int, entity_count: int) -> int:
    """
    Calculate adaptive k_related based on entity count.

    Args:
        base_k: Base k value for retrieval
        entity_count: Number of entities found in query

    Returns:
        Adaptive k_related value
    """
    # Formula: min(8, base_k + entity_count * 2)
    # This provides more context for entity-rich queries while maintaining limits
    adaptive_k = min(8, base_k + entity_count * 2)
    return max(1, adaptive_k)  # Ensure minimum of 1


def fetch_entity_adjacent_chunks(
    entities: List[Entity], k_per_entity: int = 2, stability_threshold: float = 0.7, db_dsn: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch chunks that are semantically related to the extracted entities.

    Args:
        entities: List of extracted entities
        k_per_entity: Number of chunks to retrieve per entity
        stability_threshold: Minimum similarity threshold for inclusion
        db_dsn: Database connection string

    Returns:
        List of related chunks with metadata
    """
    if not entities:
        return []

    db = get_database_manager()
    related_chunks = []

    # Extract entity texts for search
    entity_texts = [entity.text for entity in entities]

    # Build search query from entity texts
    search_query = " ".join(entity_texts)

    try:
        # Use vector search to find related chunks
        from .memory_rehydrator import vector_search

        # Calculate total k for all entities
        total_k = len(entities) * k_per_entity

        # Search for related chunks
        search_results = vector_search(search_query, k=total_k, db_dsn=db_dsn)

        # Filter by stability threshold
        for chunk in search_results:
            similarity = chunk.get("sim", 0.0)
            if similarity >= stability_threshold:
                # Add entity metadata to chunk
                chunk["entity_related"] = True
                chunk["entity_similarity"] = similarity
                chunk["related_entities"] = [
                    entity.text for entity in entities if entity.text.lower() in chunk.get("text", "").lower()
                ]
                related_chunks.append(chunk)

        # Sort by similarity descending
        related_chunks.sort(key=lambda c: -c.get("sim", 0.0))

    except Exception as e:
        print(f"Error fetching entity-adjacent chunks: {e}")
        return []

    return related_chunks


def populate_related_entities(
    base_chunks: List[Dict[str, Any]],
    entities: List[Entity],
    k_related: int,
    stability_threshold: float = 0.7,
    db_dsn: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Populate base chunks with entity-related chunks.

    Args:
        base_chunks: Base chunks from semantic search
        entities: Extracted entities from query
        k_related: Number of related chunks to add per entity
        stability_threshold: Minimum similarity threshold
        db_dsn: Database connection string

    Returns:
        Combined list of base and entity-related chunks
    """
    if not entities:
        return base_chunks

    start_time = time.time()

    # Fetch entity-related chunks
    entity_chunks = fetch_entity_adjacent_chunks(
        entities=entities, k_per_entity=k_related, stability_threshold=stability_threshold, db_dsn=db_dsn
    )

    # Combine base and entity chunks
    combined_chunks = base_chunks.copy()

    # Add entity chunks that aren't already in base chunks
    base_chunk_ids = {chunk.get("id") for chunk in base_chunks}

    for entity_chunk in entity_chunks:
        if entity_chunk.get("id") not in base_chunk_ids:
            combined_chunks.append(entity_chunk)
            base_chunk_ids.add(entity_chunk.get("id"))

    # Calculate expansion latency
    expansion_latency_ms = (time.time() - start_time) * 1000

    # Add expansion metadata to chunks
    for chunk in combined_chunks:
        if chunk.get("entity_related"):
            chunk["expansion_metadata"] = {
                "expansion_latency_ms": expansion_latency_ms,
                "related_entities": chunk.get("related_entities", []),
                "entity_similarity": chunk.get("entity_similarity", 0.0),
            }

    return combined_chunks


def extract_entities_from_chunks(chunks: List[Dict[str, Any]]) -> List[Entity]:
    """
    Extract entities from chunk text for analysis.

    Args:
        chunks: List of chunks to analyze

    Returns:
        List of entities found in chunks
    """
    all_entities = []

    for chunk in chunks:
        text = chunk.get("text", "")
        if text:
            entities = extract_entities_from_query(text)
            all_entities.extend(entities)

    # Deduplicate across all chunks
    return _deduplicate_entities(all_entities)


def validate_entity_expansion(
    base_chunks: List[Dict[str, Any]], expanded_chunks: List[Dict[str, Any]], entities: List[Entity]
) -> Dict[str, Any]:
    """
    Validate entity expansion results.

    Args:
        base_chunks: Original chunks before expansion
        expanded_chunks: Chunks after entity expansion
        entities: Entities used for expansion

    Returns:
        Validation metrics
    """
    base_count = len(base_chunks)
    expanded_count = len(expanded_chunks)
    entity_count = len(entities)

    # Calculate expansion ratio
    expansion_ratio = (expanded_count - base_count) / max(1, base_count)

    # Count entity-related chunks
    entity_related_count = sum(1 for chunk in expanded_chunks if chunk.get("entity_related", False))

    # Calculate average entity similarity
    entity_similarities = [
        chunk.get("entity_similarity", 0.0) for chunk in expanded_chunks if chunk.get("entity_related", False)
    ]
    avg_entity_similarity = sum(entity_similarities) / len(entity_similarities) if entity_similarities else 0.0

    return {
        "base_chunk_count": base_count,
        "expanded_chunk_count": expanded_count,
        "entity_count": entity_count,
        "expansion_ratio": expansion_ratio,
        "entity_related_count": entity_related_count,
        "avg_entity_similarity": avg_entity_similarity,
        "expansion_effective": expansion_ratio > 0.1 and entity_related_count > 0,
    }
