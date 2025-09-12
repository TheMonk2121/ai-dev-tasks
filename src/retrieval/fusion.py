from __future__ import annotations
from collections.abc import Mapping, Sequence
"""
Weighted Reciprocal Rank Fusion (RRF)

Implements a deterministic, parameterized fusion of ranked lists from
lexical (BM25) and semantic (vector) retrieval.

Usage (simple):
    fused = weighted_rrf(bm25_list, vector_list, k=60, lambda_lex=0.6, lambda_sem=0.4)

Where bm25_list/vector_list can be one of:
    - list[str]: ordered doc_ids (best first)
    - list[tuple[str, float]]: (doc_id, score) pairs (sorted desc or unsorted)
    - dict[str, float]: doc_id -> score (will be sorted desc)

Returns:
    list[tuple[str, float]] sorted by fused score desc
"""



DocId = str
Rank = int
Score = float


def _as_rank_map(items: Sequence[DocId] | Sequence[tuple[DocId, Score]] | Mapping[DocId, Score]) -> dict[DocId, Rank]:
    """Normalize various input formats into a 1-indexed rank map.

    - If items is a sequence of doc_ids, use their order as rank.
    - If items is (doc_id, score) pairs or a mapping, sort by score desc then assign ranks.
    """
    rank_map: dict[DocId, Rank] = {}

    if isinstance(items, dict):  # Mapping[DocId, Score]
        sorted_items = sorted(items.items(), key=lambda kv: kv[1], reverse=True)
        for idx, (doc_id, _score) in enumerate(sorted_items, start=1):
            rank_map[doc_id] = idx
        return rank_map

    if not items:
        return rank_map

    first = items[0]  # type: ignore[index]
    if isinstance(first, tuple) and len(first) == 2:  # Sequence[tuple[DocId, Score]]
        pairs = list(items)  # type: ignore[assignment]
        pairs.sort(key=lambda kv: kv[1], reverse=True)
        for idx, (doc_id, _score) in enumerate(pairs, start=1):
            rank_map[doc_id] = idx
        return rank_map

    # Sequence[DocId]
    for idx, doc_id in enumerate(items, start=1):  # type: ignore[arg-type]
        rank_map[str(doc_id)] = idx
    return rank_map


def _rrf(rank: Rank | None, k: int) -> float:
    """Reciprocal rank contribution for a given rank (1-indexed).

    If rank is None (doc not present), return 0.
    """
    if rank is None:
        return 0.0
    return 1.0 / (k + rank)


def weighted_rrf(
    bm25: Sequence[DocId] | Sequence[tuple[DocId, Score]] | Mapping[DocId, Score],
    vector: Sequence[DocId] | Sequence[tuple[DocId, Score]] | Mapping[DocId, Score],
    *,
    k: int = 60,
    lambda_lex: float = 0.6,
    lambda_sem: float = 0.4,
    limit: int | None = None,
) -> list[tuple[DocId, Score]]:
    """Fuse two ranked lists using weighted RRF.

    Args:
        bm25: lexical ranking (BM25) in any supported format
        vector: semantic ranking (vector) in any supported format
        k: RRF smoothing constant (higher reduces tail impact)
        lambda_lex: weight for lexical contribution
        lambda_sem: weight for semantic contribution
        limit: optional cap on number of results returned

    Returns:
        List of (doc_id, fused_score) sorted by fused_score desc.
    """
    if lambda_lex < 0 or lambda_sem < 0:
        raise ValueError("lambda_lex and lambda_sem must be non-negative")
    if abs((lambda_lex + lambda_sem) - 1.0) > 1e-6:
        # Normalize if not summing to 1.0
        total = max(lambda_lex + lambda_sem, 1e-9)
        lambda_lex = lambda_lex / total
        lambda_sem = lambda_sem / total

    bm25_ranks = _as_rank_map(bm25)
    vec_ranks = _as_rank_map(vector)

    all_ids = set(bm25_ranks.keys()) | set(vec_ranks.keys())

    fused: list[tuple[DocId, Score]] = []
    for doc_id in all_ids:
        r_lex = bm25_ranks.get(doc_id)
        r_sem = vec_ranks.get(doc_id)
        score = lambda_lex * _rrf(r_lex, k) + lambda_sem * _rrf(r_sem, k)
        fused.append((doc_id, score))

    fused.sort(key=lambda kv: kv[1], reverse=True)

    if limit is not None and limit >= 0:
        fused = fused[:limit]

    return fused
