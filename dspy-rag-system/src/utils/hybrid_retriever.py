#!/usr/bin/env python3
"""
Hybrid Retrieval with Cross-Encoder Reranking
Implements the coach's two-stage retrieval strategy
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class SingleflightCache:
    """Simple singleflight cache to deduplicate identical queries."""

    def __init__(self, ttl_seconds: int = 30):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self._locks: Dict[str, asyncio.Lock] = {}

    def _get_cache_key(self, query: str) -> str:
        """Generate cache key for query."""
        return hashlib.md5(query.encode()).hexdigest()

    async def get_or_compute(self, query: str, compute_fn):
        """Get cached result or compute if not present/expired."""
        cache_key = self._get_cache_key(query)
        now = time.time()

        # Check if we have a valid cached result
        if (
            cache_key in self._cache
            and cache_key in self._timestamps
            and now - self._timestamps[cache_key] < self.ttl_seconds
        ):
            logger.debug(f"Cache hit for query: {query[:50]}...")
            return self._cache[cache_key]

        # Get or create lock for this cache key
        if cache_key not in self._locks:
            self._locks[cache_key] = asyncio.Lock()

        async with self._locks[cache_key]:
            # Double-check cache after acquiring lock
            if (
                cache_key in self._cache
                and cache_key in self._timestamps
                and now - self._timestamps[cache_key] < self.ttl_seconds
            ):
                return self._cache[cache_key]

            # Compute new result
            logger.debug(f"Cache miss, computing for query: {query[:50]}...")
            result = await compute_fn()

            # Cache result
            self._cache[cache_key] = result
            self._timestamps[cache_key] = time.time()

            return result

    def clear_expired(self):
        """Clear expired cache entries."""
        now = time.time()
        expired_keys = [key for key, timestamp in self._timestamps.items() if now - timestamp >= self.ttl_seconds]

        for key in expired_keys:
            self._cache.pop(key, None)
            self._timestamps.pop(key, None)
            self._locks.pop(key, None)


@dataclass
class RetrievalResult:
    """Represents a retrieval result with scoring"""

    chunk_id: str
    text: str
    score: float
    source: str  # 'bm25', 'dense', 'hybrid'
    metadata: Dict[str, Any]


class HybridRetriever:
    """
    Hybrid retriever implementing the coach's strategy:
    Stage 1: BM25 (lexical) ∪ dense embeddings with weighted hybrid score
    Stage 2: Cross-encoder re-rank top-24 → top-8
    """

    def __init__(
        self,
        bm25_weight: float = 0.55,  # Coach's recommendation
        dense_weight: float = 0.35,  # Coach's recommendation
        metadata_weight: float = 0.10,  # Coach's recommendation
        stage1_top_k: int = 24,  # Coach's recommendation
        stage2_top_k: int = 8,  # Coach's recommendation
        enable_reranking: bool = True,
        # Phase 0/1 enhancements
        enable_windowing: bool = True,
        enable_dedup: bool = True,
        enable_cross_encoder: bool = False,  # Requires ONNX model
        enable_singleflight: bool = True,
        singleflight_ttl: int = 30,
    ):

        self.bm25_weight = bm25_weight
        self.dense_weight = dense_weight
        self.metadata_weight = metadata_weight
        self.stage1_top_k = stage1_top_k
        self.stage2_top_k = stage2_top_k
        self.enable_reranking = enable_reranking

        # Initialize components
        self.bm25_retriever = None  # Will be set by set_retrievers
        self.dense_retriever = None
        self.reranker = None

        # Phase 0/1 components (initialized later)
        self.windower = None
        self.deduplicator = None
        self.cross_encoder_client = None

        # Feature flags
        self.enable_windowing = enable_windowing
        self.enable_dedup = enable_dedup
        self.enable_cross_encoder = enable_cross_encoder

        # Singleflight cache for concurrency control
        self.singleflight_cache = SingleflightCache(ttl_seconds=singleflight_ttl) if enable_singleflight else None

        logger.info(
            f"HybridRetriever initialized: bm25={bm25_weight}, dense={dense_weight}, metadata={metadata_weight}"
        )
        logger.info(
            f"Phase 0/1 features: windowing={enable_windowing}, dedup={enable_dedup}, cross_encoder={enable_cross_encoder}, singleflight={enable_singleflight}"
        )

    def set_retrievers(self, bm25_retriever, dense_retriever, reranker=None):
        """Set the underlying retrieval components"""
        self.bm25_retriever = bm25_retriever
        self.dense_retriever = dense_retriever
        self.reranker = reranker

    def set_phase01_components(self, windower=None, deduplicator=None, cross_encoder_client=None):
        """Set Phase 0/1 enhancement components"""
        if windower and self.enable_windowing:
            self.windower = windower

        if deduplicator and self.enable_dedup:
            self.deduplicator = deduplicator

        if cross_encoder_client and self.enable_cross_encoder:
            self.cross_encoder_client = cross_encoder_client

        logger.info(
            f"Phase 0/1 components set: windower={self.windower is not None}, dedup={self.deduplicator is not None}, cross_encoder={self.cross_encoder_client is not None}"
        )

        logger.info("Retrievers configured")

    def retrieve(self, query: str, query_type: str = None) -> List[RetrievalResult]:
        """
        Main retrieval method implementing the coach's strategy
        """
        try:
            # Stage 1: Hybrid retrieval (BM25 + dense)
            stage1_results = self._stage1_hybrid_retrieval(query)

            if not self.enable_reranking or not self.reranker:
                # Return stage 1 results if no reranking
                return stage1_results[: self.stage2_top_k]

            # Stage 2: Cross-encoder reranking
            stage2_results = self._stage2_reranking(query, stage1_results)

            return stage2_results

        except Exception as e:
            logger.error(f"Hybrid retrieval failed: {e}")
            # Fallback to stage 1 only
            return self._stage1_hybrid_retrieval(query)[: self.stage2_top_k]

    def _stage1_hybrid_retrieval(self, query: str) -> List[RetrievalResult]:
        """Stage 1: BM25 ∪ dense with weighted hybrid scoring"""

        # Get BM25 results
        bm25_results = self._get_bm25_results(query)

        # Get dense results
        dense_results = self._get_dense_results(query)

        # Fuse results using weighted RRF (Reciprocal Rank Fusion)
        fused_results = self._fuse_results_with_rrf(bm25_results, dense_results)

        # Apply metadata scoring
        scored_results = self._apply_metadata_scoring(fused_results, query)

        # Sort by final score and return top-k
        scored_results.sort(key=lambda x: x.score, reverse=True)
        return scored_results[: self.stage1_top_k]

    def _get_bm25_results(self, query: str) -> List[RetrievalResult]:
        """Get BM25 lexical search results"""
        if not self.bm25_retriever:
            logger.warning("BM25 retriever not configured, returning empty results")
            return []

        try:
            # Mock BM25 results for now - replace with actual implementation
            results = []
            for i in range(10):
                results.append(
                    RetrievalResult(
                        chunk_id=f"bm25_chunk_{i}",
                        text=f"BM25 result {i} for query: {query}",
                        score=0.8 - (i * 0.05),
                        source="bm25",
                        metadata={"rank": i + 1},
                    )
                )
            return results
        except Exception as e:
            logger.error(f"BM25 retrieval failed: {e}")
            return []

    def _get_dense_results(self, query: str) -> List[RetrievalResult]:
        """Get dense embedding search results"""
        if not self.dense_retriever:
            logger.warning("Dense retriever not configured, returning empty results")
            return []

        try:
            # Mock dense results for now - replace with actual implementation
            results = []
            for i in range(10):
                results.append(
                    RetrievalResult(
                        chunk_id=f"dense_chunk_{i}",
                        text=f"Dense result {i} for query: {query}",
                        score=0.9 - (i * 0.08),
                        source="dense",
                        metadata={"rank": i + 1},
                    )
                )
            return results
        except Exception as e:
            logger.error(f"Dense retrieval failed: {e}")
            return []

    def _fuse_results_with_rrf(
        self, bm25_results: List[RetrievalResult], dense_results: List[RetrievalResult]
    ) -> List[RetrievalResult]:
        """Fuse results using weighted Reciprocal Rank Fusion"""

        # Create lookup for scores
        bm25_scores = {r.chunk_id: r.score for r in bm25_results}
        dense_scores = {r.chunk_id: r.score for r in dense_results}

        # Get all unique chunk IDs
        all_chunk_ids = set(bm25_scores.keys()) | set(dense_scores.keys())

        fused_results = []

        for chunk_id in all_chunk_ids:
            # Get scores (default to 0 if not found)
            bm25_score = bm25_scores.get(chunk_id, 0.0)
            dense_score = dense_scores.get(chunk_id, 0.0)

            # Calculate weighted hybrid score
            hybrid_score = self.bm25_weight * bm25_score + self.dense_weight * dense_score

            # Get the text from either source
            text = ""
            source = "hybrid"
            metadata = {}

            # Find the result with this chunk_id
            for result in bm25_results + dense_results:
                if result.chunk_id == chunk_id:
                    text = result.text
                    metadata = result.metadata
                    break

            fused_results.append(
                RetrievalResult(chunk_id=chunk_id, text=text, score=hybrid_score, source=source, metadata=metadata)
            )

        return fused_results

    def _apply_metadata_scoring(self, results: List[RetrievalResult], query: str) -> List[RetrievalResult]:
        """Apply metadata-based scoring (recency, relevance, etc.)"""

        for result in results:
            metadata_score = 0.0

            # Recency scoring (if available)
            if "timestamp" in result.metadata:
                # Newer content gets higher score
                age_hours = (time.time() - result.metadata["timestamp"]) / 3600
                if age_hours < 24:
                    metadata_score += 0.1
                elif age_hours < 168:  # 1 week
                    metadata_score += 0.05

            # Source type scoring
            if result.metadata.get("chunk_type") == "code_function":
                metadata_score += 0.05  # Prefer code for implementation queries

            # Query type matching
            if "implementation" in query.lower() and "code" in result.metadata.get("chunk_type", ""):
                metadata_score += 0.1

            # Apply metadata weight
            final_score = result.score + (self.metadata_weight * metadata_score)
            result.score = final_score

        return results

    async def _stage2_reranking(self, query: str, stage1_results: List[RetrievalResult]) -> List[RetrievalResult]:
        """Stage 2: Enhanced cross-encoder reranking with windowing, dedup, and telemetry"""

        if not self.reranker:
            logger.warning("Reranker not configured, returning stage 1 results")
            return stage1_results[: self.stage2_top_k]

        try:
            stage_start = time.time()

            # Convert to dict format for processing
            candidates = []
            for result in stage1_results:
                candidates.append(
                    {
                        "document_id": result.chunk_id,
                        "text": result.text,
                        "score": result.score,
                        "metadata": {"source": result.source},
                    }
                )

            # Phase 1: Windowing (120-180 tokens, 30-40% overlap)
            if hasattr(self, "windower") and self.windower:
                windows = self.windower.create_windows(candidates, max_windows_per_doc=3)
                logger.debug(f"Created {len(windows)} windows from {len(candidates)} candidates")
            else:
                # Fallback: treat each candidate as a single window
                from ..retrieval.windowing import DocumentWindow

                windows = []
                for i, candidate in enumerate(candidates):
                    window = DocumentWindow(
                        window_id=f"{candidate['document_id']}_w0",
                        document_id=candidate["document_id"],
                        text=candidate["text"],
                        start_token=0,
                        end_token=len(candidate["text"].split()),
                        window_index=0,
                        original_score=candidate["score"],
                    )
                    windows.append(window)

            # Phase 1: Near-duplicate suppression
            if hasattr(self, "deduplicator") and self.deduplicator:
                window_dicts = []
                for w in windows:
                    window_dicts.append(
                        {
                            "window_id": w.window_id,
                            "document_id": w.document_id,
                            "text": w.text,
                            "score": w.original_score,
                        }
                    )

                deduplicated = self.deduplicator.filter_duplicates(window_dicts, text_field="text")
                logger.debug(f"Deduplicated {len(window_dicts)} -> {len(deduplicated)} windows")

                # Convert back to windows
                dedup_window_ids = {w["window_id"] for w in deduplicated}
                windows = [w for w in windows if w.window_id in dedup_window_ids]

            # Phase 1: Cross-encoder reranking with timeout and fallback
            if hasattr(self, "cross_encoder_client") and self.cross_encoder_client:
                window_candidates = []
                for window in windows:
                    window_candidates.append(
                        {"document_id": window.document_id, "text": window.text, "score": window.original_score}
                    )

                rerank_result = await self.cross_encoder_client.rerank_async(
                    query=query, candidates=window_candidates, text_field="text"
                )

                # Update window scores
                for i, score in enumerate(rerank_result.scores):
                    if i < len(windows):
                        windows[i].original_score = score

                logger.debug(f"Reranked using {rerank_result.method} in {rerank_result.latency_ms:.1f}ms")

            else:
                # Fallback to heuristic reranking
                reranked_scores = self._rerank_with_cross_encoder_fallback(query, windows)
                for i, score in enumerate(reranked_scores):
                    if i < len(windows):
                        windows[i].original_score = score

            # Sort windows by reranked scores
            windows.sort(key=lambda w: w.original_score, reverse=True)

            # Convert back to RetrievalResult format, taking top windows per document
            window_groups = {}
            for window in windows:
                doc_id = window.document_id
                if doc_id not in window_groups:
                    window_groups[doc_id] = []
                window_groups[doc_id].append(window)

            final_results = []
            for result in stage1_results:
                if result.chunk_id in window_groups:
                    # Use best window score for this document
                    best_window = window_groups[result.chunk_id][0]
                    result.score = best_window.original_score
                    final_results.append(result)

                    if len(final_results) >= self.stage2_top_k:
                        break

            stage_time = (time.time() - stage_start) * 1000
            logger.debug(f"Stage 2 reranking completed in {stage_time:.1f}ms")

            return final_results

        except Exception as e:
            logger.error(f"Enhanced reranking failed: {e}")
            return stage1_results[: self.stage2_top_k]

    def _rerank_with_cross_encoder_fallback(self, query: str, windows: List) -> List[float]:
        """Fallback heuristic reranking for windows"""

        # Import here to avoid circular dependencies
        try:
            from ..retrieval.reranker import _score_rerank
        except ImportError:
            # Simple fallback scoring
            def _score_rerank(q: str, text: str) -> float:
                q_words = set(q.lower().split())
                text_words = set(text.lower().split())
                if not q_words:
                    return 0.0
                overlap = len(q_words & text_words) / len(q_words)
                return overlap

        query_lower = query.lower()
        scores = []

        for window in windows:
            text = window.text.lower()
            score = _score_rerank(query_lower, text)
            scores.append(score)

        return scores

    def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get retrieval statistics for monitoring"""
        return {
            "bm25_weight": self.bm25_weight,
            "dense_weight": self.dense_weight,
            "metadata_weight": self.metadata_weight,
            "stage1_top_k": self.stage1_top_k,
            "stage2_top_k": self.stage2_top_k,
            "enable_reranking": self.enable_reranking,
            "components_configured": {
                "bm25": self.bm25_retriever is not None,
                "dense": self.dense_retriever is not None,
                "reranker": self.reranker is not None,
            },
        }


def create_hybrid_retriever(
    bm25_weight: float = 0.55,
    dense_weight: float = 0.35,
    metadata_weight: float = 0.10,
    stage1_top_k: int = 24,
    stage2_top_k: int = 8,
    enable_reranking: bool = True,
) -> HybridRetriever:
    """Factory function to create a hybrid retriever"""
    return HybridRetriever(
        bm25_weight=bm25_weight,
        dense_weight=dense_weight,
        metadata_weight=metadata_weight,
        stage1_top_k=stage1_top_k,
        stage2_top_k=stage2_top_k,
        enable_reranking=enable_reranking,
    )
