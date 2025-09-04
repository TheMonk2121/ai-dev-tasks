#!/usr/bin/env python3
"""
Lightweight Cross-Encoder Reranker for RAGChecker Precision Optimization

Implements a lightweight cross-encoder reranking system to boost precision
by reranking top-N candidate sentences before final selection.

Based on the proven approach used by RAGAS leaders to achieve P≥0.20.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class CrossEncoderReranker:
    """Lightweight cross-encoder reranker for precision optimization."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.model = None
        self.cache = {}
        self.cache_enabled = True

        # Configuration from environment
        self.top_n = int(os.getenv("RAGCHECKER_CROSS_ENCODER_TOP_N", "50"))
        self.weight = float(os.getenv("RAGCHECKER_CROSS_ENCODER_WEIGHT", "0.15"))
        self.cache_enabled = os.getenv("RAGCHECKER_CROSS_ENCODER_CACHE", "1") == "1"

        # Initialize model if enabled
        if os.getenv("RAGCHECKER_CROSS_ENCODER_ENABLED", "0") == "1":
            self._initialize_model()

    def _initialize_model(self):
        """Initialize the cross-encoder model."""
        try:
            from sentence_transformers import CrossEncoder

            logger.info(f"🔄 Loading cross-encoder model: {self.model_name}")
            self.model = CrossEncoder(self.model_name)
            logger.info("✅ Cross-encoder model loaded successfully")
        except ImportError:
            logger.warning("⚠️ sentence-transformers not available - cross-encoder disabled")
            self.model = None
        except Exception as e:
            logger.error(f"❌ Failed to load cross-encoder model: {e}")
            self.model = None

    def _get_cache_key(self, query: str, candidate: str) -> str:
        """Generate cache key for query-candidate pair."""
        return f"{hash(query)}_{hash(candidate)}"

    def _score_pair(self, query: str, candidate: str) -> float:
        """Score a query-candidate pair using cross-encoder."""
        if not self.model:
            return 0.0

        # Check cache first
        if self.cache_enabled:
            cache_key = self._get_cache_key(query, candidate)
            if cache_key in self.cache:
                return self.cache[cache_key]

        try:
            # Get cross-encoder score
            score = self.model.predict([(query, candidate)])[0]

            # Cache the result
            if self.cache_enabled:
                self.cache[cache_key] = score

            return float(score)
        except Exception as e:
            logger.warning(f"⚠️ Cross-encoder scoring failed: {e}")
            return 0.0

    def rerank_candidates(self, query: str, candidates: List[str], contexts: List[str]) -> List[Tuple[str, float]]:
        """Rerank candidates using cross-encoder scores."""
        if not self.model or not candidates:
            return [(candidate, 0.0) for candidate in candidates]

        logger.info(f"🔄 Reranking {len(candidates)} candidates with cross-encoder")

        # Score each candidate
        scored_candidates = []
        for candidate in candidates:
            # Use the most relevant context for scoring
            best_context = self._find_best_context(candidate, contexts)
            if best_context:
                ce_score = self._score_pair(best_context, candidate)
            else:
                ce_score = 0.0

            scored_candidates.append((candidate, ce_score))

        # Sort by cross-encoder score (descending)
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        logger.info(f"✅ Reranked {len(scored_candidates)} candidates")
        return scored_candidates

    def _find_best_context(self, candidate: str, contexts: List[str]) -> Optional[str]:
        """Find the most relevant context for a candidate."""
        if not contexts:
            return None

        # Simple heuristic: find context with highest token overlap
        candidate_tokens = set(candidate.lower().split())
        best_context = None
        best_overlap = 0

        for context in contexts:
            context_tokens = set(context.lower().split())
            overlap = len(candidate_tokens & context_tokens)
            if overlap > best_overlap:
                best_overlap = overlap
                best_context = context

        return best_context

    def enhance_sentence_scores(
        self, sentences: List[str], contexts: List[str], query: str = ""
    ) -> List[Tuple[str, float]]:
        """Enhance sentence scores with cross-encoder reranking."""
        if not self.model or not sentences:
            return [(sentence, 0.0) for sentence in sentences]

        # Take top-N candidates for reranking
        top_candidates = sentences[: self.top_n]

        # Rerank using cross-encoder
        reranked = self.rerank_candidates(query, top_candidates, contexts)

        # Apply weight to cross-encoder scores
        enhanced_scores = []
        for sentence, ce_score in reranked:
            enhanced_score = ce_score * self.weight
            enhanced_scores.append((sentence, enhanced_score))

        # Add remaining sentences with zero cross-encoder score
        for sentence in sentences[self.top_n :]:
            enhanced_scores.append((sentence, 0.0))

        return enhanced_scores

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self.cache),
            "cache_enabled": self.cache_enabled,
            "model_loaded": self.model is not None,
            "model_name": self.model_name,
            "top_n": self.top_n,
            "weight": self.weight,
        }

    def clear_cache(self):
        """Clear the cross-encoder cache."""
        self.cache.clear()
        logger.info("🧹 Cross-encoder cache cleared")


