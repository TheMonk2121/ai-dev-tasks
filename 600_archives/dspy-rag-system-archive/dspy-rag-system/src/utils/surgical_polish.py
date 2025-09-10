#!/usr/bin/env python3
"""
Surgical Polish - High-ROI Production Optimizations
RRF weights by query type, content-type overrides, and idempotent chunk IDs
"""

import hashlib
import json
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

LOG = logging.getLogger(__name__)


class QueryType(Enum):
    """Query type classification."""

    SHORT_NUMERIC = "short_numeric"
    CODE_QUERY = "code_query"
    DOCUMENTATION = "documentation"
    GENERAL = "general"


class ContentType(Enum):
    """Content type classification."""

    CODE = "code"
    PROSE = "prose"
    MIXED = "mixed"
    UNKNOWN = "unknown"


@dataclass
class RRFWeights:
    """RRF (Reciprocal Rank Fusion) weights configuration."""

    dense_weight: float
    sparse_weight: float
    query_type: QueryType
    description: str


@dataclass
class ContentTypeOverride:
    """Content type specific configuration overrides."""

    content_type: ContentType
    chunk_size: int
    overlap_ratio: float
    jaccard_threshold: float
    description: str


@dataclass
class ChunkID:
    """Idempotent chunk ID with versioning."""

    doc_id: str
    byte_span: tuple[int, int]
    chunk_version: str
    config_hash: str
    content_hash: str
    chunk_id: str


