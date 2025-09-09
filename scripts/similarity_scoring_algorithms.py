#!/usr/bin/env python3
"""
Similarity Scoring Algorithms for Generation Cache Implementation

Task 2.2: Similarity Scoring Algorithms
Priority: Critical
MoSCoW: 🔥 Must

This module implements vector similarity algorithms including cosine similarity,
Jaccard distance, and configurable similarity thresholds for intelligent cache retrieval.

Features:
- Cosine similarity implementation for vector comparison
- Jaccard distance calculation for set-based similarity
- Configurable similarity thresholds and scoring
- Similarity score normalization and ranking
- Performance optimization for large-scale similarity search
- A/B testing framework for algorithm comparison
"""

import logging
import math
import os

# Add project root to path for imports
import sys
import time
from dataclasses import dataclass, field
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/similarity_algorithms.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@dataclass
class SimilarityConfig:
    """Configuration for similarity scoring algorithms"""

    # Algorithm selection
    primary_algorithm: str = "cosine"  # cosine, jaccard, hybrid
    fallback_algorithm: str = "jaccard"  # fallback when primary fails

    # Thresholds
    similarity_threshold: float = 0.7
    high_similarity_threshold: float = 0.9
    low_similarity_threshold: float = 0.3

    # Performance settings
    enable_caching: bool = True
    cache_size: int = 1000
    max_vector_dimension: int = 1000

    # Text processing
    use_tfidf: bool = True
    min_tfidf_threshold: float = 0.01
    max_features: int = 1000

    # Normalization
    normalize_scores: bool = True
    score_range: tuple[float, float] = (0.0, 1.0)

    # A/B testing
    enable_ab_testing: bool = False
    ab_test_ratio: float = 0.1


