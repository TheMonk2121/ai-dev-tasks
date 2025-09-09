"""
Recall-Friendly Pre-filtering for Retrieval Results

Applies quality gates and diversity filters before fusion to improve
retrieval quality while maintaining high recall.

Key principles:
- Conservative thresholds to preserve recall
- Remove clearly irrelevant results
- Deduplicate near-identical content
- Respect document length constraints
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Union

if TYPE_CHECKING:
    from sklearn.feature_extraction.text import TfidfVectorizer

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:  # pragma: no cover - optional dependency guard
    TfidfVectorizer = None  # type: ignore[assignment]
    cosine_similarity = None  # type: ignore[assignment]

DocId = str
Score = float
Document = str


class PrefilterConfig:
    """Configuration for pre-filtering parameters."""

    def __init__(
        self,
        min_bm25_score: float = 0.1,
        min_vector_score: float = 0.7,
        min_doc_length: int = 50,
        max_doc_length: int = 8000,
        enable_diversity: bool = True,
        diversity_threshold: float = 0.9,
    ):
        self.min_bm25_score = min_bm25_score
        self.min_vector_score = min_vector_score
        self.min_doc_length = min_doc_length
        self.max_doc_length = max_doc_length
        self.enable_diversity = enable_diversity
        self.diversity_threshold = diversity_threshold


class RecallFriendlyPrefilter:
    """Applies conservative pre-filtering to maintain high recall."""

    def __init__(self, config: PrefilterConfig | None = None):
        self.config = config or PrefilterConfig()
        self._tfidf_vectorizer: Any | None = None

    def filter_bm25_results(
        self,
        results: list[tuple[DocId, Score]],
        documents: dict[DocId, Document],
    ) -> list[tuple[DocId, Score]]:
        """Filter BM25 results by score and document quality."""
        filtered = []

        for doc_id, score in results:
            # Score threshold (recall-friendly)
            if score < self.config.min_bm25_score:
                continue

            # Document length check
            doc_text = documents.get(doc_id, "")
            if not self._is_valid_document(doc_text):
                continue

            filtered.append((doc_id, score))

        return filtered

    def filter_vector_results(
        self,
        results: list[tuple[DocId, Score]],
        documents: dict[DocId, Document],
    ) -> list[tuple[DocId, Score]]:
        """Filter vector results by similarity and document quality."""
        filtered = []

        for doc_id, score in results:
            # Score threshold (recall-friendly - 0.7 is conservative for cosine sim)
            if score < self.config.min_vector_score:
                continue

            # Document length check
            doc_text = documents.get(doc_id, "")
            if not self._is_valid_document(doc_text):
                continue

            filtered.append((doc_id, score))

        return filtered

    def apply_diversity_filter(
        self,
        results: list[tuple[DocId, Score]],
        documents: dict[DocId, Document],
    ) -> list[tuple[DocId, Score]]:
        """Remove near-duplicate documents while preserving highest scores."""
        if not self.config.enable_diversity or len(results) <= 1:
            return results

        # Extract document texts
        doc_texts = []
        doc_ids = []
        for doc_id, _ in results:
            doc_text = documents.get(doc_id, "")
            if doc_text:
                doc_texts.append(doc_text)
                doc_ids.append(doc_id)

        if len(doc_texts) <= 1:
            return results

        # Compute TF-IDF similarity matrix
        try:
            if TfidfVectorizer is None or cosine_similarity is None:
                return results
            if self._tfidf_vectorizer is None:
                self._tfidf_vectorizer = TfidfVectorizer(
                    max_features=5000, stop_words="english", ngram_range=(1, 2), max_df=0.95, min_df=1
                )

            tfidf_matrix = self._tfidf_vectorizer.fit_transform(doc_texts)
            similarity_matrix = cosine_similarity(tfidf_matrix)

        except Exception:
            # Fallback to no diversity filtering if TF-IDF fails
            return results

        # Greedy selection: keep highest scoring documents that aren't too similar
        kept_indices: set[int] = set()

        # Sort by score (descending) to prioritize highest-scoring documents
        indexed_results = [(i, doc_id, score) for i, (doc_id, score) in enumerate(results) if doc_id in doc_ids]
        indexed_results.sort(key=lambda x: x[2], reverse=True)

        for i, doc_id, score in indexed_results:
            doc_idx = doc_ids.index(doc_id)

            # Check if this document is too similar to any already kept document
            is_duplicate = False
            for kept_idx in kept_indices:
                kept_doc_idx = doc_ids.index(results[kept_idx][0])
                if similarity_matrix[doc_idx][kept_doc_idx] >= self.config.diversity_threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                kept_indices.add(i)

        # Return filtered results in original score order
        filtered_results = []
        for i, (doc_id, score) in enumerate(results):
            if i in kept_indices:
                filtered_results.append((doc_id, score))

        return filtered_results

    def prefilter_all(
        self,
        bm25_results: list[tuple[DocId, Score]],
        vector_results: list[tuple[DocId, Score]],
        documents: dict[DocId, Document],
    ) -> tuple[list[tuple[DocId, Score]], list[tuple[DocId, Score]]]:
        """Apply all pre-filtering steps to both result sets."""
        # Filter by score and quality
        filtered_bm25 = self.filter_bm25_results(bm25_results, documents)
        filtered_vector = self.filter_vector_results(vector_results, documents)

        # Apply diversity filtering
        if self.config.enable_diversity:
            filtered_bm25 = self.apply_diversity_filter(filtered_bm25, documents)
            filtered_vector = self.apply_diversity_filter(filtered_vector, documents)

        return filtered_bm25, filtered_vector

    def _is_valid_document(self, doc_text: str) -> bool:
        """Check if document meets basic quality criteria."""
        if not doc_text or not doc_text.strip():
            return False

        doc_length = len(doc_text)
        return self.config.min_doc_length <= doc_length <= self.config.max_doc_length

    def get_filter_stats(
        self,
        original_bm25: list[tuple[DocId, Score]],
        original_vector: list[tuple[DocId, Score]],
        filtered_bm25: list[tuple[DocId, Score]],
        filtered_vector: list[tuple[DocId, Score]],
    ) -> dict[str, int | float]:
        """Return filtering statistics for monitoring."""
        return {
            "bm25_original": len(original_bm25),
            "bm25_filtered": len(filtered_bm25),
            "bm25_retention_rate": len(filtered_bm25) / max(len(original_bm25), 1),
            "vector_original": len(original_vector),
            "vector_filtered": len(filtered_vector),
            "vector_retention_rate": len(filtered_vector) / max(len(original_vector), 1),
        }


def create_prefilter_from_config(config_dict: dict) -> RecallFriendlyPrefilter:
    """Create prefilter from configuration dictionary."""
    prefilter_config = config_dict.get("prefilter", {})

    config = PrefilterConfig(
        min_bm25_score=prefilter_config.get("min_bm25_score", 0.1),
        min_vector_score=prefilter_config.get("min_vector_score", 0.7),
        min_doc_length=prefilter_config.get("min_doc_length", 50),
        max_doc_length=prefilter_config.get("max_doc_length", 8000),
        enable_diversity=prefilter_config.get("enable_diversity", True),
        diversity_threshold=prefilter_config.get("diversity_threshold", 0.9),
    )

    return RecallFriendlyPrefilter(config)