class SurgicalPolish:
    """High-ROI production optimizations."""

    def __init__(self):
        self.rrf_weights: dict[QueryType, RRFWeights] = {}
        self.content_overrides: dict[ContentType, ContentTypeOverride] = {}
        self.chunk_version = "v1.0"

        # Initialize default configurations
        self._initialize_rrf_weights()
        self._initialize_content_overrides()

    def _initialize_rrf_weights(self):
        """Initialize RRF weights by query type."""
        self.rrf_weights = {
            QueryType.SHORT_NUMERIC: RRFWeights(
                dense_weight=0.4,
                sparse_weight=0.6,
                query_type=QueryType.SHORT_NUMERIC,
                description="Boost BM25 for short/numeric queries",
            ),
            QueryType.CODE_QUERY: RRFWeights(
                dense_weight=0.5,
                sparse_weight=0.5,
                query_type=QueryType.CODE_QUERY,
                description="Equal weights for code queries",
            ),
            QueryType.DOCUMENTATION: RRFWeights(
                dense_weight=0.6,
                sparse_weight=0.4,
                query_type=QueryType.DOCUMENTATION,
                description="Boost dense for documentation queries",
            ),
            QueryType.GENERAL: RRFWeights(
                dense_weight=0.6,
                sparse_weight=0.4,
                query_type=QueryType.GENERAL,
                description="Default weights for general queries",
            ),
        }

    def _initialize_content_overrides(self):
        """Initialize content type specific overrides."""
        self.content_overrides = {
            ContentType.CODE: ContentTypeOverride(
                content_type=ContentType.CODE,
                chunk_size=300,
                overlap_ratio=0.1,
                jaccard_threshold=0.7,
                description="Code-heavy sections prefer smaller chunks",
            ),
            ContentType.PROSE: ContentTypeOverride(
                content_type=ContentType.PROSE,
                chunk_size=450,
                overlap_ratio=0.15,
                jaccard_threshold=0.8,
                description="Prose keeps standard chunk size",
            ),
            ContentType.MIXED: ContentTypeOverride(
                content_type=ContentType.MIXED,
                chunk_size=400,
                overlap_ratio=0.12,
                jaccard_threshold=0.75,
                description="Mixed content uses balanced settings",
            ),
            ContentType.UNKNOWN: ContentTypeOverride(
                content_type=ContentType.UNKNOWN,
                chunk_size=450,
                overlap_ratio=0.15,
                jaccard_threshold=0.8,
                description="Unknown content uses defaults",
            ),
        }

    def classify_query_type(self, query: str) -> QueryType:
        """Classify query type for RRF weight selection."""
        query_lower = query.lower().strip()

        # Short numeric queries (numbers, short terms)
        if len(query_lower) <= 20 and (re.search(r"\d+", query_lower) or len(query_lower.split()) <= 3):
            return QueryType.SHORT_NUMERIC

        # Code queries (function names, variables, technical terms)
        code_patterns = [
            r"\b(function|def|class|import|from|return|if|else|for|while)\b",
            r"\b[a-zA-Z_][a-zA-Z0-9_]*\(\)",  # Function calls
            r"\b[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*",  # Method calls
            r"[{}();]",  # Code punctuation
        ]

        if any(re.search(pattern, query_lower) for pattern in code_patterns):
            return QueryType.CODE_QUERY

        # Documentation queries (how-to, what is, explain)
        doc_patterns = [
            r"\b(how to|what is|explain|describe|documentation|guide|tutorial)\b",
            r"\b(overview|introduction|getting started|setup|configuration)\b",
        ]

        if any(re.search(pattern, query_lower) for pattern in doc_patterns):
            return QueryType.DOCUMENTATION

        return QueryType.GENERAL

    def get_rrf_weights(self, query: str) -> RRFWeights:
        """Get RRF weights for a query based on its type."""
        query_type = self.classify_query_type(query)
        return self.rrf_weights.get(query_type, self.rrf_weights[QueryType.GENERAL])

    def classify_content_type(self, content: str) -> ContentType:
        """Classify content type for chunking overrides."""
        if not content:
            return ContentType.UNKNOWN

        # Count code indicators
        code_indicators = 0
        code_patterns = [
            r"```",  # Code blocks
            r"def\s+\w+",  # Python functions
            r"function\s+\w+",  # JavaScript functions
            r"class\s+\w+",  # Classes
            r"import\s+\w+",  # Imports
            r"from\s+\w+",  # From imports
            r"#include",  # C includes
            r"<[^>]+>",  # HTML/XML tags
            r"\{[^}]*\}",  # Braces
            r"\([^)]*\)",  # Parentheses
        ]

        for pattern in code_patterns:
            code_indicators += len(re.findall(pattern, content))

        # Count prose indicators
        prose_indicators = 0
        prose_patterns = [
            r"\b(the|and|or|but|in|on|at|to|for|of|with|by)\b",  # Common words
            r"[.!?]",  # Sentence endings
            r"\b[a-z]{4,}\b",  # Long words
        ]

        for pattern in prose_patterns:
            prose_indicators += len(re.findall(pattern, content))

        # Determine content type
        total_indicators = code_indicators + prose_indicators
        if total_indicators == 0:
            return ContentType.UNKNOWN

        code_ratio = code_indicators / total_indicators

        if code_ratio > 0.6:
            return ContentType.CODE
        elif code_ratio < 0.3:
            return ContentType.PROSE
        else:
            return ContentType.MIXED

    def get_content_override(self, content: str) -> ContentTypeOverride:
        """Get content type specific configuration overrides."""
        content_type = self.classify_content_type(content)
        return self.content_overrides.get(content_type, self.content_overrides[ContentType.UNKNOWN])

    def generate_idempotent_chunk_id(
        self, doc_id: str, content: str, byte_span: tuple[int, int], config_hash: str
    ) -> ChunkID:
        """Generate idempotent chunk ID with versioning."""

        # Generate content hash
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]

        # Create chunk ID components
        chunk_id = hashlib.sha256(
            f"{doc_id}|{byte_span[0]}-{byte_span[1]}|{self.chunk_version}|{config_hash}|{content_hash}".encode()
        ).hexdigest()[:16]

        return ChunkID(
            doc_id=doc_id,
            byte_span=byte_span,
            chunk_version=self.chunk_version,
            config_hash=config_hash,
            content_hash=content_hash,
            chunk_id=chunk_id,
        )

    def apply_query_optimizations(
        self, query: str, dense_results: list[dict], sparse_results: list[dict]
    ) -> list[dict]:
        """Apply query-specific optimizations to results."""
        # Get RRF weights for this query type
        rrf_weights = self.get_rrf_weights(query)

        # Apply RRF fusion with query-specific weights
        fused_results = self._apply_rrf_fusion(
            dense_results, sparse_results, rrf_weights.dense_weight, rrf_weights.sparse_weight
        )

        # Add query type metadata
        for result in fused_results:
            result["query_type"] = rrf_weights.query_type.value
            result["rrf_weights"] = {"dense": rrf_weights.dense_weight, "sparse": rrf_weights.sparse_weight}

        return fused_results

    def _apply_rrf_fusion(
        self, dense_results: list[dict], sparse_results: list[dict], dense_weight: float, sparse_weight: float
    ) -> list[dict]:
        """Apply RRF fusion with custom weights."""
        # Create result maps
        dense_map = {f"{r['document_id']}_{r['chunk_index']}": r for r in dense_results}
        sparse_map = {f"{r['document_id']}_{r['chunk_index']}": r for r in sparse_results}

        # Get all unique keys
        all_keys = set(dense_map.keys()) | set(sparse_map.keys())

        # Calculate RRF scores
        fused_results = []
        for key in all_keys:
            dense_result = dense_map.get(key, {})
            sparse_result = sparse_map.get(key, {})

            # Get ranks (assuming results are already ranked)
            dense_rank = dense_result.get("rank", 1000)
            sparse_rank = sparse_result.get("rank", 1000)

            # Calculate RRF score
            rrf_score = dense_weight * (1.0 / (60.0 + dense_rank)) + sparse_weight * (1.0 / (60.0 + sparse_rank))

            # Merge results
            merged_result = dense_result.copy() if dense_result else sparse_result.copy()
            merged_result["rrf_score"] = rrf_score
            merged_result["dense_rank"] = dense_rank
            merged_result["sparse_rank"] = sparse_rank

            fused_results.append(merged_result)

        # Sort by RRF score
        fused_results.sort(key=lambda x: x["rrf_score"], reverse=True)

        return fused_results

    def get_chunking_config_for_content(self, content: str, base_config: dict[str, Any]) -> dict[str, Any]:
        """Get chunking configuration overrides for specific content."""
        content_override = self.get_content_override(content)

        # Start with base config
        config = base_config.copy()

        # Apply content-specific overrides
        config.update(
            {
                "chunk_size": content_override.chunk_size,
                "overlap_ratio": content_override.overlap_ratio,
                "jaccard_threshold": content_override.jaccard_threshold,
                "content_type": content_override.content_type.value,
                "override_reason": content_override.description,
            }
        )

        return config

    def validate_chunk_id(self, chunk_id: str, expected_components: dict[str, str]) -> bool:
        """Validate chunk ID against expected components."""
        try:
            # Parse chunk ID components (this would depend on your actual chunk ID format)
            # For now, we'll do a basic validation

            # Check if chunk ID matches expected pattern
            if not re.match(r"^[a-f0-9]{16}$", chunk_id):
                return False

            # Additional validation could be added here
            return True

        except Exception as e:
            LOG.error(f"Chunk ID validation failed: {e}")
            return False

    def get_optimization_summary(self) -> dict[str, Any]:
        """Get summary of all optimizations."""
        return {
            "rrf_weights": {
                query_type.value: {
                    "dense_weight": weights.dense_weight,
                    "sparse_weight": weights.sparse_weight,
                    "description": weights.description,
                }
                for query_type, weights in self.rrf_weights.items()
            },
            "content_overrides": {
                content_type.value: {
                    "chunk_size": override.chunk_size,
                    "overlap_ratio": override.overlap_ratio,
                    "jaccard_threshold": override.jaccard_threshold,
                    "description": override.description,
                }
                for content_type, override in self.content_overrides.items()
            },
            "chunk_version": self.chunk_version,
            "optimizations_enabled": [
                "query_type_classification",
                "rrf_weight_optimization",
                "content_type_overrides",
                "idempotent_chunk_ids",
            ],
        }