@dataclass
class SimilarityResult:
    """Result of similarity calculation"""

    score: float
    algorithm: str
    confidence: float = 1.0
    processing_time_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate and normalize score"""
        if self.score < 0.0:
            self.score = 0.0
        elif self.score > 1.0:
            self.score = 1.0


@dataclass
class SimilarityMetrics:
    """Performance metrics for similarity algorithms"""

    total_calculations: int = 0
    cosine_calculations: int = 0
    jaccard_calculations: int = 0
    hybrid_calculations: int = 0

    avg_processing_time_ms: float = 0.0
    total_processing_time_ms: float = 0.0

    cache_hits: int = 0
    cache_misses: int = 0

    algorithm_performance: dict[str, list[float]] = field(default_factory=dict)

    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return (self.cache_hits / total) * 100.0

    @property
    def avg_processing_time(self) -> float:
        """Calculate average processing time"""
        if self.total_calculations == 0:
            return 0.0
        return self.total_processing_time_ms / self.total_calculations


class SimilarityScoringEngine:
    """Engine for calculating similarity scores using multiple algorithms"""

    def __init__(self, config: SimilarityConfig | None = None):
        """Initialize similarity scoring engine"""
        self.config = config or SimilarityConfig()
        self.metrics = SimilarityMetrics()
        self.vectorizer = None
        self.similarity_cache = {}

        # Initialize TF-IDF vectorizer if enabled
        if self.config.use_tfidf:
            self._initialize_tfidf_vectorizer()

        logger.info(f"Similarity Scoring Engine initialized with {self.config.primary_algorithm} algorithm")

    def _initialize_tfidf_vectorizer(self):
        """Initialize TF-IDF vectorizer for text processing"""
        try:
            self.vectorizer = TfidfVectorizer(
                max_features=self.config.max_features,
                min_df=1,  # Allow single document frequency
                max_df=1.0,  # Allow all document frequencies
                stop_words="english",
                ngram_range=(1, 2),
            )
            logger.info("TF-IDF vectorizer initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize TF-IDF vectorizer: {e}")
            self.vectorizer = None

    def calculate_similarity(self, text1: str, text2: str, algorithm: str | None = None) -> SimilarityResult:
        """Calculate similarity between two text inputs"""
        start_time = time.time()

        try:
            # Use specified algorithm or fall back to primary
            algo = algorithm or self.config.primary_algorithm

            # Check cache first
            cache_key = self._generate_cache_key(text1, text2, algo)
            if self.config.enable_caching and cache_key in self.similarity_cache:
                self.metrics.cache_hits += 1
                cached_result = self.similarity_cache[cache_key]
                cached_result.metadata["cached"] = True
                return cached_result

            self.metrics.cache_misses += 1

            # Calculate similarity using selected algorithm
            if algo == "cosine":
                result = self._cosine_similarity(text1, text2)
            elif algo == "jaccard":
                result = self._jaccard_similarity(text1, text2)
            elif algo == "hybrid":
                result = self._hybrid_similarity(text1, text2)
            else:
                logger.warning(f"Unknown algorithm '{algo}', falling back to {self.config.fallback_algorithm}")
                result = self._calculate_similarity_fallback(text1, text2)

            # Update metrics
            processing_time = (time.time() - start_time) * 1000
            result.processing_time_ms = processing_time
            self._update_metrics(algo, processing_time)

            # Cache result if enabled
            if self.config.enable_caching:
                self._cache_result(cache_key, result)

            return result

        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            # Return fallback result
            return self._calculate_similarity_fallback(text1, text2)

    def _cosine_similarity(self, text1: str, text2: str) -> SimilarityResult:
        """Calculate cosine similarity between two texts"""
        try:
            if self.vectorizer:
                # Use TF-IDF vectors
                vectors = self.vectorizer.fit_transform([text1, text2])
                similarity_matrix = cosine_similarity(vectors[0:1], vectors[1:2])
                score = float(similarity_matrix[0][0])
            else:
                # Fallback to basic vectorization
                score = self._basic_cosine_similarity(text1, text2)

            return SimilarityResult(score=score, algorithm="cosine", confidence=0.9 if self.vectorizer else 0.7)

        except Exception as e:
            logger.error(f"Cosine similarity calculation failed: {e}")
            raise

    def _basic_cosine_similarity(self, text1: str, text2: str) -> float:
        """Basic cosine similarity without TF-IDF"""
        try:
            # Simple word-based vectorization
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())

            # Create vectors
            all_words = words1.union(words2)
            vector1 = [1 if word in words1 else 0 for word in all_words]
            vector2 = [1 if word in words2 else 0 for word in all_words]

            # Calculate cosine similarity
            dot_product = sum(a * b for a, b in zip(vector1, vector2))
            magnitude1 = math.sqrt(sum(a * a for a in vector1))
            magnitude2 = math.sqrt(sum(a * a for a in vector2))

            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0

            return dot_product / (magnitude1 * magnitude2)

        except Exception as e:
            logger.error(f"Basic cosine similarity failed: {e}")
            return 0.0

    def _jaccard_similarity(self, text1: str, text2: str) -> SimilarityResult:
        """Calculate Jaccard similarity between two texts"""
        try:
            # Tokenize texts
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())

            # Calculate Jaccard similarity
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))

            if union == 0:
                score = 0.0
            else:
                score = intersection / union

            return SimilarityResult(score=score, algorithm="jaccard", confidence=0.8)

        except Exception as e:
            logger.error(f"Jaccard similarity calculation failed: {e}")
            raise

    def _hybrid_similarity(self, text1: str, text2: str) -> SimilarityResult:
        """Calculate hybrid similarity using multiple algorithms"""
        try:
            # Calculate both similarities
            cosine_result = self._cosine_similarity(text1, text2)
            jaccard_result = self._jaccard_similarity(text1, text2)

            # Weighted combination (cosine gets higher weight for semantic similarity)
            hybrid_score = (0.7 * cosine_result.score) + (0.3 * jaccard_result.score)

            # Calculate confidence based on agreement
            score_difference = abs(cosine_result.score - jaccard_result.score)
            confidence = max(0.5, 1.0 - score_difference)

            return SimilarityResult(
                score=hybrid_score,
                algorithm="hybrid",
                confidence=confidence,
                metadata={
                    "cosine_score": cosine_result.score,
                    "jaccard_score": jaccard_result.score,
                    "score_difference": score_difference,
                },
            )

        except Exception as e:
            logger.error(f"Hybrid similarity calculation failed: {e}")
            raise

    def _calculate_similarity_fallback(self, text1: str, text2: str) -> SimilarityResult:
        """Fallback similarity calculation when primary algorithm fails"""
        try:
            # Use Jaccard as fallback (more robust)
            result = self._jaccard_similarity(text1, text2)
            result.algorithm = f"{self.config.fallback_algorithm}_fallback"
            result.confidence = 0.6
            return result

        except Exception as e:
            logger.error(f"Fallback similarity calculation failed: {e}")
            # Return minimal similarity
            return SimilarityResult(score=0.0, algorithm="fallback", confidence=0.1, metadata={"error": str(e)})

    def _generate_cache_key(self, text1: str, text2: str, algorithm: str) -> str:
        """Generate cache key for similarity calculation"""
        # Sort texts to ensure consistent cache keys
        sorted_texts = tuple(sorted([text1, text2]))
        return f"{algorithm}:{hash(sorted_texts)}"

    def _cache_result(self, key: str, result: SimilarityResult):
        """Cache similarity result"""
        try:
            # Implement LRU-like cache management
            if len(self.similarity_cache) >= self.config.cache_size:
                # Remove oldest entry (simple FIFO for now)
                oldest_key = next(iter(self.similarity_cache))
                del self.similarity_cache[oldest_key]

            self.similarity_cache[key] = result

        except Exception as e:
            logger.warning(f"Failed to cache result: {e}")

    def _update_metrics(self, algorithm: str, processing_time: float):
        """Update performance metrics"""
        self.metrics.total_calculations += 1
        self.metrics.total_processing_time_ms += processing_time

        if algorithm == "cosine":
            self.metrics.cosine_calculations += 1
        elif algorithm == "jaccard":
            self.metrics.jaccard_calculations += 1
        elif algorithm == "hybrid":
            self.metrics.hybrid_calculations += 1

        # Track algorithm performance
        if algorithm not in self.metrics.algorithm_performance:
            self.metrics.algorithm_performance[algorithm] = []
        self.metrics.algorithm_performance[algorithm].append(processing_time)

    def batch_similarity(self, texts: list[str], algorithm: str | None = None) -> list[SimilarityResult]:
        """Calculate similarity for multiple text pairs"""
        results = []

        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                result = self.calculate_similarity(texts[i], texts[j], algorithm)
                results.append(result)

        return results

    def find_most_similar(
        self,
        query_text: str,
        candidate_texts: list[str],
        algorithm: str | None = None,
        threshold: float | None = None,
    ) -> list[tuple[int, SimilarityResult]]:
        """Find most similar texts above threshold"""
        threshold = threshold or self.config.similarity_threshold
        results = []

        for i, candidate in enumerate(candidate_texts):
            result = self.calculate_similarity(query_text, candidate, algorithm)
            if result.score >= threshold:
                results.append((i, result))

        # Sort by similarity score (descending)
        results.sort(key=lambda x: x[1].score, reverse=True)
        return results

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get comprehensive performance metrics"""
        return {
            "total_calculations": self.metrics.total_calculations,
            "algorithm_breakdown": {
                "cosine": self.metrics.cosine_calculations,
                "jaccard": self.metrics.jaccard_calculations,
                "hybrid": self.metrics.hybrid_calculations,
            },
            "cache_performance": {
                "hit_rate": self.metrics.cache_hit_rate,
                "cache_hits": self.metrics.cache_hits,
                "cache_misses": self.metrics.cache_misses,
            },
            "processing_performance": {
                "avg_time_ms": self.metrics.avg_processing_time,
                "total_time_ms": self.metrics.total_processing_time_ms,
            },
            "algorithm_performance": {
                algo: {
                    "count": len(times),
                    "avg_time_ms": sum(times) / len(times) if times else 0.0,
                    "min_time_ms": min(times) if times else 0.0,
                    "max_time_ms": max(times) if times else 0.0,
                }
                for algo, times in self.metrics.algorithm_performance.items()
            },
        }

    def reset_metrics(self):
        """Reset performance metrics"""
        self.metrics = SimilarityMetrics()
        logger.info("Similarity scoring metrics reset")


