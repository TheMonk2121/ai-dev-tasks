#!/usr/bin/env python3
"""
LIMIT-Inspired Precision Recovery Configuration
Implements the transcript's key insights for hybrid retrieval with geometry-failure routing.
"""

import os
from typing import Any, Dict, List

import numpy as np


class GeometryFailureRouter:
    """Detects flat vectors and routes to BM25 when cosine space is geometrically broken."""

    def __init__(self, margin_threshold: float = 0.20):
        self.margin_threshold = margin_threshold

    def calculate_top1_margin(self, scores: list[float]) -> float:
        """Calculate top-1 margin: (top1 - median(top10)) / (std(top10) + ε)"""
        if len(scores) < 10:
            return 0.0

        top10 = sorted(scores, reverse=True)[:10]
        top1 = top10[0]
        median_top10 = np.median(top10)
        std_top10 = np.std(top10)
        epsilon = 1e-8

        if std_top10 < epsilon:
            return 0.0

        margin = (top1 - median_top10) / (std_top10 + epsilon)
        return float(margin)

    def calculate_entropy(self, scores: list[float]) -> float:
        """Calculate entropy of top-k scores (higher = flatter)."""
        if not scores:
            return 0.0

        # Normalize scores to probabilities
        scores_array = np.array(scores)
        if scores_array.sum() == 0:
            return 0.0

        probs = scores_array / scores_array.sum()
        probs = probs[probs > 0]  # Remove zeros

        if len(probs) == 0:
            return 0.0

        entropy = -np.sum(probs * np.log2(probs))
        return entropy

    def should_route_to_bm25(self, vector_scores: list[float], rewrite_agreement: float = 0.0) -> bool:
        """Determine if we should route to BM25 due to flat vectors."""
        margin = self.calculate_top1_margin(vector_scores)
        entropy = self.calculate_entropy(vector_scores)

        # Route to BM25 if margin is low and rewrite agreement is low
        # Also consider entropy as a secondary indicator of flat vectors
        low_margin = margin < self.margin_threshold
        low_agreement = rewrite_agreement < 0.50
        high_entropy = entropy > 2.0  # High entropy indicates flat distribution

        return low_margin and low_agreement and high_entropy


class FacetYieldCalculator:
    """Calculates facet yield to determine which facets to keep."""

    def __init__(self, new_docs_weight: float = 0.6, entity_overlap_weight: float = 0.4):
        self.new_docs_weight = new_docs_weight
        self.entity_overlap_weight = entity_overlap_weight

    def calculate_facet_yield(self, new_docs_count: int, entity_overlap: float) -> float:
        """Calculate facet yield: 0.6 * (# new docs) + 0.4 * entity overlap."""
        return self.new_docs_weight * new_docs_count + self.entity_overlap_weight * entity_overlap

    def should_keep_facet(self, yield_score: float, min_yield: float = 1.0) -> bool:
        """Determine if facet should be kept based on yield."""
        return yield_score >= min_yield


class BooleanQueryParser:
    """Parses Boolean logic from queries for BM25 enforcement."""

    def __init__(self):
        self.include_patterns = ["AND", "and", "+", "must include"]
        self.exclude_patterns = ["NOT", "not", "-", "exclude", "without"]
        self.or_patterns = ["OR", "or", "|", "either"]

    def parse_boolean_logic(self, query: str) -> dict[str, list[str]]:
        """Parse Boolean logic from query."""
        tokens = query.split()

        include_terms = []
        exclude_terms = []
        or_terms = []

        current_mode = "include"

        for i, token in enumerate(tokens):
            if token.lower() in self.include_patterns:
                current_mode = "include"
            elif token.lower() in self.exclude_patterns:
                current_mode = "exclude"
            elif token.lower() in self.or_patterns:
                current_mode = "or"
            else:
                # Clean token (remove punctuation)
                clean_token = "".join(c for c in token if c.isalnum())
                if clean_token:
                    if current_mode == "include":
                        include_terms.append(clean_token)
                    elif current_mode == "exclude":
                        exclude_terms.append(clean_token)
                    elif current_mode == "or":
                        or_terms.append(clean_token)

        return {"include": include_terms, "exclude": exclude_terms, "or": or_terms}


