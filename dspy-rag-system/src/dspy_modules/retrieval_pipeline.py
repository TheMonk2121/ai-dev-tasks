#!/usr/bin/env python3
"""
Enhanced Retrieval Pipeline with Hybrid Retrieval and Reranking
Implements the coach's strategy for pushing F1 over 20%
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.hybrid_retriever import create_hybrid_retriever
from utils.smart_chunker import create_smart_chunker

logger = logging.getLogger(__name__)


class EnhancedRetrievalPipeline:
    """
    Enhanced retrieval pipeline implementing the coach's strategy:
    - Code-aware chunking with stitching
    - Hybrid retrieval (BM25 + dense + metadata)
    - Cross-encoder reranking
    - Query-aware routing
    """

    def __init__(
        self,
        max_tokens: int = 300,
        overlap_tokens: int = 64,
        bm25_weight: float = 0.55,
        dense_weight: float = 0.35,
        metadata_weight: float = 0.10,
        stage1_top_k: int = 24,
        stage2_top_k: int = 8,
    ):
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

        # Initialize smart chunker
        self.chunker = create_smart_chunker(
            max_tokens=max_tokens, overlap_tokens=overlap_tokens, preserve_code_units=True, enable_stitching=True
        )

        # Initialize hybrid retriever
        self.retriever = create_hybrid_retriever(
            bm25_weight=bm25_weight,
            dense_weight=dense_weight,
            metadata_weight=metadata_weight,
            stage1_top_k=stage1_top_k,
            stage2_top_k=stage2_top_k,
            enable_reranking=True,
        )

        logger.info(
            f"EnhancedRetrievalPipeline initialized: max_tokens={max_tokens}, "
            f"overlap_tokens={overlap_tokens}, bm25={bm25_weight}, dense={dense_weight}"
        )

    def retrieve_with_context(
        self, query: str, query_type: Optional[str] = None, enable_stitching: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Enhanced retrieval with context-aware processing
        """
        try:
            # Determine query type for routing
            if not query_type:
                query_type = self._classify_query(query)

            # Get initial retrieval results
            retrieval_results = self.retriever.retrieve(query, query_type)

            # Apply chunk stitching if enabled
            if enable_stitching:
                stitched_results = self._stitch_related_chunks(retrieval_results, query_type)
            else:
                stitched_results = retrieval_results

            # Add metadata for answer generation
            enhanced_results = self._enhance_with_metadata(stitched_results, query, query_type)

            logger.info(f"Retrieved {len(enhanced_results)} chunks for query type: {query_type}")
            return enhanced_results

        except Exception as e:
            logger.error(f"Enhanced retrieval failed: {e}")
            # Fallback to basic retrieval
            return self._fallback_retrieval(query)

    def _classify_query(self, query: str) -> str:
        """Classify query type for routing"""
        query_lower = query.lower()

        if any(term in query_lower for term in ["implement", "code", "function", "class", "method"]):
            return "implementation"
        elif any(term in query_lower for term in ["how", "what", "explain", "describe"]):
            return "explanatory"
        elif any(term in query_lower for term in ["error", "fix", "debug", "troubleshoot"]):
            return "troubleshooting"
        elif any(term in query_lower for term in ["optimize", "performance", "speed", "efficiency"]):
            return "optimization"
        else:
            return "general"

    def _stitch_related_chunks(self, results: List[Any], query_type: str) -> List[Dict[str, Any]]:
        """Stitch related chunks for better context"""
        # Convert to list of dicts if needed
        dict_results = [dict(r) if hasattr(r, "__dict__") else r for r in results]

        if query_type == "implementation":
            # For implementation queries, prefer complete code units
            return self.chunker.stitch_adjacent_chunks(dict_results, query_type)
        else:
            # For other queries, use standard stitching
            return self.chunker.stitch_adjacent_chunks(dict_results)

    def _enhance_with_metadata(self, results: List[Any], query: str, query_type: str) -> List[Dict[str, Any]]:
        """Enhance results with metadata for answer generation"""
        enhanced = []

        for i, result in enumerate(results):
            enhanced_result = {
                **result,
                "retrieval_rank": i + 1,
                "query_type": query_type,
                "is_code_chunk": result.get("chunk_type", "").startswith("code"),
                "stitching_key": result.get("metadata", {}).get("stitching_key", ""),
                "completeness_score": self._calculate_completeness(result, query_type),
            }
            enhanced.append(enhanced_result)

        return enhanced

    def _calculate_completeness(self, result: Any, query_type: str) -> float:
        """Calculate completeness score for the chunk"""
        base_score = 0.5

        # Boost for complete functions/classes
        if result.get("metadata", {}).get("is_complete_function", False):
            base_score += 0.3
        elif result.get("metadata", {}).get("is_complete_section", False):
            base_score += 0.2

        # Boost for code chunks in implementation queries
        if query_type == "implementation" and result.get("chunk_type", "").startswith("code"):
            base_score += 0.2

        return min(base_score, 1.0)

    def _fallback_retrieval(self, query: str) -> List[Dict]:
        """Fallback retrieval method"""
        logger.warning("Using fallback retrieval")
        return [
            {
                "chunk_id": "fallback_1",
                "text": "Fallback content - retrieval failed",
                "score": 0.1,
                "metadata": {"fallback": True},
            }
        ]

    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        return {
            "chunker_config": {
                "max_tokens": self.max_tokens,
                "overlap_tokens": self.overlap_tokens,
                "preserve_code_units": True,
                "enable_stitching": True,
            },
            "retriever_config": self.retriever.get_retrieval_stats(),
            "pipeline_type": "enhanced_hybrid",
        }


def create_enhanced_pipeline(
    max_tokens: int = 300,
    overlap_tokens: int = 64,
    bm25_weight: float = 0.55,
    dense_weight: float = 0.35,
    metadata_weight: float = 0.10,
    stage1_top_k: int = 24,
    stage2_top_k: int = 8,
) -> EnhancedRetrievalPipeline:
    """Factory function to create enhanced retrieval pipeline"""
    return EnhancedRetrievalPipeline(
        max_tokens=max_tokens,
        overlap_tokens=overlap_tokens,
        bm25_weight=bm25_weight,
        dense_weight=dense_weight,
        metadata_weight=metadata_weight,
        stage1_top_k=stage1_top_k,
        stage2_top_k=stage2_top_k,
    )