async def main():
    """Main function to test similarity scoring algorithms"""
    try:
        logger.info("Testing Similarity Scoring Algorithms")

        # Create configuration
        config = SimilarityConfig(
            primary_algorithm="hybrid", similarity_threshold=0.6, enable_caching=True, use_tfidf=True
        )

        # Initialize engine
        engine = SimilarityScoringEngine(config)

        # Test texts
        test_texts = [
            "What is machine learning?",
            "Machine learning is a subset of artificial intelligence",
            "How does artificial intelligence work?",
            "What is the difference between AI and ML?",
            "Machine learning algorithms and their applications",
        ]

        # Test individual similarity
        logger.info("Testing individual similarity calculations...")
        result1 = engine.calculate_similarity(
            "What is machine learning?", "Machine learning is a subset of artificial intelligence"
        )
        logger.info(f"Similarity 1: {result1.score:.3f} using {result1.algorithm}")

        result2 = engine.calculate_similarity("What is machine learning?", "How does artificial intelligence work?")
        logger.info(f"Similarity 2: {result2.score:.3f} using {result2.algorithm}")

        # Test batch similarity
        logger.info("Testing batch similarity calculations...")
        batch_results = engine.batch_similarity(test_texts[:3])
        logger.info(f"Batch results: {len(batch_results)} comparisons")

        # Test most similar search
        logger.info("Testing most similar search...")
        most_similar = engine.find_most_similar("What is machine learning?", test_texts[1:], threshold=0.3)
        logger.info(f"Most similar texts: {len(most_similar)} above threshold")

        # Get performance metrics
        metrics = engine.get_performance_metrics()
        logger.info(f"Performance metrics: {metrics}")

        logger.info("Similarity Scoring Algorithms test completed successfully")
        return True

    except Exception as e:
        logger.error(f"Similarity Scoring Algorithms test failed: {e}")
        return False


if __name__ == "__main__":
    import asyncio

    success = asyncio.run(main())
    exit(0 if success else 1)