class LimitInspiredPrecisionRecovery:
    """LIMIT-inspired precision recovery with geometry-failure routing."""

    def __init__(self):
        self.geometry_router = GeometryFailureRouter()
        self.facet_calculator = FacetYieldCalculator()
        self.boolean_parser = BooleanQueryParser()
        self.config = self._get_enhanced_config()

    def _get_enhanced_config(self) -> dict[str, Any]:
        """Get enhanced configuration with LIMIT-inspired features."""
        return {
            # Geometry routing
            "RAGCHECKER_ROUTE_BM25_MARGIN": "0.20",
            "RAGCHECKER_REWRITE_AGREE_STRONG": "0.50",
            # Facet selection with yield gate
            "RAGCHECKER_REWRITE_K": "4",
            "RAGCHECKER_REWRITE_KEEP": "2",
            "RAGCHECKER_REWRITE_YIELD_MIN": "1.0",
            # Retrieval hygiene
            "RAGCHECKER_USE_RRF": "1",
            "RAGCHECKER_USE_MMR": "1",
            "RAGCHECKER_MMR_LAMBDA": "0.65",
            "RAGCHECKER_CONTEXT_TOPK": "16",
            "RAGCHECKER_PER_DOC_LINE_CAP": "8",
            "RAGCHECKER_LONG_TAIL_SLOT": "1",
            # Chunking optimization (baseline density)
            "RAGCHECKER_CHUNK_TOK": "160",
            "RAGCHECKER_CHUNK_OVERLAP": "40",
            "RAGCHECKER_ENTITY_SNIPPETS": "0",
            # Boolean handling
            "RAGCHECKER_BM25_BOOST_ANCHORS": "1.4",
            "RAGCHECKER_ENABLE_BOOLEAN_LOGIC": "1",
            # Precision recovery settings
            "RAGCHECKER_REDUNDANCY_TRIGRAM_MAX": "0.45",
            "RAGCHECKER_PER_CHUNK_CAP": "2",
            "RAGCHECKER_MIN_WORDS_AFTER_BINDING": "140",
            "RAGCHECKER_TARGET_K_STRONG": "8",
            # Judge calibration
            "RAGCHECKER_JUDGE_MODE": "haiku",
            "RAGCHECKER_HAIKU_FLOORS": "1",
        }

    def apply_environment(self) -> None:
        """Apply enhanced configuration to environment variables."""
        for key, value in self.config.items():
            os.environ[key] = str(value)
            print(f"Set {key}={value}")

    def analyze_query_geometry(
        self, query: str, vector_scores: list[float], rewrite_agreement: float = 0.0
    ) -> dict[str, Any]:
        """Analyze query geometry and determine routing strategy."""

        # Calculate geometry metrics
        margin = self.geometry_router.calculate_top1_margin(vector_scores)
        entropy = self.geometry_router.calculate_entropy(vector_scores)
        should_route_bm25 = self.geometry_router.should_route_to_bm25(vector_scores, rewrite_agreement)

        # Parse Boolean logic
        boolean_logic = self.boolean_parser.parse_boolean_logic(query)

        return {
            "vector_margin": margin,
            "vector_entropy": entropy,
            "should_route_bm25": should_route_bm25,
            "rewrite_agreement": rewrite_agreement,
            "boolean_logic": boolean_logic,
            "geometry_healthy": margin >= 0.20 and entropy < 2.0,
        }

    def calculate_facet_yields(self, facets: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Calculate yields for all facets and determine which to keep."""

        enhanced_facets = []
        for facet in facets:
            new_docs = facet.get("new_docs_count", 0)
            entity_overlap = facet.get("entity_overlap", 0.0)

            yield_score = self.facet_calculator.calculate_facet_yield(new_docs, entity_overlap)
            should_keep = self.facet_calculator.should_keep_facet(yield_score)

            enhanced_facet = {**facet, "yield_score": yield_score, "should_keep": should_keep}
            enhanced_facets.append(enhanced_facet)

        return enhanced_facets

    def get_health_metrics(
        self, query_id: str, geometry_analysis: dict[str, Any], facet_yields: list[dict[str, Any]], fusion_gain: int
    ) -> dict[str, Any]:
        """Get LIMIT-style health metrics for monitoring."""

        return {
            "query_id": query_id,
            "vector_margin": geometry_analysis["vector_margin"],
            "vector_entropy": geometry_analysis["vector_entropy"],
            "rewrite_agreement": geometry_analysis["rewrite_agreement"],
            "fusion_gain": fusion_gain,
            "facets_kept": len([f for f in facet_yields if f["should_keep"]]),
            "total_facets": len(facet_yields),
            "geometry_healthy": geometry_analysis["geometry_healthy"],
            "routed_to_bm25": geometry_analysis["should_route_bm25"],
            "boolean_terms": {
                "include": len(geometry_analysis["boolean_logic"]["include"]),
                "exclude": len(geometry_analysis["boolean_logic"]["exclude"]),
                "or": len(geometry_analysis["boolean_logic"]["or"]),
            },
        }

    def should_promote_changes(
        self, health_metrics: dict[str, Any], precision: float, recall: float, f1_score: float
    ) -> bool:
        """Determine if retrieval changes should be promoted based on health metrics."""

        # Promotion rule: only keep changes if fusion_gain > 0 and floors hold
        fusion_gain_positive = health_metrics["fusion_gain"] > 0
        floors_hold = precision >= 0.135 and recall >= 0.160 and f1_score >= 0.145

        return fusion_gain_positive and floors_hold


def apply_limit_inspired_config() -> LimitInspiredPrecisionRecovery:
    """Apply LIMIT-inspired precision recovery configuration."""
    config = LimitInspiredPrecisionRecovery()
    config.apply_environment()
    return config


if __name__ == "__main__":

    config = apply_limit_inspired_config()

    print("\n🎯 LIMIT-Inspired Precision Recovery Configuration Applied")
    print(f"📊 Geometry Router: margin_threshold={config.geometry_router.margin_threshold}")
    print(f"📊 Facet Calculator: new_docs_weight={config.facet_calculator.new_docs_weight}")
    print("📊 Boolean Parser: Ready for AND/OR/NOT logic")

    # Test geometry analysis
    test_scores = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05]
    test_query = "DSPy integration AND optimization NOT debugging"

    analysis = config.analyze_query_geometry(test_query, test_scores, 0.3)
    print("\n🧪 Test Analysis:")
    print(f"   Vector Margin: {analysis['vector_margin']:.3f}")
    print(f"   Vector Entropy: {analysis['vector_entropy']:.3f}")
    print(f"   Route to BM25: {analysis['should_route_bm25']}")
    print(f"   Boolean Logic: {analysis['boolean_logic']}")
