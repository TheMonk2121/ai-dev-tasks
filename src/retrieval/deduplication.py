"""
Near-duplicate suppression for retrieval candidates.

Removes near-identical content at the window level before reranking
to avoid wasting cross-encoder compute budget on redundant content.

Supports both cosine similarity (fast, embedding-based) and MinHash
(more robust, token-based) deduplication methods.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    cosine_similarity = None
    TfidfVectorizer = None
    np = None


class CosineDeduplicator:
    """Fast cosine similarity-based deduplication using TF-IDF vectors."""

    def __init__(
        self, threshold: float = 0.9, max_features: int = 1000, min_df: int = 1, ngram_range: Tuple[int, int] = (1, 2)
    ):
        if not HAS_SKLEARN:
            raise ImportError("sklearn required for CosineDeduplicator")

        self.threshold = threshold
        self.vectorizer = TfidfVectorizer(
            max_features=max_features, min_df=min_df, ngram_range=ngram_range, stop_words="english", lowercase=True
        )

    def deduplicate(self, candidates: List[Dict[str, Any]], text_field: str = "text") -> List[Dict[str, Any]]:
        """
        Remove near-duplicates using cosine similarity.

        Args:
            candidates: List of candidate dicts with text content
            text_field: Field name containing text to compare

        Returns:
            Filtered list with near-duplicates removed
        """
        if len(candidates) <= 1:
            return candidates

        # Extract texts
        texts = [candidate.get(text_field, "") for candidate in candidates]
        texts = [text for text in texts if text.strip()]

        if len(texts) <= 1:
            return candidates

        try:
            # Compute TF-IDF matrix
            tfidf_matrix = self.vectorizer.fit_transform(texts)

            # Compute pairwise cosine similarities
            similarities = cosine_similarity(tfidf_matrix)

            # Find near-duplicates
            to_remove = set()
            n = len(candidates)

            for i in range(n):
                if i in to_remove:
                    continue

                for j in range(i + 1, n):
                    if j in to_remove:
                        continue

                    if similarities[i, j] >= self.threshold:
                        # Keep the one with higher score, remove the other
                        score_i = candidates[i].get("score", 0.0)
                        score_j = candidates[j].get("score", 0.0)

                        if score_i >= score_j:
                            to_remove.add(j)
                        else:
                            to_remove.add(i)
                            break  # Move to next i

            # Return filtered candidates
            return [candidates[i] for i in range(n) if i not in to_remove]

        except Exception as e:
            # Fallback: return original candidates on error
            print(f"Cosine deduplication failed: {e}")
            return candidates


class MinHashDeduplicator:
    """MinHash-based deduplication for robust near-duplicate detection."""

    def __init__(self, threshold: float = 0.8, num_hashes: int = 128, ngram_size: int = 3):
        self.threshold = threshold
        self.num_hashes = num_hashes
        self.ngram_size = ngram_size

    def deduplicate(self, candidates: List[Dict[str, Any]], text_field: str = "text") -> List[Dict[str, Any]]:
        """
        Remove near-duplicates using MinHash signatures.

        Args:
            candidates: List of candidate dicts with text content
            text_field: Field name containing text to compare

        Returns:
            Filtered list with near-duplicates removed
        """
        if len(candidates) <= 1:
            return candidates

        # Compute MinHash signatures for all candidates
        signatures = []
        for candidate in candidates:
            text = candidate.get(text_field, "")
            signature = self._compute_minhash(text)
            signatures.append(signature)

        # Find near-duplicates using Jaccard similarity
        to_remove = set()
        n = len(candidates)

        for i in range(n):
            if i in to_remove:
                continue

            for j in range(i + 1, n):
                if j in to_remove:
                    continue

                jaccard_sim = self._jaccard_similarity(signatures[i], signatures[j])

                if jaccard_sim >= self.threshold:
                    # Keep the one with higher score
                    score_i = candidates[i].get("score", 0.0)
                    score_j = candidates[j].get("score", 0.0)

                    if score_i >= score_j:
                        to_remove.add(j)
                    else:
                        to_remove.add(i)
                        break

        return [candidates[i] for i in range(n) if i not in to_remove]

    def _compute_minhash(self, text: str) -> List[int]:
        """Compute MinHash signature for text."""
        if not text.strip():
            return [0] * self.num_hashes

        # Generate n-grams
        ngrams = self._get_ngrams(text.lower())

        if not ngrams:
            return [0] * self.num_hashes

        # Compute hash values for each n-gram
        signature = []
        for i in range(self.num_hashes):
            min_hash = float("inf")
            salt = f"hash_{i}".encode()

            for ngram in ngrams:
                hash_val = int(hashlib.sha1(ngram.encode() + salt).hexdigest()[:8], 16)
                min_hash = min(min_hash, hash_val)

            signature.append(min_hash)

        return signature

    def _get_ngrams(self, text: str) -> Set[str]:
        """Extract n-grams from text."""
        # Simple word-based n-grams
        words = text.split()
        ngrams = set()

        # Character n-grams for robustness
        for i in range(len(text) - self.ngram_size + 1):
            ngram = text[i : i + self.ngram_size]
            if ngram.strip():  # Skip whitespace-only n-grams
                ngrams.add(ngram)

        return ngrams

    def _jaccard_similarity(self, sig1: List[int], sig2: List[int]) -> float:
        """Compute Jaccard similarity from MinHash signatures."""
        if len(sig1) != len(sig2):
            return 0.0

        matches = sum(1 for a, b in zip(sig1, sig2) if a == b)
        return matches / len(sig1)


class SimpleHashDeduplicator:
    """Simple hash-based deduplication fallback."""

    def __init__(self, threshold: float = 1.0):
        self.threshold = threshold  # 1.0 = exact matches only

    def deduplicate(self, candidates: List[Dict[str, Any]], text_field: str = "text") -> List[Dict[str, Any]]:
        """Remove exact duplicates using text hashing."""
        seen_hashes = set()
        unique_candidates = []

        for candidate in candidates:
            text = candidate.get(text_field, "").strip().lower()
            text_hash = hashlib.md5(text.encode()).hexdigest()

            if text_hash not in seen_hashes:
                seen_hashes.add(text_hash)
                unique_candidates.append(candidate)

        return unique_candidates


class NearDuplicateFilter:
    """Main interface for near-duplicate filtering with method selection."""

    def __init__(self, method: str = "cosine", threshold: float = 0.9, **kwargs: Any):  # cosine | minhash | simple
        self.method = method
        self.threshold = threshold

        # Initialize appropriate deduplicator
        if method == "cosine" and HAS_SKLEARN:
            self.deduplicator = CosineDeduplicator(threshold=threshold, **kwargs)
        elif method == "minhash":
            self.deduplicator = MinHashDeduplicator(threshold=threshold, **kwargs)
        elif method == "simple":
            self.deduplicator = SimpleHashDeduplicator(threshold=threshold)
        else:
            # Fallback to simple hash deduplication
            print(f"Method '{method}' not available, falling back to simple hash")
            self.deduplicator = SimpleHashDeduplicator(threshold=1.0)

    def filter_duplicates(
        self, candidates: List[Dict[str, Any]], text_field: str = "text", preserve_order: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Filter near-duplicates from candidates.

        Args:
            candidates: List of candidate documents/windows
            text_field: Field containing text to compare
            preserve_order: Whether to preserve original ordering

        Returns:
            Filtered candidates with near-duplicates removed
        """
        if not candidates:
            return candidates

        # Store original indices if preserving order
        if preserve_order:
            for i, candidate in enumerate(candidates):
                candidate["_original_index"] = i

        # Apply deduplication
        filtered = self.deduplicator.deduplicate(candidates, text_field)

        # Restore original order if requested
        if preserve_order and "_original_index" in (filtered[0] if filtered else {}):
            filtered.sort(key=lambda x: x.get("_original_index", 0))

            # Clean up temporary indices
            for candidate in filtered:
                candidate.pop("_original_index", None)

        return filtered


def create_deduplicator(config: Optional[Dict[str, Any]] = None) -> NearDuplicateFilter:
    """Factory function to create a deduplicator from config."""

    if not config:
        # Default configuration
        return NearDuplicateFilter(method="cosine" if HAS_SKLEARN else "simple")

    return NearDuplicateFilter(
        method=config.get("method", "cosine"),
        threshold=config.get("threshold", 0.9),
        **{k: v for k, v in config.items() if k not in ["method", "threshold"]},
    )
