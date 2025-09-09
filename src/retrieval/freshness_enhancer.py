"""
Phase 1.5: Freshness Enhancement for RAG Retrieval

Implements light time-decay in BM25 and recency prior in tie-breaks for newsy queries.
Detects freshness-sensitive queries via simple classifier or regex for dates.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

import numpy as np


@dataclass
class FreshnessConfig:
    """Configuration for freshness enhancement."""

    # Time decay parameters
    enable_time_decay: bool = True
    decay_half_life_days: float = 30.0  # 30 days for 50% decay
    max_decay_factor: float = 0.3  # Minimum score multiplier

    # Recency prior parameters
    enable_recency_prior: bool = True
    recency_boost_factor: float = 1.2  # 20% boost for recent docs
    recency_threshold_days: int = 7  # Docs within 7 days get boost

    # Freshness detection
    date_patterns: list[str] = None
    news_keywords: list[str] = None
    freshness_threshold: float = 0.6  # Confidence threshold for newsy queries


class FreshnessDetector:
    """Detects freshness-sensitive queries via patterns and keywords."""

    def __init__(self, config: FreshnessConfig):
        self.config = config

        # Default date patterns
        if not self.config.date_patterns:
            self.config.date_patterns = [
                r"\b\d{4}-\d{2}-\d{2}\b",  # YYYY-MM-DD
                r"\b\d{1,2}/\d{1,2}/\d{4}\b",  # MM/DD/YYYY
                r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}\b",  # Month DD, YYYY
                r"\b(yesterday|today|tomorrow)\b",  # Relative dates
                r"\b(last|this|next)\s+(week|month|year|quarter)\b",  # Relative periods
                r"\b\d{4}\b",  # Just year
            ]

        # Default news keywords
        if not self.config.news_keywords:
            self.config.news_keywords = [
                "latest",
                "recent",
                "new",
                "update",
                "announcement",
                "release",
                "breaking",
                "news",
                "today",
                "yesterday",
                "this week",
                "current",
                "trending",
                "hot",
                "fresh",
                "just in",
            ]

    def detect_freshness_sensitivity(self, query: str) -> tuple[bool, float, str]:
        """
        Detect if query is freshness-sensitive.

        Returns:
            (is_freshness_sensitive, confidence, reasoning)
        """
        query_lower = query.lower()
        confidence = 0.0
        reasoning = []

        # Check for date patterns
        date_matches = 0
        for pattern in self.config.date_patterns:
            matches = re.findall(pattern, query_lower, re.IGNORECASE)
            if matches:
                date_matches += len(matches)
                reasoning.append(f"Date pattern: {matches[0]}")

        if date_matches > 0:
            confidence += 0.4
            confidence += min(0.2, date_matches * 0.1)

        # Check for news keywords
        keyword_matches = 0
        for keyword in self.config.news_keywords:
            if keyword in query_lower:
                keyword_matches += 1
                reasoning.append(f"News keyword: {keyword}")

        if keyword_matches > 0:
            confidence += 0.3
            confidence += min(0.2, keyword_matches * 0.1)

        # Check for time-sensitive verbs
        time_verbs = ["announce", "release", "launch", "publish", "update", "change"]
        verb_matches = sum(1 for verb in time_verbs if verb in query_lower)
        if verb_matches > 0:
            confidence += 0.2
            reasoning.append(f"Time-sensitive verbs: {verb_matches}")

        # Check for comparison with time
        time_comparisons = ["newer", "older", "recent", "latest", "previous", "current"]
        comparison_matches = sum(1 for comp in time_comparisons if comp in query_lower)
        if comparison_matches > 0:
            confidence += 0.1
            reasoning.append(f"Time comparisons: {comparison_matches}")

        is_freshness_sensitive = confidence >= self.config.freshness_threshold

        if not reasoning:
            reasoning = ["No freshness indicators detected"]

        return is_freshness_sensitive, confidence, "; ".join(reasoning)


class TimeDecayCalculator:
    """Calculates time-based decay factors for document scores."""

    def __init__(self, config: FreshnessConfig):
        self.config = config

    def calculate_decay_factor(self, doc_timestamp: float | None, current_time: float | None = None) -> float:
        """
        Calculate decay factor based on document age.

        Args:
            doc_timestamp: Document timestamp (Unix timestamp)
            current_time: Current time (Unix timestamp), defaults to now

        Returns:
            Decay factor (1.0 = no decay, 0.3 = 70% decay)
        """
        if not self.config.enable_time_decay or not doc_timestamp:
            return 1.0

        if current_time is None:
            current_time = time.time()

        # Calculate age in days
        age_days = (current_time - doc_timestamp) / (24 * 3600)

        if age_days <= 0:
            return 1.0  # Future or current documents

        # Exponential decay with half-life
        decay_factor = np.exp(-age_days * np.log(2) / self.config.decay_half_life_days)

        # Apply minimum decay limit
        decay_factor = max(decay_factor, self.config.max_decay_factor)

        return decay_factor

    def calculate_recency_boost(self, doc_timestamp: float | None, current_time: float | None = None) -> float:
        """
        Calculate recency boost factor for very recent documents.

        Args:
            doc_timestamp: Document timestamp (Unix timestamp)
            current_time: Current time (Unix timestamp), defaults to now

        Returns:
            Boost factor (1.0 = no boost, 1.2 = 20% boost)
        """
        if not self.config.enable_recency_prior or not doc_timestamp:
            return 1.0

        if current_time is None:
            current_time = time.time()

        # Calculate age in days
        age_days = (current_time - doc_timestamp) / (24 * 3600)

        if age_days <= self.config.recency_threshold_days:
            # Linear boost from 1.0 to recency_boost_factor
            boost_factor = 1.0 + (self.config.recency_boost_factor - 1.0) * (
                1.0 - age_days / self.config.recency_threshold_days
            )
            return boost_factor

        return 1.0


class FreshnessEnhancer:
    """Main freshness enhancement orchestrator."""

    def __init__(self, config: FreshnessConfig):
        self.config = config
        self.detector = FreshnessDetector(config)
        self.decay_calculator = TimeDecayCalculator(config)

    def enhance_retrieval_results(
        self, query: str, results: list[dict[str, Any]], current_time: float | None = None
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """
        Enhance retrieval results with freshness-aware scoring.

        Args:
            query: User query
            results: List of retrieval results
            current_time: Current timestamp (optional)

        Returns:
            (enhanced_results, enhancement_metadata)
        """
        # Detect freshness sensitivity
        is_freshness_sensitive, confidence, reasoning = self.detector.detect_freshness_sensitivity(query)

        enhancement_metadata = {
            "is_freshness_sensitive": is_freshness_sensitive,
            "confidence": confidence,
            "reasoning": reasoning,
            "enhancements_applied": [],
        }

        if not is_freshness_sensitive:
            return results, enhancement_metadata

        enhanced_results = []

        for result in results:
            enhanced_result = result.copy()

            # Extract timestamp from result
            doc_timestamp = self._extract_timestamp(result)

            # Apply time decay
            decay_factor = self.decay_calculator.calculate_decay_factor(doc_timestamp, current_time)
            if decay_factor != 1.0:
                enhanced_result["original_score"] = enhanced_result.get("score", 1.0)
                enhanced_result["score"] *= decay_factor
                enhanced_result["freshness_decay"] = decay_factor
                enhancement_metadata["enhancements_applied"].append("time_decay")

            # Apply recency boost
            recency_boost = self.decay_calculator.calculate_recency_boost(doc_timestamp, current_time)
            if recency_boost != 1.0:
                enhanced_result["original_score"] = enhanced_result.get("score", 1.0)
                enhanced_result["score"] *= recency_boost
                enhanced_result["recency_boost"] = recency_boost
                enhancement_metadata["enhancements_applied"].append("recency_boost")

            # Add freshness metadata
            enhanced_result["freshness_metadata"] = {
                "doc_timestamp": doc_timestamp,
                "doc_age_days": (
                    (current_time - doc_timestamp) / (24 * 3600) if doc_timestamp and current_time else None
                ),
                "decay_factor": decay_factor,
                "recency_boost": recency_boost,
            }

            enhanced_results.append(enhanced_result)

        # Re-sort by enhanced scores
        enhanced_results.sort(key=lambda x: x.get("score", 0.0), reverse=True)

        enhancement_metadata["total_results"] = len(enhanced_results)
        enhancement_metadata["enhanced_scores"] = [r.get("score", 0.0) for r in enhanced_results[:5]]

        return enhanced_results, enhancement_metadata

    def _extract_timestamp(self, result: dict[str, Any]) -> float | None:
        """Extract timestamp from result document."""

        # Try various timestamp fields
        timestamp_fields = [
            "timestamp",
            "created_at",
            "updated_at",
            "date",
            "published_at",
            "last_modified",
            "modified_at",
            "created",
            "updated",
        ]

        for field in timestamp_fields:
            if field in result:
                timestamp = result[field]

                # Handle different timestamp formats
                if isinstance(timestamp, int | float):
                    return float(timestamp)
                elif isinstance(timestamp, str):
                    # Try parsing common date formats
                    try:
                        # Try ISO format first
                        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                        return dt.timestamp()
                    except ValueError:
                        try:
                            # Try common formats
                            for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d"]:
                                try:
                                    dt = datetime.strptime(timestamp, fmt)
                                    return dt.timestamp()
                                except ValueError:
                                    continue
                        except:
                            continue

        # Try to extract from metadata
        metadata = result.get("metadata", {})
        for field in timestamp_fields:
            if field in metadata:
                timestamp = metadata[field]
                if isinstance(timestamp, int | float):
                    return float(timestamp)

        return None


def create_freshness_enhancer(config: FreshnessConfig | None = None) -> FreshnessEnhancer:
    """Factory function to create a FreshnessEnhancer."""

    if not config:
        config = FreshnessConfig()

    return FreshnessEnhancer(config)