# Global instance
_surgical_polish = None


def get_surgical_polish() -> SurgicalPolish:
    """Get or create the global surgical polish instance."""
    global _surgical_polish
    if _surgical_polish is None:
        _surgical_polish = SurgicalPolish()
    return _surgical_polish


def optimize_query(query: str, dense_results: list[dict], sparse_results: list[dict]) -> list[dict]:
    """Convenience function for query optimization."""
    return get_surgical_polish().apply_query_optimizations(query, dense_results, sparse_results)


def get_chunking_config(content: str, base_config: dict[str, Any]) -> dict[str, Any]:
    """Convenience function for content-specific chunking config."""
    return get_surgical_polish().get_chunking_config_for_content(content, base_config)


if __name__ == "__main__":
    # Test the surgical polish system
    polish = SurgicalPolish()

    # Test query classification
    test_queries = ["What is DSPy?", "function calculateTotal", "42", "How to implement RAG?", "import numpy"]

    print("🔍 Query Type Classification")
    print("=" * 50)
    for query in test_queries:
        query_type = polish.classify_query_type(query)
        rrf_weights = polish.get_rrf_weights(query)
        print(f"Query: '{query}'")
        print(f"  Type: {query_type.value}")
        print(f"  RRF Weights: dense={rrf_weights.dense_weight}, sparse={rrf_weights.sparse_weight}")
        print()

    # Test content classification
    test_contents = [
        "def hello_world():\n    print('Hello, World!')",
        "This is a documentation about how to use the system.",
        "def calculate(x):\n    return x * 2\n\nThis function calculates the double of a number.",
        "import os\nimport sys",
    ]

    print("📄 Content Type Classification")
    print("=" * 50)
    for content in test_contents:
        content_type = polish.classify_content_type(content)
        override = polish.get_content_override(content)
        print(f"Content: '{content[:50]}...'")
        print(f"  Type: {content_type.value}")
        print(f"  Override: chunk_size={override.chunk_size}, overlap={override.overlap_ratio}")
        print()

    # Test chunk ID generation
    print("🆔 Idempotent Chunk ID Generation")
    print("=" * 50)
    chunk_id = polish.generate_idempotent_chunk_id(
        doc_id="test_doc_123", content="This is a test chunk", byte_span=(0, 100), config_hash="abc123"
    )
    print(f"Chunk ID: {chunk_id.chunk_id}")
    print(f"Components: {chunk_id}")

    # Print optimization summary
    print("\n📊 Optimization Summary")
    print("=" * 50)
    summary = polish.get_optimization_summary()
    print(json.dumps(summary, indent=2))