class EnhancedEvidenceFilter:
    """Enhanced evidence filter with cross-encoder integration."""

    def __init__(self):
        self.cross_encoder = CrossEncoderReranker()

    def filter_with_cross_encoder(self, answer: str, contexts: List[str], query: str = "") -> str:
        """Filter evidence with cross-encoder enhancement."""
        if not self.cross_encoder.model:
            # Fall back to basic filtering
            return self._basic_filter(answer, contexts)

        # Split into sentences
        sentences = self._split_sentences(answer)
        if not sentences:
            return answer

        # Get cross-encoder enhanced scores
        enhanced_scores = self.cross_encoder.enhance_sentence_scores(sentences, contexts, query)

        # Apply threshold filtering
        filtered_sentences = []
        for sentence, ce_score in enhanced_scores:
            if self._should_keep_sentence(sentence, contexts, ce_score):
                filtered_sentences.append(sentence)

        return " ".join(filtered_sentences)

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        import re

        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def _should_keep_sentence(self, sentence: str, contexts: List[str], ce_score: float) -> bool:
        """Determine if a sentence should be kept based on cross-encoder score."""
        # Get base evidence score
        base_score = self._calculate_base_evidence_score(sentence, contexts)

        # Combine base score with cross-encoder score
        combined_score = base_score + ce_score

        # Apply threshold
        threshold = float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.07"))
        return combined_score >= threshold

    def _calculate_base_evidence_score(self, sentence: str, contexts: List[str]) -> float:
        """Calculate base evidence score using existing methods."""
        # This would integrate with the existing evidence scoring logic
        # For now, return a simple token overlap score
        sentence_tokens = set(sentence.lower().split())
        max_overlap = 0

        for context in contexts:
            context_tokens = set(context.lower().split())
            overlap = len(sentence_tokens & context_tokens)
            if overlap > max_overlap:
                max_overlap = overlap

        return max_overlap / len(sentence_tokens) if sentence_tokens else 0.0

    def _basic_filter(self, answer: str, contexts: List[str]) -> str:
        """Basic filtering without cross-encoder."""
        sentences = self._split_sentences(answer)
        filtered_sentences = []

        for sentence in sentences:
            if self._should_keep_sentence(sentence, contexts, 0.0):
                filtered_sentences.append(sentence)

        return " ".join(filtered_sentences)


def main():
    """Test the cross-encoder reranker."""
    import argparse

    parser = argparse.ArgumentParser(description="Cross-Encoder Reranker Test")
    parser.add_argument("--test", action="store_true", help="Run basic test")
    parser.add_argument("--stats", action="store_true", help="Show cache statistics")
    parser.add_argument("--clear-cache", action="store_true", help="Clear cache")

    args = parser.parse_args()

    # Enable cross-encoder
    os.environ["RAGCHECKER_CROSS_ENCODER_ENABLED"] = "1"

    reranker = CrossEncoderReranker()

    if args.stats:
        stats = reranker.get_cache_stats()
        print("📊 Cross-Encoder Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    if args.clear_cache:
        reranker.clear_cache()
        print("✅ Cache cleared")

    if args.test:
        print("🧪 Running cross-encoder test...")

        # Test data
        query = "What is the memory system architecture?"
        candidates = [
            "The memory system uses a three-tier architecture with SQL, pgvector, and knowledge graph storage.",
            "Memory rehydration is handled by the unified orchestrator.",
            "The system supports both local and cloud-based memory storage.",
            "Cross-encoder reranking improves precision by reranking top candidates.",
        ]
        contexts = [
            "The memory system architecture consists of three main components: SQL database for structured data, pgvector for semantic embeddings, and knowledge graph for relational information.",
            "Memory rehydration is a critical process that restores context from previous sessions using the unified memory orchestrator.",
        ]

        # Test reranking
        reranked = reranker.rerank_candidates(query, candidates, contexts)

        print("📊 Reranking Results:")
        for i, (candidate, score) in enumerate(reranked, 1):
            print(f"  {i}. Score: {score:.3f} - {candidate[:60]}...")

        # Test enhanced filtering
        filter_enhanced = EnhancedEvidenceFilter()
        test_answer = " ".join(candidates)
        filtered = filter_enhanced.filter_with_cross_encoder(test_answer, contexts, query)

        print(f"\n📝 Original: {len(test_answer)} chars")
        print(f"📝 Filtered: {len(filtered)} chars")
        print(f"📝 Filtered text: {filtered[:200]}...")


if __name__ == "__main__":
    main()
